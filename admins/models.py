from datetime import datetime
from django.db import models
from django.contrib.auth.models import AbstractUser, UserManager
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
import uuid

# Create your models here.
def numeric_validator(value):
    if not value.isnumeric():
        raise ValidationError(_("This field should only contain numbers"))
def phone_validator(value):
    if not value.isnumeric():
        raise ValidationError(_("The phone number is not a number"))
    if len(value) != 11:
        raise ValidationError(_("The phone number should be 11 digits"))
    phone_start_number = ['081','080','090','091','070']
    if value[:3]  in phone_start_number:
        pass
    else:
        raise ValidationError(_("Enter a valid nigerian number"))

def alpha_validator(value):
    if not value.isalpha():
        raise ValidationError(_("This field should only contain alphabets"))

class BaseManager(UserManager):
    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        """
        Create and save a user with the given username, email, and password.
        """
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(email, password, **extra_fields)
class User(AbstractUser):
    username = None
    email = models.EmailField(
        _('Email'),
        max_length=150,
        unique=True,
        help_text=_('Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.'),
        error_messages={
            'unique': _("A user with that email already exists."),
        },
    )
    is_student = models.BooleanField(default=False)
    is_auth_staff = models.BooleanField(default=False)
    objects = BaseManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

def get_deleted_user():
    return User.objects.get_or_create(email ="deleted_user@gmail.com")[0]


class Admin(models.Model):
    class ROLE(models.TextChoices):
        SUPERADMIN = 1,"superadmin"
        NORMALADMIN = 2,"normaladmin"

    user = models.OneToOneField(User,on_delete=models.CASCADE)
    firstname = models.CharField(max_length=55,validators=[alpha_validator])
    lastname = models.CharField(max_length=55,validators=[alpha_validator])
    
    image = models.ImageField(upload_to = 'admin-images',blank = True)
    phonenumber = models.CharField(
        _('Phone Number'),
        max_length=11,
        validators = [phone_validator],
        help_text=_('Required. 11 Nigeria Phone Numbers.'),
        error_messages={
            'max_length': _("11 Numbers required."),
        },
        unique=True,
    )
    role = models.CharField(max_length=2, choices=ROLE.choices, default=ROLE.NORMALADMIN)
    def __str__(self):
        return self.firstname+" "+self.lastname

class Faculty(models.Model):
    id = models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True)
    name = models.CharField(max_length=100)
    department_numbers = models.IntegerField()
    officer = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return self.name

class Department(models.Model):
    id = models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True)
    name =  models.CharField(max_length=100, unique=True)
    faculty = models.ForeignKey(Faculty, on_delete=models.CASCADE)
    level_number = models.IntegerField(default=4)
    slug = models.SlugField(blank=True, null=True)
    head_of_dept = models.OneToOneField("Staff",related_name="depthead",null=True,blank=True, on_delete=models.SET_NULL)

    def __str__(self):
        return self.name

def get_deleted_faculty():
    return Faculty.objects.get_or_create(name="deleted_faculty", department_numbers = 0)[0]

def get_deleted_department():
    deleted_user = Department.objects.get_or_create(name="deleted_department",faculty=get_deleted_faculty(),slug="deleted-department")
    return deleted_user[0]

class LEVEL(models.IntegerChoices):
        LEVEL100 = 1,"100 Level"
        LEVEL200 = 2,"200 Level"
        LEVEL300 = 3,"300 Level"
        LEVEL400 = 4,"400 Level"
        LEVEL500 = 5,"500 Level"
        LEVEL600 = 6,"600 Level"
class SEMESTER(models.IntegerChoices):
        FIRST = 1, "First Semester"
        SECOND = 2, "Second Semester"

class Course(models.Model):
    class SEMESTER(models.IntegerChoices):
        FIRST = 1, "First Semester"
        SECOND = 2, "Second Semester"
    title = models.CharField(max_length=100)
    code = models.CharField(max_length=10)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    level = models.IntegerField(choices=LEVEL.choices)
    semester = models.IntegerField(choices=SEMESTER.choices)
    course_outline = models.TextField()

    def __str__(self):
        return self.code



class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    matric_number = models.CharField(max_length=11, unique=True)
    department = models.ForeignKey(Department,on_delete=models.SET(get_deleted_department))
    level = models.IntegerField(choices=LEVEL.choices)
    firstname = models.CharField("First Name",max_length=55,validators=[alpha_validator])
    middlename = models.CharField("Middle Name",max_length=55,blank=True,validators=[alpha_validator])
    lastname = models.CharField("Last Name",max_length=55,validators=[alpha_validator])
    dob = models.DateField("Date of Birth")
    sex = models.CharField(max_length=10,choices=(('M','Male'),('F','Female')))
    phonenumber = models.CharField(
        _('Phone Number'),
        max_length=11,
        validators = [phone_validator],
        help_text=_('Required. 11 Nigeria Phone Numbers.'),
        error_messages={
            'max_length': _("11 Numbers required."),
        },
        unique=True,
    )
    email = models.EmailField(
        _('Email'),
        max_length=150,
        unique=True,
        help_text=_('Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.'),
        error_messages={
            'unique': _("A user with that email already exists."),
        },
    )
    state = models.CharField(max_length=20)
    lga = models.CharField("Local Government Area",max_length=50)
    hometown = models.CharField("Home Town",max_length=50)
    residential_address = models.TextField(default="Prefer not to say",max_length=1000)
    image = models.ImageField(upload_to = "students",blank = True,null = True)
    guardianname = models.CharField("Guardian Name",max_length=55, blank=True)
    guardianphonenumber = models.CharField(_('Phone Number'),max_length=11,validators = [phone_validator],
        help_text=_('Required. 11 Nigeria Phone Numbers.'),error_messages={
            'max_length': _("11 Numbers required."),
        }, blank=True)
    guardianemail = models.EmailField(blank=True)
    status = models.BooleanField(default=True)
    profile_complete = models.BooleanField(default=False)
    def __str__(self):
        return self.firstname +' '+self.lastname

class Staff(models.Model):

    class ROLE(models.TextChoices):
        HOD = 1,"Head of Department"
        DEPARTMENTADMIN = 2,"Department Admin"
        EXAMOFFICER = 3,"Exam Officer"
        NORMALSTAFF = 4,"Normal Staff"
    
    user = models.OneToOneField(User,on_delete=models.CASCADE, blank = True,null = True)
    firstname = models.CharField("First Name",max_length=55,validators=[alpha_validator])
    lastname = models.CharField("Last Name",max_length=55,validators=[alpha_validator])
    dob = models.DateField("Date of Birth", blank=True, null=True)
    sex = models.CharField(max_length=10,choices=(('M','Male'),('F','Female')))
    phonenumber = models.CharField(_('Phone Number'),max_length=11,validators = [phone_validator],
        help_text=_('Required. 11 Nigeria Phone Numbers.'),error_messages={
            'max_length': _("11 Numbers required."),
        },unique=True, blank=True)
    state = models.CharField(max_length=20, blank=True, null=True)
    lga = models.CharField("Local Government Area",max_length=50, blank=True, null=True)
    hometown = models.CharField("Home Town",max_length=50, blank=True, null=True)
    residential_address = models.TextField(default="Prefer not to say",blank=True,max_length=1000)
    image = models.ImageField(upload_to = "staffs",blank = True,null = True)
    
    department = models.ForeignKey(Department, on_delete=models.SET(get_deleted_department))
    role = models.CharField(max_length=2, choices=ROLE.choices, default=ROLE.NORMALSTAFF)


    def __str__(self):
        return self.firstname +" "+self.lastname





class Event(models.Model):
    name = models.CharField(max_length = 50)
    image = models.ImageField(blank=True, null=True, upload_to="events")
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    description = models.TextField(max_length=1500)
    startdate = models.DateField()
    starttime = models.TimeField()
    enddate = models.DateField()
    endtime = models.TimeField()
    attendies_needed = models.BooleanField(default=False)
    attendees = models.ManyToManyField(Student, blank=True)
    published_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class CourseResource(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    name = models.CharField(max_length=200, blank=True, null=True)
    file = models.FileField(upload_to="resources")

    def __str__(self):
        self.course.code

class Information(models.Model):
    title = models.CharField(max_length=100)
    message = models.TextField()
    department = models.ForeignKey(Department,on_delete=models.CASCADE)
    level = models.IntegerField(null=True,choices=LEVEL.choices)
    file = models.FileField(blank=True,null=True, upload_to="infos")
    published_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    
class Clearance(models.Model):
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=300, blank=True, null=True)
    departments = models.ManyToManyField(Department, blank=True)
    cleared_students = models.ManyToManyField(Student, blank=True)

    def __str__(self):
        return self.name

class Registration(models.Model):
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=300, blank=True, null=True)
    departments = models.ManyToManyField(Department, blank=True)
    cleared_students = models.ManyToManyField(Student, blank=True)

    def __str__(self):
        return self.name
class Upload_Assignment(models.Model):
    staff = models.ManyToManyField(Staff,blank=True)
    name = models.CharField(max_length=100)
    def __str__(self):
        return self.name


class Uploads(models.Model):
    staff = models.ForeignKey(Staff,null = True,blank=True,on_delete=models.SET_NULL)
    department = models.ForeignKey(Department,null=True,blank=True,on_delete=models.SET_NULL)
    description = models.TextField(max_length=1000, blank=True)
    document = models.FileField(upload_to="uploads")
    section = models.ForeignKey(Upload_Assignment,null = True,blank=True,on_delete=models.SET_NULL)
    sent_on = models.DateTimeField(auto_now_add=True)

    def save(self, *args,**kwargs):
        if not self.description:
            self.description = self.staff.firstname +" Upload for "+self.department.name
        return super().save(*args,**kwargs)

    def __str__(self):
        return self.description

class SchoolSession(models.Model):
    year = models.CharField(max_length=10, unique=True)
    current = models.BooleanField()

    def __str__(self):
        return self.year

class CourseRegistration(models.Model):
    
    session = models.ForeignKey(SchoolSession,on_delete=models.SET_NULL,null=True)
    semester = models.IntegerField(choices=SEMESTER.choices)
    level = models.IntegerField(choices=LEVEL.choices)
    student = models.ForeignKey(Student,on_delete=models.CASCADE)
    date_submitted = models.DateField(auto_now_add=True)
    last_updated = models.DateField(auto_now=True)

    
    def calculate_unit(self):
        return sum(x.unit for x in self.courseregistrationline_set.all())

    def __str__(self):
        return  "{} - {}".format(self.session,self.student)
    

class CourseRegistrationLine(models.Model):
    course_reg = models.ForeignKey(CourseRegistration, on_delete=models.CASCADE)
    unit = models.IntegerField()
    course = models.ForeignKey(Course,on_delete=models.CASCADE)
    session = models.ForeignKey(SchoolSession, on_delete=models.CASCADE, blank=True, null=True)


    def __str__(self) :
        return "{} - {}".format(self.course,self.session)
        

class DepartmentCourse(models.Model):
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    level = models.IntegerField(choices=LEVEL.choices)
    semester = models.IntegerField(choices=SEMESTER.choices)
    min_unit = models.IntegerField(default=15)
    max_unit  = models.IntegerField(default=25)
    def __str__(self):
        return "{} {} Courses".format(self.get_level_display(), self.get_semester_display())

class DepartmentCourseLine(models.Model):
    dept_course = models.ForeignKey(DepartmentCourse,on_delete=models.CASCADE)
    unit = models.IntegerField()
    course = models.ForeignKey(Course,on_delete=models.CASCADE)

    def __str__(self):
        return "{}".format(self.course)




class SiteSetting(models.Model):
    name = models.CharField(max_length=20)
    value = models.CharField(max_length=50)

    def __str__(self):
        return self.name