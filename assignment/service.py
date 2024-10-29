import docker
import json
from typing import List, Dict, Any

class CodeExecutionService:
    """
    Service to execute users' code in sandboxed environment supporting Python and Java.
    """
    def __init__(self):
        self.client = docker.from_env()

    def prepare_python_code(self, user_code: str, input_array: List) -> str:
        """Prepare Python code with direct input array for execution."""
        input_str = json.dumps(input_array)
        complete_code = f"""
{user_code}

print(main({input_str}))
"""
        return complete_code

    def prepare_java_code(self, user_code: str, input_array: List) -> str:
        """Prepare Java code with direct input array for execution."""
        # Convert input array to Java array string representation
        input_str = str(input_array).replace('[', '{').replace(']', '}')
        
        # Extract the user's method from their code
        method_lines = [line for line in user_code.split('\n') if line.strip()]
        
        complete_code = f"""
public class Main {{
    {user_code}
    
    public static void main(String[] args) {{
        int[] input = {input_str};
        System.out.println(main(input));
    }}
}}
"""
        return complete_code

    def create_java_container(self, code: str) -> Any:
        """Create a Java container and set up the environment."""
        return self.client.containers.run(
            'openjdk:11-slim',
            command=['/bin/bash', '-c', 'mkdir -p /app && cd /app && echo "$JAVA_CODE" > Main.java && javac Main.java && java Main'],
            environment={
                'JAVA_CODE': code
            },
            detach=True,
            stdout=True,
            stderr=True,
            mem_limit='128m',
            cpu_period=100000,
            cpu_quota=50000,
            network_disabled=True
        )

    def create_python_container(self, code: str) -> Any:
        """Create a Python container and set up the environment."""
        return self.client.containers.run(
            'python:3.9-slim',
            command=['python', '-c', code],
            detach=True,
            stdout=True,
            stderr=True,
            mem_limit='128m',
            cpu_period=100000,
            cpu_quota=50000,
            network_disabled=True
        )

    def execute_code(self, code: str, language: str, test_cases: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Executes user's code for multiple test cases and returns results.
        
        Args:
            code (str): The source code to execute.
            language (str): Programming language ("Python" or "Java").
            test_cases (List[Dict[str, Any]]): Test cases with input and output values.
        Returns:
            Dict[str, Any]: Dictionary containing test results and statistics.
        """
        if language not in ["Python", "Java"]:
            return {"error": "Unsupported language. Only Python and Java are supported."}

        try:
            passed_count = 0
            total_tests = len(test_cases)
            test_results = []

            for test_case in test_cases:
                # Prepare the code based on language
                if language == "Python":
                    complete_code = self.prepare_python_code(code, test_case['input'])
                    container = self.create_python_container(complete_code)
                else:  # Java
                    complete_code = self.prepare_java_code(code, test_case['input'])
                    container = self.create_java_container(complete_code)

                try:
                    # Wait for execution with timeout
                    result = container.wait(timeout=10)
                    
                    # Get the output
                    stdout = container.logs(stdout=True, stderr=False).decode('utf-8').strip()
                    stderr = container.logs(stdout=False, stderr=True).decode('utf-8').strip()
                    
                    if stderr:
                        actual_output = f"Error: {stderr}"
                        passed = False
                    else:
                        try:
                            actual_output = int(stdout)  # Convert output to integer
                            passed = actual_output == test_case['output']
                            if passed:
                                passed_count += 1
                        except ValueError:
                            actual_output = f"Error: Invalid output format - {stdout}"
                            passed = False

                    test_results.append({
                        "input": test_case['input'],
                        "expected_output": test_case['output'],
                        "actual_output": actual_output,
                        "passed": passed
                    })

                finally:
                    # Clean up container
                    try:
                        container.stop(timeout=1)
                    except:
                        pass
                    container.remove(force=True)

            return {
                "total_tests": total_tests,
                "passed_count": passed_count,
                "test_results": test_results
            }

        except docker.errors.DockerException as e:
            return {"error": f"Docker error: {str(e)}"}
        except Exception as e:
            return {"error": f"Unexpected error: {str(e)}"}