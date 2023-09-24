from django.urls import path
from . import views

app_name = 'staff'

urlpatterns = [
    path('', views.home,name = "home"),
    path('login/', views.LoginView.as_view(),name = "login"),
    path('dashboard/', views.DashboardView.as_view(),name = "dashboard"),
    # path('dashboard/get-schedule/', views.scheduleGetView),
    path('profile/', views.ProfileView.as_view(),name = "profile"),
    path('profile/edit/', views.EditProfileView.as_view(),name = "edit-profile"),
    path('profile/change-password/', views.UserPasswordChangeView.as_view(),name = "change-password"),
    path('resources/', views.ResourceView.as_view(),name = "resources"),
    path('resources/upload/', views.ResourceUploadView.as_view(),name = "resources-upload"),
    # path('classes/<int:id>/', views.ClassDetailsView.as_view(),name = "class-details"),
    path('students/', views.StudentListView.as_view(),name = "student-list"),
    path('students/<int:pk>/', views.StudentDetailView.as_view(),name = "student-details"),
    path('newsletter/', views.NewsletterView.as_view(),name = "newsletter"),
    # path('newsletter/<int:id>/', views.NewsletterDetailsView.as_view(),name = "newsletter-details"),
    path('newsletter/create/', views.NewsletterCreateView.as_view(),name = "newsletter-create"),
    path('department-course/', views.DepartmentCourseList.as_view(),name = "department-course-list"),
    path('department-course/create/', views.DepartmentCourseFormView.as_view(),name = "department-course-form"),
    path('department-course/<int:id>/add/', views.DepartmentCourseAddView.as_view(),name = "department-course-add"),
    # path('inbox/<int:id>/delete', views.InboxDeleteView.as_view(),name = "inbox-delete"),
    # path('uploads/', views.UploadView.as_view(),name = "uploads"),
    path('logout/', views.LogoutView.as_view(),name = "logout"),
]