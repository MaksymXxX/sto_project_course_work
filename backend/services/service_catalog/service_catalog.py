"""Сервіс роботи з каталогом послуг та інформацією про СТО."""

from ...api.data_access import DataAccessLayer


class ServiceCatalog:
    """Каталог послуг згідно з архітектурною діаграмою"""

    @staticmethod
    def get_all_services():
        """Отримання всіх активних послуг"""
        return DataAccessLayer.get_all_services()

    @staticmethod
    def get_service_by_id(service_id):
        """Отримання послуги за ID"""
        return DataAccessLayer.get_service_by_id(service_id)

    @staticmethod
    def create_service(data):
        """Створення нової послуги"""
        try:
            service = DataAccessLayer.create_service(
                name=data['name'],
                description=data['description'],
                price=data['price'],
                duration=data['duration'],
                is_active=data.get('is_active', True)
            )
            return {
                'success': True,
                'service': service
            }
        except Exception as e:  # pylint: disable=broad-exception-caught
            return {
                'success': False,
                'error': str(e)
            }

    @staticmethod
    def update_service(service_id, data):
        """Оновлення послуги"""
        service = DataAccessLayer.get_service_by_id(service_id)
        if service:
            DataAccessLayer.update_service(service, **data)
            return {
                'success': True,
                'service': service
            }
        return {
            'success': False,
            'error': 'Послугу не знайдено'
        }

    @staticmethod
    def delete_service(service_id):
        """Видалення послуги (деактивація)"""
        service = DataAccessLayer.get_service_by_id(service_id)
        if service:
            DataAccessLayer.update_service(service, is_active=False)
            return True
        return False

    @staticmethod
    def get_sto_info():
        """Отримання інформації про СТО"""
        return DataAccessLayer.get_sto_info()

    @staticmethod
    def update_sto_info(data):
        """Оновлення інформації про СТО"""
        try:
            sto_info = DataAccessLayer.get_sto_info()
            if sto_info:
                for key, value in data.items():
                    if key == 'what_you_can_items' and isinstance(value, list):
                        # Фільтруємо порожні елементи
                        filtered_items = [
                            item for item in value if item and item.strip()]
                        setattr(sto_info, key, filtered_items)
                    else:
                        setattr(sto_info, key, value)
                sto_info.save()
                return {
                    'success': True,
                    'sto_info': sto_info
                }
            # Фільтруємо what_you_can_items якщо це список
            if 'what_you_can_items' in data and isinstance(
                    data['what_you_can_items'], list):
                data['what_you_can_items'] = [
                    item for item in data['what_you_can_items']
                    if item and item.strip()
                ]

            sto_info = DataAccessLayer.create_or_update_sto_info(**data)
            return {
                'success': True,
                'sto_info': sto_info
            }
        except Exception as e:  # pylint: disable=broad-exception-caught
            return {
                'success': False,
                'error': str(e)
            }

    @staticmethod
    def get_services_statistics():
        """Отримання статистики по послугах"""
        return DataAccessLayer.get_services_statistics()  # pylint: disable=no-member
