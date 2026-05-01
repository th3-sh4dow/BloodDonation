"""
Admin registration for Blood Donation models.
"""
from django.contrib import admin
from .models import UserProfile, BloodRequest, Donation, Notification, BloodInventory, ContactMessage


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'blood_group', 'phone', 'city', 'state', 'is_available', 'total_donations', 'last_donation_date']
    list_filter = ['blood_group', 'is_available', 'city', 'state']
    search_fields = ['user__first_name', 'user__last_name', 'user__email', 'phone', 'city']


@admin.register(BloodRequest)
class BloodRequestAdmin(admin.ModelAdmin):
    list_display = ['patient_name', 'blood_group_needed', 'units_needed', 'hospital_name', 'city', 'urgency', 'status', 'created_at']
    list_filter = ['blood_group_needed', 'urgency', 'status', 'city']
    search_fields = ['patient_name', 'hospital_name', 'city']


@admin.register(Donation)
class DonationAdmin(admin.ModelAdmin):
    list_display = ['donor', 'blood_group', 'units', 'donation_date', 'hospital_name']
    list_filter = ['blood_group', 'donation_date']
    search_fields = ['donor__first_name', 'donor__last_name', 'hospital_name']


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['user', 'title', 'notification_type', 'is_read', 'created_at']
    list_filter = ['notification_type', 'is_read']
    search_fields = ['title', 'message', 'user__username']


@admin.register(BloodInventory)
class BloodInventoryAdmin(admin.ModelAdmin):
    list_display = ['blood_group', 'units_available', 'last_updated']
    list_filter = ['blood_group']


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'subject', 'is_read', 'created_at']
    list_filter = ['is_read']
    search_fields = ['name', 'email', 'subject', 'message']
