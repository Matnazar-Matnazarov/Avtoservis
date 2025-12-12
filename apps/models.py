from typing import Any
from decimal import Decimal
from django.db import models
from django.db.models import Sum
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from django.core.validators import RegexValidator


class Role(models.TextChoices):
    ADMIN = "admin", _("Admin")
    MASTER = "master", _("Master")
    RECEPTION = "reception", _("Reception")
    USER = "user", _("User")


class User(AbstractUser):
    telegram_username = models.CharField(
        _("Telegram username"), max_length=255, null=True, blank=True
    )
    telegram_id = models.BigIntegerField(_("Telegram ID"), null=True, blank=True)
    telegram_chat_id = models.BigIntegerField(
        _("Telegram chat ID"), null=True, blank=True
    )
    telegram_username_validator = RegexValidator(
        regex=r"^[a-zA-Z0-9_]{5,32}$",
        message=_(
            "Telegram username can only contain letters, numbers and underscores"
        ),
    )
    role = models.CharField(
        _("Role"), max_length=32, choices=Role.choices, default=Role.USER
    )
    phone = models.CharField(
        _("Phone number"),
        max_length=20,
        blank=True,
        help_text=_("Contact phone number"),
    )

    class Meta:
        verbose_name = _("User")
        verbose_name_plural = _("Users")

    def __str__(self):
        return self.get_full_name() or self.username


class Customer(models.Model):
    full_name = models.CharField(_("Full name"), max_length=255)
    phone = models.CharField(
        _("Phone"),
        max_length=20,
        db_index=True,
    )
    telegram_username = models.CharField(
        _("Telegram username"), max_length=255, null=True, blank=True
    )

    class Meta:
        verbose_name = _("Customer")
        verbose_name_plural = _("Customers")

    def __str__(self) -> str:
        return f"{self.full_name} ({self.phone})"


class Car(models.Model):
    customer = models.ForeignKey(
        Customer, on_delete=models.CASCADE, related_name="cars"
    )
    brand = models.CharField(_("Brand"), max_length=100)
    model = models.CharField(_("Model"), max_length=100, blank=True)
    plate_number = models.CharField(
        _("Plate number"),
        max_length=20,
        db_index=True,
    )
    vin = models.CharField(_("VIN"), max_length=64, blank=True)

    class Meta:
        verbose_name = _("Car")
        verbose_name_plural = _("Cars")

    def __str__(self) -> str:
        return f"{self.plate_number} - {self.brand} {self.model}".strip()


class Master(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.SET_NULL,
        related_name="master_profile",
        null=True,
        blank=True,
    )
    full_name = models.CharField(_("Full name"), max_length=255)
    phone = models.CharField(_("Phone"), max_length=20, blank=True)
    specialization = models.CharField(
        _("Specialization"), max_length=100, blank=True
    )

    class Meta:
        verbose_name = _("Master")
        verbose_name_plural = _("Masters")

    def __str__(self) -> str:
        return self.full_name


class Service(models.Model):
    name = models.CharField(_("Service name"), max_length=255)
    base_price = models.DecimalField(
        _("Base price"), max_digits=12, decimal_places=2
    )

    class Meta:
        verbose_name = _("Service")
        verbose_name_plural = _("Services")

    def __str__(self) -> str:
        return self.name


class Part(models.Model):
    name = models.CharField(_("Part name"), max_length=255)
    article = models.CharField(
        _("Article"), max_length=100, unique=True, db_index=True
    )
    price = models.DecimalField(_("Price"), max_digits=12, decimal_places=2)
    stock_quantity = models.PositiveIntegerField(_("Stock quantity"), default=0)

    class Meta:
        verbose_name = _("Part")
        verbose_name_plural = _("Parts")

    def __str__(self) -> str:
        return f"{self.name} ({self.article})"


class OrderStatus(models.TextChoices):
    NEW = "new", _("New")
    IN_PROGRESS = "in_progress", _("Jarayonda")
    CHECKING = "checking", _("Tekshirilmoqda")
    COMPLETED = "completed", _("Yakunlangan")


class ServiceStatus(models.TextChoices):
    IN_PROGRESS = "in_progress", _("Jarayonda")
    CHECKING = "checking", _("Tekshirilmoqda")
    DONE = "done", _("Bajarildi")


class PaymentStatus(models.TextChoices):
    UNPAID = "unpaid", _("To'lanmadi")
    PARTIAL = "partial", _("Qisman to'landi")
    PAID = "paid", _("To'landi")


class PaymentType(models.TextChoices):
    CASH = "cash", _("Naqd")
    CARD = "card", _("Karta")
    TRANSFER = "transfer", _("Perevod")


class Order(models.Model):
    customer = models.ForeignKey(
        Customer, on_delete=models.CASCADE, related_name="orders"
    )
    car = models.ForeignKey(
        Car, on_delete=models.CASCADE, related_name="orders"
    )
    master = models.ForeignKey(
        Master,
        on_delete=models.SET_NULL,
        related_name="orders",
        null=True,
        blank=True,
    )
    description = models.TextField(_("Problem description"), blank=True)
    status = models.CharField(
        _("Status"),
        max_length=32,
        choices=OrderStatus.choices,
        default=OrderStatus.NEW,
        db_index=True,
    )
    payment_status = models.CharField(
        _("Payment status"),
        max_length=32,
        choices=PaymentStatus.choices,
        default=PaymentStatus.UNPAID,
    )
    payment_type = models.CharField(
        _("Payment type"),
        max_length=32,
        choices=PaymentType.choices,
        blank=True,
    )
    total_amount = models.DecimalField(
        _("Total amount"),
        max_digits=14,
        decimal_places=2,
        default=0,
    )
    created_at = models.DateTimeField(_("Created at"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Updated at"), auto_now=True)

    class Meta:
        verbose_name = _("Order")
        verbose_name_plural = _("Orders")
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"Order #{self.id} - {self.car}"

    @property
    def services_total(self):
        return sum(item.line_total for item in self.service_items.all())

    @property
    def parts_total(self):
        return sum(item.line_total for item in self.part_items.all())

    def recalculate_total(self, save: bool = True):
        self.total_amount = self.services_total + self.parts_total
        if save:
            self.save(update_fields=["total_amount"])
        return self.total_amount

    @property
    def paid_total(self):
        return (
            self.payments.aggregate(total=Sum("amount"))["total"]
            or Decimal("0")
        )

    @property
    def remaining_amount(self):
        return self.total_amount - self.paid_total

    def update_payment_state(self, save: bool = True):
        paid = self.paid_total
        total = self.total_amount
        # To'lov miqdorini umumiy summa bilan solishtirish
        status_changed = False
        if paid <= Decimal("0"):
            self.payment_status = PaymentStatus.UNPAID
        elif abs(paid - total) < Decimal("0.01"):  # Kichik farqni e'tiborsiz qoldirish
            self.payment_status = PaymentStatus.PAID
            # To'liq to'langanida avtomatik yakunlangan deb belgilash
            if self.status != OrderStatus.COMPLETED:
                self.status = OrderStatus.COMPLETED
                status_changed = True
        elif paid < total:
            self.payment_status = PaymentStatus.PARTIAL
        else:
            # To'langan summa katta bo'lsa ham PAID deb belgilash
            self.payment_status = PaymentStatus.PAID
            if self.status != OrderStatus.COMPLETED:
                self.status = OrderStatus.COMPLETED
                status_changed = True
        
        # Agar order "completed" bo'lsa, barcha xizmatlarni ham "done" qilish
        if self.status == OrderStatus.COMPLETED:
            self.service_items.filter(status__in=[ServiceStatus.IN_PROGRESS, ServiceStatus.CHECKING]).update(
                status=ServiceStatus.DONE
            )
        
        if save:
            self.save(update_fields=["payment_status", "status"])
        return paid


class OrderService(models.Model):
    order = models.ForeignKey(
        Order, on_delete=models.CASCADE, related_name="service_items"
    )
    service = models.ForeignKey(Service, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(
        _("Price"), max_digits=12, decimal_places=2
    )
    discount = models.DecimalField(
        _("Discount"), max_digits=5, decimal_places=2, null=True, blank=True, default=Decimal('0')
    )
    status = models.CharField(
        _("Status"),
        max_length=32,
        choices=ServiceStatus.choices,
        default=ServiceStatus.IN_PROGRESS,
    )

    class Meta:
        verbose_name = _("Order service")
        verbose_name_plural = _("Order services")
    def __str__(self) -> str:
        return f"{self.service} x{self.quantity}"

    @property
    def line_total(self):
        # Xizmatlar uchun quantity yo'q, faqat price va discount
        total = self.price
        if self.discount:
            total = total * (1 - self.discount / 100)
        return total


class OrderPart(models.Model):
    order = models.ForeignKey(
        Order, on_delete=models.CASCADE, related_name="part_items"
    )
    part = models.ForeignKey(Part, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(
        _("Price"), max_digits=12, decimal_places=2
    )
    discount = models.DecimalField(
        _("Discount"), max_digits=5, decimal_places=2, null=True, blank=True, default=Decimal('0')
    )

    class Meta:
        verbose_name = _("Order part")
        verbose_name_plural = _("Order parts")

    def __str__(self) -> str:
        return f"{self.part} x{self.quantity}"

    @property
    def line_total(self):
        total = self.price * self.quantity
        if self.discount:
            total = total * (1 - self.discount / 100)
        return total

    def save(self, *args, **kwargs):
        # Skladni oddiy tarzda boshqarish:
        # yangi yozuvda quantity miqdoriga kamaytirish,
        # mavjud yozuv tahrirlanganda farqni hisoblash mumkin.
        if self.pk:
            old = OrderPart.objects.get(pk=self.pk)
            diff = self.quantity - old.quantity
        else:
            diff = self.quantity

        result = super().save(*args, **kwargs)

        if diff:
            self.part.stock_quantity = models.F("stock_quantity") - diff
            self.part.save(update_fields=["stock_quantity"])
        return result


class OrderPhoto(models.Model):
    order = models.ForeignKey(
        Order, on_delete=models.CASCADE, related_name="photos"
    )
    image = models.ImageField(upload_to="orders/photos/")
    is_before = models.BooleanField(
        _("Is 'before' photo"), default=True
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _("Order photo")
        verbose_name_plural = _("Order photos")

    def __str__(self) -> str:
        label = _("Before") if self.is_before else _("After")
        return f"{label} photo for order #{self.order_id}"


class OrderPayment(models.Model):
    order = models.ForeignKey(
        Order, on_delete=models.CASCADE, related_name="payments"
    )
    amount = models.DecimalField(
        _("Amount"), max_digits=14, decimal_places=2
    )
    payment_type = models.CharField(
        _("Payment type"),
        max_length=32,
        choices=PaymentType.choices,
    )
    paid_at = models.DateTimeField(_("Paid at"), auto_now_add=True)
    note = models.CharField(_("Note"), max_length=255, blank=True)

    class Meta:
        verbose_name = _("Order payment")
        verbose_name_plural = _("Order payments")
        ordering = ["paid_at"]

    def __str__(self) -> str:
        return f"{self.order_id} - {self.amount}"

    def save(self, *args, **kwargs):
        result = super().save(*args, **kwargs)
        # To'lovdan keyin buyurtma holatini yangilab qo'yamiz
        self.order.update_payment_state(save=True)
        return result

    def delete(self, *args, **kwargs):
        order = self.order
        result = super().delete(*args, **kwargs)
        order.update_payment_state(save=True)
        return result
