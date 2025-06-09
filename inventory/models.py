from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class Production(models.Model):
    """Model for ice block production records"""
    date = models.DateField(default=timezone.now)
    quantity = models.PositiveIntegerField()
    cost_per_unit = models.DecimalField(max_digits=10, decimal_places=2)
    total_cost = models.DecimalField(max_digits=12, decimal_places=2, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    def save(self, *args, **kwargs):
        # Calculate total cost
        self.total_cost = self.quantity * self.cost_per_unit
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Production on {self.date} - {self.quantity} units"

    class Meta:
        ordering = ['-date']

class Sale(models.Model):
    """Model for ice block sales records"""
    date = models.DateField(default=timezone.now)
    quantity = models.PositiveIntegerField()
    price_per_unit = models.DecimalField(max_digits=10, decimal_places=2)
    total_revenue = models.DecimalField(max_digits=12, decimal_places=2, editable=False)
    customer = models.CharField(max_length=255, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    def save(self, *args, **kwargs):
        # Calculate total revenue
        self.total_revenue = self.quantity * self.price_per_unit
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Sale on {self.date} - {self.quantity} units"

    class Meta:
        ordering = ['-date']

class Expense(models.Model):
    """Model for business expenses"""
    EXPENSE_TYPES = [
        ('utility', 'Utilities'),
        ('maintenance', 'Maintenance'),
        ('salary', 'Salaries'),
        ('rent', 'Rent'),
        ('equipment', 'Equipment'),
        ('raw_material', 'Raw Materials'),
        ('transportation', 'Transportation'),
        ('marketing', 'Marketing'),
        ('other', 'Other'),
    ]

    date = models.DateField(default=timezone.now)
    description = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    expense_type = models.CharField(max_length=20, choices=EXPENSE_TYPES, default='other')
    notes = models.TextField(blank=True)
    receipt = models.ImageField(upload_to='expense_receipts/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"{self.expense_type.capitalize()} - {self.date} - ₹{self.amount}"

    class Meta:
        ordering = ['-date']

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_pic = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    deactivation_reason = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"{self.user.username} Profile"

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()