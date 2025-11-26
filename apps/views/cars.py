from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from ..forms import CarForm
from ..models import Car


@login_required
def car_list(request):
    """Mashinalar ro'yxati: raqam, brand/model, mijoz bo'yicha qidiruv."""
    qs = Car.objects.select_related("customer").all().order_by("plate_number")
    q = request.GET.get("q")
    if q:
        qs = qs.filter(
            Q(plate_number__icontains=q)
            | Q(brand__icontains=q)
            | Q(model__icontains=q)
            | Q(customer__full_name__icontains=q)
            | Q(customer__phone__icontains=q)
        )
    context = {"cars": qs, "q": q or ""}
    return render(request, "cars/car_list.jinja", context)


@login_required
def car_create(request):
    if request.method == "POST":
        form = CarForm(request.POST)
        if form.is_valid():
            car = form.save()
            messages.success(request, "Mashina muvaffaqiyatli yaratildi.")
            return redirect("apps:car_history", pk=car.pk)
    else:
        initial = {}
        customer_id = request.GET.get("customer")
        if customer_id:
            initial["customer"] = customer_id
        form = CarForm(initial=initial)
    return render(
        request,
        "cars/car_form.jinja",
        {"form": form, "car": None},
    )


@login_required
def car_update(request, pk: int):
    car = get_object_or_404(Car, pk=pk)
    if request.method == "POST":
        form = CarForm(request.POST, instance=car)
        if form.is_valid():
            form.save()
            messages.success(request, "Mashina ma'lumotlari yangilandi.")
            return redirect("apps:car_history", pk=car.pk)
    else:
        form = CarForm(instance=car)
    return render(
        request,
        "cars/car_form.jinja",
        {"form": form, "car": car},
    )


@login_required
def car_history(request, pk: int):
    car = get_object_or_404(Car, pk=pk)
    orders = car.orders.select_related("customer", "master").all()
    return render(
        request,
        "cars/car_history.jinja",
        {"car": car, "orders": orders},
    )


