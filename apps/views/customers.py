from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from ..forms import CustomerForm
from ..models import Customer


@login_required
def customer_list(request):
    """Mijozlar ro'yxati va qidiruv (ism, telefon, telegram)."""
    qs = Customer.objects.all().order_by("full_name")
    q = request.GET.get("q")
    if q:
        qs = qs.filter(
            Q(full_name__icontains=q)
            | Q(phone__icontains=q)
            | Q(telegram_username__icontains=q)
        )
    context = {"customers": qs, "q": q or ""}
    return render(request, "customers/customer_list.jinja", context)


@login_required
def customer_create(request):
    if request.method == "POST":
        form = CustomerForm(request.POST)
        if form.is_valid():
            customer = form.save()
            messages.success(request, "Mijoz muvaffaqiyatli yaratildi.")
            return redirect("apps:customer_detail", pk=customer.pk)
    else:
        form = CustomerForm()
    return render(
        request,
        "customers/customer_form.jinja",
        {"form": form, "customer": None},
    )


@login_required
def customer_update(request, pk: int):
    customer = get_object_or_404(Customer, pk=pk)
    if request.method == "POST":
        form = CustomerForm(request.POST, instance=customer)
        if form.is_valid():
            form.save()
            messages.success(request, "Mijoz ma'lumotlari yangilandi.")
            return redirect("apps:customer_detail", pk=customer.pk)
    else:
        form = CustomerForm(instance=customer)
    return render(
        request,
        "customers/customer_form.jinja",
        {"form": form, "customer": customer},
    )


@login_required
def customer_detail(request, pk: int):
    customer = get_object_or_404(Customer, pk=pk)
    orders = customer.orders.select_related("car").all()
    return render(
        request,
        "customers/customer_detail.jinja",
        {"customer": customer, "orders": orders},
    )


