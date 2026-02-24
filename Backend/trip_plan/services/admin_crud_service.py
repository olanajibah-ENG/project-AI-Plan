from django.db import transaction
from ..models.travel_model import Destination, Hotel, ImageAsset, Event
from django.shortcuts import get_object_or_404

class AdminCRUDService:

    # -----------------------
    # إدارة الوجهات (Destinations)
    # -----------------------
    @staticmethod
    @transaction.atomic
    def create_destination(data, images=None):
        """إنشاء وجهة مع صورها في عملية واحدة"""
        destination = Destination.objects.create(**data)
        if images:
            for img in images:
                ImageAsset.objects.create(destination=destination, file=img)
        return destination

    @staticmethod
    @transaction.atomic
    def update_destination(dest_id, data, new_images=None):
        """تعديل وجهة مع إضافة صور جديدة"""
        destination = Destination.objects.filter(id=dest_id)
        if not destination.exists():
            raise Exception("الوجهة غير موجودة")
        
        destination.update(**data)
        instance = destination.first()
        
        if new_images:
            for img in new_images:
                ImageAsset.objects.create(destination=instance, file=img)
        return instance

    @staticmethod
    def delete_destination(dest_id):
        """حذف الوجهة (سيتم حذف الفنادق والصور المرتبطة تلقائياً بسبب CASCADE)"""
        return Destination.objects.filter(id=dest_id).delete()

    # -----------------------
    # إدارة الفنادق (Hotels)
    # -----------------------
    @staticmethod
    @transaction.atomic
    def create_hotel(data, images=None):
        """إنشاء فندق مرتبط بوجهة محددة مع صوره"""
        hotel = Hotel.objects.create(**data)
        if images:
            for img in images:
                ImageAsset.objects.create(hotel=hotel, file=img)
        return hotel

    @staticmethod
    def update_hotel(hotel_id, data, new_images=None):
        hotel = Hotel.objects.filter(id=hotel_id)
        if not hotel.exists():
            raise Exception("الفندق غير موجود")
        
        hotel.update(**data)
        instance = hotel.first()
        
        if new_images:
            for img in new_images:
                ImageAsset.objects.create(hotel=instance, file=img)
        return instance

    @staticmethod
    def delete_hotel(hotel_id):
        return Hotel.objects.filter(id=hotel_id).delete()

    # -----------------------
    # إدارة الصور (Images)
    # -----------------------
    @staticmethod
    def delete_image(image_id):
        """حذف صورة محددة فقط (RE-FR-16)"""
        return ImageAsset.objects.filter(id=image_id).delete()

    # -----------------------
    # إدارة الفعاليات (Events)
    # -----------------------
    @staticmethod
    @transaction.atomic
    def create_event(data, images=None):
        event = Event.objects.create(**data)
        if images:
            for img in images:
                ImageAsset.objects.create(event=event, file=img)
        return event

    @staticmethod
    @transaction.atomic
    def update_event(event_id, data, new_images=None):
        event = Event.objects.filter(id=event_id)
        if not event.exists():
            raise Exception("الفعالية غير موجودة")

        event.update(**data)
        instance = event.first()

        if new_images:
            for img in new_images:
                ImageAsset.objects.create(event=instance, file=img)
        return instance

    @staticmethod
    def delete_event(event_id):
        return Event.objects.filter(id=event_id).delete()