from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView

urlpatterns = [
    path('', RedirectView.as_view(url='/notes/', permanent=False)),
    path('admin/', admin.site.urls),
    path('notes/', include('notes.urls')),
    path('notes/security/', RedirectView.as_view(url='/security/', permanent=False)),
    path('security/', include('notes.security_urls')),
     
    path('api/registration/', include('registration.urls')),
]