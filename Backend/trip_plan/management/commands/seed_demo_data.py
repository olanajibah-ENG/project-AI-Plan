from __future__ import annotations

import re
from decimal import Decimal
from pathlib import Path

from django.conf import settings
from django.core.files import File
from django.core.management.base import BaseCommand

from trip_plan.models.auth_model import User
from trip_plan.models.travel_model import Destination, Event, Hotel, ImageAsset


DESTINATION_BLUEPRINTS = [
    {"name": "Abha", "country": "Saudi Arabia", "is_coastal": False, "best_seasons": "summer,spring"},
    {"name": "Jeddah", "country": "Saudi Arabia", "is_coastal": True, "best_seasons": "winter,spring"},
    {"name": "Tabuk", "country": "Saudi Arabia", "is_coastal": False, "best_seasons": "summer,autumn"},
    {"name": "Antalya", "country": "Turkey", "is_coastal": True, "best_seasons": "summer,spring"},
    {"name": "Bursa", "country": "Turkey", "is_coastal": False, "best_seasons": "winter,spring"},
    {"name": "Muscat", "country": "Oman", "is_coastal": True, "best_seasons": "winter,autumn"},
    {"name": "Salalah", "country": "Oman", "is_coastal": True, "best_seasons": "summer,autumn"},
    {"name": "Amman", "country": "Jordan", "is_coastal": False, "best_seasons": "spring,autumn"},
    {"name": "Aqaba", "country": "Jordan", "is_coastal": True, "best_seasons": "winter,spring"},
    {"name": "Istanbul", "country": "Turkey", "is_coastal": True, "best_seasons": "spring,autumn"},
    {"name": "Baku", "country": "Azerbaijan", "is_coastal": True, "best_seasons": "spring,autumn"},
    {"name": "Tbilisi", "country": "Georgia", "is_coastal": False, "best_seasons": "spring,autumn"},
    {"name": "Batumi", "country": "Georgia", "is_coastal": True, "best_seasons": "summer,autumn"},
    {"name": "Sharm El Sheikh", "country": "Egypt", "is_coastal": True, "best_seasons": "winter,spring"},
    {"name": "Luxor", "country": "Egypt", "is_coastal": False, "best_seasons": "winter,autumn"},
    {"name": "Marrakesh", "country": "Morocco", "is_coastal": False, "best_seasons": "spring,autumn"},
    {"name": "Tangier", "country": "Morocco", "is_coastal": True, "best_seasons": "summer,spring"},
    {"name": "Sarajevo", "country": "Bosnia and Herzegovina", "is_coastal": False, "best_seasons": "summer,winter"},
]

EVENT_TEMPLATES = [
    ("جولة مشي تراثية", "رحلة تعريفية في المعالم التاريخية والأسواق الشعبية.", "all"),
    ("فعالية موسيقى صيفية", "أمسية موسيقية مباشرة في الهواء الطلق.", "summer"),
    ("مهرجان المأكولات", "تذوق أطباق محلية وإقليمية متنوعة.", "spring"),
    ("سوق شتوي ليلي", "أكشاك وهدايا ومنتجات يدوية بأجواء شتوية.", "winter"),
    ("مسار مغامرات طبيعي", "نشاط خارجي يجمع المشي والتصوير والأنشطة الخفيفة.", "autumn"),
]


def slugify(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-") or "item"


class Command(BaseCommand):
    help = "Seeds reproducible demo data with admin user and media assets."

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE("Seeding demo data..."))

        self._ensure_admin()

        dest_assets = sorted((Path(settings.BASE_DIR) / "seed_assets").glob("destination_*.svg"))
        hotel_assets = sorted((Path(settings.BASE_DIR) / "seed_assets").glob("hotel_*.svg"))
        event_assets = sorted((Path(settings.BASE_DIR) / "seed_assets").glob("event_*.svg"))

        if not dest_assets or not hotel_assets or not event_assets:
            self.stdout.write(self.style.WARNING("Seed asset SVG files missing in Backend/seed_assets; continuing without media."))

        total_dest = 0
        total_hotels = 0
        total_events = 0

        for idx, blueprint in enumerate(DESTINATION_BLUEPRINTS):
            flight_cost = Decimal(180 + (idx % 6) * 35)
            living_cost = Decimal(45 + (idx % 7) * 12)

            destination, _created = Destination.objects.update_or_create(
                name=blueprint["name"],
                country=blueprint["country"],
                defaults={
                    "flight_cost": flight_cost,
                    "daily_living_cost": living_cost,
                    "is_coastal": blueprint["is_coastal"],
                    "description": f"وجهة مميزة في {blueprint['country']} مناسبة لرحلات متنوعة وتجارب محلية.",
                    "best_seasons": blueprint["best_seasons"],
                },
            )
            total_dest += 1

            if dest_assets:
                self._attach_media_if_missing(destination=destination, asset_path=dest_assets[idx % len(dest_assets)], stem=f"dest-{slugify(destination.name)}")

            for hotel_idx in range(1, 4):
                stars = min(5, 2 + hotel_idx)
                price = Decimal(70 + hotel_idx * 25 + (idx % 5) * 10)
                hotel_name = f"{destination.name} Hotel {hotel_idx}"
                hotel, _ = Hotel.objects.update_or_create(
                    destination=destination,
                    name=hotel_name,
                    defaults={
                        "stars": stars,
                        "price_per_night": price,
                        "is_sea_view": bool(destination.is_coastal and hotel_idx != 1),
                    },
                )
                total_hotels += 1

                if hotel_assets:
                    self._attach_media_if_missing(hotel=hotel, asset_path=hotel_assets[(idx + hotel_idx) % len(hotel_assets)], stem=f"hotel-{slugify(hotel.name)}")

            for ev_idx, (title, description, season) in enumerate(EVENT_TEMPLATES):
                event_name = f"{title} - {destination.name}"
                event, _ = Event.objects.update_or_create(
                    destination=destination,
                    name=event_name,
                    season=season,
                    defaults={
                        "description": description,
                        "price_per_person": Decimal(0 if ev_idx == 0 else 15 + ev_idx * 8),
                        "duration_hours": 2 + (ev_idx % 4),
                        "is_free": ev_idx == 0,
                    },
                )
                total_events += 1

                if event_assets:
                    self._attach_media_if_missing(event=event, asset_path=event_assets[(idx + ev_idx) % len(event_assets)], stem=f"event-{slugify(event.name)}")

        self.stdout.write(self.style.SUCCESS(f"Seed complete: {total_dest} destinations, {total_hotels} hotels, {total_events} events."))

    def _ensure_admin(self):
        admin_password = "11223344"
        admin, created = User.objects.get_or_create(
            username="admin",
            defaults={
                "email": "admin@local.test",
                "role": "admin",
                "is_staff": True,
                "is_superuser": True,
            },
        )

        admin.role = "admin"
        admin.is_staff = True
        admin.is_superuser = True
        admin.email = admin.email or "admin@local.test"
        admin.set_password(admin_password)
        admin.save()

        if created:
            self.stdout.write(self.style.SUCCESS("Created default admin user (admin/11223344)."))
        else:
            self.stdout.write(self.style.NOTICE("Updated default admin user password to 11223344."))

    def _attach_media_if_missing(self, asset_path: Path, stem: str, destination=None, hotel=None, event=None):
        qs = ImageAsset.objects
        if destination is not None:
            qs = qs.filter(destination=destination)
        if hotel is not None:
            qs = qs.filter(hotel=hotel)
        if event is not None:
            qs = qs.filter(event=event)
        if qs.exists():
            return

        with asset_path.open("rb") as fh:
            image = ImageAsset(destination=destination, hotel=hotel, event=event)
            image.file.save(f"{stem}.svg", File(fh), save=True)
