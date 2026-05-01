"""
Models for the Blood Donation Management System.
"""
from django.db import models
from django.contrib.auth.models import User
from datetime import date, timedelta


BLOOD_GROUP_CHOICES = [
    ('A+', 'A+'), ('A-', 'A-'),
    ('B+', 'B+'), ('B-', 'B-'),
    ('AB+', 'AB+'), ('AB-', 'AB-'),
    ('O+', 'O+'), ('O-', 'O-'),
]

URGENCY_CHOICES = [
    ('emergency', 'Emergency'),
    ('urgent', 'Urgent'),
    ('routine', 'Routine'),
]

REQUEST_STATUS_CHOICES = [
    ('open', 'Open'),
    ('fulfilled', 'Fulfilled'),
    ('expired', 'Expired'),
    ('cancelled', 'Cancelled'),
]


class UserProfile(models.Model):
    """Extended user profile for donors."""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    blood_group = models.CharField(max_length=5, choices=BLOOD_GROUP_CHOICES)
    phone = models.CharField(max_length=15)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    date_of_birth = models.DateField(null=True, blank=True)
    last_donation_date = models.DateField(null=True, blank=True)
    is_available = models.BooleanField(default=True)
    total_donations = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.get_full_name()} ({self.blood_group})"

    @property
    def is_eligible(self):
        """Check if donor is eligible (56 days since last donation)."""
        if not self.last_donation_date:
            return True
        return (date.today() - self.last_donation_date).days >= 56

    @property
    def next_eligible_date(self):
        """Return next eligible donation date."""
        if not self.last_donation_date:
            return date.today()
        return self.last_donation_date + timedelta(days=56)

    @property
    def age(self):
        """Calculate age from date_of_birth."""
        if not self.date_of_birth:
            return None
        today = date.today()
        return today.year - self.date_of_birth.year - (
            (today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day)
        )


class BloodRequest(models.Model):
    """Blood request submitted by a user or hospital."""
    requester = models.ForeignKey(User, on_delete=models.CASCADE, related_name='blood_requests')
    patient_name = models.CharField(max_length=200)
    blood_group_needed = models.CharField(max_length=5, choices=BLOOD_GROUP_CHOICES)
    units_needed = models.IntegerField(default=1)
    hospital_name = models.CharField(max_length=300)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100, blank=True)
    contact_number = models.CharField(max_length=15)
    urgency = models.CharField(max_length=20, choices=URGENCY_CHOICES, default='routine')
    status = models.CharField(max_length=20, choices=REQUEST_STATUS_CHOICES, default='open')
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.blood_group_needed} - {self.hospital_name} ({self.urgency})"


class Donation(models.Model):
    """Record of a blood donation."""
    donor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='donations')
    blood_request = models.ForeignKey(BloodRequest, on_delete=models.SET_NULL, null=True, blank=True, related_name='donations')
    donation_date = models.DateField(default=date.today)
    units = models.IntegerField(default=1)
    blood_group = models.CharField(max_length=5, choices=BLOOD_GROUP_CHOICES)
    hospital_name = models.CharField(max_length=300, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-donation_date']

    def __str__(self):
        return f"{self.donor.get_full_name()} donated {self.units} unit(s) on {self.donation_date}"


class Notification(models.Model):
    """User notifications."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(max_length=200)
    message = models.TextField()
    notification_type = models.CharField(max_length=50, default='info')  # info, success, warning, emergency
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} → {self.user.username}"


class BloodInventory(models.Model):
    """Blood bank inventory tracking."""
    blood_group = models.CharField(max_length=5, choices=BLOOD_GROUP_CHOICES, unique=True)
    units_available = models.IntegerField(default=0)
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Blood Inventory"
        ordering = ['blood_group']

    def __str__(self):
        return f"{self.blood_group}: {self.units_available} units"


class ContactMessage(models.Model):
    """Contact form messages."""
    name = models.CharField(max_length=200)
    email = models.EmailField()
    subject = models.CharField(max_length=300)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} - {self.subject}"
