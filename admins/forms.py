from django import forms
from .models import *
from django.conf import settings
from django.contrib.auth import authenticate


class AdminLoginForm(forms.Form):
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
           if not user.is_staff:
                raise forms.ValidationError("Unauthorized Account")
        self.user = user
        if not self.user:
            raise forms.ValidationError("Incorrect Credentials")
        return self.cleaned_data
    def get_user(self):
        return self.user

# class AddClassForm(forms.ModelForm):
#     class Meta:
#         model = Class
#         fields = "__all__"
#         widgets = {
#             'subject':forms.SelectMultiple(attrs={'class':'form-control'}),
#             'name':forms.TextInput(attrs={'class':'form-control','placeholder':' '}),
#             'classteacher':forms.TextInput(attrs={'class':'form-control','placeholder':' '})
#         }
# class AddSubjectForm(forms.ModelForm):
#     class Meta:
#         model = Subject
#         fields = "__all__"
#         widgets = {
#             'name':forms.TextInput(attrs={'class':'form-control','placeholder':' '}),
#             'abbr':forms.TextInput(attrs={'class':'form-control','placeholder':' '}),   
#         }
# class AddProgrammeForm(forms.Form):
#     klass = forms.ModelChoiceField(queryset=None,widget=forms.Select(attrs={'class':'form-control','placeholder':' '}))
#     subject = forms.ModelChoiceField(queryset=None,widget=forms.Select(attrs={'class':'form-control','placeholder':' '}))
#     def __init__(self,*args, **kwargs):
#         super(). __init__(*args, **kwargs)
#         queryset1 = Class.objects.all()
#         queryset2 = Subject.objects.all()
#         self.fields['klass'].queryset = queryset1
#         self.fields['subject'].queryset = queryset2
class StudentAddForm(forms.ModelForm):
    email= forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput,required = False,min_length=8)
    password2 = forms.CharField(widget=forms.PasswordInput, required = False)
    department = forms.ModelChoiceField(queryset=None,widget=forms.Select(attrs={'class':'form-control','placeholder':' '}))
    class Meta:
        model = Student
        exclude = ['user']
    def __init__(self,*args, **kwargs):
        super(). __init__(*args, **kwargs)
        queryset1 = Department.objects.all()
        self.fields['department'].queryset = queryset1
    def clean(self):
        email = self.cleaned_data.get('email')
        print(email)
        print(self.cleaned_data.get("password"))
        print(self.cleaned_data.get("password2"))
        if not email:
            self.add_error('email','Email is required for teaching staffs')
        if not self.cleaned_data.get('password'):
            self.add_error('password','Password is required for teaching staffs')
        if User.objects.filter(email = email).exists():
            self.add_error('email','User already Exists')
        if self.cleaned_data.get('password') != self.cleaned_data.get('password2'):
            self.add_error('password2',"Passwords deos not match")
        return self.cleaned_data


class StaffAddForm(forms.ModelForm):
    # department = forms.ModelChoiceField(queryset=None,widget=forms.Select(attrs={'class':'form-control','placeholder':' '}),required=False)
    email= forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput,required = False,min_length=8)
    password2 = forms.CharField(widget=forms.PasswordInput, required = False)
    auth_staff = forms.BooleanField()
    class Meta:
        model = Staff
        exclude = ['user','status']
    def clean(self):
        email = self.cleaned_data.get('email')
        if not email:
            self.add_error('email','Email is required for teaching staffs')
        if not self.cleaned_data.get('password'):
            self.add_error('password','Password is required for teaching staffs')
        if User.objects.filter(email = email).exists():
            self.add_error('email','User already Exists')
        if self.cleaned_data.get('password') != self.cleaned_data.get('password2'):
            self.add_error('password2',"Passwords deos not match")
        return self.cleaned_data

class StaffEditForm(forms.ModelForm):
    department = forms.ModelChoiceField(queryset=None,widget=forms.Select(attrs={'class':'form-control','placeholder':' '}),required=False)
    email= forms.EmailField()
    class Meta:
        model = Staff
        exclude = ['user','status']
    def clean(self):
        email = self.cleaned_data.get('email')
        if not email:
            self.add_error('email','Email is required for staffs')
        return self.cleaned_data


class AddEventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = "__all__"
        widgets = {
            'name':forms.TextInput(attrs={'class':'form-control','placeholder':' '}),
            'description':forms.TextInput(attrs={'class':'form-control','placeholder':' '}),
            'startdate':forms.DateInput(attrs={'class':'form-control','placeholder':' '}),
            'starttime':forms.TimeInput(attrs={'class':'form-control','placeholder':' '}),
        }
    
# class AddMailForm(forms.ModelForm):
#     # receivers = forms.ModelChoiceField(queryset=None,widget=forms.SelectMultiple(attrs={'class':'form-control'}),required=True)
#     class Meta:
#         model = Mail
#         fields = ['subject','message','flag','attachment']
#         widgets={
#             'flag':forms.Select(attrs={'class':'form-control','placeholder':' '}),
#         }
#     # def __init__(self,*args, **kwargs):
#     #     super(). __init__(*args, **kwargs)
#     #     queryset1 = User.objects.all()
#     #     self.fields['receivers'].queryset = queryset1

class ResetPasswordForm(forms.Form):
    password1 = forms.CharField(widget=forms.PasswordInput,required = True,min_length=8)
    password2 = forms.CharField(widget=forms.PasswordInput, required = True,min_length = 8)
    def clean(self):
        if self.cleaned_data.get('password1') != self.cleaned_data.get('password2'):
            self.add_error('password2',"Passwords deos not match")
        return self.cleaned_data
    
class AdminUpdateForm(forms.ModelForm):
    email= forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput,required = True,min_length=8)
    class Meta:
        model = Admin
        exclude = ['user']
    def clean(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email = email).exists():
            self.add_error('email','User already Exists')
        return self.cleaned_data
class UploadAssignmentAddForm(forms.ModelForm):
 
    class Meta:
        model = Upload_Assignment
        fields = ['name','staff']
        widgets = {'staff':forms.SelectMultiple(attrs={"class":"form-control"})}

