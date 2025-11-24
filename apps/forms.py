from django import forms
from django.forms import inlineformset_factory

from .models import (
    Customer,
    Car,
    Order,
    OrderService,
    OrderPart,
    OrderPhoto,
    OrderPayment,
    Master,
    Service,
    Part,
)


TAILWIND_INPUT = (
    "w-full rounded-lg border border-slate-700 bg-slate-900/80 px-3 py-2 "
    "text-sm text-slate-100 placeholder-slate-500 focus:outline-none "
    "focus:ring-2 focus:ring-emerald-500/60 focus:border-emerald-500"
)


class TailwindModelForm(forms.ModelForm):
    """
    Barcha ModelFormlar uchun umumiy Tailwind klasslarini qo'llash.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            css = TAILWIND_INPUT
            existing = field.widget.attrs.get("class", "")
            field.widget.attrs["class"] = (existing + " " + css).strip()


class CustomerForm(TailwindModelForm):
    class Meta:
        model = Customer
        fields = ["full_name", "phone", "telegram_username"]
        widgets = {
            "full_name": forms.TextInput(attrs={"autocomplete": "off"}),
            "phone": forms.TextInput(attrs={"autocomplete": "off"}),
            "telegram_username": forms.TextInput(
                attrs={"autocomplete": "off"}
            ),
        }


class CarForm(TailwindModelForm):
    class Meta:
        model = Car
        fields = ["customer", "brand", "model", "plate_number", "vin"]


class OrderForm(TailwindModelForm):
    class Meta:
        model = Order
        fields = [
            "customer",
            "car",
            "master",
            "description",
            "status",
            "payment_status",
            "payment_type",
        ]


class OrderServiceForm(TailwindModelForm):
    class Meta:
        model = OrderService
        fields = ["service", "status", "quantity", "price"]


class OrderPartForm(TailwindModelForm):
    class Meta:
        model = OrderPart
        fields = ["part", "quantity", "price"]


class OrderPhotoForm(TailwindModelForm):
    class Meta:
        model = OrderPhoto
        fields = ["image", "is_before"]


class OrderPaymentForm(TailwindModelForm):
    class Meta:
        model = OrderPayment
        fields = ["amount", "payment_type", "note"]


class MasterForm(TailwindModelForm):
    class Meta:
        model = Master
        fields = ["full_name", "phone", "specialization", "user"]


class ServiceForm(TailwindModelForm):
    class Meta:
        model = Service
        fields = ["name", "base_price"]


class PartForm(TailwindModelForm):
    class Meta:
        model = Part
        fields = ["name", "article", "price", "stock_quantity"]


OrderServiceFormSet = inlineformset_factory(
    Order,
    OrderService,
    form=OrderServiceForm,
    extra=1,
    can_delete=True,
)

OrderPartFormSet = inlineformset_factory(
    Order,
    OrderPart,
    form=OrderPartForm,
    extra=1,
    can_delete=True,
)

OrderPhotoFormSet = inlineformset_factory(
    Order,
    OrderPhoto,
    form=OrderPhotoForm,
    extra=1,
    can_delete=True,
)

OrderPaymentFormSet = inlineformset_factory(
    Order,
    OrderPayment,
    form=OrderPaymentForm,
    extra=1,
    can_delete=True,
)


