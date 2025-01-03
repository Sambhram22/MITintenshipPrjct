from django.db import models



# class tb_users(models.Model):
#     userName = models.CharField(max_length=100)
#     emailID = models.EmailField(unique=True)
#     phoneNo = models.CharField(max_length=15)

#     def __str__(self):
#         return self.userName
    
# class tb_user_new(models.Model):
#     userName1 = models.CharField(max_length=100)
#     emailId1 = models.EmailField(unique=True)
#     phoneNo1 = models.CharField(max_length=15)

#     def __str__(self):
#         return self.userName1

class tb_roles(models.Model):
    role_id = models.AutoField(primary_key=True)  # Auto incremented primary key
    role_name = models.CharField(max_length=45, null=True, blank=True)
    faculty = models.CharField(max_length=45, null=True, blank=True)

    class Meta:
        db_table = 'tb_roles'  # Specify the table name

    def __str__(self):
        return self.role_name or "No Name"

class tb_faculty(models.Model):
    seniority = models.IntegerField(null=False)
    faculty_id = models.CharField(max_length=45, primary_key=True)
    faculty_name = models.CharField(max_length=255, null=False)
    faculty_password = models.CharField(max_length=50, null=False)
    role_id = models.IntegerField()  # Storing role_id as an integer, no foreign key
    designation = models.CharField(max_length=45, null=False)

    class Meta:
        db_table = 'tb_faculty'  # The table name in MySQL

    def __str__(self):
        return self.faculty_name



class tb_course(models.Model):
    course_id = models.AutoField(primary_key=True)
    course_name = models.CharField(max_length=255)
    academic_year = models.IntegerField()
    faculty_id = models.IntegerField(null=True, blank=True)  # faculty_id as IntegerField
    course_number = models.CharField(max_length=45, null=True, blank=True)  # Added course_number field

    class Meta:
        db_table = 'tb_course'  # The table name in MySQL

    def __str__(self):
        return self.course_name
    

class tb_course_faculty_mapping(models.Model):
    course_code = models.CharField(max_length=45, primary_key=False)  
    faculty_id = models.CharField(max_length=45)
    academic_year = models.IntegerField()
   
    class Meta:
        db_table = 'tb_course_faculty_mapping'  # Table name in MySQL

    def __str__(self):
        return self.student_name
class tb_lesson_plan(models.Model):
    id = models.AutoField(primary_key=True)  # Auto-incrementing primary key
    lesson_id = models.IntegerField(unique=True)  # Unique lesson_id
    description = models.CharField(max_length=255)  # Lesson description
    course_no = models.CharField(max_length=5)  # CO number
    course_id = models.IntegerField()  # Course ID
    academic_year = models.IntegerField()
    class Meta:
        db_table = 'tb_lesson_plan'  # The table name in MySQL

    def __str__(self):
        return f"Lesson Plan {self.lesson_id} for Course {self.course_id}"



class tb_course_outcomes(models.Model):
    id = models.BigAutoField(primary_key=True)
    co_num = models.CharField(max_length=255)
    description = models.TextField()
    contact_hours = models.PositiveIntegerField()  # Ensures non-negative integers
    marks = models.IntegerField()
    program_outcomes = models.CharField(max_length=15)
    program_spec_outcomes = models.CharField(max_length=50)
    learning_outcomes = models.CharField(max_length=20)
    bl = models.CharField(max_length=10)
    course_code = models.CharField(max_length=45)

    class Meta:
        db_table = 'tb_course_outcomes'  # Optional: matches the table name in the database
        constraints = [
            models.CheckConstraint(check=models.Q(contact_hours__gte=0), name='tb_course_outcomes_chk_1'),
        ]

    def __str__(self):
        return f"{self.co_num}: {self.description[:50]}..."  # Truncate for readability
    

from django.db import models

class TbIctTool(models.Model):
    id = models.AutoField(primary_key=True)  # Auto-incrementing primary key
    ict_tool_used = models.CharField(max_length=200)  # Corresponds to VARCHAR(200)
    details = models.CharField(max_length=250)  # Corresponds to VARCHAR(250)
    course_code = models.CharField(max_length=45)  # Corresponds to VARCHAR(45)

    class Meta:
        db_table = 'tb_ict_tools'  # Explicitly sets the table name
        verbose_name = 'ICT Tool'
        verbose_name_plural = 'ICT Tools'

    def __str__(self):
        return f"{self.ict_tool_used} - {self.course_code}"



