from rest_framework import serializers
from .models import tb_course_outcomes

class CourseOutcomeSerializer(serializers.ModelSerializer):
    class Meta:
        model = tb_course_outcomes
        fields = '__all__'