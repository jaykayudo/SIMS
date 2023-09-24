from django.contrib import admin
from django.contrib.auth.admin import Group, UserAdmin as DjangoUserAdmin
from .models import *

# # Register your models here.
class UserAdmin(DjangoUserAdmin):
    fieldsets = (
        (None,{"fields":("email","password","is_auth_staff","is_student")}),
        ("Personal info",{"fields":("first_name","last_name")}),
        ("Permission",{"fields":("is_active","is_staff","is_superuser","groups","user_permissions")}),
        ("Important dates",{"fields":("last_login","date_joined")}),
    )
    add_fieldsets = ( (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2','is_auth_staff','is_student','is_staff'),
        }),)

    list_display = ("email","is_active","is_staff","is_auth_staff","is_student","is_superuser")
    search_fields = ("email",)
    ordering = ("email",)
    actions = ("make_active","make_inactive")
    def make_active(self,request,queryset):
        queryset.update(is_active = True)
    def make_inactive(self,request,queryset):
        queryset.update(is_active = False)
    make_active.short_description = 'Make Selected Users Active'
    make_inactive.short_description = 'Make Selected Users Inactive'

class DepartmentCourseLineAdmin(admin.TabularInline):
    model = DepartmentCourseLine
    raw_id_fields = ('course',)

class DepartmentCourseAdmin(admin.ModelAdmin):
    inlines = [DepartmentCourseLineAdmin]
    list_display = ['department','level','semester']

class CourseRegistrationLineAdmin(admin.TabularInline):
    model = CourseRegistrationLine
    raw_id_fields = ('course',)

class CourseRegistrationAdmin(admin.ModelAdmin):
    inlines = [CourseRegistrationLineAdmin]
    list_display = ['student','level']

admin.site.register(User,UserAdmin)
# admin.site.register(Subject)
admin.site.register(Course)
admin.site.register(Faculty)
admin.site.register(Staff)
admin.site.register(Student)
admin.site.register(Admin)
admin.site.register(Department)
admin.site.register(Event)
admin.site.register(CourseResource)
admin.site.register(DepartmentCourse,DepartmentCourseAdmin)
admin.site.register(SchoolSession)
admin.site.register(CourseRegistration, CourseRegistrationAdmin)
# admin.site.register(Mail)
# admin.site.register(Uploads)
# admin.site.register(Upload_Assignment)
# admin.site.register(SiteSetting)