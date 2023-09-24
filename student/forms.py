from typing import Any, Mapping, Optional, Type, Union
from django import forms
from django.contrib.auth import authenticate
from django.forms.utils import ErrorList
from admins.models import User,Admin,Staff,Student, phone_validator, SchoolSession, LEVEL, SEMESTER
class StudentLoginForm(forms.Form):
    regno = forms.CharField()
    password = forms.CharField(widget= forms.PasswordInput, strip =False)
    def __init__(self,request = None,*args,**kwargs):
        self.request = request
        self.user = None
        super().__init__(*args,**kwargs)
    def clean(self):
        regno = self.cleaned_data.get('regno')
        password = self.cleaned_data.get('password')
        self.user  = authenticate(self.request,username = regno,password=password)
        if not self.user:
            raise forms.ValidationError("Incorrect Credentials")
        return self.cleaned_data
    def get_user(self):
        return self.user

class EditProfileForm(forms.ModelForm):
    model = Student
    exclude = ['matric_number','user','status']

class CourseRegForm(forms.Form):
    session = forms.ModelChoiceField(queryset=None, widget=forms.Select(attrs={"class":"form-control"}))
    level = forms.ChoiceField(choices=LEVEL.choices, widget=forms.Select(attrs={"class":"form-control"}),label="Level")
    semester = forms.ChoiceField(choices=SEMESTER.choices, widget=forms.Select(attrs={"class":"form-control"}),label="Semester")

    def __init__(self, *args, **kwargs):
        super().__init__(*args,**kwargs)
        queryset = SchoolSession.objects.all().order_by('-year')
        self.fields['session'].queryset = queryset