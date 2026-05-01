"""
API Views for Blood Donation System.
"""
from rest_framework import status, generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.db.models import Q, Count, Sum
from datetime import date, timedelta

from .models import UserProfile, BloodRequest, Donation, Notification, BloodInventory, ContactMessage
from .serializers import (
    UserSerializer, UserProfileSerializer, RegisterSerializer,
    BloodRequestSerializer, DonationSerializer, NotificationSerializer,
    BloodInventorySerializer, ContactMessageSerializer
)
from .utils import get_compatible_donors, get_compatible_recipients


# ── Authentication ──

@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def register_view(request):
    """Register a new user + donor profile."""
    serializer = RegisterSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        login(request, user)
        profile = UserProfile.objects.get(user=user)
        return Response({
            'message': 'Registration successful!',
            'user': UserSerializer(user).data,
            'profile': UserProfileSerializer(profile).data,
        }, status=status.HTTP_201_CREATED)
    return Response({'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def login_view(request):
    """Login with username/email and password."""
    username = request.data.get('username', '')
    password = request.data.get('password', '')

    # Allow login with email
    if '@' in username:
        try:
            user_obj = User.objects.get(email=username)
            username = user_obj.username
        except User.DoesNotExist:
            return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

    user = authenticate(request, username=username, password=password)
    if user is not None:
        login(request, user)
        try:
            profile = UserProfileSerializer(user.profile).data
        except UserProfile.DoesNotExist:
            profile = None
        return Response({
            'message': 'Login successful!',
            'user': UserSerializer(user).data,
            'profile': profile,
            'is_staff': user.is_staff,
        })
    return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)


@api_view(['POST'])
def logout_view(request):
    """Logout the current user."""
    logout(request)
    return Response({'message': 'Logged out successfully!'})


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def check_auth(request):
    """Check if user is authenticated."""
    if request.user.is_authenticated:
        try:
            profile = UserProfileSerializer(request.user.profile).data
        except UserProfile.DoesNotExist:
            profile = None
        return Response({
            'authenticated': True,
            'user': UserSerializer(request.user).data,
            'profile': profile,
            'is_staff': request.user.is_staff,
        })
    return Response({'authenticated': False})


# ── Profile ──

@api_view(['GET', 'PUT'])
@permission_classes([permissions.IsAuthenticated])
def profile_view(request):
    """Get or update the current user's profile."""
    try:
        profile = request.user.profile
    except UserProfile.DoesNotExist:
        return Response({'error': 'Profile not found'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        return Response(UserProfileSerializer(profile).data)

    # PUT — update profile
    serializer = UserProfileSerializer(profile, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        # Also update User fields if provided
        user = request.user
        if 'first_name' in request.data:
            user.first_name = request.data['first_name']
        if 'last_name' in request.data:
            user.last_name = request.data['last_name']
        if 'email' in request.data:
            user.email = request.data['email']
        user.save()
        return Response(UserProfileSerializer(profile).data)
    return Response({'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


# ── Donors ──

@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def donor_list(request):
    """Search and list donors. Filter by blood_group, city, availability."""
    queryset = UserProfile.objects.select_related('user').all()

    blood_group = request.query_params.get('blood_group')
    city = request.query_params.get('city')
    available_only = request.query_params.get('available', 'true')

    if blood_group:
        queryset = queryset.filter(blood_group=blood_group)
    if city:
        queryset = queryset.filter(city__icontains=city)
    if available_only.lower() == 'true':
        queryset = queryset.filter(is_available=True)

    serializer = UserProfileSerializer(queryset, many=True)
    data = serializer.data

    # Add compatibility info if blood_group filter is used
    if blood_group:
        compatible = get_compatible_donors(blood_group)
        # Also include compatible groups
        compatible_donors = UserProfile.objects.select_related('user').filter(
            blood_group__in=compatible,
            is_available=True
        )
        if city:
            compatible_donors = compatible_donors.filter(city__icontains=city)
        all_data = UserProfileSerializer(compatible_donors, many=True).data
        return Response({
            'donors': all_data,
            'compatible_groups': compatible,
            'total': len(all_data),
        })

    return Response({
        'donors': data,
        'total': len(data),
    })


# ── Blood Requests ──

@api_view(['GET', 'POST'])
def blood_request_list(request):
    """List all blood requests or create a new one."""
    if request.method == 'GET':
        queryset = BloodRequest.objects.all()
        status_filter = request.query_params.get('status', 'open')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        blood_group = request.query_params.get('blood_group')
        if blood_group:
            queryset = queryset.filter(blood_group_needed=blood_group)
        city = request.query_params.get('city')
        if city:
            queryset = queryset.filter(city__icontains=city)
        serializer = BloodRequestSerializer(queryset, many=True)
        return Response({'requests': serializer.data, 'total': queryset.count()})

    # POST — create new request
    if not request.user.is_authenticated:
        return Response({'error': 'Login required'}, status=status.HTTP_401_UNAUTHORIZED)
    serializer = BloodRequestSerializer(data=request.data)
    if serializer.is_valid():
        blood_request = serializer.save(requester=request.user)
        # Create notifications for compatible donors
        compatible_groups = get_compatible_donors(blood_request.blood_group_needed)
        compatible_donors = UserProfile.objects.filter(
            blood_group__in=compatible_groups,
            is_available=True,
            city__icontains=blood_request.city
        ).select_related('user')
        for donor_profile in compatible_donors:
            if donor_profile.user != request.user:
                Notification.objects.create(
                    user=donor_profile.user,
                    title=f"🚨 Blood Request: {blood_request.blood_group_needed}",
                    message=f"{blood_request.patient_name} needs {blood_request.units_needed} unit(s) of {blood_request.blood_group_needed} blood at {blood_request.hospital_name}, {blood_request.city}. Urgency: {blood_request.urgency}.",
                    notification_type='emergency' if blood_request.urgency == 'emergency' else 'info',
                )
        return Response(BloodRequestSerializer(blood_request).data, status=status.HTTP_201_CREATED)
    return Response({'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT'])
def blood_request_detail(request, pk):
    """View or update a blood request."""
    try:
        blood_request = BloodRequest.objects.get(pk=pk)
    except BloodRequest.DoesNotExist:
        return Response({'error': 'Request not found'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        return Response(BloodRequestSerializer(blood_request).data)

    # PUT — update status
    if not request.user.is_authenticated:
        return Response({'error': 'Login required'}, status=status.HTTP_401_UNAUTHORIZED)
    serializer = BloodRequestSerializer(blood_request, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response({'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


# ── Donations ──

@api_view(['GET', 'POST'])
@permission_classes([permissions.IsAuthenticated])
def donation_list(request):
    """List user's donations or record a new one."""
    if request.method == 'GET':
        donations = Donation.objects.filter(donor=request.user)
        serializer = DonationSerializer(donations, many=True)
        return Response({'donations': serializer.data, 'total': donations.count()})

    # POST — record donation
    serializer = DonationSerializer(data=request.data)
    if serializer.is_valid():
        donation = serializer.save(donor=request.user)
        # Update donor profile
        profile = request.user.profile
        profile.last_donation_date = donation.donation_date
        profile.total_donations += donation.units
        profile.save()
        # Update inventory
        inventory, _ = BloodInventory.objects.get_or_create(blood_group=donation.blood_group)
        inventory.units_available += donation.units
        inventory.save()
        return Response(DonationSerializer(donation).data, status=status.HTTP_201_CREATED)
    return Response({'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


# ── Notifications ──

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def notification_list(request):
    """List user's notifications."""
    notifications = Notification.objects.filter(user=request.user)
    unread_count = notifications.filter(is_read=False).count()
    serializer = NotificationSerializer(notifications[:50], many=True)
    return Response({
        'notifications': serializer.data,
        'unread_count': unread_count,
    })


@api_view(['PUT'])
@permission_classes([permissions.IsAuthenticated])
def mark_notification_read(request, pk):
    """Mark a notification as read."""
    try:
        notification = Notification.objects.get(pk=pk, user=request.user)
        notification.is_read = True
        notification.save()
        return Response({'message': 'Marked as read'})
    except Notification.DoesNotExist:
        return Response({'error': 'Not found'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['PUT'])
@permission_classes([permissions.IsAuthenticated])
def mark_all_notifications_read(request):
    """Mark all notifications as read."""
    Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
    return Response({'message': 'All notifications marked as read'})


# ── Inventory ──

@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def inventory_list(request):
    """Get blood inventory."""
    inventory = BloodInventory.objects.all()
    serializer = BloodInventorySerializer(inventory, many=True)
    return Response({'inventory': serializer.data})


# ── Stats ──

@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def stats_view(request):
    """Get dashboard stats."""
    total_donors = UserProfile.objects.count()
    available_donors = UserProfile.objects.filter(is_available=True).count()
    total_requests = BloodRequest.objects.count()
    open_requests = BloodRequest.objects.filter(status='open').count()
    fulfilled_requests = BloodRequest.objects.filter(status='fulfilled').count()
    total_donations = Donation.objects.aggregate(total=Sum('units'))['total'] or 0

    # Recent activity
    recent_requests = BloodRequestSerializer(
        BloodRequest.objects.filter(status='open').order_by('-created_at')[:5],
        many=True
    ).data

    # Blood group distribution
    group_distribution = list(
        UserProfile.objects.values('blood_group')
        .annotate(count=Count('id'))
        .order_by('blood_group')
    )

    return Response({
        'total_donors': total_donors,
        'available_donors': available_donors,
        'total_requests': total_requests,
        'open_requests': open_requests,
        'fulfilled_requests': fulfilled_requests,
        'total_donations': total_donations,
        'lives_saved': total_donations * 3,  # Each donation saves up to 3 lives
        'recent_requests': recent_requests,
        'group_distribution': group_distribution,
    })


# ── Contact ──

@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def contact_view(request):
    """Submit a contact message."""
    serializer = ContactMessageSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response({'message': 'Message sent successfully!'}, status=status.HTTP_201_CREATED)
    return Response({'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


# ── Admin endpoints ──

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def admin_donors(request):
    """Admin: list all donors."""
    if not request.user.is_staff:
        return Response({'error': 'Admin access required'}, status=status.HTTP_403_FORBIDDEN)
    donors = UserProfile.objects.select_related('user').all()
    search = request.query_params.get('search')
    if search:
        donors = donors.filter(
            Q(user__first_name__icontains=search) |
            Q(user__last_name__icontains=search) |
            Q(user__email__icontains=search) |
            Q(city__icontains=search) |
            Q(blood_group=search)
        )
    serializer = UserProfileSerializer(donors, many=True)
    return Response({'donors': serializer.data, 'total': donors.count()})


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def admin_requests(request):
    """Admin: list all blood requests (all statuses)."""
    if not request.user.is_staff:
        return Response({'error': 'Admin access required'}, status=status.HTTP_403_FORBIDDEN)
    requests_qs = BloodRequest.objects.all()
    status_filter = request.query_params.get('status')
    if status_filter:
        requests_qs = requests_qs.filter(status=status_filter)
    serializer = BloodRequestSerializer(requests_qs, many=True)
    return Response({'requests': serializer.data, 'total': requests_qs.count()})


@api_view(['PUT'])
@permission_classes([permissions.IsAuthenticated])
def admin_update_inventory(request, blood_group):
    """Admin: update blood inventory."""
    if not request.user.is_staff:
        return Response({'error': 'Admin access required'}, status=status.HTTP_403_FORBIDDEN)
    inventory, _ = BloodInventory.objects.get_or_create(blood_group=blood_group)
    units = request.data.get('units_available')
    if units is not None:
        inventory.units_available = int(units)
        inventory.save()
    return Response(BloodInventorySerializer(inventory).data)
