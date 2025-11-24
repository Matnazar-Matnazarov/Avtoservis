from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.shortcuts import get_object_or_404, redirect, render

from ..forms import MasterForm
from ..models import Master


@login_required
def master_list(request):
    masters = Master.objects.all().order_by("full_name")
    return render(request, "masters/master_list.html", {"masters": masters})


@login_required
def master_create(request):
    if request.method == "POST":
        form = MasterForm(request.POST)
        if form.is_valid():
            master = form.save()
            messages.success(request, "Usta muvaffaqiyatli qo'shildi.")
            return redirect("apps:master_list")
    else:
        form = MasterForm()
    return render(
        request,
        "masters/master_form.html",
        {"form": form, "master": None},
    )


@login_required
def master_update(request, pk: int):
    master = get_object_or_404(Master, pk=pk)
    if request.method == "POST":
        form = MasterForm(request.POST, instance=master)
        if form.is_valid():
            form.save()
            messages.success(request, "Usta ma'lumotlari yangilandi.")
            return redirect("apps:master_list")
    else:
        form = MasterForm(instance=master)
    return render(
        request,
        "masters/master_form.html",
        {"form": form, "master": master},
    )


@login_required
def master_workload(request):
    """
    Har bir usta bo'yicha buyurtmalar soni.
    """
    masters = Master.objects.annotate(total_orders=Count("orders")).all()
    return render(
        request,
        "masters/master_workload.html",
        {"masters": masters},
    )


