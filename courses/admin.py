from django.contrib import admin
from .models import tb_roles, tb_course, tb_faculty, tb_lesson_plan
# Register your models here.
admin.site.register(tb_roles)
admin.site.register(tb_course)
admin.site.register(tb_faculty)
admin.site.register(tb_lesson_plan)
