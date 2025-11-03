from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from . import views
from .views import CustomTokenObtainPairView

urlpatterns = [
    path('', views.api_root, name='api_root'),
    path('token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('assignment/', views.GuardAssignmentView.as_view(), name='guard_assignment'),
    path('start-run/', views.start_route_run, name='start_route_run'),
    path('scan/', views.scan_checkpoint, name='scan_checkpoint'),
    path('create-route/', views.create_route, name='create_route'),
    path('list-routes/', views.list_routes, name='list_routes'),
    path('assign-guard/', views.assign_guard, name='assign_guard'),
    path('list-guards/', views.list_guards, name='list_guards'),
    path('daily-report/', views.daily_report, name='daily_report'),
    path('create-guard/', views.create_guard, name='create_guard'),
    path('update-guard/<int:pk>/', views.update_guard, name='update_guard'),
    path('delete-guard/<int:pk>/', views.delete_guard, name='delete_guard'),
    path('end-shift/', views.end_shift, name='end_shift'),
    path('check-role/', views.check_role, name='check_role'),
    path('create-incident/', views.create_incident, name='create_incident'),
    path('create-occurrence/', views.create_occurrence, name='create_occurrence'),
    path('clients/', views.ClientViewSet.as_view({'get': 'list', 'post': 'create'}), name='client_list'),
    path('clients/<int:pk>/', views.ClientViewSet.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'}), name='client_detail'),
    path('freeze-client/<int:pk>/', views.freeze_client, name='freeze_client'),
    path('create-client/', views.create_client, name='create_client'),
    path('create-admin/', views.create_admin, name='create_admin'),
    path('list-admins/', views.list_admins, name='list_admins'),
    path('update-admin/<int:pk>/', views.update_admin, name='update_admin'),
    path('delete-admin/<int:pk>/', views.delete_admin, name='delete_admin'),
    path('update-client/<int:pk>/', views.update_client, name='update_client'),
    path('delete-client/<int:pk>/', views.delete_client, name='delete_client'),
    path('update-guard/<int:pk>/', views.update_guard, name='update_guard'),
    path('health/', views.health_check, name='health_check'),
    path('static-debug/', views.static_files_debug, name='static_files_debug'),
]

