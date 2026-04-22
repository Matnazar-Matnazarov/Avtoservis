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


TAILWIND_INPUT = "input input-bordered w-full text-sm"
TAILWIND_SELECT = "select select-bordered w-full text-sm"
TAILWIND_TEXTAREA = "textarea textarea-bordered w-full min-h-28 text-sm"
TAILWIND_FILE = "file-input file-input-bordered w-full text-sm"
TAILWIND_CHECKBOX = "checkbox checkbox-sm"


class TailwindModelForm(forms.ModelForm):
    """
    Barcha ModelFormlar uchun umumiy Tailwind klasslarini qo'llash.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            widget = field.widget
            if isinstance(widget, forms.Select):
                css = TAILWIND_SELECT
            elif isinstance(widget, forms.Textarea):
                css = TAILWIND_TEXTAREA
            elif isinstance(widget, forms.ClearableFileInput):
                css = TAILWIND_FILE
            elif isinstance(widget, forms.CheckboxInput):
                css = TAILWIND_CHECKBOX
            else:
                css = TAILWIND_INPUT

            existing = field.widget.attrs.get("class", "")
            field.widget.attrs["class"] = (existing + " " + css).strip()
            if field.widget.attrs.get("readonly"):
                field.widget.attrs["class"] += " input-disabled opacity-70 cursor-not-allowed"


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
        fields = ["service", "status", "price", "discount"]
        widgets = {
            "price": forms.NumberInput(attrs={
                "readonly": True,
                "step": "0.01",
                "class": "w-full rounded-lg border border-slate-700 bg-slate-800/60 px-3 py-2 text-sm text-slate-400 cursor-not-allowed"
            }),
            "discount": forms.NumberInput(attrs={
                "step": "0.01",
                "min": "0",
                "max": "100",
                "placeholder": "0.00",
                "value": "0"
            }),
        }


class OrderPartForm(TailwindModelForm):
    class Meta:
        model = OrderPart
        fields = ["part", "quantity", "price", "discount"]
        widgets = {
            "price": forms.NumberInput(attrs={
                "readonly": True,
                "step": "0.01",
                "class": "w-full rounded-lg border border-slate-700 bg-slate-800/60 px-3 py-2 text-sm text-slate-400 cursor-not-allowed"
            }),
            "discount": forms.NumberInput(attrs={
                "step": "0.01",
                "min": "0",
                "max": "100",
                "placeholder": "0.00",
                "value": "0"
            }),
        }


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


class BaseOrderServiceFormSet(forms.BaseInlineFormSet):
    def clean(self):
        """Bo'sh formlarni o'tkazib yuborish"""
        if any(self.errors):
            return
        # Bo'sh formlarni o'tkazib yuborish
        for form in self.forms:
            if form in self.deleted_forms:
                continue
            # cleaned_data hali mavjud emas, shuning uchun data dan tekshiramiz
            service_value = form.data.get(form.add_prefix('service'), '')
            if not service_value or service_value == '':
                # Bo'sh form - required fieldlarni o'chirish
                for field_name in form.fields:
                    form.fields[field_name].required = False

class BaseOrderPartFormSet(forms.BaseInlineFormSet):
    def clean(self):
        """Bo'sh formlarni o'tkazib yuborish"""
        if any(self.errors):
            return
        # Bo'sh formlarni o'tkazib yuborish
        for form in self.forms:
            if form in self.deleted_forms:
                continue
            # cleaned_data hali mavjud emas, shuning uchun data dan tekshiramiz
            part_value = form.data.get(form.add_prefix('part'), '')
            if not part_value or part_value == '':
                # Bo'sh form - required fieldlarni o'chirish
                for field_name in form.fields:
                    form.fields[field_name].required = False

OrderServiceFormSet = inlineformset_factory(
    Order,
    OrderService,
    form=OrderServiceForm,
    formset=BaseOrderServiceFormSet,
    extra=1,
    can_delete=True,
    validate_min=False,
)

OrderPartFormSet = inlineformset_factory(
    Order,
    OrderPart,
    form=OrderPartForm,
    formset=BaseOrderPartFormSet,
    extra=1,
    can_delete=True,
    validate_min=False,
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


