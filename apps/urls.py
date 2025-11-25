from django.urls import path

from .views.orders import (
    order_list,
    order_detail,
    order_create,
    order_update,
    order_receipt,
    daily_report_csv,
    monthly_report_csv,
    api_service_price,
    api_part_price,
)
from .views.customers import (
    customer_list,
    customer_create,
    customer_update,
    customer_detail,
)
from .views.cars import car_list, car_create, car_update, car_history
from .views.masters import master_list, master_create, master_update, master_workload
from .views.services import (
    service_list,
    service_create,
    service_update,
    part_list,
    part_create,
    part_update,
)

app_name = "apps"

urlpatterns = [
    path("", order_list, name="order_list"),
    path("order/<int:pk>/", order_detail, name="order_detail"),
    path("order/new/", order_create, name="order_create"),
    path("order/<int:pk>/edit/", order_update, name="order_update"),
    path("order/<int:pk>/receipt/", order_receipt, name="order_receipt"),
    path("customers/", customer_list, name="customer_list"),
    path("customer/new/", customer_create, name="customer_create"),
    path("customer/<int:pk>/edit/", customer_update, name="customer_update"),
    path("customer/<int:pk>/", customer_detail, name="customer_detail"),
    path("cars/", car_list, name="car_list"),
    path("car/new/", car_create, name="car_create"),
    path("car/<int:pk>/edit/", car_update, name="car_update"),
    path("car/<int:pk>/history/", car_history, name="car_history"),
    path("masters/", master_list, name="master_list"),
    path("masters/new/", master_create, name="master_create"),
    path("masters/<int:pk>/edit/", master_update, name="master_update"),
    path("masters/workload/", master_workload, name="master_workload"),
    path("services/", service_list, name="service_list"),
    path("services/new/", service_create, name="service_create"),
    path("services/<int:pk>/edit/", service_update, name="service_update"),
    path("parts/", part_list, name="part_list"),
    path("parts/new/", part_create, name="part_create"),
    path("parts/<int:pk>/edit/", part_update, name="part_update"),
    path("reports/daily.csv", daily_report_csv, name="daily_report_csv"),
    path("reports/monthly.csv", monthly_report_csv, name="monthly_report_csv"),
    path("api/service/<int:service_id>/price/", api_service_price, name="api_service_price"),
    path("api/part/<int:part_id>/price/", api_part_price, name="api_part_price"),
]