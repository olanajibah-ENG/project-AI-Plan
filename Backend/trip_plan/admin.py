from django.contrib import admin
from django.utils.html import format_html
from .models.auth_model import User
from .models.travel_model import Destination, Hotel, ImageAsset

# 1. إعداد إدارة الصور كـ "Inline" لتظهر داخل الوجهة أو الفندق مباشرة
class ImageAssetInline(admin.TabularInline):
    model = ImageAsset
    extra = 1
    readonly_fields = ('preview',)

    def preview(self, obj):
        if obj.file:
            return format_html('<img src="{}" style="width: 100px; height: auto;" />', obj.file.url)
        return "لا توجد صورة"

# 2. تخصيص لوحة تحكم الوجهات (Destinations)
@admin.register(Destination)
class DestinationAdmin(admin.ModelAdmin):
    list_display = ('name', 'country', 'flight_cost', 'daily_living_cost', 'is_coastal', 'image_count')
    list_filter = ('is_coastal', 'country')
    search_fields = ('name', 'country')
    inlines = [ImageAssetInline] # عرض الصور وإضافتها من نفس الصفحة

    def image_count(self, obj):
        return obj.dest_images.count()
    image_count.short_description = "عدد الصور المرفوعة"

# 3. تخصيص لوحة تحكم الفنادق (Hotels)
@admin.register(Hotel)
class HotelAdmin(admin.ModelAdmin):
    list_display = ('name', 'destination', 'stars', 'price_per_night', 'is_sea_view', 'thumbnail')
    list_filter = ('stars', 'is_sea_view', 'destination')
    search_fields = ('name',)
    inlines = [ImageAssetInline]

    def thumbnail(self, obj):
        # عرض أول صورة للفندق في القائمة الرئيسية
        first_image = obj.hotel_images.first()
        if first_image:
            return format_html('<img src="{}" style="width: 50px; border-radius: 5px;" />', first_image.file.url)
        return "N/A"
    thumbnail.short_description = "صورة"

# 4. تخصيص لوحة تحكم المستخدمين (Users)
@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'role', 'is_staff')
    list_filter = ('role', 'is_staff')
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email')}),
        ('Permissions', {'fields': ('role', 'is_active', 'is_staff', 'is_superuser')}),
    )

# 5. تسجيل جدول الصور بشكل منفصل (اختياري للتحكم الدقيق)
@admin.register(ImageAsset)
class ImageAssetAdmin(admin.ModelAdmin):
    list_display = ('id', 'destination', 'hotel', 'preview')
    
    def preview(self, obj):
        if obj.file:
            return format_html('<img src="{}" style="width: 150px;" />', obj.file.url)
        return "لا توجد صورة"
    preview.short_description = "معاينة"