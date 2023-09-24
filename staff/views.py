from typing import Any, Dict
from django.db.models.query import QuerySet
from django.db.models import Q
from django.shortcuts import render, redirect,reverse,get_object_or_404
from django.urls import reverse_lazy
from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin
from django.contrib import messages
from django.contrib.auth.views import PasswordChangeView
from django.views import View
from django.views.generic import FormView, ListView, CreateView, DetailView
from django.contrib.auth import logout, login
import datetime


from pytz import timezone

# from staff.forms import ScheduleForm,EditProfileForm,UploadForm
from .forms import *
from datetime import date
from django.utils.translation import gettext_lazy as _
from django.http import HttpResponse, JsonResponse,Http404

# Create your views here.
from admins.models import *

def home(request):
    return redirect(reverse('staff:dashboard'))

class AuthStaffRequiredMixin(LoginRequiredMixin,UserPassesTestMixin):
    login_url = reverse_lazy("staff:login")
    def test_func(self):
        return self.request.user.is_auth_staff
    
class StaffRequiredMixin(LoginRequiredMixin,UserPassesTestMixin):
    login_url = reverse_lazy("staff:login")
    def test_func(self):
        return Staff.objects.filter(user = self.request.user).exists()
class LoginView(FormView):
    form_class = StaffLoginForm
    template_name = "staff/login.html"
    success_url = reverse_lazy("staff:dashboard")

    def form_valid(self, form):
        user = form.get_user()
        department = Staff.objects.get(user = user).department
        login(self.request,user,'django.contrib.auth.backends.ModelBackend')
        self.request.session['department'] = str(department.id)
        return super().form_valid(form)
    
class DashboardView(StaffRequiredMixin,View):
    def get(self,request):
        return render(request,"staff/index.html")

class ProfileView(StaffRequiredMixin,View):
    def get(self,request):
        context = {
        }
        data = Staff.objects.get(id = request.user.staff.id )
        context['data'] = data
    
        return render(request,'staff/profile.html',context)


class EditProfileView(StaffRequiredMixin,View):
    def get(self,request):
        id = request.user.staff.id
        staff = Staff.objects.get(id = id)
        form = EditProfileForm(instance=staff)
        return render(request,'staff/edit-profile.html',{'form':form})
    def post(self,request):
        id = request.user.staff.id
        staff = Staff.objects.get(id = id)
        form = EditProfileForm(request.POST,request.FILES, instance=staff)
        if form.is_valid():
            obj = form.cleaned_data
            form.save()
            messages.success(request,"Profile Edited Successfully")
            return redirect(reverse('staff:profile'))
        return render(request,'staff/edit-profile.html',{'form':form})





class UserPasswordChangeView(StaffRequiredMixin,PasswordChangeView):
    template_name = "staff/change-password.html"
    success_url = reverse_lazy("staff:profile")
    def form_valid(self,form):
        messages.success(self.request,_("Password changed."))
        return super().form_valid(form)
    
class ResourceView(StaffRequiredMixin,ListView):
    paginate_by = 50
    template_name = "staff/resources.html"
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
    

class ResourceUploadView(StaffRequiredMixin,CreateView):
    model = CourseResource
    fields = '__all__'
    template_name = "staff/resources-upload.html"
    success_url = reverse_lazy('staff:resources')

    def get_context_data(self,**kwargs):
        context = super().get_context_data(**kwargs)
        context['courses'] = Course.objects.filter(department =  self.request.department)
        return context

class NewsletterView(StaffRequiredMixin, ListView):
    template_name = "staff/newsletter.html"
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
    
class NewsletterCreateView(AuthStaffRequiredMixin, CreateView):
    model  = Information
    template_name = "staff/newsletter-create.html"
    fields = "__all__"
# def student_name_sort(obj):
#     return obj.firstname


class StudentListView(StaffRequiredMixin,ListView):
    paginate_by = 30
    template_name = "staff/student.html"
    def get_context_data(self, **kwargs):
        context =  super().get_context_data(**kwargs)
        level = [x+1 for x in range(self.request.department.level_number)]
        context['level'] = level
        return context
    def get_queryset(self):
        student = Student.objects.filter(department = self.request.department)
        if self.request.GET.get('search'):
            search  = self.request.GET['search']
            string_list = search.strip().split(" ")
            if len(string_list) == 1:
                student = student.filter(Q(firstname__istartswith = string_list[0])|Q(lastname__istartswith = string_list[0]))
            elif len(string_list) == 2:
                student = Student.filter(Q(firstname__istartswith = string_list[0])|Q(lastname__istartswith = string_list[0]
                                            )|Q(firstname__istartswith = string_list[1])|Q(lastname__istartswith = string_list[1]
                                            ))
        if self.request.GET.get('sex'):
            student = student.filter(sex = self.request.GET['sex'])
        if self.request.GET.get("level"):
            student = student.filter(sex = self.request.GET['level'])
            
        return student.order_by('firstname','lastname')
        
class StudentDetailView(StaffRequiredMixin,DetailView):
    model = Student
    template_name = 'staff/student-details.html'


class DepartmentCourseList(AuthStaffRequiredMixin,ListView):
    template_name = 'staff/dept-course-list.html'
    
    def get_queryset(self):
        return DepartmentCourse.objects.filter(department = self.request.department)

class DepartmentCourseFormView(AuthStaffRequiredMixin,FormView):
    form_class = DepartmentCourseForm
    template_name = 'staff/dept-course-form.html'
    success_url = reverse_lazy('staff:department-course-list')
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        courses = Course.objects.all()
        context['courses'] = courses
        return context
    def form_valid(self, form):
        response = super().form_valid(form)
        obj = form.create(self.request)
        messages.success(self.request,"Course Registration Format Created")
        return response

class DepartmentCourseAddView(AuthStaffRequiredMixin,View):
    def get(self,request,id):
        object = get_object_or_404(DepartmentCourse,id = id)
        courses = Course.objects.all()
        context = {
            'object':object,
            'courses':courses
        }
        return render(request,"staff/dept-course-add-form.html", context)
    def post(self,request,id):
        object = get_object_or_404(DepartmentCourse,id = id)
        units = request.POST.getlist("units")
        courses = request.POST.getlist("courses")
        for unit, course_id in zip(units,courses):
            course = Course.objects.get(id = int(course_id))
            DepartmentCourseLine.objects.get_or_create(dept_course = object,unit = int(unit), course = course)
        messages.success(self.request,"Courses Added")
        return redirect("staff:department-course-list")    


# class InboxListView(StaffRequiredMixin,ListView):
#     paginate_by = 15
#     template_name = 'staff/inbox.html'
#     def get_queryset(self):
#         to_user = self.request.user
#         if self.request.GET.get('date'):
#             inbox = Mail.objects.filter(to = to_user,date = self.request.GET['date'])
#             return inbox.order_by('-time')
#         else:
#             inbox = Mail.objects.filter(to = to_user)
#             return inbox.order_by("-date")

# class InboxDetailsView(StaffRequiredMixin,View):
#     def get(self,request,id):
#         try:
#             letter = Mail.objects.get(to = request.user,id = id)
#         except:
#             messages.error(request,"Mail does not Exist")
#             return redirect(reverse('staff:inbox-list'))
        
#         letter.read = True
#         letter.save()
        
#         context = {'object':letter}
#         return render(request,'staff/inbox-details.html',context)


# class InboxDeleteView(StaffRequiredMixin,View):
#     def get(self,request,id):
#         try:
#             letter = Mail.objects.get(to = request.user,id = id)
#         except:
#             messages.error(request,"Mail does not Exist")
#             return redirect(reverse('staff:inbox-list'))
        
#         letter.to = None
#         letter.save()
#         messages.success(request,"Mail deleted")
#         return redirect(reverse('staff:inbox-list'))


# class UploadView(StaffRequiredMixin,FormView):
#     form_class = UploadForm
#     template_name = "Staff/upload.html"
#     success_url = reverse_lazy("staff:uploads")
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         staff = self.request.user.staff
#         context_data = []
#         teacher_programme = staff.programme.all()
#         for x in teacher_programme:
#             if not x.report:
#                 context_data.append(x)
#         context['programmes'] = context_data
#         all_uploads = []
#         for x in Upload_Assignment.objects.all():
#             if staff in x.staff.all():
#                 if Uploads.objects.filter(staff = staff, section = x).exists():
#                     done = True
#                 else:
#                     done = False
#                 all_uploads.append({"upload":{**x.__dict__},'done':done})
#         context['all_uploads'] = all_uploads
#         return context
#     def form_valid(self,form):
#         response = super().form_valid(form)
#         data = form.cleaned_data
#         staff = self.request.user.staff
#         obj = form.save(commit = False)
#         obj.staff = staff
#         obj.save()
#         messages.success(self.request,"Upload Successful")
#         return response

class LogoutView(StaffRequiredMixin,View):
    def get(self,request):
        logout(request)
        messages.success(request,"Logout Successful")
        return redirect(reverse('staff:login'))

         

