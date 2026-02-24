from rest_framework import serializers
from ..models.travel_model import Destination, Hotel, ImageAsset, Event

class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ImageAsset
        fields = ['id', 'file']

class HotelSerializer(serializers.ModelSerializer):
    hotel_images = ImageSerializer(many=True, read_only=True)
    class Meta:
        model = Hotel
        fields = '__all__'

class EventSerializer(serializers.ModelSerializer):
    event_images = ImageSerializer(many=True, read_only=True)
    class Meta:
        model = Event
        fields = '__all__'

class DestinationSerializer(serializers.ModelSerializer):
    dest_images = ImageSerializer(many=True, read_only=True)
    hotels = HotelSerializer(many=True, read_only=True)
    events = EventSerializer(many=True, read_only=True)
    class Meta:
        model = Destination
        fields = '__all__'