from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import ServiceCategory, Service, Customer, Appointment, ServiceHistory, LoyaltyTransaction, STOInfo, Box


@admin.register(ServiceCategory)
class ServiceCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'name_en', 'order', 'created_at']
    list_filter = ['created_at']
    search_fields = ['name', 'name_en', 'description', 'description_en']
    ordering = ['order', 'name']
    fieldsets = (
        ('Українська версія', {
            'fields': ('name', 'description', 'order')
        }),
        ('Англійська версія', {
            'fields': ('name_en', 'description_en')
        }),
    )


@admin.register(Box)
class BoxAdmin(admin.ModelAdmin):
    list_display = ['name', 'name_en', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'name_en', 'description', 'description_en']
    ordering = ['name']
    fieldsets = (
        ('Основна інформація', {
            'fields': ('is_active', 'working_hours')
        }),
        ('Українська версія', {
            'fields': ('name', 'description')
        }),
        ('Англійська версія', {
            'fields': ('name_en', 'description_en')
        }),
    )


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ['name', 'name_en', 'category', 'price', 'duration_minutes', 'is_active', 'created_at']
    list_filter = ['category', 'is_active', 'created_at']
    search_fields = ['name', 'name_en', 'description', 'description_en']
    ordering = ['category__order', 'category__name', 'name']
    fieldsets = (
        ('Основна інформація', {
            'fields': ('category', 'price', 'duration_minutes', 'is_active')
        }),
        ('Українська версія', {
            'fields': ('name', 'description')
        }),
        ('Англійська версія', {
            'fields': ('name_en', 'description_en')
        }),
    )


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ['user', 'loyalty_points', 'is_blocked', 'created_at']
    list_filter = ['is_blocked', 'created_at']
    search_fields = ['user__username', 'user__email', 'user__first_name', 'user__last_name']
    ordering = ['user__username']


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ['get_customer_name', 'service', 'appointment_date', 'appointment_time', 'status', 'total_price']
    list_filter = ['status', 'appointment_date', 'service']
    search_fields = ['guest_name', 'guest_phone', 'guest_email']
    ordering = ['-appointment_date', '-appointment_time']
    
    def get_customer_name(self, obj):
        if obj.customer:
            return obj.customer.user.get_full_name()
        return obj.guest_name
    get_customer_name.short_description = 'Клієнт'


@admin.register(ServiceHistory)
class ServiceHistoryAdmin(admin.ModelAdmin):
    list_display = ['appointment', 'completed_at', 'actual_duration', 'final_price']
    list_filter = ['completed_at']
    search_fields = ['appointment__guest_name', 'appointment__service__name']
    ordering = ['-completed_at']


@admin.register(LoyaltyTransaction)
class LoyaltyTransactionAdmin(admin.ModelAdmin):
    list_display = ['customer', 'transaction_type', 'points', 'description', 'created_at']
    list_filter = ['transaction_type', 'created_at']
    search_fields = ['customer__user__username', 'description']
    ordering = ['-created_at']


@admin.register(STOInfo)
class STOInfoAdmin(admin.ModelAdmin):
    list_display = ['name', 'name_en', 'phone', 'email', 'is_active']
    list_filter = ['is_active']
    search_fields = ['name', 'name_en', 'description', 'description_en', 'motto', 'motto_en']
    fieldsets = (
        ('Основна інформація (Українська)', {
            'fields': ('name', 'description', 'motto', 'welcome_text', 'what_you_can_title', 'what_you_can_items')
        }),
        ('Основна інформація (Англійська)', {
            'fields': ('name_en', 'description_en', 'motto_en', 'welcome_text_en', 'what_you_can_title_en', 'what_you_can_items_en')
        }),
        ('Контактна інформація (Українська)', {
            'fields': ('address', 'phone', 'email', 'working_hours')
        }),
        ('Контактна інформація (Англійська)', {
            'fields': ('address_en', 'phone_en', 'email_en', 'working_hours_en')
        }),
        ('Статус', {
            'fields': ('is_active',)
        }),
    ) 