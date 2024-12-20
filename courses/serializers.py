from rest_framework import serializers
from .models import tb_course_outcomes

class CourseOutcomeSerializer(serializers.ModelSerializer):
    class Meta:
        model = tb_course_outcomes
        fields = '__all__'



from .models import TbIctTool

class TbIctToolSerializer(serializers.ModelSerializer):
    class Meta:
        model = TbIctTool
        fields = ['id', 'ict_tool_used', 'details', 'course_code']