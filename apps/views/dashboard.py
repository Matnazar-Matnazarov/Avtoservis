from datetime import timedelta
from decimal import Decimal

from django.contrib.auth.decorators import login_required
from django.db.models import Count, Sum, Q, F, DecimalField
from django.db.models.functions import Coalesce, TruncDate
from django.shortcuts import render
from django.utils import timezone

from ..models import (
    Car,
    Customer,
    Master,
    Order,
    OrderPart,
    OrderPayment,
    OrderService,
    OrderStatus,
    PaymentStatus,
)


@login_required
def dashboard(request):
    """
    Statistika sahifasi:
    - Asosiy KPI'lar (buyurtmalar soni, daromad, qoldiqlar, mijozlar)
    - Statuslar bo'yicha taqsimot
    - Oxirgi 14 kunlik daromad dinamikasi
    - Top xizmatlar, top detallar, top ustalar
    """
    now = timezone.localtime()
    today = now.date()
    start_of_month = today.replace(day=1)
    last_30_start = today - timedelta(days=29)
    last_14_start = today - timedelta(days=13)

    orders_qs = Order.objects.all()
    money_field = DecimalField(max_digits=14, decimal_places=2)

    total_orders = orders_qs.count()
    active_orders = orders_qs.exclude(status=OrderStatus.COMPLETED).count()
    completed_orders = orders_qs.filter(status=OrderStatus.COMPLETED).count()

    today_orders_qs = orders_qs.filter(created_at__date=today)
    today_orders = today_orders_qs.count()
    today_revenue = today_orders_qs.aggregate(
        total=Coalesce(Sum("total_amount"), Decimal("0"), output_field=money_field)
    )["total"]

    month_orders_qs = orders_qs.filter(created_at__date__gte=start_of_month)
    month_revenue = month_orders_qs.aggregate(
        total=Coalesce(Sum("total_amount"), Decimal("0"), output_field=money_field)
    )["total"]

    all_time_revenue = orders_qs.aggregate(
        total=Coalesce(Sum("total_amount"), Decimal("0"), output_field=money_field)
    )["total"]
    all_time_paid = OrderPayment.objects.aggregate(
        total=Coalesce(Sum("amount"), Decimal("0"), output_field=money_field)
    )["total"]
    outstanding = max(all_time_revenue - all_time_paid, Decimal("0"))

    unpaid_orders = orders_qs.filter(
        payment_status__in=[PaymentStatus.UNPAID, PaymentStatus.PARTIAL]
    ).count()

    customers_count = Customer.objects.count()
    cars_count = Car.objects.count()
    masters_count = Master.objects.count()

    # Status taqsimoti
    status_labels = {
        OrderStatus.NEW: "Yangi",
        OrderStatus.IN_PROGRESS: "Jarayonda",
        OrderStatus.CHECKING: "Tekshirilmoqda",
        OrderStatus.COMPLETED: "Yakunlangan",
    }
    status_counts_raw = dict(
        orders_qs.values_list("status").annotate(count=Count("id"))
    )
    status_stats = [
        {
            "code": code,
            "label": label,
            "count": status_counts_raw.get(code, 0),
        }
        for code, label in status_labels.items()
    ]
    max_status = max((s["count"] for s in status_stats), default=0) or 1
    for s in status_stats:
        s["percent"] = round((s["count"] / max_status) * 100)

    # Oxirgi 14 kunlik daromad dinamikasi
    daily_qs = (
        orders_qs.filter(created_at__date__gte=last_14_start)
        .annotate(d=TruncDate("created_at"))
        .values("d")
        .annotate(
            revenue=Coalesce(Sum("total_amount"), Decimal("0"), output_field=money_field),
            orders=Count("id"),
        )
        .order_by("d")
    )
    daily_map = {row["d"]: row for row in daily_qs}
    daily_labels = []
    daily_revenue = []
    daily_orders = []
    for i in range(14):
        d = last_14_start + timedelta(days=i)
        row = daily_map.get(d)
        daily_labels.append(d.strftime("%d.%m"))
        daily_revenue.append(float(row["revenue"]) if row else 0)
        daily_orders.append(row["orders"] if row else 0)
    max_daily_revenue = max(daily_revenue) if daily_revenue else 0

    # Oxirgi 30 kun ichidagi top xizmatlar
    top_services = (
        OrderService.objects.filter(order__created_at__date__gte=last_30_start)
        .values("service__name")
        .annotate(
            qty=Coalesce(Sum("quantity"), 0),
            revenue=Coalesce(
                Sum(F("price") * F("quantity"), output_field=money_field),
                Decimal("0"),
                output_field=money_field,
            ),
        )
        .order_by("-revenue")[:5]
    )

    # Top ehtiyot qismlar
    top_parts = (
        OrderPart.objects.filter(order__created_at__date__gte=last_30_start)
        .values("part__name", "part__article")
        .annotate(
            qty=Coalesce(Sum("quantity"), 0),
            revenue=Coalesce(
                Sum(F("price") * F("quantity"), output_field=money_field),
                Decimal("0"),
                output_field=money_field,
            ),
        )
        .order_by("-revenue")[:5]
    )

    # Top ustalar (30 kun)
    top_masters = (
        Master.objects.filter(orders__created_at__date__gte=last_30_start)
        .annotate(
            orders_count=Count("orders"),
            revenue=Coalesce(
                Sum("orders__total_amount"), Decimal("0"), output_field=money_field
            ),
        )
        .order_by("-revenue")[:5]
    )

    recent_orders = (
        orders_qs.select_related("customer", "car")
        .order_by("-created_at")[:6]
    )

    context = {
        "kpi": {
            "total_orders": total_orders,
            "active_orders": active_orders,
            "completed_orders": completed_orders,
            "today_orders": today_orders,
            "today_revenue": today_revenue,
            "month_revenue": month_revenue,
            "all_time_revenue": all_time_revenue,
            "outstanding": outstanding,
            "unpaid_orders": unpaid_orders,
            "customers_count": customers_count,
            "cars_count": cars_count,
            "masters_count": masters_count,
        },
        "status_stats": status_stats,
        "daily_labels": daily_labels,
        "daily_revenue": daily_revenue,
        "daily_orders": daily_orders,
        "max_daily_revenue": max_daily_revenue,
        "top_services": top_services,
        "top_parts": top_parts,
        "top_masters": top_masters,
        "recent_orders": recent_orders,
    }
    return render(request, "dashboard/dashboard.jinja", context)
