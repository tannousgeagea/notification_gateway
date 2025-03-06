from django.db import models
import pytz

# Create your models here.
class Tenant(models.Model):
    tenant_id = models.CharField(max_length=255, unique=True)
    tenant_name = models.CharField(max_length=255)
    location = models.CharField(max_length=100)
    domain = models.CharField(max_length=50)
    logo = models.ImageField(upload_to='logos/')
    is_active = models.BooleanField(default=True, help_text="Indicates if the tenant is currently active.")
    created_at = models.DateTimeField(auto_now_add=True)
    meta_info = models.JSONField(null=True, blank=True)
    timezone = models.CharField(
        max_length=50,
        choices=[(tz, tz) for tz in pytz.all_timezones],
        default="Europe/Berlin",
        help_text="Timezone for the tenant"
    )

    class Meta:
        db_table = "wa_tenant"
        verbose_name_plural = "Tenants"
        
    def __str__(self):
        return f"{self.tenant_name}"
    
class Recipient(models.Model):
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name="recipients")
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    is_active = models.BooleanField(default=True, help_text="Indicates if the recipient is currently active.")

    class Meta:
        db_table = 'recipient'
        verbose_name_plural = "Recipients"
        unique_together = ('tenant', 'email')  # Prevent duplicate emails for the same tenant

    def __str__(self):
        return f"{self.name} ({self.email}) - {self.tenant.tenant_name}"

class TenantStorageSettings(models.Model):
    tenant = models.OneToOneField(Tenant, on_delete=models.RESTRICT, related_name='storage_settings')
    provider_name = models.CharField(max_length=100, choices=[('azure', 'Azure'), ('aws', 'AWS'), ('gcp', 'GCP')])
    account_name = models.CharField(max_length=255, help_text="Storage Account Name")
    account_key = models.CharField(max_length=255, blank=True, help_text="Storage Account Key or equivalent")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "tenant_storage_settings"
        verbose_name_plural = "Tenant Storage Settings"

    def __str__(self):
        return f"{self.provider_name} settings for {self.tenant.tenant_name}"

class NotificationTemplate(models.Model):
    subject = models.CharField(max_length=255)
    template_body = models.TextField()
    template_type = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'notification_template'
        verbose_name_plural = "Notification Templates"
        
    def __str__(self):
        return self.subject
    

class NotificationRequest(models.Model):
    
    STATUS_CHOICES = [
        ('pending', 'Pending'), 
        ('sent', 'Sent'), 
        ('failed', 'Failed')
    ]
    
    tenant = models.ForeignKey(Tenant, on_delete=models.RESTRICT)
    notification_template = models.ForeignKey(NotificationTemplate, on_delete=models.RESTRICT)
    request_id = models.CharField(max_length=255, unique=True)
    request_name = models.CharField(max_length=100)
    request_status = models.CharField(max_length=50, choices=STATUS_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    sent_at = models.DateTimeField(null=True, blank=True)
    error_message = models.TextField(null=True, blank=True)  # In case of failure
    
    class Meta:
        db_table = 'notification_request'
        verbose_name_plural = "Notification Requests"

    def __str__(self):
        return f"Notification to {self.tenant.tenant_name} - {self.notification_template.subject}"
    
class EmailSettings(models.Model):
    host = models.CharField(max_length=255)
    port = models.IntegerField()
    username = models.CharField(max_length=255)
    password = models.CharField(max_length=255)  # Store this securely
    use_tls = models.BooleanField(default=True)
    use_ssl = models.BooleanField(default=False)

    def __str__(self):
        return f"Email Settings ({self.host})"
