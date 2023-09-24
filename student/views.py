#django imports
from typing import Any
from django.db.models import Q
from django.db.models.query import QuerySet
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import FormView, View, UpdateView, ListView
from django.urls import reverse_lazy, reverse
from django.contrib.auth import login, logout
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.core.mail import send_mail, EmailMessage
from django.http import HttpResponse
from django.contrib.auth.views import PasswordChangeView
from django.utils import timezone

# local imports
from .forms import StudentLoginForm, EditProfileForm, CourseRegForm
from admins.models import Student, Event, Information, CourseResource, Registration, Clearance, Course, DepartmentCourse, CourseRegistration,\
SchoolSession, CourseRegistrationLine


def update_attrs(instance, **kwargs):
    """
    Update multiple attrs of models
    """
    instance_pk = instance.pk
    for key, value in kwargs.items():
        print(value)
        if hasattr(instance, key):
            setattr(instance, key, value)
    instance.save(force_update = True)
    return instance.__class__.objects.get(pk=instance_pk)


def testmailview(request):
    # email = EmailMessage(
    #     "hello from schoolportal",
    #     "I am testing a mail",
    #     ['joshkayweb@gmail.com']
    # )
    # email.send(fail_silently=False)
    send_mail(
        "hello from schoolportal",
        "I am testing a mail",
        "support@vestonoasis.pro",
        ['basetrust22@gmail.com'],
        fail_silently=False,
    )
    return HttpResponse("Mail sent")

def landingview(request):
    return redirect(reverse("student:login"))

class StudentMixin(LoginRequiredMixin, UserPassesTestMixin):
    login_url = "/student/login/"
    def test_func(self):
        return self.request.user.is_student

class LoginView(FormView):
    form_class = StudentLoginForm
    success_url = reverse_lazy("student:dashboard")
    template_name = "student/login.html"

    def get_form_kwargs(self):
        kwargs  = super().get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs
    def form_valid(self, form):
        user = form.get_user()
        department = Student.objects.get(user = user).department
        login(self.request,user,'django.contrib.auth.backends.ModelBackend')
        self.request.session['department'] = str(department.id)
        return super().form_valid(form)
    
class DashboardView(StudentMixin,View):
    def get(self,request):
        return render(request, "student/index.html")
class LogoutView(StudentMixin,View):
    def get(self,request):
        logout(request)
        messages.success(request,"Logout Successful")
        return redirect(reverse('student:login'))
class ProfileView(StudentMixin,View):
    def get(self,request):
        context = {
        }

        data = Student.objects.get(id = request.user.student.id )
  
        context['data'] = data
        return render(request,'student/profile.html',context)

class EditProfileView(StudentMixin,UpdateView):
    model = Student
    template_name = "student/edit-profile.html"
    fields = '__all__'
    success_url = reverse_lazy("student:profile")
    def get_object(self):
        return self.request.user.student
    def form_valid(self,form):
        messages.success(self.request,"Profile Edited Successfully.")
        return super().form_valid(form)
    

class UserPasswordChangeView(StudentMixin,PasswordChangeView):
    template_name = "student/change-password.html"
    success_url = reverse_lazy("student:profile")
    def form_valid(self,form):
        messages.success(self.request,"Password changed.")
        return super().form_valid(form)
    
class CoursesView(StudentMixin, ListView):
    paginate_by = 50
    template_name = "student/courses.html"
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        level = [x+1 for x in range(self.request.department.level_number)]
        context['level'] = level
        return context
    def get_queryset(self):
        course = Course.objects.filter(department = self.request.department)
        getdata = self.request.GET
        if getdata.get("level"):
            course = course.filter(level = getdata['level'])
        if getdata.get("semester"):
            course = course.filter(semester = getdata['semester'])
        return course.order_by('code')

class ResourcesView(StudentMixin, ListView):
    paginate_by = 50
    template_name = "student/resources.html"
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        level = [x+1 for x in range(self.request.department.level_number)]
        context['level'] = level
        return context
    def get_queryset(self):
        resource = CourseResource.objects.filter(course__department = self.request.department)
        getdata = self.request.GET
        if getdata.get("level"):
            resource = resource.filter(course__level = getdata['level'])
        if getdata.get("semester"):
            resource = resource.filter(course__semester = getdata['semester'])
        return resource
    
class InformationView(StudentMixin, ListView):
    template_name = "student/information.html"
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        level = [x+1 for x in range(self.request.department.level_number)]
        context['level'] = level
        return context
    def get_queryset(self):
        information = Information.objects.filter(department = self.request.department)
        getdata = self.request.GET
        if getdata.get("level"):
            information = information.filter(Q(level = getdata['level'])|Q(level = None))
        return information.order_by("-published_date")
    

class EventView(StudentMixin,ListView):
    paginate_by = 15
    template_name = 'student/event.html'
    def get_queryset(self):
        if self.request.GET.get('date'):
            event = Event.objects.filter(startdate = self.request.GET['date']).filter(Q(department = self.request.department)|Q(department  = None))
            return event.order_by('-starttime')
        else:
            event = Event.objects.filter(Q(department = self.request.department)|Q(department  = None))
            return event.order_by("-startdate")

class EventDetailsView(StudentMixin,View):
    def get(self,request,id):
        event = get_object_or_404(Event.objects.filter(Q(department = request.department)|Q(department  = None)),id=id)
        if event.enddate < timezone.now().date():
            event.ended = True
        else:
            event.ended = False
        attending = False
        if request.user.student in event.attendees.all():
            attending = True
        context = {'object':event,'attending':attending}
        return render(request,'student/event-details.html',context)

class EventAttendanceView(StudentMixin,View):
    def get(self,request,id):
        event = get_object_or_404(Event.objects.filter(Q(department = request.department)|Q(department  = None)),id=id)
        event.attendees.add(request.user.student)
        event.save()
        messages.success(request,"You have been added to the attendance list")
        return redirect(reverse("student:event-details", kwargs={'id': id}))
    

def clear_course_reg_session(request):
    if 'session' in request.session:
        del request.session['session'] 
    if 'level' in request.session:    
        del request.session['level'] 
    if 'semester' in request.session:
        del request.session['semester']
    if 'aux_courses' in request.session:
        del request.session['aux_courses']

class CourseRegistrationView(StudentMixin, FormView):
    form_class = CourseRegForm
    template_name = "student/course-reg.html"
    success_url = reverse_lazy('student:register-course')

    
    def form_valid(self, form):
        session = form.cleaned_data['session']
        level = form.cleaned_data['level']
        semester = form.cleaned_data['semester']
        print(session)
        print(level)
        print(semester)
        self.request.session['session'] = str(session)
        self.request.session['level'] = str(level)
        self.request.session['semester'] = str(semester)

        return super().form_valid(form)

class RegisterCourseView(StudentMixin, View):
    def get(self, request):
        if not 'level' in request.session or not 'session' in request.session or not 'semester' in request.session:
            return redirect("student:register-course-form")

        level = request.session['level']
        session = request.session['session']
        semester = request.session['semester']
        department = request.department
        schoolsession = SchoolSession.objects.get(year = session)
        student = request.user.student

        course_reg = CourseRegistration.objects.filter(student = student, session = schoolsession, semester = int(semester))
        if course_reg.exists():
            course_reg = course_reg.first()
            return render(request,'student/registered-courses.html',{'course_reg':course_reg})

        course_list = DepartmentCourse.objects.filter(department = department,level = level, semester = semester)
        courses = []

        if course_list.exists():
            course_list = course_list.first()
            courses = course_list.departmentcourseline_set.all().values('course__id','unit','course__code','course__title')
            # print(courses) # for debugging

        if  'aux_courses' in request.session:
            courses = list(courses)
            courses.extend(request.session['aux_courses'])
        
        return render(request,'student/course-reg-form.html', {'courses':courses,'session':session,'level':level,'semester':semester,
                                                               "min_unit":course_list.min_unit,"max_unit":course_list.max_unit})
    
    def post(self,request):
        if not 'level' in request.POST or not 'session' in request.POST or not 'semester' in request.POST:
            messages.error(request,"Incomplete parameters")
            return redirect("student:register-course-form")
        
        level = int(request.POST['level'])
        session = request.POST['session']
        semester = int(request.POST['semester'])
        department = request.department
        student  = Student.objects.get(user = request.user)
        schoolsession = SchoolSession.objects.get(year = session)

        courses = request.POST.getlist('courses')
        units = request.POST.getlist('units')

        if len(courses) < 1:
            messages.error(request,"You have not registered any course")
            return redirect("student:register-course-form")
        
        course_list = DepartmentCourse.objects.filter(department = department,level = level, semester = semester)
        if course_list.exists():
            course_list = course_list.first()
            units_sum = sum(list(map(int,units)))
            if units_sum < course_list.min_unit:
                messages.error(request,f"Your selected courses unit should not be less than {course_list.min_unit} units")
                return redirect("student:register-course-form")
            elif units_sum > course_list.max_unit:
                messages.error(request,f"Your selected courses unit should not be greater than {course_list.max_unit} units")
                return redirect("student:register-course-form")



        if CourseRegistration.objects.filter(student = student, session = schoolsession, semester = semester).exists():
            messages.error(request,"you have already registered for this session")
            return redirect('student:register-course-form')
        
        course_reg = CourseRegistration()
        course_reg.student = student
        course_reg.session = schoolsession
        course_reg.level = level
        course_reg.semester = semester
        course_reg.save()

        for id,unit in zip(courses,units):
            course = Course.objects.get(id= id)
            CourseRegistrationLine.objects.create(course_reg = course_reg,course = course,unit = unit, session = schoolsession)

        context = {
            'course_reg':course_reg
        }

        return render(request,'student/registered-courses.html',context)


class AddAuxilaryCourse(StudentMixin, View):
    def get(self,request):
        level = request.session['level']
        session = request.session['session']
        semester = request.session['semester']
        department = request.department

        course_list = DepartmentCourse.objects.filter(department = department, semester = semester)
        courses = []

        if course_list.exists():
            for course in course_list:
                dept_course = course.departmentcourseline_set.all().values('course__id','unit','course__code','course__title')
                courses.extend(list(dept_course))
            # request.session['aux_courses'] = courses
        return render(request,"student/aux-courses.html",{'courses':courses})
    
    def post(self,request):
        course_ids = request.POST.getlist('courses')
        units = request.POST.getlist('units')
        semester = request.session['semester']
        department = request.department
        course_list = DepartmentCourse.objects.filter(department = department, semester = semester)
        courses = []
        for id in course_ids:
            for course in course_list:
                for courseline in course.departmentcourseline_set.all():
                    if courseline.course.id == int(id):
                        dictionary = {
                            'course__id':courseline.course.id,
                            'unit':courseline.unit,
                            'course__code':courseline.course.code,
                            'course__title':courseline.course.title
                        }
                        courses.append(dictionary)
        request.session['aux_courses'] = courses
        print(request.session['aux_courses'])
        return redirect("student:register-course")




            
            



class RegistrationListView(StudentMixin, ListView):
    template_name = "student/registration.html"

    def get_queryset(self):
        department = self.request.department
        reg = department.registration_set.all().prefetch_related('cleared_students')
        registration = Registration.objects.filter(departments  = None).prefetch_related('cleared_students')
        
        registration = [*registration,*reg]
        print(registration)
        for object in registration:
            if self.request.user.student in object.cleared_students.all():
                object.completed = True
            else:
                object.completed = False
        return registration

class ClearanceListView(StudentMixin, ListView):
    template_name = "student/clearance.html"

    def get_queryset(self):
        department = self.request.department
        cleared = department.clearance_set.all().prefetch_related('cleared_students')
        clearance = Clearance.objects.filter(departments  = None).prefetch_related('cleared_students')
        
        clearance = [*clearance,*cleared]
        for object in clearance:
            if self.request.user.student in object.cleared_students.all():
                object.completed = True
            else:
                object.completed = False
        return clearance