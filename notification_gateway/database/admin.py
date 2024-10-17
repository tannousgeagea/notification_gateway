
from django import forms
from django.contrib import admin
from unfold.admin import ModelAdmin
from .models import Tenant, NotificationTemplate, NotificationRequest, EmailSettings

class EmailSettingsAdminForm(forms.ModelForm):
    class Meta:
        model = EmailSettings
        fields = '__all__'
        widgets = {
            'password': forms.PasswordInput(render_value=True),
        }

@admin.register(Tenant)
class TenantAdmin(ModelAdmin):
    list_display = ('tenant_id', 'tenant_name', 'location', 'domain', 'logo', 'is_active', 'created_at')
    search_fields = ('tenant_name', 'tenant_id', 'location')
    list_filter = ('is_active', 'created_at')
    readonly_fields = ('created_at',)


@admin.register(NotificationTemplate)
class NotificationTemplateAdmin(ModelAdmin):
    list_display = ('subject', 'template_type', 'created_at', 'updated_at')
    search_fields = ('subject', 'template_type')
    list_filter = ('template_type', 'created_at')
    readonly_fields = ('created_at', 'updated_at')

@admin.register(NotificationRequest)
class NotificationRequestAdmin(ModelAdmin):
    list_display = ('request_id', 'request_name', 'tenant', 'notification_template', 'request_status', 'created_at', 'sent_at')
    search_fields = ('request_name', 'request_id')
    list_filter = ('request_status', 'created_at')
    readonly_fields = ('created_at', 'sent_at')

@admin.register(EmailSettings)
class EmailSettingsAdmin(ModelAdmin):
    form = EmailSettingsAdminForm
    list_display = ('host', 'port', 'username', 'use_tls', 'use_ssl')
    search_fields = ('host', 'username')
