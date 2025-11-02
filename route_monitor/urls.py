from django.contrib import admin
from django.urls import path, include
from routes.views import test_db
from django.views.generic import RedirectView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('routes.urls')),
    path('test-db/', test_db, name='test_db'),
    path('', RedirectView.as_view(url='/api/', permanent=False), name='index'),
]

