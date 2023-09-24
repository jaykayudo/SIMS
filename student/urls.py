from django.urls import path
from .views import *

app_name = "student"

urlpatterns = [
    path("login/",LoginView.as_view(), name="login"),
    path("logout/",LogoutView.as_view(), name="logout"),
    path("",DashboardView.as_view(), name="dashboard"),
    path('profile/',ProfileView.as_view(),name = "profile"),
    path('profile/edit/',EditProfileView.as_view(),name = "edit-profile"),
    path('profile/change-password/',UserPasswordChangeView.as_view(),name = "change-password"),
    path('courses/',CoursesView.as_view(),name = "courses"),
    path('resources/',ResourcesView.as_view(),name = "resources"),
    path('information/',InformationView.as_view(),name = "information"),
    path('events/',EventView.as_view(),name = "event"),
    path('events/<int:id>/',EventDetailsView.as_view(),name = "event-details"),
    path('events/<int:id>/attend/',EventAttendanceView.as_view(),name = "event-attend"),
    path('registration/',RegistrationListView.as_view(),name = "registration"),
    path('clearance/',ClearanceListView.as_view(),name = "clearance"),
    path('course-reg/', CourseRegistrationView.as_view(),name='register-course-form'),
    path('register-course/', RegisterCourseView.as_view(),name='register-course'),
    path('add-auxillary-courses/', AddAuxilaryCourse.as_view(),name='add-aux-courses'),
]