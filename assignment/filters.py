from django_filters import rest_framework as filters

from .models import Assignment


class AssignmentFilter(filters.FilterSet):
    is_draft = filters.BooleanFilter()

    class Meta:
        model = Assignment
        fields = ['is_draft']
