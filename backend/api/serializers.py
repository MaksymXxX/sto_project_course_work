from rest_framework import serializers
from django.contrib.auth.models import User
from .models import ServiceCategory, Service, Customer, Appointment, ServiceHistory, LoyaltyTransaction, STOInfo, Box


class BoxSerializer(serializers.ModelSerializer):
    working_hours = serializers.DictField(
        child=serializers.DictField(
            child=serializers.CharField(max_length=5)
        ),
        required=False,
        default=dict
    )

    class Meta:
        model = Box
        fields = ['id', 'name', 'name_en', 'description', 'description_en', 'is_active', 'working_hours', 'created_at', 'updated_at']

    def to_representation(self, instance):
        """Перетворює модель в JSON для відповіді"""
        data = super().to_representation(instance)
        
        # Отримуємо мову з контексту
        language = self.context.get('language', 'uk')
        
        # Встановлюємо назву та опис за мовою
        translated_name = instance.get_name(language)
        data['name'] = translated_name
        data['description'] = instance.get_description(language)
        
        # Переконуємося, що working_hours є словником
        if isinstance(data['working_hours'], str):
            try:
                import json
                data['working_hours'] = json.loads(data['working_hours'])
            except (json.JSONDecodeError, TypeError):
                data['working_hours'] = {}
        return data


class ServiceCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceCategory
        fields = ['id', 'name', 'name_en', 'description', 'description_en', 'order']

    def to_representation(self, instance):
        """Перетворює модель в JSON для відповіді"""
        data = super().to_representation(instance)
        
        # Отримуємо мову з контексту
        language = self.context.get('language', 'uk')
        
        # Для адмін панелі завжди повертаємо оригінальні поля
        if self.context.get('admin_panel', False):
            # Залишаємо оригінальні поля name_en та description_en
            data['name'] = instance.name
            data['description'] = instance.description
        else:
            # Для звичайного використання повертаємо перекладені версії
            data['name'] = instance.get_name(language)
            data['description'] = instance.get_description(language)
        
        return data


class ServiceSerializer(serializers.ModelSerializer):
    category = ServiceCategorySerializer(read_only=True)
    category_id = serializers.IntegerField(write_only=True)
    
    class Meta:
        model = Service
        fields = ['id', 'category', 'category_id', 'name', 'name_en', 'description', 'description_en', 'price', 'duration_minutes', 'is_active', 'is_featured', 'created_at']

    def to_representation(self, instance):
        """Перетворює модель в JSON для відповіді"""
        data = super().to_representation(instance)
        
        # Отримуємо мову з контексту
        language = self.context.get('language', 'uk')
        
        # Для адмін панелі завжди повертаємо оригінальні поля для редагування
        if self.context.get('admin_panel', False):
            # Залишаємо оригінальні поля name_en та description_en
            data['name'] = instance.name
            data['name_en'] = instance.name_en
            data['description'] = instance.description
            data['description_en'] = instance.description_en
        else:
            # Для звичайного використання повертаємо перекладені версії
            data['name'] = instance.get_name(language)
            data['description'] = instance.get_description(language)
        
        # Якщо є категорія, також оновлюємо її дані
        if instance.category:
            data['category'] = ServiceCategorySerializer(
                instance.category, 
                context={'language': language, 'admin_panel': self.context.get('admin_panel', False)}
            ).data
        
        return data


class ServiceListSerializer(serializers.ModelSerializer):
    """Серіалізатор для списку послуг в адмін панелі з перекладеними назвами"""
    category = ServiceCategorySerializer(read_only=True)
    
    class Meta:
        model = Service
        fields = ['id', 'category', 'name', 'description', 'price', 'duration_minutes', 'is_active', 'is_featured', 'created_at']

    def to_representation(self, instance):
        """Перетворює модель в JSON для відповіді з перекладеними назвами"""
        data = super().to_representation(instance)
        
        # Отримуємо мову з контексту
        language = self.context.get('language', 'uk')
        
        # Завжди повертаємо перекладені версії для відображення в таблиці
        data['name'] = instance.get_name(language)
        data['description'] = instance.get_description(language)
        
        # Якщо є категорія, також оновлюємо її дані
        if instance.category:
            data['category'] = ServiceCategorySerializer(
                instance.category, 
                context={'language': language}
            ).data
        
        return data


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']
        read_only_fields = ['id']


class CustomerSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = Customer
        fields = ['id', 'user', 'address', 'avatar', 'loyalty_points', 'is_blocked', 'created_at']
        read_only_fields = ['id', 'loyalty_points', 'created_at']


class AppointmentSerializer(serializers.ModelSerializer):
    service = ServiceSerializer(read_only=True)
    service_id = serializers.IntegerField(write_only=True)
    box = BoxSerializer(read_only=True)
    box_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)
    customer = CustomerSerializer(read_only=True)
    customer_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Appointment
        fields = [
            'id', 'customer', 'guest_name', 'guest_phone', 'guest_email',
            'service', 'service_id', 'box', 'box_id', 'appointment_date', 'appointment_time',
            'status', 'notes', 'total_price', 'created_at', 'updated_at', 'customer_name'
        ]
        read_only_fields = ['id', 'total_price', 'created_at', 'updated_at', 'customer_name']
    
    def get_customer_name(self, obj):
        if obj.customer:
            return obj.customer.user.get_full_name()
        return obj.guest_name
    
    def to_representation(self, instance):
        """Перетворює модель в JSON для відповіді з урахуванням мови"""
        try:
            data = super().to_representation(instance)
            
            # Отримуємо мову з контексту
            language = self.context.get('language', 'uk')
            
            # Якщо є сервіс, оновлюємо його дані за мовою
            if instance.service:
                data['service'] = ServiceSerializer(
                    instance.service, 
                    context={'language': language}
                ).data
            
            # Якщо є бокс, оновлюємо його дані за мовою
            if instance.box:
                data['box'] = BoxSerializer(
                    instance.box, 
                    context={'language': language}
                ).data
            
            return data
        except Exception as e:
            import traceback
            print(f"Error in AppointmentSerializer.to_representation: {str(e)}")
            print(f"Traceback: {traceback.format_exc()}")
            # Fallback to basic representation
            return super().to_representation(instance)


class ServiceHistorySerializer(serializers.ModelSerializer):
    appointment = AppointmentSerializer(read_only=True)
    
    class Meta:
        model = ServiceHistory
        fields = ['id', 'appointment', 'completed_at', 'mechanic_notes', 'actual_duration', 'final_price']


class LoyaltyTransactionSerializer(serializers.ModelSerializer):
    customer = CustomerSerializer(read_only=True)
    
    class Meta:
        model = LoyaltyTransaction
        fields = ['id', 'customer', 'transaction_type', 'points', 'description', 'created_at']
        read_only_fields = ['id', 'created_at']


class STOInfoSerializer(serializers.ModelSerializer):
    what_you_can_items = serializers.ListField(
        child=serializers.CharField(max_length=300),
        required=False,
        default=list
    )

    class Meta:
        model = STOInfo
        fields = [
            'id', 'name', 'name_en', 'description', 'description_en', 
            'motto', 'motto_en', 'welcome_text', 'welcome_text_en', 
            'what_you_can_title', 'what_you_can_title_en', 
            'what_you_can_items', 'what_you_can_items_en',
            'address', 'address_en', 'phone', 'phone_en', 
            'email', 'email_en', 'working_hours', 'working_hours_en', 
            'is_active'
        ]

    def to_representation(self, instance):
        """Перетворює модель в JSON для відповіді"""
        data = super().to_representation(instance)
        
        # Отримуємо мову з контексту
        language = self.context.get('language', 'uk')
        
        # Встановлюємо всі поля за мовою
        data['name'] = instance.get_name(language)
        data['description'] = instance.get_description(language)
        data['motto'] = instance.get_motto(language)
        data['welcome_text'] = instance.get_welcome_text(language)
        data['what_you_can_title'] = instance.get_what_you_can_title(language)
        data['what_you_can_items'] = instance.get_what_you_can_items_list(language)
        
        # Адреса, телефон, email за мовою (з фолбеком)
        data['address'] = (
            instance.address_en if language == 'en' and getattr(instance, 'address_en', None) else instance.address
        )
        data['phone'] = (
            instance.phone_en if language == 'en' and getattr(instance, 'phone_en', None) else instance.phone
        )
        data['email'] = (
            instance.email_en if language == 'en' and getattr(instance, 'email_en', None) else instance.email
        )
        
        # Робочі години: повертаємо тиждень/вихідні окремо якщо можливо
        working_hours_raw = (
            instance.working_hours_en if language == 'en' and getattr(instance, 'working_hours_en', None) else instance.working_hours
        )
        if isinstance(working_hours_raw, str) and ',' in working_hours_raw:
            parts = [p.strip() for p in working_hours_raw.split(',', 1)]
            data['working_hours'] = parts[0]
            data['working_hours_weekend'] = parts[1] if len(parts) > 1 else ''
        else:
            data['working_hours'] = working_hours_raw
            # Якщо немає другої частини, не додаємо weekend або ставимо порожнє значення
            data['working_hours_weekend'] = ''
        
        # Переконуємося, що what_you_can_items є списком
        if isinstance(data['what_you_can_items'], str):
            try:
                import json
                data['what_you_can_items'] = json.loads(data['what_you_can_items'])
            except (json.JSONDecodeError, TypeError):
                data['what_you_can_items'] = []
        
        return data


class GuestAppointmentSerializer(serializers.ModelSerializer):
    service = ServiceSerializer(read_only=True)
    service_id = serializers.IntegerField(write_only=True)
    box = BoxSerializer(read_only=True)
    box_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)
    
    class Meta:
        model = Appointment
        fields = [
            'id', 'guest_name', 'guest_phone', 'guest_email',
            'service', 'service_id', 'box', 'box_id', 'appointment_date', 'appointment_time',
            'notes', 'total_price', 'created_at'
        ]
        read_only_fields = ['id', 'total_price', 'created_at']


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'first_name', 'last_name']
    
    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        Customer.objects.create(user=user)
        return user


class UserLoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField() 