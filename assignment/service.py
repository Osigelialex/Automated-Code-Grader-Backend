import docker
import tempfile
from pathlib import Path
from typing import Dict, List, Tuple
import logging

logger = logging.getLogger(__name__)

class CodeExecutionService:
    DOCKER_IMAGES = {
        'Python': 'python-runner',
        'Java': 'java-runner',
        'C++': 'cpp-runner'
    }

    FILE_EXTENSIONS = {
        'Python': '.py',
        'Java': '.java',
        'C++': '.cpp'
    }

    def __init__(self):
        self.docker_client = docker.from_client()
 
    def prepare_python_file(self, code: str, input_data: str) -> Tuple[str, str]:
        """Prepare Python file with code and input handling."""
        wrapped_code = f"""
            import sys

            def main():
            {code}

            if __name__ == '__main__':
                input_data = sys.stdin.read().strip()
                result = main(input_data)
                print(result)
            """
        return wrapped_code, input_data

    def prepare_java_file(self, code: str, input_data: str) -> Tuple[str, str]:
        """Prepare Java file with code and input handling."""
        wrapped_code = f"""
            import java.util.Scanner;

            public class Solution {{
                {code}
                
                public static void main(String[] args) {{
                    Scanner scanner = new Scanner(System.in);
                    String input = scanner.nextLine();
                    String result = main(input);
                    System.out.println(result);
                }}
            }}
            """
        return wrapped_code, input_data

    def prepare_cpp_file(self, code: str, input_data: str) -> Tuple[str, str]:
        """Prepare C++ file with code and input handling."""
        wrapped_code = f"""
            #include <iostream>
            #include <string>

            {code}

            int main() {{
                std::string input;
                std::getline(std::cin, input);
                std::string result = main(input);
                std::cout << result << std::endl;
                return 0;
            }}
            """
        return wrapped_code, input_data

    def execute_code(self, code: str, language: str, test_cases: List[Dict]) -> Dict:
        """Execute code against test cases and return results."""
        if language not in self.DOCKER_IMAGES:
            raise ValueError(f"Unsupported language: {language}")

        # Create temporary directory for code execution
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_dir_path = Path(temp_dir)

            # Select appropriate file preparation method
            prepare_method = getattr(self, f'prepare_{language.lower()}_file')

            # Prepare the code file
            file_extension = self.FILE_EXTENSIONS[language]
            code_file = temp_dir_path / f'solution{file_extension}'
            
            # Process test cases
            passed_tests = []
            failed_tests = []

            for test_case in test_cases:
                # Prepare code with input handling
                wrapped_code, input_data = prepare_method(code, test_case['input'])
                
                # Write code to file
                with open(code_file, 'w') as f:
                    f.write(wrapped_code)

                try:
                    # Run the container
                    container = self.docker_client.containers.run(
                        self.DOCKER_IMAGES[language],
                        volumes={
                            str(temp_dir_path): {'bind': '/app', 'mode': 'ro'}
                        },
                        stdin_open=True,
                        detach=True,
                        mem_limit='512m',
                        memswap_limit='512m',
                        cpus=0.5,
                        timeout=30
                    )

                    # Send input to container
                    container.exec_run(f'echo "{input_data}" | /app/solution{file_extension}')
                    
                    # Get output
                    output = container.logs().decode().strip()

                    # Clean up container
                    container.remove(force=True)
                    
                    # Compare output
                    if output == test_case['output']:
                        passed_tests.append(test_case)
                    else:
                        failed_tests.append({
                            'test_case': test_case,
                            'actual_output': output
                        })
          
                except Exception as e:
                    logger.error(f"Error executing code: {str(e)}")
                    failed_tests.append({
                        'test_case': test_case,
                        'error': str(e)
                    })

        return {
            'passed_tests': passed_tests,
            'failed_tests': failed_tests,
            'total_tests': len(test_cases),
            'passed_count': len(passed_tests)
        }
