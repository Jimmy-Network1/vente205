"""
URL configuration for config project.
"""

from django.contrib import admin
from django.urls import path, include  # Ajoutez 'include'
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('voitures.urls')),  # Ajoutez cette ligne
]

# Pour servir les fichiers médias en développement
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)