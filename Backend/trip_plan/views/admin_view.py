from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from ..models.travel_model import Destination, Hotel, ImageAsset, Event
from ..serializers.travel_serializer import DestinationSerializer, HotelSerializer, ImageSerializer, EventSerializer
from ..services.admin_crud_service import AdminCRUDService

# 1. تعريف صلاحية مخصصة للتحقق من أن المستخدم هو Admin نصياً
class IsAdminUserRole(permissions.BasePermission):
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and 
            getattr(request.user, 'role', 'user') == 'admin'
        )

# 2. واجهة التحكم بالوجهات (CRUD)
class AdminDestinationViewSet(viewsets.ModelViewSet):
    queryset = Destination.objects.all()
    serializer_class = DestinationSerializer
    permission_classes = [IsAdminUserRole]

    def create(self, request, *args, **kwargs):
        """تخصيص الإضافة لاستخدام الخدمة ومعالجة الصور"""
        images = request.FILES.getlist('images') if hasattr(request.FILES, 'getlist') else []
        data = request.data.copy() if hasattr(request.data, 'copy') else dict(request.data)
        
        # استدعاء الخدمة لإنشاء الوجهة مع صورها (Atomic Transaction)
        dest = AdminCRUDService.create_destination(data, images)
        
        serializer = self.get_serializer(dest)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        """تخصيص التعديل لدعم إضافة صور جديدة"""
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        images = request.FILES.getlist('images') if hasattr(request.FILES, 'getlist') else []
        data = request.data.copy() if hasattr(request.data, 'copy') else dict(request.data)
        
        updated_instance = AdminCRUDService.update_destination(
            instance.id, data, new_images=images
        )
        
        serializer = self.get_serializer(updated_instance)
        return Response(serializer.data)
    
    def destroy(self, request, *args, **kwargs):
        """تخصيص الحذف لإرجاع رسالة توضيحية"""
        instance = self.get_object()
        destination_name = instance.name
        destination_id = instance.id
        
        # حذف الوجهة
        AdminCRUDService.delete_destination(destination_id)
        
        return Response({
            "message": "تم حذف الوجهة بنجاح",
            "deleted_destination": {
                "id": destination_id,
                "name": destination_name
            }
        }, status=status.HTTP_200_OK)

# 3. واجهة التحكم بالفنادق (CRUD)
class AdminHotelViewSet(viewsets.ModelViewSet):
    queryset = Hotel.objects.all()
    serializer_class = HotelSerializer
    permission_classes = [IsAdminUserRole]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        images = request.FILES.getlist('images') if hasattr(request.FILES, 'getlist') else []
        hotel = AdminCRUDService.create_hotel(serializer.validated_data, images=images)

        out = self.get_serializer(hotel)
        return Response(out.data, status=status.HTTP_201_CREATED)
    
    def destroy(self, request, *args, **kwargs):
        """تخصيص الحذف لإرجاع رسالة توضيحية"""
        instance = self.get_object()
        hotel_name = instance.name
        hotel_id = instance.id
        
        # حذف الفندق
        AdminCRUDService.delete_hotel(hotel_id)
        
        return Response({
            "message": "تم حذف الفندق بنجاح",
            "deleted_hotel": {
                "id": hotel_id,
                "name": hotel_name
            }
        }, status=status.HTTP_200_OK)

# 4. واجهة التحكم بالصور (لعرض الصور بشكل منفصل أو حذف صورة محددة)
class AdminImageViewSet(viewsets.ModelViewSet):
    queryset = ImageAsset.objects.all()
    serializer_class = ImageSerializer
    permission_classes = [IsAdminUserRole]
    # يتيح هذا المسار حذف صورة واحدة فقط عبر ID الخاص بها (RE-FR-16)

# 5. واجهة التحكم بالفعاليات (CRUD)
class AdminEventViewSet(viewsets.ModelViewSet):
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    permission_classes = [IsAdminUserRole]

    def create(self, request, *args, **kwargs):
        images = request.FILES.getlist('images') if hasattr(request.FILES, 'getlist') else []
        data = request.data.copy() if hasattr(request.data, 'copy') else dict(request.data)
        event = AdminCRUDService.create_event(data, images)
        serializer = self.get_serializer(event)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        images = request.FILES.getlist('images') if hasattr(request.FILES, 'getlist') else []
        data = request.data.copy() if hasattr(request.data, 'copy') else dict(request.data)
        updated_instance = AdminCRUDService.update_event(instance.id, data, new_images=images)
        serializer = self.get_serializer(updated_instance)
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        event_id = instance.id
        event_name = instance.name
        AdminCRUDService.delete_event(event_id)
        return Response({
            "message": "تم حذف الفعالية بنجاح",
            "deleted_event": {"id": event_id, "name": event_name}
        }, status=status.HTTP_200_OK)