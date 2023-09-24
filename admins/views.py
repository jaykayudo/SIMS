# Django Import
from typing import Any, Dict, Optional
from django.db.models.query import QuerySet
from django.forms.models import BaseModelForm
from django.shortcuts import render, redirect,get_object_or_404
from django.urls import reverse_lazy, reverse
from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin
from django.contrib import messages
from django.contrib.auth.views import PasswordChangeView
from django.views import View
from django.views.generic import FormView, ListView, DetailView, UpdateView, CreateView, DeleteView
from django.contrib.auth import logout, login
from django import forms
from django.utils.translation import gettext_lazy as _
from django.http import HttpRequest, HttpResponse, JsonResponse,Http404
from django.db.models import Q
from django.contrib.auth  import update_session_auth_hash

# local imports
from .models import *
from .forms import *

# Create your views here.

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

class AdminRequiredMixin(LoginRequiredMixin,UserPassesTestMixin):
    login_url = "/admin/login/"
    def test_func(self):
        return self.request.user.is_staff
def home(request):
    return redirect(reverse('admins:dashboard'))


class LoginView(FormView):
    form_class = AdminLoginForm
    template_name = "admins/login.html"
    success_url = reverse_lazy("admins:dashboard")

    def form_valid(self, form):
        user = form.get_user()
        login(self.request,user,'django.contrib.auth.backends.ModelBackend')
        return super().form_valid(form)

# class DashboardView(AdminRequiredMixin,View):
#     def get(self,request):
#         return HttpResponse("Dashboard")

class DashboardView(AdminRequiredMixin,View):
    def get(self,request):
        students  = Student.objects.all().count()
        faculties = Faculty.objects.all().count()
        department = Department.objects.all().count()
        staffs = Staff.objects.all().count()
        
        context = {
            'student_no':students,
            'faculties_no':faculties,
            'departments_no':department,
            'staff_no':staffs,
            
        }
        return render(request,'admins/index.html',context)

class StaffListView(AdminRequiredMixin,ListView):
    paginate_by = 50
    template_name = "admins/staffs.html"
    def get_context_data(self, **kwargs):
        context =  super().get_context_data(**kwargs)
        faculties = Faculty.objects.all()
        departments = Department.objects.all()
        context['faculties'] = faculties
        context['departments'] = departments
        return context
    # def get(self,request,*args,**kwargs):
    #     data = self.get_queryset()
    #     return HttpResponse(data)
    def get_queryset(self):
        staff = Staff.objects.all()
        if self.request.GET.get('search'):
            search  = self.request.GET['search']
            string_list = search.strip().split(" ")
            if len(string_list) == 1:
                staff = staff.filter(Q(firstname__istartswith = string_list[0])|Q(lastname__istartswith = string_list[0]))
            elif len(string_list) == 2:
                staff = staff.filter(Q(firstname__istartswith = string_list[0])|Q(lastname__istartswith = string_list[0]
                                            )|Q(firstname__istartswith = string_list[1])|Q(lastname__istartswith = string_list[1]
                                            ))
        if self.request.GET.get('faculty'):
            staff = staff.filter(department__faculty__id = self.request.GET['faculty'])
        if self.request.GET.get('department'):
            staff = staff.filter(department__id = self.request.GET['department'])
        if self.request.GET.get('sex'):
            staff = staff.filter(sex = self.request.GET['sex'])
            
        return staff.order_by('firstname','lastname')
class StaffDetailView(AdminRequiredMixin,DetailView):
    model = Staff
    template_name = 'admins/staff-details.html'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # objectdata = self.get_object()
        staff = context['object']
        all_uploads = []
        for x in Upload_Assignment.objects.all():
            if staff in x.staff.all():
                if Uploads.objects.filter(staff = staff, section = x).exists():
                    done = True
                else:
                    done = False
                all_uploads.append({"upload":{**x.__dict__},'done':done})
        
        context['all_uploads'] = all_uploads
        return context

# def scheduleGetView(request,id):
#     if not request.is_ajax():
#         return redirect(reverse('staff:dashboard'))
#     date = request.GET.get('date')
#     if date:
#         date = date.split('/')
#         date = datetime.date(year = int(date[2]),month = int(date[0]),day = int(date[1]))
#         try:
#             staff = Staff.objects.get(id = id)
#         except:
#             raise ValueError('Staff does not exist')
#         schedule = Schedule.objects.filter(teacher = staff,date = date).values('description','_class__name','time')
#         schedule = list(schedule)
#         return JsonResponse({'schedule':schedule},safe = False)
#     else:
#         raise ValueError('Date not Specified')
# class StaffStatusToggle(AdminRequiredMixin,View):
#     def get(self,request,id):
#         try:
#             staff = Staff.objects.get(id = id)
#             user = User.objects.get(id = staff.user.id)
#         except:
#             messages.error(request,"Invalid Query")
#             return redirect(reverse('admins:staff'))
#         if staff.status:
#             staff.status = False
#             user.is_active = False
#             messages.success(request,"Staff Blocked Successfully")
#         else:
#             staff.status = True
#             user.is_active = True
#             messages.success(request,"Staff Activated Successfully")
#         staff.save()            
#         user.save()

#         return redirect(reverse('admins:staff-details',kwargs ={"pk":id}))
class StaffDeleteView(AdminRequiredMixin,View):
    def get(self,request,id):
        try:
            staff = Staff.objects.get(id = id)
        except:
            messages.error(request,"Invalid Query")
            return redirect(reverse('admins:staff'))
        
        return render(request,'admins/forms/delete-staff.html',{'object':staff})
    
    def post(self,request,id):
        try:
            staff = Staff.objects.get(id = id)
            staff_user = User.objects.get(id = staff.user.id)
        except:
            messages.error(request,"Invalid Query")
            return redirect(reverse('admins:staff'))
        
        
        staff.delete()
        staff_user.delete()
        messages.success(request,"Staff Deleted Successfully")
        return redirect(reverse('admins:staff'))
class StaffAddFormView(AdminRequiredMixin,FormView):
    form_class = StaffAddForm
    template_name = 'admins/forms/add-staff-form.html'
    success_url = reverse_lazy('admins:staff')
    def get_context_data(self, **kwargs):
        context =  super().get_context_data(**kwargs)
        faculties = Faculty.objects.all()
        departments = Department.objects.all()
        context['faculties'] = faculties
        context['departments'] = departments
        print(context)
        return context
    def form_valid(self,form):  
        email = form.cleaned_data.get('email')
        password = form.cleaned_data.get('password')
        user = User.objects.create_user(email = email, password = password)
        if form.cleaned_data['auth_staff']:
            user.is_auth_staff = True
        user.save()
        obj = form.save(commit = False)
        obj.user = user
        obj.save()
        messages.success(self.request,"Staff Created")
        return super().form_valid(form)

class StaffResetPassword(AdminRequiredMixin,View):
    def get(self,request,id):
        try:
            staff = Staff.objects.get(id = id)
        except:
            messages.error(request,"Invalid Query")
            return redirect(reverse('admins:staff'))
        form = ResetPasswordForm()
        return render(request,'admins/forms/reset_staff_password.html',{'form':form,'object':staff})
    def post(self,request,id):
        try:
            staff = Staff.objects.get(id = id)
            staff_user = User.objects.get(id = staff.user.id)
        except:
            messages.error(request,"Invalid Query")
            return redirect(reverse('admins:staff'))
        form = ResetPasswordForm(request.POST)
        if form.is_valid():
            password = form.cleaned_data['password1']
            staff_user.set_password(password)
            staff_user.save()
            messages.success(request,"Password Resetted")
            return redirect(reverse('admins:staff-details',kwargs={'pk':id}))
        return render(request,'admins/forms/reset_staff_password.html',{'form':form,'object':staff})
class StaffEditView(AdminRequiredMixin,View):
    def get(self,request,id):
        try:
            staff = Staff.objects.get(id = id)
        except:
            messages.error(request,"Invalid Query")
            return redirect(reverse('admins:staff'))
        department = Department.objects.all().order_by('name')
        form = StaffEditForm(instance=staff)
        context = {
            'form':form,'object':staff,'department':department,
        }
        
        return render(request,'admins/forms/edit-staff-form.html',context)
    def post(self,request,id):
        try:
            staff = Staff.objects.get(id = id)
        except:
            messages.error(request,"Invalid Query")
            return redirect(reverse('admins:staff'))
        
        form = StaffEditForm(request.POST,request.FILES,instance=staff)

        context = {
            'form':form,'object':staff,
        }
        if form.is_valid():
            obj = form.save()
            if obj.user.email != staff.user.email:
                obj.user.email = staff.user.email
                obj.user.save()
            messages.success(request,"Staff Edited")
            return redirect(reverse('admins:staff-details',kwargs={'pk':id}))
        department = Department.objects.all().order_by('name')
        context['department'] = department
        return render(request,'admins/forms/edit-staff-form.html',context)

class StudentListView(AdminRequiredMixin,ListView):
    paginate_by = 100
    template_name = "admins/students.html"
    def get_context_data(self, **kwargs):
        context =  super().get_context_data(**kwargs)
        faculties = Faculty.objects.all()
        departments = Department.objects.all()
        context['faculties'] = faculties
        context['departments'] = departments
        return context
    def get_queryset(self):
        student = Student.objects.all()
        if self.request.GET.get('search'):
            search  = self.request.GET['search']
            string_list = search.strip().split(" ")
            if len(string_list) == 1:
                student = student.filter(Q(firstname__istartswith = string_list[0])|Q(lastname__istartswith = string_list[0]))
            elif len(string_list) == 2:
                student = Student.filter(Q(firstname__istartswith = string_list[0])|Q(lastname__istartswith = string_list[0]
                                            )|Q(firstname__istartswith = string_list[1])|Q(lastname__istartswith = string_list[1]
                                            ))
        if self.request.GET.get('faculty'):
            student = student.filter(department__faculty__id = self.request.GET['faculty'])
        if self.request.GET.get('department'):
            student = student.filter(department__id = self.request.GET['department'])
        if self.request.GET.get('sex'):
            student = student.filter(sex = self.request.GET['sex'])
            
        return student.order_by('firstname','lastname')

class StudentDetailView(AdminRequiredMixin,DetailView):
    model = Student
    template_name = 'admins/students-profile.html'


# class StudentStatusToggle(AdminRequiredMixin,View):
#     def get(self,request,id):
#         try:
#             student = Student.objects.get(id = id)
#         except:
#             messages.error(request,"Invalid Query")
#             return redirect(reverse('admins:student'))
        
#         if student.status:
#             student.status = False
#             messages.success(request,"Student Blocked Successfully")
#         else:
#             student.status = True
#             messages.success(request,"Student Activated Successfully")
#         student.save()            
        

#         return redirect(reverse('admins:student-details',kwargs ={"pk":id}))

class StudentResetPassword(AdminRequiredMixin,View):
    def get(self,request,id):
        try:
            student = Student.objects.get(id = id)
        except:
            messages.error(request,"Invalid Query")
            return redirect(reverse('admins:student'))
        form = ResetPasswordForm()
        return render(request,'admins/forms/reset_student_password.html',{'form':form,'object':student})
    def post(self,request,id):
        try:
            student = Student.objects.get(id = id)
            student_user = User.objects.get(id = student.user.id)
        except:
            messages.error(request,"Invalid Query")
            return redirect(reverse('admins:student'))
        form = ResetPasswordForm(request.POST)
        if form.is_valid():
            password = form.cleaned_data['password1']
            student_user.set_password(password)
            student_user.save()
            messages.success(request,"Password Resetted")
            return redirect(reverse('admins:student-details',kwargs={'pk':id}))
        return render(request,'admins/forms/reset_student_password.html',{'form':form,'object':student})

class StudentDeleteView(AdminRequiredMixin,View):
    def get(self,request,id):
        try:
            student = Student.objects.get(id = id)
        except:
            messages.error(request,"Invalid Query")
            return redirect(reverse('admins:student'))
        
        return render(request,'admins/forms/delete-student.html',{'object':student})
    
    def post(self,request,id):
        if not request.user.is_superuser:
            messages.success(request,"You do not have the right authorization to delete a student")
            return redirect(reverse("admins:student"))
        try:
            student = Student.objects.get(id = id)
        except:
            messages.error(request,"Invalid Query")
            return redirect(reverse('admins:student'))
        student.delete()
        messages.success(request,"Student Deleted Successfully")
        return redirect(reverse('admins:student'))
class StudentAddFormView(AdminRequiredMixin,FormView):
    form_class = StudentAddForm
    template_name = "admins/forms/add-student-form.html"
    success_url = reverse_lazy('admins:student')

    def form_valid(self, form):
        email = form.cleaned_data.get('email')
        password = form.cleaned_data.get('password')
        user = User.objects.create_user(email = email, password = password)
        user.is_student = True
        user.save()
        obj = form.save(commit = False)
        obj.user = user
        obj.save()
        messages.success(self.request,"Student Added")
        if self.request.GET.get('submit') == 'Save and Add Another':
            self.success_url = reverse('admins:student-add-form')
        return super().form_valid(form)
class StudentUpdateFormView(AdminRequiredMixin,UpdateView):
    model = Student
    fields = '__all__'
    template_name = 'admins/forms/edit-student-form.html'
    extra_context = {'department':Department.objects.all()}
    def get_success_url(self):
        object = self.get_object()
        url = reverse('admins:student-details',kwargs={'pk':object.id})
        if not url:
            url = reverse('admins:student')
        return url
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        object = self.get_object()
        user = object.user.id
        context['user'] = user
        return context
    def form_valid(self, form):
        obj = form.save()
        if obj.user.email != form.cleaned_data['email']:
            obj.user.email = form.cleaned_data['email']
            obj.user.save()

        return super().form_valid(form)

class FacultyListView(AdminRequiredMixin,ListView):
    template_name = "admins/faculty.html"
    queryset = Faculty.objects.all().order_by("name")

class FacultyDetailView(AdminRequiredMixin,DetailView):
    model = Faculty
    template_name = 'admins/faculty-details.html'
class FacultyAddView(AdminRequiredMixin,CreateView):
    model = Faculty
    fields = "__all__"
    template_name = "admins/forms/add-faculty-form.html"
    success_url = reverse_lazy("admins:faculty")
    def form_valid(self, form):
        messages.success(self.request,"Faculty Added Successfully")
        return super().form_valid(form)
class FacultyUpdateView(AdminRequiredMixin,UpdateView):
    model = Faculty
    fields = "__all__"
    template_name = "admins/forms/edit-faculty-form.html"
    def get_success_url(self):
        object = self.get_object()
        url = reverse("admins:faculty-details",kwargs={"pk":object.pk})
        messages.success(self.request,"Faculty Updated Successfully")
        return url
    
   
class FacultyDeleteView(AdminRequiredMixin,DeleteView):
    model = Faculty
    fields = "__all__"
    template_name = "admins/forms/delete-faculty.html"
    success_url = reverse_lazy("admins:faculty")
    def post(self, request, *args, **kwargs):
        if not request.user.is_superuser:
            messages.error(request,"Unauthorized Action")
            return redirect(reverse("admins:faculty-details",kwargs={'pk':kwargs['pk']}))
        return super().post(request, *args, **kwargs)
    def form_valid(self, form):
        messages.success(self.request,"Faculty Deleted Successfully")
        return super().form_valid(form)
class DepartmentDetailView(AdminRequiredMixin,DetailView):
    model = Department
    template_name = 'admins/department-details.html'
class DepartmentAddView(AdminRequiredMixin,CreateView):
    model = Department
    fields = "__all__"
    template_name = "admins/forms/add-department-form.html"
    def get(self, request, *args, **kwargs: Any):
        self.faculty_id = kwargs['fid']
        return super().get(request, *args, **kwargs)
    def post(self, request, *args, **kwargs: Any):
        self.faculty_id = kwargs['fid']
        return super().post(request, *args, **kwargs)
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['faculty_id'] = self.faculty_id
        return context
    def get_success_url(self):
        
        url = reverse("admins:faculty-details",kwargs={'pk':self.faculty_id})
        return url
    def form_valid(self, form):
        messages.success(self.request,"Department Added Successfully")
        return super().form_valid(form)
class DepartmentUpdateView(AdminRequiredMixin,UpdateView):
    model = Department
    fields = "__all__"
    template_name = "admins/forms/edit-department-form.html"
    def get_success_url(self):
        object = self.get_object()
        url = reverse("admins:department-details",kwargs={'pk':object.pk})
        return url
    def form_valid(self, form):
        messages.success(self.request,"Department Updated Successfully")
        return super().form_valid(form)
class DepartmentDeleteView(AdminRequiredMixin,DeleteView):
    model = Department
    fields = "__all__"
    template_name = "admins/forms/delete-department.html"
    def get_success_url(self):
        object = self.get_object()
        url = reverse("admins:faculty-details",kwargs={'pk':object.faculty.pk})
        return url
    def post(self, request, *args, **kwargs):
        if not request.user.is_superuser:
            messages.error(request,"Unauthorized Action")
            return redirect(reverse("admins:faculty-details",kwargs={'pk':kwargs['pk']}))
        return super().post(request, *args, **kwargs)
    def form_valid(self, form):
        messages.success(self.request,"Department Deleted Successfully")
        return super().form_valid(form)
class RegistrationListView(AdminRequiredMixin, ListView):
    model = Registration
    queryset = Registration.objects.all().order_by("name")
    template_name = "admins/registration.html"

class RegistrationAddView(AdminRequiredMixin,CreateView):
    model = Registration
    fields = "__all__"
    template_name = "admins/forms/add-registration-form.html"
    success_url = reverse_lazy("admins:registration")

class RegistrationDetailView(AdminRequiredMixin,DetailView):
    model = Registration
    template_name = "admins/registration-details.html"
class RegistrationAddStudentView(AdminRequiredMixin,View):
    def get(self, request, id):
        registration = get_object_or_404(Registration,id = id)
        registered_student = registration.cleared_students.all().values_list("id",flat=True)
        student = Student.objects.exclude(id__in = registered_student)
        print(student)
        return render(request, "admins/forms/add-registered-student.html", {'students':student})
    def post(self,request,id):
        registration = get_object_or_404(Registration,id = id)
        student_id = request.POST.get("student")
        student= Student.objects.get(id = student_id)
        registration.cleared_students.add(student)
        registration.save()
        return redirect(reverse("admins:registration-details",kwargs={'pk':id}))

class RegistrationEditView(AdminRequiredMixin,UpdateView):
    model = Registration
    template_name = "admins/forms/edit-registration-form.html"
    fields = "__all__"
    def get_success_url(self):
        object = self.get_object()
        url = reverse("admins:registration-details",{'pk':object.pk})
        return url
class RegistrationDeleteView(AdminRequiredMixin,DeleteView):
    model = Registration
    template_name = "admins/forms/delete-registration.html"
class ClearanceListView(AdminRequiredMixin, ListView):
    model = Clearance
    queryset = Clearance.objects.all().order_by("name")
    template_name = "admins/clearance.html"

class ClearanceAddView(AdminRequiredMixin,CreateView):
    model = Clearance
    fields = "__all__"
    template_name = "admins/forms/add-clearance-form.html"
    success_url = reverse_lazy("admins:clearance")

class ClearanceDetailView(AdminRequiredMixin,DetailView):
    model = Clearance
    template_name = "admins/clearance-details.html"
class ClearanceAddStudentView(AdminRequiredMixin,View):
    def get(self, request, id):
        clearance = get_object_or_404(Clearance,id = id)
        registered_student = clearance.cleared_students.all().values_list(id,flat=True)
        student = Student.objects.exclude(id__in = registered_student)
        return render(request, "admins/forms/add-cleared-student.html", {'students':student})
    def post(self,request,id):
        clearance = get_object_or_404(Clearance,id = id)
        student_id = request.POST.get("student")
        student= Student.objects.get(id = student_id)
        clearance.cleared_students.add(student)
        clearance.save()
        return redirect(reverse("admins:clearance-details",kwargs={'id':id}))

class ClearanceEditView(AdminRequiredMixin,UpdateView):
    model = Clearance
    template_name = "admins/forms/edit-clearance-form.html"
    fields = "__all__"
class ClearanceDeleteView(AdminRequiredMixin,DeleteView):
    model = Clearance
    template_name = "admins/forms/delete-clearance.html"

class CourseListView(AdminRequiredMixin, ListView):
    template_name = "admins/course.html"
    paginate_by = 50
    def get_context_data(self, **kwargs):
        context =  super().get_context_data(**kwargs)
        faculties = Faculty.objects.all()
        departments = Department.objects.all()
        context['faculties'] = faculties
        context['departments'] = departments
        return context
    def get_queryset(self):
        course = Course.objects.all()
        if self.request.GET.get('search'):
            search  = self.request.GET['search']
            string_list = search
            course = course.filter(Q(title__istartswith = string_list)|Q(code__istartwith = string_list))
        if self.request.GET.get('faculty'):
            course = course.filter(department__faculty__id = self.request.GET['faculty'])
        if self.request.GET.get('department'):
            course = course.filter(department__id = self.request.GET['department'])
        if self.request.GET.get('level'):
            course = course.filter(level = int(self.request.GET['level']))
            
        return course.order_by('code','title')
class CourseAddView(AdminRequiredMixin,CreateView):
    model = Course
    fields = "__all__"
    template_name = "admins/forms/add-course-form.html"
    success_url = reverse_lazy("admins:courses")
    def get_context_data(self, **kwargs):
        context =  super().get_context_data(**kwargs)
        context['title'] = "Add Course"
        context['btn_text'] = "Add Course"
        return context
class CourseEditView(AdminRequiredMixin,UpdateView):
    model = Course
    template_name = "admins/forms/add-course-form.html"
    fields = "__all__"
    success_url = reverse_lazy("admins:courses")
    def get_context_data(self, **kwargs):
        context =  super().get_context_data(**kwargs)
        context['title'] = "Edit Course"
        context['btn_text'] = "Edit Course"
        return context
class CourseDeleteView(AdminRequiredMixin,DeleteView):
    model = Course
    template_name = "admins/forms/delete-course.html"
    success_url = reverse_lazy("admins:courses")

class EventView(AdminRequiredMixin,ListView):
    paginate_by = 15
    template_name = 'admins/events.html'
    def get_queryset(self):
        if self.request.GET.get('date'):
            event = Event.objects.filter(startdate = self.request.GET['date'])
            return event.order_by('-starttime')
        else:
            event = Event.objects.all()
            return event.order_by("-startdate")
class EventFormView(AdminRequiredMixin,CreateView):
    model = Event
    template_name = 'admins/forms/add-event.html'
    fields = "__all__"
    success_url = reverse_lazy('admins:event')
    def get_context_data(self, **kwargs):
        context =  super().get_context_data(**kwargs)
        context['title'] = "Create Event"
        context['btn_text'] = "Create Event"
        return context
    def form_valid(self, form):
        form.save()
        messages.success(self.request,"Event Created")
        return super().form_valid(form)
class EventEditView(AdminRequiredMixin,UpdateView):
    model = Event
    template_name = 'admins/forms/add-event.html'
    fields = "__all__"
    success_url = reverse_lazy('admins:event')
    def get_context_data(self, **kwargs):
        context =  super().get_context_data(**kwargs)
        context['title'] = "Edit Event"
        context['btn_text'] = "Edit Event"
        return context 
class EventDetailsView(AdminRequiredMixin,View):
    def get(self,request,id):
        event = get_object_or_404(Event,id=id)
        context = {'object':event}
        return render(request,'admins/event-details.html',context)
class EventDeleteView(AdminRequiredMixin,DeleteView):
    model = Event
    template_name = "admins/forms/delete-event.html"
    success_url = reverse_lazy("admins:event")
class AdminListView(UserPassesTestMixin, ListView):
    template_name = "admins/admins-list.html"
    def get_queryset(self):
        return Admin.objects.all()
    def test_func(self):
        return self.request.user.is_superuser
class AdminCreateView(UserPassesTestMixin, CreateView):
    model = Admin
    template_name = "admins/forms/add-admin-form.html"
    fields = "__all__"
    success_url = reverse_lazy("")
    def form_valid(self, form):
        return super().form_valid(form)
    def test_func(self):
        return self.request.user.is_superuser
    
class AdminDetailView(UserPassesTestMixin,DetailView):
    model = Admin
    template_name = "admins/admins-details.html"
    def test_func(self):
        return self.request.user.is_superuser
class AdminStatusToggle(UserPassesTestMixin,View):
    def get(self,request,id):
        try:
            admin = User.objects.get(id = id)
        except:
            messages.error(request,"Invalid Query")
            return redirect(reverse('admins:admin-list'))
        
        if admin.active:
            admin.active = False
            messages.success(request,"Admin Blocked Successfully")
        else:
            admin.active = True
            messages.success(request,"Admin Activated Successfully")
        admin.save()            
        

        return redirect(reverse('admins:admin-details',kwargs ={"pk":id}))
    def test_func(self):
        return self.request.user.is_superuser


class CourseRegistrationView(AdminRequiredMixin,ListView):
    paginate_by = 100
    template_name = "admins/course-registration.html"
    def get_context_data(self, **kwargs):
        context =  super().get_context_data(**kwargs)
        faculties = Faculty.objects.all()
        departments = Department.objects.all()
        sessions = SchoolSession.objects.all().order_by("-year")
        context['faculties'] = faculties
        context['departments'] = departments
        context['sessions'] = sessions
        return context
    def get_queryset(self):
        course_reg = CourseRegistration.objects.all()
        if self.request.GET.get('search'):
            search  = self.request.GET['search']
            course_reg = course_reg.filter(student__matric_number = search)
        if self.request.GET.get('faculty'):
            course_reg = course_reg.filter(student__department__faculty__id = self.request.GET['faculty'])
        if self.request.GET.get('department'):
            course_reg = course_reg.filter(student__department__id = self.request.GET['department'])
        if self.request.GET.get('session'):
            course_reg = course_reg.filter(session__id = self.request.GET['session'])
        if self.request.GET.get('semester'):
            course_reg = course_reg.filter(semester = self.request.GET['semester'])  
        return course_reg.order_by('student')

class CourseRegistrationDetailView(AdminRequiredMixin,DetailView):
    model = CourseRegistration
    template_name = "admins/course-registration-details.html"

class CourseRegistrationAddView(AdminRequiredMixin,View):
    def get(self,request,id):
        course_reg = get_object_or_404(CourseRegistration, id = id)
        semester = course_reg.semester
        department = course_reg.student.department
        department_course_reg = DepartmentCourse.objects.filter(semester = semester,department = department)
        courseline_list = []
        for dept_course in department_course_reg:
            courses = dept_course.departmentcourseline_set.all()
            courseline_list.extend(courses)
        return render(request,"admins/course-registration-add.html",{'dept_course':courseline_list,'course_id':id})
    
    def post(self,request,id):
        course_reg = get_object_or_404(CourseRegistration, id = id)
        department_line = DepartmentCourseLine.objects.get(id = request.POST['course_id'])
        CourseRegistrationLine.objects.get_or_create(course_reg = course_reg,session = course_reg.session,unit = department_line.unit,
                                              course = department_line.course)
        messages.success(request,"Course Added Successfully")
        return redirect(reverse("admins:course-reg-details",kwargs={'pk':id}))

class CourseRegistrationRemoveView(AdminRequiredMixin,View):
    def get(self,request,course_id,id):
        # course_reg = get_object_or_404(CourseRegistration, id = course_id)
        CourseRegistrationLine.objects.get(id = id).delete()
        messages.success(request,"Course Removed Successfully")
        return redirect(reverse("admins:course-reg-details",kwargs={'pk':course_id}))


class UploadView(AdminRequiredMixin,ListView):
    model = Uploads
    paginate_by = 20
    template_name = "admins/uploads.html"
    def get_queryset(self):
        uploads = Uploads.objects.all().order_by('-sent_on')
        return uploads

class UploadAssignmentView(AdminRequiredMixin,ListView):
    model = Upload_Assignment
    paginate_by = 20
    template_name  = "admins/uploads-assignment.html"

class CreateUploadAssignmentView(AdminRequiredMixin,FormView):
    model = Upload_Assignment
    form_class = UploadAssignmentAddForm
    success_url = reverse_lazy("admins:uploads-assignment")
    template_name = "admins/forms/add-upload-assignment.html"

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)

class UploadAssignmentDetailView(AdminRequiredMixin,DetailView):
    model = Upload_Assignment
    template_name = "admins/upload-assignment-details.html"



class SettingsView(AdminRequiredMixin,View):
    def get(self,request):
        admin = Admin.objects.get(id = request.user.admin.id)
        form = AdminUpdateForm()
        return render(request,'admins/settings/settings.html',{'object':admin,'form':form})
    def post(self,request):
        data = request.POST
        file = request.FILES
        form = AdminUpdateForm(data,file)
        user = User.objects.get(id = request.user.id)
        admin = Admin.objects.get(user = user)
        if form.is_valid():
            if request.POST.get('email'):
                if request.POST['email'] != user.email:
                    user.email = request.POST['email']
                    user.save()
            update_attrs(admin,**form.cleaned_data)
            messages.success(request,'Profile Updated')
            return redirect(reverse('admins:settings'))
        messages.error(request,'Error Occurred')
        return render(request,'admins/settings/settings.html',{'object':admin,'form':form})

class SettingsPasswordChangeView(AdminRequiredMixin,PasswordChangeView):
    template_name = "admins/settings/change-password.html"
    success_url = reverse_lazy("staff:profile")
    def form_valid(self,form):
        messages.success(self.request,_("Password changed."))
        return super().form_valid(form)
class SessionListView(AdminRequiredMixin,ListView):
    model = SchoolSession
    queryset = SchoolSession.objects.all().order_by("-year")
    template_name = "admins/settings/session.html"

class SessionCreateView(AdminRequiredMixin,CreateView):
    model = SchoolSession
    fields = "__all__"
    template_name  = "admins/settings/session-form.html"
    success_url = reverse_lazy("admins:school-session")

class SessionActiveView(AdminRequiredMixin,View):
    def get(self,request,id):
        SchoolSession.objects.all().update(current = False)
        session = SchoolSession.objects.get(id = id)
        session.current = True
        session.save()
        messages.success(request,f"Session of {session.year} is the current Session")
        return redirect("admins:school-session")


# class SettingsAdminView(AdminRequiredMixin,View):
#     def get(self,request):
#         admin = Admin.objects.all()
#         return render(request,'admins/settings/Users.html',{'object_list':admin})
# class SettingsAdminFormView(AdminRequiredMixin,FormView):
#     template_name = 'admins/settings/add-admin.html'
#     form_class = AdminUpdateForm
#     success_url = reverse_lazy('admins:settings-admin')
#     def form_valid(self,form):
#         obj = form.save(commit = False)
#         user = User.objects.create_user(email = form.cleaned_data['email'],is_staff = True,password = form.cleaned_data['password'])
#         obj.user = user
#         obj.save()
#         messages.success(self.request,"Admin Created")
#         return super().form_valid(form)
class LogoutView(AdminRequiredMixin,View):
    def get(self,request):
        logout(request)
        messages.success(request,"Logout Successful")
        return redirect(reverse('admins:login'))