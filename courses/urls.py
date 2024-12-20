from django.urls import path  # Use path() instead of url()
from . import views

urlpatterns = [


    path('getcourselist/', views.getCourseList, name='getCourseList'),
    path('addLessonDetails/', views.addLessonDetails, name='addLessonDetails'), 
    path('uploadFacultyList/', views.uploadFacultyList, name='uploadFacultyList'),
    path('addFacultyRow/', views.addFacultyRow, name='addFacultyRow'),
    path('addCourseDesc/', views.addCourseDesc, name='addCourseDesc'),
    path('getFacultyList/', views.getFacultyList, name='getFacultyList'),
    path('getCourseOutcomes/', views.getCourseOutcomes, name='getCourseOutcomes'),
    path('getCourseOutcomesPage/', views.getCourseOutcomesPage, name='getCourseOutcomesPage'),
    path('getCourseOutcomesPage/api/add_course_outcome/', views.add_course_outcome_api, name='add_course_outcome_api'),
    path('updateCourseOutcome/<int:id>/', views.updateCourseOutcome, name='updateCourseOutcome')
   
    
]
