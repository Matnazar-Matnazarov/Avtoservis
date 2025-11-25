from datetime import datetime, date
import csv

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Sum
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render

from ..forms import (
    OrderForm,
    OrderServiceFormSet,
    OrderPartFormSet,
    OrderPhotoFormSet,
    OrderPaymentFormSet,
)
from ..models import Order, Service, Part, PaymentStatus


@login_required
def order_list(request):
    """
    Buyurtmalar ro'yxati:
    - Telefon, mashina raqami, sana va status bo'yicha qidiruv/filtr
    - Har bir buyurtma uchun rangli status
    """

    orders = Order.objects.select_related("customer", "car", "master")

    phone = request.GET.get("phone")
    plate = request.GET.get("plate")
    status = request.GET.get("status")
    date_from = request.GET.get("date_from")
    date_to = request.GET.get("date_to")
    query = request.GET.get("q")

    if phone:
        orders = orders.filter(customer__phone__icontains=phone)

    if plate:
        orders = orders.filter(car__plate_number__icontains=plate)

    if status:
        orders = orders.filter(status=status)

    if date_from:
        try:
            df = datetime.strptime(date_from, "%Y-%m-%d").date()
            orders = orders.filter(created_at__date__gte=df)
        except ValueError:
            pass

    if date_to:
        try:
            dt = datetime.strptime(date_to, "%Y-%m-%d").date()
            orders = orders.filter(created_at__date__lte=dt)
        except ValueError:
            pass

    if query:
        orders = orders.filter(
            Q(customer__phone__icontains=query)
            | Q(car__plate_number__icontains=query)
            | Q(customer__full_name__icontains=query)
        )

    context = {
        "orders": orders,
        "filter": {
            "phone": phone or "",
            "plate": plate or "",
            "status": status or "",
            "date_from": date_from or "",
            "date_to": date_to or "",
            "q": query or "",
        },
    }
    return render(request, "orders/order_list.html", context)


@login_required
def order_detail(request, pk: int):
    """
    Buyurtma ichidagi batafsil sahifa:
    - Xizmatlar ro'yxati + narxi + status
    - Zapchastlar ro'yxati + narxi
    - Umumiy summa avtomatik hisoblanadi
    - Oldin/Keyin fotolar
    """
    order = get_object_or_404(
        Order.objects.select_related("customer", "car", "master").prefetch_related(
            "service_items__service",
            "part_items__part",
            "photos",
            "payments",
        ),
        pk=pk,
    )

    # Umumiy summani qayta hisoblash
    order.recalculate_total(save=True)

    services = order.service_items.all()
    parts = order.part_items.all()
    photos_before = order.photos.filter(is_before=True)
    photos_after = order.photos.filter(is_before=False)

    context = {
        "order": order,
        "services": services,
        "parts": parts,
        "photos_before": photos_before,
        "photos_after": photos_after,
        "payments": order.payments.all(),
    }
    return render(request, "orders/order_detail.html", context)


@login_required
def order_create(request):
    if request.method == "POST":
        form = OrderForm(request.POST)
        service_formset = OrderServiceFormSet(request.POST, prefix="services")
        part_formset = OrderPartFormSet(request.POST, prefix="parts")
        photo_formset = OrderPhotoFormSet(
            request.POST, request.FILES, prefix="photos"
        )
        payment_formset = OrderPaymentFormSet(
            request.POST, prefix="payments"
        )
        
        # Bo'sh formlarni o'tkazib yuborish - faqat to'ldirilgan formlarni validate qilish
        # Service formset uchun bo'sh formlarni o'tkazib yuborish
        for service_form in service_formset.forms:
            if service_form in service_formset.deleted_forms:
                continue
            service_value = service_form.data.get(service_form.add_prefix('service'), '')
            if not service_value or service_value == '':
                # Bo'sh form - required fieldlarni o'chirish
                for field_name in service_form.fields:
                    service_form.fields[field_name].required = False
        
        # Part formset uchun bo'sh formlarni o'tkazib yuborish
        for part_form in part_formset.forms:
            if part_form in part_formset.deleted_forms:
                continue
            part_value = part_form.data.get(part_form.add_prefix('part'), '')
            if not part_value or part_value == '':
                # Bo'sh form - required fieldlarni o'chirish
                for field_name in part_form.fields:
                    part_form.fields[field_name].required = False
        
        # Validation tekshiruvi
        form_valid = form.is_valid()
        service_formset_valid = service_formset.is_valid()
        part_formset_valid = part_formset.is_valid()
        photo_formset_valid = photo_formset.is_valid()
        payment_formset_valid = payment_formset.is_valid()
        
        if (
            form_valid
            and service_formset_valid
            and part_formset_valid
            and photo_formset_valid
            and payment_formset_valid
        ):
            order = form.save()
            service_formset.instance = order
            part_formset.instance = order
            photo_formset.instance = order
            payment_formset.instance = order
            
            # Faqat to'ldirilgan formlarni saqlash
            service_formset.save(commit=False)
            for service_form in service_formset.forms:
                if service_form in service_formset.deleted_forms:
                    if service_form.instance.pk:
                        service_form.instance.delete()
                elif service_form.cleaned_data.get('service'):
                    service_form.save()
            
            part_formset.save(commit=False)
            for part_form in part_formset.forms:
                if part_form in part_formset.deleted_forms:
                    if part_form.instance.pk:
                        part_form.instance.delete()
                elif part_form.cleaned_data.get('part'):
                    part_form.save()
            
            photo_formset.save()
            payment_formset.save()
            order.recalculate_total(save=True)
            order.update_payment_state(save=True)
            messages.success(request, f"Buyurtma #{order.id} yaratildi.")
            return redirect("apps:order_detail", pk=order.pk)
        else:
            # Validation xatolarini ko'rsatish
            if not form_valid:
                for field, errors in form.errors.items():
                    for error in errors:
                        messages.error(request, f"{form.fields[field].label if field in form.fields else field}: {error}")
            
            if not service_formset_valid:
                for idx, service_form in enumerate(service_formset.forms):
                    if service_form.errors:
                        for field, errors in service_form.errors.items():
                            for error in errors:
                                field_label = service_form.fields[field].label if field in service_form.fields else field
                                messages.error(request, f"Xizmat #{idx + 1} - {field_label}: {error}")
                    if service_form.non_field_errors():
                        for error in service_form.non_field_errors():
                            messages.error(request, f"Xizmat #{idx + 1}: {error}")
            
            if not part_formset_valid:
                for idx, part_form in enumerate(part_formset.forms):
                    if part_form.errors:
                        for field, errors in part_form.errors.items():
                            for error in errors:
                                field_label = part_form.fields[field].label if field in part_form.fields else field
                                messages.error(request, f"Ehtiyot qism #{idx + 1} - {field_label}: {error}")
                    if part_form.non_field_errors():
                        for error in part_form.non_field_errors():
                            messages.error(request, f"Ehtiyot qism #{idx + 1}: {error}")
            
            if not photo_formset_valid:
                for idx, photo_form in enumerate(photo_formset.forms):
                    if photo_form.errors:
                        for field, errors in photo_form.errors.items():
                            for error in errors:
                                field_label = photo_form.fields[field].label if field in photo_form.fields else field
                                messages.error(request, f"Foto #{idx + 1} - {field_label}: {error}")
            
            if not payment_formset_valid:
                for idx, payment_form in enumerate(payment_formset.forms):
                    if payment_form.errors:
                        for field, errors in payment_form.errors.items():
                            for error in errors:
                                field_label = payment_form.fields[field].label if field in payment_form.fields else field
                                messages.error(request, f"To'lov #{idx + 1} - {field_label}: {error}")
    else:
        initial = {}
        customer_id = request.GET.get("customer")
        car_id = request.GET.get("car")
        if customer_id:
            initial["customer"] = customer_id
        if car_id:
            initial["car"] = car_id
        form = OrderForm(initial=initial)
        service_formset = OrderServiceFormSet(prefix="services")
        part_formset = OrderPartFormSet(prefix="parts")
        photo_formset = OrderPhotoFormSet(prefix="photos")
        payment_formset = OrderPaymentFormSet(prefix="payments")

    context = {
        "form": form,
        "service_formset": service_formset,
        "part_formset": part_formset,
        "photo_formset": photo_formset,
        "payment_formset": payment_formset,
    }
    return render(request, "orders/order_form.html", context)


@login_required
def order_update(request, pk: int):
    order = get_object_or_404(Order, pk=pk)
    
    # To'langan buyurtmalarni edit qilib bo'lmaydi
    if order.payment_status == PaymentStatus.PAID:
        messages.error(request, f"To'langan buyurtma #{order.id} ni tahrirlab bo'lmaydi.")
        return redirect("apps:order_detail", pk=order.pk)
    
    if request.method == "POST":
        form = OrderForm(request.POST, instance=order)
        service_formset = OrderServiceFormSet(
            request.POST, instance=order, prefix="services"
        )
        part_formset = OrderPartFormSet(
            request.POST, instance=order, prefix="parts"
        )
        photo_formset = OrderPhotoFormSet(
            request.POST, request.FILES, instance=order, prefix="photos"
        )
        payment_formset = OrderPaymentFormSet(
            request.POST, instance=order, prefix="payments"
        )
        
        # Bo'sh formlarni o'tkazib yuborish - faqat to'ldirilgan formlarni validate qilish
        # Service formset uchun bo'sh formlarni o'tkazib yuborish
        for service_form in service_formset.forms:
            if service_form in service_formset.deleted_forms:
                continue
            service_value = service_form.data.get(service_form.add_prefix('service'), '')
            if not service_value or service_value == '':
                # Bo'sh form - required fieldlarni o'chirish
                for field_name in service_form.fields:
                    service_form.fields[field_name].required = False
        
        # Part formset uchun bo'sh formlarni o'tkazib yuborish
        for part_form in part_formset.forms:
            if part_form in part_formset.deleted_forms:
                continue
            part_value = part_form.data.get(part_form.add_prefix('part'), '')
            if not part_value or part_value == '':
                # Bo'sh form - required fieldlarni o'chirish
                for field_name in part_form.fields:
                    part_form.fields[field_name].required = False
        
        # Validation tekshiruvi
        form_valid = form.is_valid()
        service_formset_valid = service_formset.is_valid()
        part_formset_valid = part_formset.is_valid()
        photo_formset_valid = photo_formset.is_valid()
        payment_formset_valid = payment_formset.is_valid()
        
        if (
            form_valid
            and service_formset_valid
            and part_formset_valid
            and photo_formset_valid
            and payment_formset_valid
        ):
            form.save()
            service_formset.save()
            part_formset.save()
            photo_formset.save()
            payment_formset.save()
            order.recalculate_total(save=True)
            order.update_payment_state(save=True)
            messages.success(request, f"Buyurtma #{order.id} yangilandi.")
            return redirect("apps:order_detail", pk=order.pk)
        else:
            # Validation xatolarini ko'rsatish
            if not form_valid:
                for field, errors in form.errors.items():
                    for error in errors:
                        messages.error(request, f"{form.fields[field].label if field in form.fields else field}: {error}")
            
            if not service_formset_valid:
                for idx, service_form in enumerate(service_formset.forms):
                    if service_form.errors:
                        for field, errors in service_form.errors.items():
                            for error in errors:
                                field_label = service_form.fields[field].label if field in service_form.fields else field
                                messages.error(request, f"Xizmat #{idx + 1} - {field_label}: {error}")
                    if service_form.non_field_errors():
                        for error in service_form.non_field_errors():
                            messages.error(request, f"Xizmat #{idx + 1}: {error}")
            
            if not part_formset_valid:
                for idx, part_form in enumerate(part_formset.forms):
                    if part_form.errors:
                        for field, errors in part_form.errors.items():
                            for error in errors:
                                field_label = part_form.fields[field].label if field in part_form.fields else field
                                messages.error(request, f"Ehtiyot qism #{idx + 1} - {field_label}: {error}")
                    if part_form.non_field_errors():
                        for error in part_form.non_field_errors():
                            messages.error(request, f"Ehtiyot qism #{idx + 1}: {error}")
            
            if not photo_formset_valid:
                for idx, photo_form in enumerate(photo_formset.forms):
                    if photo_form.errors:
                        for field, errors in photo_form.errors.items():
                            for error in errors:
                                field_label = photo_form.fields[field].label if field in photo_form.fields else field
                                messages.error(request, f"Foto #{idx + 1} - {field_label}: {error}")
            
            if not payment_formset_valid:
                for idx, payment_form in enumerate(payment_formset.forms):
                    if payment_form.errors:
                        for field, errors in payment_form.errors.items():
                            for error in errors:
                                field_label = payment_form.fields[field].label if field in payment_form.fields else field
                                messages.error(request, f"To'lov #{idx + 1} - {field_label}: {error}")
    else:
        form = OrderForm(instance=order)
        service_formset = OrderServiceFormSet(instance=order, prefix="services")
        part_formset = OrderPartFormSet(instance=order, prefix="parts")
        photo_formset = OrderPhotoFormSet(instance=order, prefix="photos")
        payment_formset = OrderPaymentFormSet(instance=order, prefix="payments")

    context = {
        "order": order,
        "form": form,
        "service_formset": service_formset,
        "part_formset": part_formset,
        "photo_formset": photo_formset,
        "payment_formset": payment_formset,
    }
    return render(request, "orders/order_form.html", context)


@login_required
def order_receipt(request, pk: int):
    order = get_object_or_404(Order, pk=pk)
    order.recalculate_total(save=True)
    services = order.service_items.all()
    parts = order.part_items.all()
    return render(
        request,
        "orders/order_receipt.html",
        {"order": order, "services": services, "parts": parts},
    )


@login_required
def daily_report_csv(request):
    """
    Kunlik hisobotni CSV ko'rinishida chiqarish (Excel uchun).
    """
    day_str = request.GET.get("date")
    if day_str:
        try:
            day = datetime.strptime(day_str, "%Y-%m-%d").date()
        except ValueError:
            day = date.today()
    else:
        day = date.today()

    orders = Order.objects.filter(created_at__date=day).select_related(
        "customer", "car"
    )
    total = orders.aggregate(total=Sum("total_amount"))["total"] or 0

    response = HttpResponse(content_type="text/csv")
    response[
        "Content-Disposition"
    ] = f'attachment; filename="daily_report_{day.isoformat()}.csv"'

    writer = csv.writer(response)
    writer.writerow(
        ["ID", "Sana", "Mijoz", "Telefon", "Mashina", "Status", "Umumiy summa"]
    )
    for o in orders:
        writer.writerow(
            [
                o.id,
                o.created_at.strftime("%Y-%m-%d %H:%M"),
                o.customer.full_name,
                o.customer.phone,
                f"{o.car.plate_number} {o.car.brand} {o.car.model}",
                o.get_status_display(),
                float(o.total_amount),
            ]
        )
    writer.writerow([])
    writer.writerow(["Jami", "", "", "", "", "", float(total)])
    return response


@login_required
def monthly_report_csv(request):
    """
    Oylik hisobotni CSV ko'rinishida chiqarish (Excel uchun).
    """
    year = int(request.GET.get("year", date.today().year))
    month = int(request.GET.get("month", date.today().month))

    orders = Order.objects.filter(
        created_at__year=year, created_at__month=month
    ).select_related("customer", "car")
    total = orders.aggregate(total=Sum("total_amount"))["total"] or 0

    response = HttpResponse(content_type="text/csv")
    response[
        "Content-Disposition"
    ] = f'attachment; filename="monthly_report_{year}_{month}.csv"'

    writer = csv.writer(response)
    writer.writerow(
        ["ID", "Sana", "Mijoz", "Telefon", "Mashina", "Status", "Umumiy summa"]
    )
    for o in orders:
        writer.writerow(
            [
                o.id,
                o.created_at.strftime("%Y-%m-%d %H:%M"),
                o.customer.full_name,
                o.customer.phone,
                f"{o.car.plate_number} {o.car.brand} {o.car.model}",
                o.get_status_display(),
                float(o.total_amount),
            ]
        )
    writer.writerow([])
    writer.writerow(["Jami", "", "", "", "", "", float(total)])
    return response


@login_required
def api_service_price(request, service_id: int):
    """API endpoint to get service price by ID"""
    try:
        service = get_object_or_404(Service, pk=service_id)
        return JsonResponse({"price": str(service.base_price)})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)


@login_required
def api_part_price(request, part_id: int):
    """API endpoint to get part price by ID"""
    try:
        part = get_object_or_404(Part, pk=part_id)
        return JsonResponse({"price": str(part.price)})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)

