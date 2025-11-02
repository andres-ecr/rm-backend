from django.utils import timezone
from django.db import transaction, IntegrityError
from rest_framework import status, generics, viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.reverse import reverse
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.exceptions import InvalidToken
from django.contrib.auth.models import User
from django.db.models import Prefetch
from django.http import JsonResponse
from .models import Client, Route, GuardAssignment, RouteRun, Checkpoint, CheckpointScan, UserProfile, Incident, Occurrence
from .serializers import (
    ClientSerializer, RouteSerializer, OptimizedGuardAssignmentSerializer, UserSerializer,
    AssignmentCheckpointScanSerializer, IncidentSerializer, ReportRouteRunSerializer, OccurrenceSerializer,
    AssignmentRouteRunSerializer
)
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .permissions import IsSuperAdmin, IsAdminUser, IsClientUser, IsGuardUser
import logging

logger = logging.getLogger(__name__)

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # Add custom claims
        token['username'] = user.username
        token['is_superadmin'] = user.is_superuser
        if user.is_superuser:
            token['is_admin'] = True
            token['client_id'] = None
        elif hasattr(user, 'userprofile'):
            token['is_admin'] = user.userprofile.is_admin
            token['client_id'] = user.userprofile.client.id if user.userprofile.client else None
        elif hasattr(user, 'client'):
            token['is_client'] = True
            token['client_id'] = user.client.id
        else:
            token['is_guard'] = True
            token['client_id'] = getattr(user.userprofile, 'client_id', None) if hasattr(user, 'userprofile') else None

        return token

class CustomTokenObtainPairView(TokenObtainPairView):
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        
        try:
            serializer.is_valid(raise_exception=True)
        except Exception as e:
            # Handle wrong credentials
            if 'no active account' in str(e).lower() or 'credenciales no tiene una cuenta activa' in str(e).lower():
                return Response(
                    {'error': 'Credenciales inválidas. Usuario o contraseña incorrectos'}, 
                    status=status.HTTP_401_UNAUTHORIZED
                )
            raise e

        user = serializer.user

        # Check if user's account is frozen (after successful authentication)
        if user.is_superuser:
            # Superadmins bypass the frozen check
            pass
        elif hasattr(user, 'userprofile') and hasattr(user.userprofile, 'client') and not user.userprofile.client.is_active:
            return Response(
                {'error': 'Cuenta congelada. Por favor contacte a su administrador'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        elif hasattr(user, 'client') and not user.client.is_active:
            return Response(
                {'error': 'Cuenta congelada. Por favor contacte a soporte'}, 
                status=status.HTTP_403_FORBIDDEN
            )

        if user.is_superuser:
            role = 'superadmin'
        elif hasattr(user, 'client'):
            role = 'client'
        elif hasattr(user, 'userprofile') and user.userprofile.is_admin:
            role = 'admin'
        else:
            role = 'guard'

        return Response({
            'access': str(serializer.validated_data.get('access')),
            'refresh': str(serializer.validated_data.get('refresh')),
            'role': role,
        }, status=status.HTTP_200_OK)

class ClientViewSet(viewsets.ModelViewSet):
    queryset = Client.objects.all()
    serializer_class = ClientSerializer
    permission_classes = [IsSuperAdmin]

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def freeze_client(request, pk):
    if not request.user.is_superuser:
        return Response({'error': 'Unauthorized. Only super admins can freeze or unfreeze clients.'}, status=status.HTTP_403_FORBIDDEN)

    try:
        with transaction.atomic():
            client = Client.objects.get(id=pk)
            client.is_active = not client.is_active
            client.save()

            # Freeze/unfreeze all associated user accounts
            User.objects.filter(userprofile__client=client).update(is_active=client.is_active)

            action = "frozen" if not client.is_active else "activated"
            return Response({
                'message': f'Client and associated accounts {action} successfully',
                'is_active': client.is_active,
                'client_id': client.id,
                'client_name': client.name
            }, status=status.HTTP_200_OK)
    except Client.DoesNotExist:
        return Response({'error': 'Client not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'error': f'An error occurred: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def api_root(request, format=None):
    return Response({
        'assignment': reverse('guard_assignment', request=request, format=format),
        'start_run': reverse('start_route_run', request=request, format=format),
        'scan': reverse('scan_checkpoint', request=request, format=format),
        'create_route': reverse('create_route', request=request, format=format),
        'assign_guard': reverse('assign_guard', request=request, format=format),
        'daily_report': reverse('daily_report', request=request, format=format),
        'create_guard': reverse('create_guard', request=request, format=format),
        'list_guards': reverse('list_guards', request=request, format=format),
        'update_guard': 'api/update-guard/{pk}/',
        'delete_guard': 'api/delete-guard/{pk}/',
        'end_shift': reverse('end_shift', request=request, format=format),
        'check_role': reverse('check_role', request=request, format=format),
        'create_incident': reverse('create_incident', request=request, format=format),
        'create_occurrence': reverse('create_occurrence', request=request, format=format),
        'clients': reverse('client_list', request=request, format=format),
        'freeze_client': 'api/freeze-client/{pk}/',
        'create_admin': reverse('create_admin', request=request, format=format),
        'list_admins': reverse('list_admins', request=request, format=format),
        'create_client': reverse('create_client', request=request, format=format)
    })

class GuardAssignmentView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = OptimizedGuardAssignmentSerializer

    def get_object(self):
        return GuardAssignment.objects.select_related('route', 'guard__userprofile').prefetch_related(
            'route__checkpoints',
            Prefetch('route_runs', queryset=RouteRun.objects.filter(completed=False).order_by('-start_time'))
        ).get(guard=self.request.user)

    def retrieve(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            if not instance.guard.userprofile.client.is_active:
                return Response({'error': 'Your client account is frozen'}, status=status.HTTP_403_FORBIDDEN)
            serializer = self.get_serializer(instance)
            data = serializer.data
            
            active_run = instance.route_runs.first()
            if active_run:
                run_data = AssignmentRouteRunSerializer(active_run).data
                latest_scan = CheckpointScan.objects.filter(route_run=active_run).order_by('-scanned_at').first()
                if latest_scan:
                    run_data['latest_scan'] = AssignmentCheckpointScanSerializer(latest_scan).data
                data['active_run'] = run_data
            else:
                last_run = instance.route_runs.filter(completed=True).order_by('-end_time').first()
                if last_run:
                    data['last_completed_run'] = AssignmentRouteRunSerializer(last_run).data

            return Response(data)
        except GuardAssignment.DoesNotExist:
            return Response(
                {'error': 'No tienes una asignación'},
                status=status.HTTP_404_NOT_FOUND
            )

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def start_route_run(request):
    try:
        assignment = GuardAssignment.objects.get(guard=request.user)
        if not assignment.guard.userprofile.client.is_active:
            return Response({'error': 'Your client account is frozen'}, status=status.HTTP_403_FORBIDDEN)
        
        active_run = RouteRun.objects.filter(assignment=assignment, completed=False).first()
        if active_run:
            return Response(
                {'error': 'Ya tienes un recorrido activo sin completar'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        new_run = RouteRun.objects.create(assignment=assignment)
        serializer = AssignmentRouteRunSerializer(new_run)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    except GuardAssignment.DoesNotExist:
        return Response(
            {'error': 'No tienes una ruta asignada'},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
@permission_classes([IsAdminUser|IsClientUser])
def daily_report(request):
    date = request.query_params.get('date', timezone.now().date())
    guard_id = request.query_params.get('guard_id')

    if not guard_id:
        return Response({'error': 'Se requiere el ID del guardia'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        guard = User.objects.get(id=guard_id)
        if not guard.userprofile.client.is_active:
            return Response({'error': 'Client account is frozen'}, status=status.HTTP_403_FORBIDDEN)
        
        route_runs = RouteRun.objects.filter(
            assignment__guard=guard,
            start_time__date=date
        ).select_related('assignment__guard').prefetch_related(
            Prefetch('checkpoint_scans', queryset=CheckpointScan.objects.order_by('scanned_at')),
            'incidents'
        ).order_by('start_time')

        run_data = ReportRouteRunSerializer(route_runs, many=True).data

        response_data = {
            'guard': guard.username,
            'date': date,
            'route_runs': run_data
        }

        return Response(response_data)
    except User.DoesNotExist:
        return Response({'error': 'Guardia no encontrado'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def scan_checkpoint(request):
    qr_code = request.data.get('qr_code')
    if not qr_code:
        return Response({'error': 'Se requiere el código QR'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        with transaction.atomic():
            assignment = GuardAssignment.objects.select_related('route').prefetch_related(
                Prefetch('route__checkpoints', queryset=Checkpoint.objects.order_by('order')),
                Prefetch('route_runs', queryset=RouteRun.objects.filter(completed=False), to_attr='active_runs')
            ).get(guard=request.user)

            if not assignment.guard.userprofile.client.is_active:
                return Response({'error': 'Your client account is frozen'}, status=status.HTTP_403_FORBIDDEN)

            active_run = assignment.active_runs[0] if assignment.active_runs else None
            if not active_run:
                return Response({'error': 'No hay un recorrido activo'}, status=status.HTTP_400_BAD_REQUEST)
            
            checkpoint = next((cp for cp in assignment.route.checkpoints.all() if cp.qr_code == qr_code), None)
            if not checkpoint:
                return Response({'error': 'Código QR no válido para esta ruta'}, status=status.HTTP_400_BAD_REQUEST)
            
            last_scan = CheckpointScan.objects.filter(route_run=active_run).order_by('-checkpoint__order').first()
            expected_order = 1 if not last_scan else last_scan.checkpoint.order + 1
            
            if checkpoint.order != expected_order:
                return Response({
                    'error': f'Orden incorrecto. Se esperaba el punto de control {expected_order}, pero se escaneó el {checkpoint.order}'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            checkpoint_scan, created = CheckpointScan.objects.get_or_create(
                checkpoint=checkpoint,
                route_run=active_run,
                defaults={'scanned_at': timezone.now()}
            )
            
            if not created:
                return Response({
                    'message': 'Este punto de control ya fue escaneado en este recorrido',
                    'scan_data': AssignmentCheckpointScanSerializer(checkpoint_scan).data
                }, status=status.HTTP_200_OK)
            
            total_checkpoints = assignment.route.checkpoints.count()
            scanned_checkpoints = active_run.checkpoint_scans.count()
            
            if scanned_checkpoints == total_checkpoints:
                active_run.completed = True
                active_run.end_time = timezone.now()
                active_run.save()
            
            serializer = AssignmentCheckpointScanSerializer(checkpoint_scan)
            return Response({
                'message': 'Punto de control escaneado exitosamente',
                'scan_data': serializer.data,
                'run_completed': active_run.completed
            }, status=status.HTTP_201_CREATED)
            
    except GuardAssignment.DoesNotExist:
        return Response({'error': 'No tienes una ruta asignada'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([IsSuperAdmin])
def create_route(request):
    client_id = request.data.get('client_id')
    if not client_id:
        return Response({'error': 'client_id is required'}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        client = Client.objects.get(id=client_id)
    except Client.DoesNotExist:
        return Response({'error': 'Invalid client_id'}, status=status.HTTP_404_NOT_FOUND)
    
    serializer = RouteSerializer(data=request.data)
    if serializer.is_valid():
        route = serializer.save(client=client)
        return Response(RouteSerializer(route).data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsSuperAdmin|IsAdminUser|IsClientUser])
def list_routes(request):
    if request.user.is_superuser:
        routes = Route.objects.all()
    elif hasattr(request.user, 'userprofile'):
        routes = Route.objects.filter(client=request.user.userprofile.client)
    elif hasattr(request.user, 'client'):
        routes = Route.objects.filter(client=request.user.client)
    else:
        return Response({'error': 'Unauthorized'}, status=status.HTTP_403_FORBIDDEN)
    
    serializer = RouteSerializer(routes, many=True)
    return Response(serializer.data)

@api_view(['POST'])
@permission_classes([IsAdminUser|IsClientUser])
def assign_guard(request):
    guard_id = request.data.get('guard_id')
    route_id = request.data.get('route_id')
    shift = request.data.get('shift')

    if not all([guard_id, route_id, shift]):
        return Response({'error': 'Faltan datos requeridos'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        guard = User.objects.get(id=guard_id)
        route = Route.objects.get(id=route_id)
        
        # Check if the user is a client or admin and verify permissions
        if hasattr(request.user, 'client'):
            client = request.user.client
        else:
            client = request.user.userprofile.client
            
        if guard.userprofile.client != client:
            return Response({'error': 'No puedes asignar guardias de otros clientes'}, status=status.HTTP_403_FORBIDDEN)
        
        if route.client != client:
            return Response({'error': 'No puedes asignar rutas de otros clientes'}, status=status.HTTP_403_FORBIDDEN)
        
        assignment, created = GuardAssignment.objects.update_or_create(
            guard=guard,
            defaults={'route': route, 'shift': shift}
        )
        serializer = OptimizedGuardAssignmentSerializer(assignment)
        return Response(serializer.data, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)
    except User.DoesNotExist:
        return Response({'error': 'Usuario no encontrado'}, status=status.HTTP_404_NOT_FOUND)
    except Route.DoesNotExist:
        return Response({'error': 'Ruta no encontrada'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_guards(request):
    logger.info(f"Listing guards for user: {request.user.username}")
    
    if request.user.is_superuser:
        guards = User.objects.filter(
            is_staff=False,
            userprofile__is_admin=False
        ).select_related('userprofile__client')
        logger.info("Superadmin fetching all guards")
    elif (hasattr(request.user, 'userprofile') and request.user.userprofile.is_admin) or hasattr(request.user, 'client'):
        client = request.user.client if hasattr(request.user, 'client') else request.user.userprofile.client
        logger.info(f"Fetching guards for client: {client.name}")
        guards = User.objects.filter(
            is_staff=False,
            userprofile__is_admin=False,
            userprofile__client=client
        ).select_related('userprofile__client')
    else:
        logger.warning(f"Unauthorized access attempt by user: {request.user.username}")
        return Response({'error': 'Unauthorized'}, status=status.HTTP_403_FORBIDDEN)

    logger.info(f"Found {guards.count()} guards")

    serializer = UserSerializer(guards, many=True)
    return Response(serializer.data)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_guard(request):
    logger.info(f"Creating guard, requested by user: {request.user.username}")
    
    if not (hasattr(request.user, 'userprofile') and request.user.userprofile.is_admin) and not hasattr(request.user, 'client'):
        logger.warning(f"Unauthorized guard creation attempt by user: {request.user.username}")
        return Response({'error': 'Unauthorized'}, status=status.HTTP_403_FORBIDDEN)

    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        try:
            with transaction.atomic():
                password = request.data.get('password')
                if not password:
                    logger.warning("Guard creation attempt without password")
                    return Response({'error': 'Password is required'}, status=status.HTTP_400_BAD_REQUEST)
                
                user = serializer.save()
                user.set_password(password)
                user.is_staff = False
                user.save()
                
                client = request.user.client if hasattr(request.user, 'client') else request.user.userprofile.client
                logger.info(f"Associating guard with client: {client.name}")
                
                profile, created = UserProfile.objects.update_or_create(
                    user=user,
                    defaults={
                        'is_admin': False,
                        'client': client
                    }
                )
                
                # Verify the client association
                if profile.client != client:
                    logger.error(f"Failed to associate guard with client. Expected: {client.name}, Got: {profile.client.name if profile.client else 'None'}")
                    raise ValueError("Failed to associate guard with the correct client")
                
                # Refresh the user object to include the newly created profile
                user.refresh_from_db()
                
                logger.info(f"Guard created successfully: {user.username}, associated with client: {user.userprofile.client.name}")
                return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)
        except ValueError as ve:
            logger.error(f"Error in guard creation: {str(ve)}")
            return Response({'error': str(ve)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Unexpected error in guard creation: {str(e)}")
            return Response({'error': 'An unexpected error occurred while creating the guard'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    logger.warning(f"Invalid data for guard creation: {serializer.errors}")
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['DELETE'])
@permission_classes([IsAdminUser|IsClientUser])
def delete_guard(request, pk):
    try:
        user = User.objects.get(pk=pk)
        
        # Get the client based on the user type
        if hasattr(request.user, 'client'):
            client = request.user.client
        else:
            client = request.user.userprofile.client
            
        if user.userprofile.client != client:
            return Response({'error': 'No puedes eliminar guardias de otros clientes'}, status=status.HTTP_403_FORBIDDEN)
    except User.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    user.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_incident(request):
    try:
        active_run = RouteRun.objects.filter(assignment__guard=request.user, completed=False).first()
        if not active_run:
            return Response({'error': 'No hay un recorrido activo'}, status=status.HTTP_400_BAD_REQUEST)
        
        if not active_run.assignment.guard.userprofile.client.is_active:
            return Response({'error': 'Your client account is frozen'}, status=status.HTTP_403_FORBIDDEN)
        
        serializer = IncidentSerializer(data=request.data)
        if serializer.is_valid():
            incident = serializer.save(guard=request.user, route_run=active_run)
            return Response(IncidentSerializer(incident).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def end_shift(request):
    try:
        assignment = GuardAssignment.objects.get(guard=request.user)
        if not assignment.guard.userprofile.client.is_active:
            return Response({'error': 'Your client account is frozen'}, status=status.HTTP_403_FORBIDDEN)
        
        active_run = RouteRun.objects.filter(assignment=assignment, completed=False).first()
        if active_run:
            active_run.mark_as_completed()
        
        return Response({"message": "Shift ended successfully"}, status=status.HTTP_200_OK)
    except GuardAssignment.DoesNotExist:
        return Response({"error": "No active assignment found"}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def check_role(request):
    user = request.user
    if user.is_superuser:
        role = 'superadmin'
    elif hasattr(user, 'client'):
        role = 'client'
    elif hasattr(user, 'userprofile') and user.userprofile.is_admin:
        role = 'admin'
    else:
        role = 'guard'
    
    return Response({'role': role})

@api_view(['POST'])
@permission_classes([IsSuperAdmin])
def create_client(request):
    serializer = ClientSerializer(data=request.data)
    if serializer.is_valid():
        client = serializer.save()
        return Response(ClientSerializer(client).data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([IsSuperAdmin|IsClientUser])
def create_admin(request):
    if not (request.user.is_superuser or hasattr(request.user, 'client')):
        return Response({'error': 'Only super admins and clients can create admins'}, status=status.HTTP_403_FORBIDDEN)

    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        user.is_staff = True
        user.save()
        
        client = None
        if request.user.is_superuser:
            client_id = request.data.get('client_id')
            if client_id:
                try:
                    client = Client.objects.get(id=client_id)
                except Client.DoesNotExist:
                    return Response({'error': 'Invalid client_id'}, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({'error': 'client_id is required for super admin'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            client = request.user.client

        UserProfile.objects.create(user=user, is_admin=True, client=client)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsSuperAdmin|IsClientUser])
def list_admins(request):
    if request.user.is_superuser:
        admins = User.objects.filter(
            is_staff=True,
            userprofile__is_admin=True
        ).select_related('userprofile__client')
    elif hasattr(request.user, 'client'):
        admins = User.objects.filter(
            is_staff=True,
            userprofile__is_admin=True,
            userprofile__client=request.user.client
        ).select_related('userprofile__client')
    else:
        return Response({'error': 'Unauthorized'}, status=status.HTTP_403_FORBIDDEN)
    
    serializer = UserSerializer(admins, many=True)
    return Response(serializer.data)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_occurrence(request):
    try:
        active_run = RouteRun.objects.filter(assignment__guard=request.user, completed=False).first()
        if not active_run:
            return Response({'error': 'No hay un recorrido activo'}, status=status.HTTP_400_BAD_REQUEST)
        
        if not active_run.assignment.guard.userprofile.client.is_active:
            return Response({'error': 'Your client account is frozen'}, status=status.HTTP_403_FORBIDDEN)
        
        serializer = OccurrenceSerializer(data=request.data)
        if serializer.is_valid():
            occurrence = serializer.save(route_run=active_run)
            return Response(OccurrenceSerializer(occurrence).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['DELETE'])
@permission_classes([IsSuperAdmin|IsClientUser])
def delete_admin(request, pk):
    try:
        admin = User.objects.get(pk=pk)
        
        # Check permissions based on role
        if request.user.is_superuser:
            # Superadmin can delete any admin
            pass
        elif hasattr(request.user, 'client'):
            # Client can only delete admins associated with their client
            if not hasattr(admin, 'userprofile') or not admin.userprofile.is_admin or admin.userprofile.client != request.user.client:
                return Response({'error': 'No puedes eliminar administradores de otros clientes'}, 
                               status=status.HTTP_403_FORBIDDEN)
        else:
            return Response({'error': 'No tienes permisos para eliminar administradores'}, 
                           status=status.HTTP_403_FORBIDDEN)
        
        # Perform the deletion
        admin.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    except User.DoesNotExist:
        return Response({'error': 'Administrador no encontrado'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['PUT', 'PATCH'])
@permission_classes([IsSuperAdmin|IsClientUser])
def update_admin(request, pk):
    try:
        admin = User.objects.get(pk=pk)
        
        # Check permissions based on role
        if request.user.is_superuser:
            # Superadmin can update any admin
            pass
        elif hasattr(request.user, 'client'):
            # Client can only update admins associated with their client
            if not hasattr(admin, 'userprofile') or not admin.userprofile.is_admin or admin.userprofile.client != request.user.client:
                return Response({'error': 'No puedes actualizar administradores de otros clientes'}, 
                               status=status.HTTP_403_FORBIDDEN)
        else:
            return Response({'error': 'No tienes permisos para actualizar administradores'}, 
                           status=status.HTTP_403_FORBIDDEN)
        
        # Update the admin
        serializer = UserSerializer(admin, data=request.data, partial=True)
        if serializer.is_valid():
            # Handle password update if provided
            password = request.data.get('password')
            if password:
                admin.set_password(password)
                admin.save()
            
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except User.DoesNotExist:
        return Response({'error': 'Administrador no encontrado'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['PUT', 'PATCH'])
@permission_classes([IsSuperAdmin])
def update_client(request, pk):
    try:
        client = Client.objects.get(pk=pk)
        
        # Only update the client fields, not the associated user credentials
        serializer = ClientSerializer(client, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except Client.DoesNotExist:
        return Response({'error': 'Cliente no encontrado'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['DELETE'])
@permission_classes([IsSuperAdmin])
def delete_client(request, pk):
    try:
        client = Client.objects.get(pk=pk)
        client.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    except Client.DoesNotExist:
        return Response({'error': 'Cliente no encontrado'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['PUT', 'PATCH'])
@permission_classes([IsSuperAdmin|IsClientUser|IsAdminUser])
def update_guard(request, pk):
    try:
        guard = User.objects.get(pk=pk)
        
        # Check permissions based on role
        if request.user.is_superuser:
            # Superadmin can update any guard
            pass
        elif hasattr(request.user, 'userprofile') and request.user.userprofile.is_admin:
            # Admin can only update guards associated with their client
            if not hasattr(guard, 'userprofile') or guard.userprofile.is_admin or guard.userprofile.client != request.user.userprofile.client:
                return Response({'error': 'No puedes actualizar vigilantes de otros clientes'}, 
                               status=status.HTTP_403_FORBIDDEN)
        elif hasattr(request.user, 'client'):
            # Client can only update guards associated with their client
            if not hasattr(guard, 'userprofile') or guard.userprofile.is_admin or guard.userprofile.client != request.user.client:
                return Response({'error': 'No puedes actualizar vigilantes de otros clientes'}, 
                               status=status.HTTP_403_FORBIDDEN)
        else:
            return Response({'error': 'No tienes permisos para actualizar vigilantes'}, 
                           status=status.HTTP_403_FORBIDDEN)
        
        # Update the guard
        serializer = UserSerializer(guard, data=request.data, partial=True)
        if serializer.is_valid():
            # Handle password update if provided
            password = request.data.get('password')
            if password:
                guard.set_password(password)
                guard.save()
            
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except User.DoesNotExist:
        return Response({'error': 'Vigilante no encontrado'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

def test_db(request):
    try:
        user_count = User.objects.count()
        return JsonResponse({"message": "Database connection successful", "user_count": user_count})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

@api_view(['GET'])
def health_check(request):
    """Simple health check endpoint for monitoring"""
    return Response({
        'status': 'healthy',
        'timestamp': timezone.now().isoformat(),
        'message': 'Service is running'
    })

