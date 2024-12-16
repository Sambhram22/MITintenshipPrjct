from django.urls import path  # Use path() instead of url()
from . import views

urlpatterns = [


    path('getcourselist/', views.getCourseList, name='getCourseList'),
    path('addLessonDetails/', views.addLessonDetails, name='addLessonDetails'), 
    path('uploadFacultyList/', views.uploadFacultyList, name='uploadFacultyList'),
    path('addFacultyRow/', views.addFacultyRow, name='addFacultyRow'),
    path('addCourseDesc/', views.addCourseDesc, name='addCourseDesc')
]
