from django.contrib import admin
from django.urls import path,include
from django.conf import settings
from django.conf.urls.static import static
from student.views import landingview, testmailview


urlpatterns = [
    path('superadmin/', admin.site.urls),
    path('student/',include("student.urls")),
    path('admin/',include("admins.urls")),
    path('staff/',include("staff.urls")),
    path('mail-test/',testmailview),
    path('',landingview),
]
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root = settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)
