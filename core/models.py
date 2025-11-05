from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models.signals import post_save
from django.dispatch import receiver

# Create your models here.

class User(AbstractUser):
    """
    Custom User model inheriting from AbstractUser.
    Adds a 'role' to differentiate between user types.
    """
    class Role(models.TextChoices):
        DONOR = "DONOR", "Donor"
        RECEIVER = "RECEIVER", "Receiver"
        ADMIN = "ADMIN", "Admin"

    role = models.CharField(max_length=50, choices=Role.choices, default=Role.DONOR)

    def __str__(self):
        return self.username

class DonorProfile(models.Model):
    """
    Profile for a 'DONOR' user.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True, related_name='donor_profile')
    
    # --- FIX: Added null=True, blank=True to make fields optional ---
    first_name = models.CharField(max_length=100, blank=True, null=True)
    last_name = models.CharField(max_length=100, blank=True, null=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        # Handle cases where new fields might be None
        return f"{self.first_name or ''} {self.last_name or ''} (Donor)"

class ReceiverProfile(models.Model):
    """
    Profile for a 'RECEIVER' (NGO) user.
    Includes verification status.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True, related_name='receiver_profile')
    ngo_name = models.CharField(max_length=255)
    registration_number = models.CharField(max_length=100, unique=True, help_text="Official NGO registration number")
    
    # --- FIX: Added null=True, blank=True to make field optional ---
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    
    is_verified = models.BooleanField(default=False, help_text="Verified by admin (FR1)")

    def __str__(self):
        return f"{self.ngo_name} (Receiver)"

# --- Signal to auto-create profile when a User is created ---
# This ensures that when a User is made, their profile is created instantly.

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        if instance.role == User.Role.DONOR:
            DonorProfile.objects.create(user=instance)
        elif instance.role == User.Role.RECEIVER:
            ReceiverProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    try:
        if instance.role == User.Role.DONOR:
            instance.donor_profile.save()
        elif instance.role == User.Role.RECEIVER:
            instance.receiver_profile.save()
    except (DonorProfile.DoesNotExist, ReceiverProfile.DoesNotExist):
        # This can happen during initial creation if profile hasn't been made yet
        # The create_user_profile signal will handle it.
        pass


# --- Other Models (Donation, Review, etc.) ---

class Donation(models.Model):
    """
    Represents a donation post created by a Donor.
    (FR4, FR15, FR16)
    """
    class Status(models.TextChoices):
        AVAILABLE = "AVAILABLE", "Available"
        RESERVED = "RESERVED", "Reserved"
        COLLECTED = "COLLECTED", "Collected"
        EXPIRED = "EXPIRED", "Expired"

    donor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='donations')
    title = models.CharField(max_length=255)
    description = models.TextField()
    category = models.CharField(max_length=100) # e.g., "Food", "Clothing", "Electronics"
    quantity = models.PositiveIntegerField(default=1)
    
    # Image for the donation (FR16)
    image = models.ImageField(upload_to='donation_images/', blank=True, null=True)
    
    # Location/Pickup (FR17)
    pickup_location = models.CharField(max_length=255)
    pickup_instructions = models.TextField(blank=True, null=True)

    status = models.CharField(max_length=50, choices=Status.choices, default=Status.AVAILABLE)
    created_at = models.DateTimeField(auto_now_add=True)
    expiry_date = models.DateTimeField(blank=True, null=True, help_text="e.g., for perishable goods")

    def __str__(self):
        return f"{self.title} (by {self.donor.username})"

class DonationRequest(models.Model):
    """
    Links a Receiver to a Donation they have requested.
    (FR6)
    """
    class Status(models.TextChoices):
        PENDING = "PENDING", "Pending"
        ACCEPTED = "ACCEPTED", "Accepted"
        REJECTED = "REJECTJED", "Rejected"
        COLLECTED = "COLLECTED", "Collected"

    donation = models.ForeignKey(Donation, on_delete=models.CASCADE, related_name='requests')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='requests_made')
    status = models.CharField(max_length=50, choices=Status.choices, default=Status.PENDING)
    requested_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # A receiver can only request a specific donation once
        unique_together = ('donation', 'receiver')

    def __str__(self):
        return f"Request for '{self.donation.title}' by '{self.receiver.username}'"


class Review(models.Model):
    """
    Review and rating system.
    (FR9)
    """
    # --- FIX: Added null=True, blank=True to all new non-nullable fields ---
    donation = models.ForeignKey(Donation, on_delete=models.CASCADE, related_name='reviews', blank=True, null=True)
    reviewer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews_given', blank=True, null=True)
    rating = models.PositiveIntegerField(blank=True, null=True) # e.g., 1 to 5
    
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Review for '{self.donation.title}' by {self.reviewer.username}"

class Report(models.Model):
    """
    A report filed by a user against a donation post or another user.
    (FR10)
    """
    class ReportType(models.TextChoices):
        SPAM = "SPAM", "Spam"
        INAPPROPRIATE = "INAPPROPRIATE", "Inappropriate"
        SCAM = "SCAM", "Scam"
        OTHER = "OTHER", "Other"

    # The user who filed the report
    reporter = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='reports_filed')
    
    # The donation being reported (optional)
    donation = models.ForeignKey(Donation, on_delete=models.CASCADE, blank=True, null=True, related_name='reports')
    
    # The user being reported (optional)
    user_reported = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True, related_name='reports_received')

    # --- FIX: Added null=True, blank=True to make field optional ---
    report_type = models.CharField(max_length=50, choices=ReportType.choices, blank=True, null=True)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Report {self.report_type or 'N/A'} by {self.reporter.username if self.reporter else 'Unknown'}"

