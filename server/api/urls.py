"""
URL patterns for Blood Donation API.
"""
from django.urls import path
from . import views

urlpatterns = [
    # Auth
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('auth/check/', views.check_auth, name='check-auth'),

    # Profile
    path('profile/', views.profile_view, name='profile'),

    # Donors
    path('donors/', views.donor_list, name='donor-list'),

    # Blood Requests
    path('requests/', views.blood_request_list, name='request-list'),
    path('requests/<int:pk>/', views.blood_request_detail, name='request-detail'),

    # Donations
    path('donations/', views.donation_list, name='donation-list'),

    # Notifications
    path('notifications/', views.notification_list, name='notification-list'),
    path('notifications/<int:pk>/read/', views.mark_notification_read, name='notification-read'),
    path('notifications/read-all/', views.mark_all_notifications_read, name='notifications-read-all'),

    # Inventory
    path('inventory/', views.inventory_list, name='inventory-list'),

    # Stats
    path('stats/', views.stats_view, name='stats'),

    # Contact
    path('contact/', views.contact_view, name='contact'),

    # Admin
    path('admin/donors/', views.admin_donors, name='admin-donors'),
    path('admin/requests/', views.admin_requests, name='admin-requests'),
    path('admin/inventory/<str:blood_group>/', views.admin_update_inventory, name='admin-update-inventory'),
]
