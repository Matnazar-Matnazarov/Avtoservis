from django.contrib import admin

from .models import (
    Car,
    Customer,
    Master,
    Order,
    OrderPart,
    OrderPhoto,
    OrderService,
    OrderPayment,
    Part,
    Service,
    User,
)


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ("username", "first_name", "last_name", "role", "phone")
    search_fields = ("username", "first_name", "last_name", "phone")


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ("full_name", "phone", "telegram_username")
    search_fields = ("full_name", "phone", "telegram_username")


@admin.register(Car)
class CarAdmin(admin.ModelAdmin):
    list_display = ("plate_number", "brand", "model", "customer")
    search_fields = ("plate_number", "brand", "model", "customer__full_name")
    list_filter = ("brand",)


@admin.register(Master)
class MasterAdmin(admin.ModelAdmin):
    list_display = ("full_name", "phone", "specialization")
    search_fields = ("full_name", "phone", "specialization")


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ("name", "base_price")
    search_fields = ("name",)


@admin.register(Part)
class PartAdmin(admin.ModelAdmin):
    list_display = ("name", "article", "price", "stock_quantity")
    search_fields = ("name", "article")


class OrderServiceInline(admin.TabularInline):
    model = OrderService
    extra = 1


class OrderPartInline(admin.TabularInline):
    model = OrderPart
    extra = 1


class OrderPhotoInline(admin.TabularInline):
    model = OrderPhoto
    extra = 1


class OrderPaymentInline(admin.TabularInline):
    model = OrderPayment
    extra = 1


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "customer",
        "car",
        "master",
        "status",
        "payment_status",
        "total_amount",
        "created_at",
    )
    list_filter = ("status", "payment_status", "payment_type", "created_at")
    search_fields = ("customer__full_name", "customer__phone", "car__plate_number")
    inlines = [OrderServiceInline, OrderPartInline, OrderPhotoInline, OrderPaymentInline]


@admin.register(OrderService)
class OrderServiceAdmin(admin.ModelAdmin):
    list_display = ("order", "service", "status", "quantity", "price")


@admin.register(OrderPart)
class OrderPartAdmin(admin.ModelAdmin):
    list_display = ("order", "part", "quantity", "price")


@admin.register(OrderPhoto)
class OrderPhotoAdmin(admin.ModelAdmin):
    list_display = ("order", "is_before", "uploaded_at")


@admin.register(OrderPayment)
class OrderPaymentAdmin(admin.ModelAdmin):
    list_display = ("order", "amount", "payment_type", "paid_at")
