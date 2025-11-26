from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from ..forms import ServiceForm, PartForm
from ..models import Service, Part


@login_required
def service_list(request):
    services = Service.objects.all().order_by("name")
    return render(request, "services/service_list.jinja", {"services": services})


@login_required
def service_create(request):
    if request.method == "POST":
        form = ServiceForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Xizmat qo'shildi.")
            return redirect("apps:service_list")
    else:
        form = ServiceForm()
    return render(
        request,
        "services/service_form.jinja",
        {"form": form, "service": None},
    )


@login_required
def service_update(request, pk: int):
    service = get_object_or_404(Service, pk=pk)
    if request.method == "POST":
        form = ServiceForm(request.POST, instance=service)
        if form.is_valid():
            form.save()
            messages.success(request, "Xizmat yangilandi.")
            return redirect("apps:service_list")
    else:
        form = ServiceForm(instance=service)
    return render(
        request,
        "services/service_form.jinja",
        {"form": form, "service": service},
    )


@login_required
def part_list(request):
    parts = Part.objects.all().order_by("name")
    return render(request, "services/part_list.jinja", {"parts": parts})


@login_required
def part_create(request):
    if request.method == "POST":
        form = PartForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Ehtiyot qism qo'shildi.")
            return redirect("apps:part_list")
    else:
        form = PartForm()
    return render(
        request,
        "services/part_form.jinja",
        {"form": form, "part": None},
    )


@login_required
def part_update(request, pk: int):
    part = get_object_or_404(Part, pk=pk)
    if request.method == "POST":
        form = PartForm(request.POST, instance=part)
        if form.is_valid():
            form.save()
            messages.success(request, "Ehtiyot qism yangilandi.")
            return redirect("apps:part_list")
    else:
        form = PartForm(instance=part)
    return render(
        request,
        "services/part_form.jinja",
        {"form": form, "part": part},
    )



