from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.db import connection
from .models import tb_faculty, tb_course_outcomes
import pandas as pd
from django.http import JsonResponse  # Add this import
from .models import tb_course_faculty_mapping
from django.db.models import Max, F
from . import models
from django.db.models import F







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

from django.http import JsonResponse

@api_view(['POST', 'GET'])
def uploadFacultyList(request):
    if request.method == 'POST':
        try:
            # Get the uploaded file
            excel_file = request.FILES['file']
            print(f"Received file: {excel_file.name}")

            # Check if the file has the correct extension
            if not excel_file.name.endswith(('.xlsx', '.xls')):
                return JsonResponse({
                    "result": False,
                    "message": "Invalid file format. Please upload an Excel file."
                })

            # Use pandas to read the Excel file
            df = pd.read_excel(excel_file)
            print(f"Data read from Excel: {df}")

            # Initialize variables to store error and success information
            existing_faculty_ids = set(tb_faculty.objects.values_list('faculty_id', flat=True))
            error_rows = []  # List to track existing faculty IDs
            uploaded_rows = []  # List to track successfully uploaded records

            used_seniorities = set(tb_faculty.objects.values_list('seniority', flat=True))

            # Loop through the rows of the DataFrame
            for index, row in df.iterrows():
                # Extract data from the row
                seniority = row.get('Sl.No')
                faculty_id = row.get('ID')
                faculty_name = row.get('Name of the Faculty', '')
                faculty_designation = row.get('Designation', '')

                # Skip if faculty_id or seniority is missing or invalid
                if pd.isna(faculty_id) or pd.isna(seniority):
                    continue

                conflicting_records = tb_faculty.objects.filter(seniority__gte=seniority).order_by('seniority')

                if conflicting_records.exists():
                # Step 2: Shift the seniority of existing records in ascending order
                    for record in conflicting_records:
                    # Only increment seniority if the record's seniority is >= excel_seniority
                        if record.seniority >= seniority:
                            record.seniority += 1
                            record.save()



                # Check if the faculty ID already exists
                if faculty_id in existing_faculty_ids:
                    # If the faculty ID exists, add to the error list
                    error_rows.append(faculty_id)
                else:
                    # If faculty ID does not exist, add to the database and track success
                    tb_faculty.objects.create(
                        seniority=seniority,
                        faculty_id=faculty_id,
                        faculty_name=faculty_name,
                        faculty_password="Manipal@123",  # Default password
                        role_id=1,
                        designation=faculty_designation
                    )
                    uploaded_rows.append(faculty_id)

                used_seniorities.add(seniority)

            # Prepare messages based on the result
            if error_rows:
                error_message = f"Some faculty IDs already exist in the database:\n" + "\n".join(map(str, error_rows))
                success_message = f"{len(uploaded_rows)} records successfully uploaded!"
                return JsonResponse({
                    "result": False,
                    "message": error_message + "\n\n" + success_message
                })

            success_message = f"Successfully uploaded {len(uploaded_rows)} records!"
            return JsonResponse({
                "result": True,
                "message": success_message
            })

        except Exception as e:
            # Print the error and traceback
            print(f"Error: {e}")
            return JsonResponse({
                "result": False,
                "message": f"An error occurred while uploading the file: {str(e)}"
            })
    else:
        return render(request, "courses/index.html")


    

@api_view(['POST'])
def addFacultyRow(request):
    if request.method == 'POST':
        try:
            # Extract form data
            faculty_id = request.POST.get('facultyID', None)
            faculty_name = request.POST.get('facultyName', None)
            designation = request.POST.get('designation', None)
            seniority = request.POST.get('seniority', None)

            # Ensure required fields are provided
            if not all([faculty_id, faculty_name, designation, seniority]):
                return JsonResponse({
                    "result": False,
                    "message": "All fields (Faculty ID, Name, Designation, Seniority) are required."
                })

            # Check if the faculty ID already exists
            if tb_faculty.objects.filter(faculty_id=faculty_id).exists():
                return JsonResponse({
                    "result": False,
                    "message": f"Faculty ID '{faculty_id}' already exists in the database."
                })

            # Additional seniority validation (if applicable)
            max_seniority = tb_faculty.objects.aggregate(Max('seniority'))['seniority__max'] or 0
            if int(seniority) > max_seniority + 1:
                return JsonResponse({
                    "result": False,
                    "message": f"Seniority can be at max {max_seniority + 1}."
                })

            # Update seniority of existing records
            tb_faculty.objects.filter(seniority__gte=int(seniority)).update(
                seniority=F('seniority') + 1
            )

            # Create the new faculty record
            tb_faculty.objects.create(
                faculty_id=faculty_id,
                faculty_name=faculty_name,
                designation=designation,
                seniority=seniority,
                faculty_password="Manipal@123",  # Default password
                role_id=2  # Assuming role_id is 2 for non-admin faculty
            )

            return JsonResponse({
                "result": True,
                "message": "Faculty member added successfully."
            })

        except Exception as e:
            print(f"Error: {e}")
            return JsonResponse({
                "result": False,
                "message": "An error occurred while adding the faculty member."
            })



#api to fetch courseid from database for adding course description
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

@csrf_exempt
def addCourseDesc(request):
    if request.method == "GET":
        faculty_id = request.GET.get("facultyId")
        # Replace with actual query logic to fetch courses for the faculty
        courses = [
            {"course_id": "CSE101"},
            {"course_id": "CSE102"},
        ]
        return JsonResponse({"courses": courses})

    elif request.method == "POST":
        data = json.loads(request.body)
        faculty_id = data.get("facultyId")
        course_id = data.get("courseId")
        description = data.get("description")

        # Replace with logic to save the description to the database
        # Example:
        # Course.objects.filter(course_id=course_id, faculty_id=faculty_id).update(description=description)

        return JsonResponse({"message": "Description saved successfully!"})

    return JsonResponse({"error": "Invalid request method."}, status=400)


@api_view(['GET'])
def getFacultyList(request):
    try:
        # SQL query to fetch faculty details
        query = """
            SELECT seniority, faculty_id, faculty_name, designation
            FROM tb_faculty
            ORDER BY seniority
        """

        # Execute the query using the database connection
        with connection.cursor() as cursor:
            cursor.execute(query)
            rows = cursor.fetchall()

        # Prepare the response data
        faculty_list = []
        for row in rows:
            faculty_list.append({
                'seniority': row[0],
                'faculty_id': row[1],
                'faculty_name': row[2],
                'designation': row[3]
            })

        # Response structure
        result = {
            "result": True,
            "message": "Fetched successfully",
            "faculty_list": faculty_list
        }

        return Response(result, status=status.HTTP_200_OK)

    except Exception as e:
        # Catch any exception and return a server error message
        return Response({
            "result": False,
            "message": f"An error occurred: {str(e)}"
        }, status=status.HTTP_200_OK)



@api_view(['GET'])
def getCourseOutcomes(request):
    try:
        # Get faculty ID and role ID
        faculty_id = request.query_params.get('faculty_id')
        role_id = request.query_params.get('role_id')
        print(role_id)
        print(faculty_id)
        
        whereClause = ' WHERE 1=1 '
        if role_id == '2' or role_id=='3':  # Ensure role_id is compared as a string
            # Sanitize faculty_id to prevent SQL injection
            faculty_id = str(faculty_id).replace("'", "''")
            whereClause = f" WHERE course_code IN (SELECT course_code FROM tb_course_faculty_mapping WHERE faculty_id = '{faculty_id}')"
        
        # Construct the query
        query = f"""
            SELECT co_num, description, contact_hours, marks, program_outcomes, program_spec_outcomes, bl, course_code,id
            FROM tb_course_outcomes
            {whereClause}
            ORDER BY id
        """

        # Execute the query using the database connection
        with connection.cursor() as cursor:
            cursor.execute(query)
            rows = cursor.fetchall()

        # Debugging: Print the fetched rows
      #  print("Fetched rows:", rows)

        # Prepare the response data
        course_outcome = []

        for row in rows:
            course_outcome.append({
                'co_num': row[0],
                'description': row[1],
                'contact_hours': row[2],
                'marks': row[3],
                'program_outcomes': row[4],
                'program_spec_outcomes': row[5],
                'bl': row[6],
                'course_code': row[7],
                'id':row[8]
            })
        print(course_outcome)
        # Response structure
        result = {
            "result": True,
            "message": "Fetched successfully",
            "course_outcome": course_outcome
        }

        return Response(result, status=status.HTTP_200_OK)

    except Exception as e:
        # Debugging: Log the exception
        print("Error occurred:", str(e))
        return Response({
            "result": False,
            "message": f"An error occurred: {str(e)}"
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



from django.shortcuts import render, redirect

@api_view(['GET'])
def getCourseOutcomesPage(request):
    return render(request, 'courses/course_outcome.html')  # Render form template for GET requests


from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .serializers import CourseOutcomeSerializer

@api_view(['POST'])
def add_course_outcome_api(request):
    if request.method == 'POST':
        serializer = CourseOutcomeSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'Course outcome added successfully'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



@api_view(['PUT'])
def updateCourseOutcome(request,id):
    try:
        # Get parameters from the request
        # id = request.query_params.get('id')
        contact_hours = request.data.get('contact_hours')
        marks = request.data.get('marks')

        if not id or contact_hours is None or marks is None:
            return Response({"result": False, "message": "Missing required parameters"}, status=status.HTTP_400_BAD_REQUEST)

        # Update query
        query = "UPDATE tb_course_outcomes SET contact_hours = %s, marks = %s WHERE id = %s"

        with connection.cursor() as cursor:
            cursor.execute(query, [contact_hours, marks, id])
            rows = cursor.fetchall()

        if rows:
            return Response({"result": False, "message": "Course outcome not found"}, status=status.HTTP_404_NOT_FOUND)

        # Return success response
        result = {
            "result": True,
            "message": "Updated successfully",
        }

        return Response(result, status=status.HTTP_200_OK)

    except Exception as e:
        # Log the exception (optional)
        print(f"Error occurred: {e}")
        
        # Return error response
        return Response({"result": False, "message": f"An error occurred: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

