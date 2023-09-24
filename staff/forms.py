from django import forms
# from django.forms import ValidationError
from admins.models import Staff, DepartmentCourse, DepartmentCourseLine, Course
from django.contrib.auth import authenticate
# from admins.models import Admin

class StaffLoginForm(forms.Form):
    email = forms.EmailField()
    password = forms.CharField(widget= forms.PasswordInput, strip =False)
    def __init__(self,request = None,*args,**kwargs):
        self.request = request
        self.user = None
        super().__init__(*args,**kwargs)
    def clean(self):
        email = self.cleaned_data.get('email')
        password = self.cleaned_data.get('password')
        user  = authenticate(self.request,email = email,password=password)
        if user:
           if not user.is_auth_staff:
                raise forms.ValidationError("Unauthorized Account")
        self.user = user
        if not self.user:
            raise forms.ValidationError("Incorrect Credentials")
        return self.cleaned_data
    def get_user(self):
        return self.user


# class ScheduleForm(forms.ModelForm):
#     class Meta:
#         model = Schedule
#         # fields = '__all__'
#         exclude = ['teacher']
#         widgets = {
#             'klass':forms.Select(attrs={'class':'form-control'})
#         }

# class UploadForm(forms.ModelForm):
#     class Meta:
#         model = Uploads
#         exclude = ['id','staff','klass']
class EditProfileForm(forms.ModelForm):
    class Meta:
        model = Staff
        exclude = ['role','department']
class DepartmentCourseForm(forms.ModelForm):
    class Meta:
        model = DepartmentCourse
        fields = "__all__"
    def create(self,request):
        object = self.save()
        units = request.POST.getlist("units")
        courses = request.POST.getlist("courses")
        for unit, course_id in zip(units,courses):
            course = Course.objects.get(id = int(course_id))
            DepartmentCourseLine.objects.get_or_create(dept_course = object,unit = int(unit), course = course)
        return object