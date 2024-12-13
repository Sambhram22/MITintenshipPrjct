from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.db import connection
from .models import tb_faculty
import pandas as pd
from django.http import JsonResponse  # Add this import




# from .models import tb_users
from datetime import datetime
from django.utils import timezone
from django.db import connection
from rest_framework import status
# Create your views here.

@api_view(['POST'])
def getCourseList(request):
    print("sdjfnjiosnfoj")
    faculty_id = request.data.get('faculty_id')
    academic_year = request.data.get('academic_year')

    query = """
        SELECT course_id, course_name, course_number
        FROM tb_course
        WHERE faculty_id = %s AND academic_year = %s
    """
    
    # Execute the query using the database connection
    with connection.cursor() as cursor:
        cursor.execute(query, [faculty_id, academic_year])
        rows = cursor.fetchall()

    # Prepare the response data
    courses = []
    for row in rows:
        courses.append({
            'course_id': row[0],
            'course_name': row[1],
            'course_no': row[2]
        })
    print(courses)
    result = {
        "result":True,
        "message":"Fetched succesfully",
        "courses":courses
    }
    
    return Response(result, status=status.HTTP_200_OK)







@api_view(['POST'])
def addLessonDetails(request):
    """
    API to add 'description' and 'co_num' for multiple lesson plans.
    Input: lesson_id (array), description (array), co_num (array), course_id, academic_year
    """
    # Extract input data from the request
    lesson_ids = request.data.get('lesson_id')
    descriptions = request.data.get('description')
    co_nums = request.data.get('co_num')
    course_id = request.data.get('course_id')
    academic_year = request.data.get('academic_year')

    # Validate input
    if not all([lesson_ids, descriptions, co_nums, course_id, academic_year]):
        return Response({"result": False, "message": "All fields are required."}, status=status.HTTP_400_BAD_REQUEST)

    if not (isinstance(lesson_ids, list) and isinstance(descriptions, list) and isinstance(co_nums, list)):
        return Response({"result": False, "message": "lesson_id, description, and co_num must be arrays."}, status=status.HTTP_400_BAD_REQUEST)

    if not (len(lesson_ids) == len(descriptions) == len(co_nums)):
        return Response({"result": False, "message": "Arrays lesson_id, description, and co_num must have the same length."}, status=status.HTTP_400_BAD_REQUEST)

    try:
        # Insert the data into the database
        query = """
            INSERT INTO tb_lesson_plan (lesson_id, descrption, co_num, course_id, academic_year)
            VALUES (%s, %s, %s, %s, %s)
        """
        with connection.cursor() as cursor:
            for lesson_id, description, co_num in zip(lesson_ids, descriptions, co_nums):
                cursor.execute(query, [lesson_id, description, co_num, course_id, academic_year])

        result = {
            "result": True,
            "message": "Lesson details inserted successfully."
        }
        return Response(result, status=status.HTTP_200_OK)

    except Exception as e:
        # Handle any errors that occur during the database operation
        return Response({
            "result": False,
            "message": f"An error occurred: {str(e)}"
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET', 'POST'])
def uploadFacultyList(request):
    if request.method == 'POST':
        try:
            # Get the uploaded file
            excel_file = request.FILES['file']
            print(excel_file)

            # Check if the file has the correct extension
            if not excel_file.name.endswith('.xlsx') and not excel_file.name.endswith('.xls'):
                return render(request, 'courses/index.html', {
                    "result": False,
                    "message": "File not proper"
                })

            # Use pandas to read the Excel file (openpyxl is used under the hood)
            df = pd.read_excel(excel_file)
            print(df)

            # Loop through the rows of the DataFrame and save to the database
            for index, row in df.iterrows():
                # Extract data from the row
                seniority = row.get('Sl.No')
                id = row.get('ID')
                faculty_name = row.get('Name of the Faculty', '')  # Default empty string if not present
                faculty_designation = row.get('Designation', '')  # Default empty string if not present

                # Create a new student record in the database
                tb_faculty.objects.create(
                    seniority=seniority,
                    faculty_id=id,
                    faculty_name=faculty_name,
                    faculty_password="Manipal@123",
                    role_id=1,
                    designation = faculty_designation
                )

            return render(request, 'courses/index.html', {
                "result": True,
                "message": "Data successfully uploaded!"
            })
        except Exception as e:
            print(f"Error: {e}")
            return render(request, 'courses/index.html', {
                "result": False,
                "message": "Error occurred while uploading the file."
            })
    else:
        return render(request, 'courses/index.html')

@api_view(['POST'])
def addFacultyRow(request):
    if request.method == 'POST':
        try:
            # Extract form data from the POST request
            seniority = request.POST.get('seniority', None)
            faculty_id = request.POST.get('facultyID', None)
            faculty_name = request.POST.get('facultyName', None)
            designation = request.POST.get('designation', None)
            # Assuming faculty is non-admin
            role = 2

            # Ensure all fields are provided
            if not all([faculty_id, faculty_name, designation]):
                return JsonResponse({
                    "result": False,
                    "message": "All fields (Faculty ID, Name, Designation) are required."
                })

            # Query to get the max seniority value
            query_seniority = "SELECT MAX(seniority) FROM tb_faculty"
            
            # Execute the query to get the current max seniority
            with connection.cursor() as cursor:
                cursor.execute(query_seniority)
                rows = cursor.fetchall()

            # Ensure we have a result from the query
            if rows and rows[0][0] is not None:
                max_seniority = int(rows[0][0])
            else:
                max_seniority = 0  # If no records exist, max seniority would be 0

            # Check if the seniority value is within acceptable range
            if int(seniority) > max_seniority + 1:
                return JsonResponse({
                    "result": False,
                    "message": f"Seniority can be at max {max_seniority + 1}!"
                })
            
            # Update the seniority of existing faculty records if necessary
            query_update_seniority = "UPDATE tb_faculty SET seniority = seniority + 1 WHERE seniority >= %s"
            with connection.cursor() as cursor:
                cursor.execute(query_update_seniority, [int(seniority)])

            # Create a new faculty record in the database
            tb_faculty.objects.create(
                seniority=seniority,
                faculty_id=faculty_id,
                faculty_name=faculty_name,
                faculty_password="Manipal@123",  # Default password 
                role_id=role,  # Assuming role_id is 2 for non-admin faculty
                designation=designation
            )

            # Return success response
            return JsonResponse({
                "result": True,
                "message": "Faculty member added successfully!"
            })
        except Exception as e:
            # Log and return error response
            print(f"Error: {e}")
            return JsonResponse({
                "result": False,
                "message": "An error occurred while adding the faculty member."
            })

 


