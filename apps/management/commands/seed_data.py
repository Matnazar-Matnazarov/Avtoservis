import random
from decimal import Decimal
from django.core.management.base import BaseCommand
from faker import Faker

from apps.models import (
    Customer,
    Car,
    Part,
    Service,
    Master,
)


class Command(BaseCommand):
    help = "Seeds auto-service system with realistic demo data (customers, cars, parts, services)"

    def handle(self, *args, **kwargs):
        fake = Faker("uz_UZ")

        self.stdout.write(self.style.WARNING("Seeding started..."))

        # ============================
        # 1) CUSTOMERS
        # ============================
        customers = []
        for _ in range(20):
            c = Customer.objects.create(
                full_name=fake.name(),
                phone=f"+9989{random.randint(10, 99)}{random.randint(100000, 999999)}",
                telegram_username=fake.user_name(),
            )
            customers.append(c)

        self.stdout.write(self.style.SUCCESS("✓ Customers created: 20"))

        # ============================
        # 2) CARS
        # ============================
        car_data = {
            "Chevrolet": ["Cobalt", "Gentra", "Malibu", "Onix", "Tracker"],
            "Toyota": ["Camry", "Corolla", "RAV4", "Prado"],
            "Kia": ["K5", "Sportage", "Rio"],
            "Hyundai": ["Elantra", "Sonata", "Tucson"],
            "Mercedes": ["C200", "E200", "GLA"],
        }

        cars = []
        for customer in customers:
            brand = random.choice(list(car_data.keys()))
            model = random.choice(car_data[brand])

            car = Car.objects.create(
                customer=customer,
                brand=brand,
                model=model,
                plate_number=f"{random.randint(10, 99)}X{random.randint(100,999)}AA",
                vin=fake.pystr(min_chars=17, max_chars=17).upper(),
            )
            cars.append(car)

        self.stdout.write(self.style.SUCCESS(f"✓ Cars created: {len(cars)}"))

        # ============================
        # 3) MASTERS
        # ============================
        masters = []
        specs = ["Dvigatel", "Elektrik", "Xodovoy", "Kuzov", "Diagnostika"]

        for i in range(10):
            m = Master.objects.create(
                full_name=fake.name(),
                phone=f"+9989{random.randint(10, 99)}{random.randint(100000, 999999)}",
                specialization=random.choice(specs),
            )
            masters.append(m)

        self.stdout.write(self.style.SUCCESS(f"✓ Masters created: {len(masters)}"))

        # ============================
        # 4) PARTS
        # ============================
        parts_data = [
            ("Motor moyi Liqui Moly 5W30", "ML5W30", 180000),
            ("Yog‘ filtri MANN", "YN001", 45000),
            ("Vozdux filtri", "VF221", 60000),
            ("Tormoz kolodkalari", "TK900", 250000),
            ("Antifriz G12", "AFG12", 35000),
            ("Konditsioner freoni R134a", "FR134", 85000),
            ("Generator remni", "GR777", 90000),
            ("Svetodiod far lampasi", "LED12", 110000),
            ("Kuzov kraskasi", "KR500", 70000),
            ("Yuqori bosimli nasos", "YBN444", 850000),
        ]

        parts = []
        for name, article, price in parts_data:
            part = Part.objects.create(
                name=name,
                article=article,
                price=Decimal(price),
                stock_quantity=random.randint(5, 50),
            )
            parts.append(part)

        self.stdout.write(self.style.SUCCESS(f"✓ Parts created: {len(parts)}"))

        # ============================
        # 5) SERVICES
        # ============================
        service_data = [
            ("Dvigatel moyini almashtirish", 45000),
            ("Yog‘ filtrini almashtirish", 25000),
            ("Diagnostika", 40000),
            ("Kuzov yuvish", 20000),
            ("Tormoz kolodkalarini almashtirish", 60000),
            ("Antifriz almashtirish", 50000),
            ("Shinalarni almashtirish (4 dona)", 80000),
            ("Xodovoy tekshiruvi", 30000),
            ("Konditsioner freon to‘ldirish", 75000),
            ("Kompyuter diagnostikasi", 50000),
        ]

        services = []
        for name, price in service_data:
            service = Service.objects.create(
                name=name,
                base_price=Decimal(price)
            )
            services.append(service)

        self.stdout.write(self.style.SUCCESS(f"✓ Services created: {len(services)}"))

        # ============================
        # DONE
        # ============================

        self.stdout.write(self.style.SUCCESS("\n=== SEED COMPLETED SUCCESSFULLY ==="))
