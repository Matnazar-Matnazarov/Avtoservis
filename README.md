# Django bilan ishlangan loyiha — o'rnatish va ishga tushirish (uv bilan)

<p align="left">
  <a href="https://www.python.org/">
    <img src="https://img.shields.io/badge/Python-3.12%2B-3776AB?logo=python&logoColor=white" alt="Python" />
  </a>
  <a href="https://www.djangoproject.com/">
    <img src="https://img.shields.io/badge/Django-5.x-092E20?logo=django&logoColor=white" alt="Django" />
  </a>
  <a href="https://jinja.palletsprojects.com/">
    <img src="https://img.shields.io/badge/Jinja-Templates-B41717" alt="Jinja" />
  </a>
  <a href="https://tailwindcss.com/">
    <img src="https://img.shields.io/badge/Tailwind_CSS-3.x-06B6D4?logo=tailwindcss&logoColor=white" alt="Tailwind CSS" />
  </a>
  <a href="https://www.sqlite.org/">
    <img src="https://img.shields.io/badge/SQLite-3-003B57?logo=sqlite&logoColor=white" alt="SQLite" />
  </a>
</p>

## Texnologiyalar
- Python (Django web framework) yordamida.
- Django (backend).
- Shablonlar: Jinja (`.jinja`).
- Tailwind CSS (UI/Design).
- SQLite (standart ma'lumotlar bazasi).

## O'rnatish (Windows / Linux / macOS)

### 1) uv (tezkor Python menejeri) ni o'rnatish
- Windows (PowerShell):
```powershell
irm https://astral.sh/uv/install.ps1 | iex
```
- Linux/macOS (bash/zsh):
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```
Eslatma: O'rnatishdan so'ng terminalni qayta oching yoki `PATH` yangilang. Tekshirish: `uv --version`

### 2) Loyihani klonlash
```bash
git clone https://github.com/Matnazar-Matnazarov/Avtoservis.git
cd Avtoservis
```

### 3) Virtual muhit yaratish (ixtiyoriy, tavsiya etiladi)
```bash
uv venv .venv
```
Faollashtirish (ixtiyoriy):
- Windows (PowerShell):
```powershell
.\.venv\Scripts\Activate.ps1
```
- Linux/macOS:
```bash
source .venv/bin/activate
```

### 4) Kutubxonalarni o'rnatish
```bash
uv pip install -r requirements.txt
```

### 5) Ma'lumotlar bazasini tayyorlash (Django)
```bash
uv run python manage.py makemigrations
uv run python manage.py migrate
```

### 6) Admin (superuser) yaratish
```bash
uv run python manage.py createsuperuser
```

### 7) Dastur serverini ishga tushirish
```bash
uv run python manage.py runserver
```
Brauzerda: http://127.0.0.1:8000  |  Admin: http://127.0.0.1:8000/admin

---

# Avtoservis Boshqaruv Tizimi

## Asosiy Funksionallik

### 1. Buyurtma Boshqaruvi (Order Management)
- **Batafsil Buyurtma Ko'rinishi**
  - Har bir buyurtma uchun alohida batafsil sahifa
  - Tanlangan xizmatlar ro'yxati va ularning narxlari
  - Xizmat holatlari: Jarayonda / Bajarildi / Tekshirilmoqda
  - Avtomatik hisoblanadigan umumiy summa
  - Qo'shimcha ehtiyot qismlarni qo'shish imkoniyati

### 2. Ehtiyot Qismlar Boshqaruvi (Parts Management)
- **Asosiy Xususiyatlar**
  - Ehtiyot qismlarning to'liq ro'yxati
  - Har bir qism uchun: Nomi, artikuli, narxi, qoldiq soni
  - Buyurtmalarga ehtiyot qismlarni qo'shish imkoniyati
  - Sklad balansini avtomatik hisoblash va yangilash

### 3. Ustalar Boshqaruvi (Masters Management)
- **Ustalar Profillari**
  - To'liq ism-sharifi, telefon raqami
  - Mutaxassislik turlari (motorchi, elektrik, shinomontaj va boshqalar)
  - Buyurtmalarni ustalarga biriktirish
  - Ustalarning ish yuklanishi monitoringi (kunlik/haftalik)

### 4. To'lov Tizimi (Payment System)
- **To'lov Boshqaruvi**
  - To'lov holati admin tomonidan qo'lda belgilanadi: To'landi / To'lanmadi
  - To'langanida to'lov turi tanlanadi va saqlanadi: Naqd / Karta / Perevod
  - Hozircha onlayn/avtomatik to'lov integratsiyasi yo'q

### 5. Telegram Integratsiyasi
- **Bildirishnoma Xizmati**
  - Buyurtma holati o'zgarganda mijozga avtomatik xabar yuboriladi
  - Faqat mijozning `telegram_username` mavjud bo'lsa va botga Start bosgan bo'lsa
  - Shaxsiy xabarlar orqali buyurtma holati haqida xabardor qilish

### 6. Kengaytirilchi Qidiruv va Filtrlash
- **Qidiruv Imkoniyatlari**
  - Mijozlar bo'yicha telefon raqami orqali tezkor qidiruv
  - Mashina raqami bo'yicha aniq qidiruv
  - Sana oralig'i bo'yicha filtrlash

### 7. Tarix va Hisobotlar
- **Buyurtmalar Tarixi**
  - Har bir avtomobilning servis tarixi
  - Oldingi xizmatlar va to'lovlar tarixi
  - Mijozlar uchun to'liq xizmat tarixi

### 8. Fotosuratlar Bilan Ishlash
- **Rasmlar Bilan Ishlash**
  - Buyurtmalarga "oldindan" va "keyin" fotosuratlarni yuklash
  - Mijozlarga ko'rsatish uchun vizual dalillar

### 9. Eksport va Hisobotlar
- **Ma'lumotlarni Eksport Qilish**
  - Kunlik va oylik hisobotlarni Excel/CSV formatida yuklab olish
  - Tahlil uchun ma'lumotlarni tayyor formatda olish

### 10. Foydalanuvchi Tizimi
- **Kirish va Ruxsatnomalar**
  - Turli foydalanuvchi rollari (Admin, Usta, Qabulxona)
  - Faqat Admin uchun maxsus huquqlar va imtiyozlar qolganlari esa kirolmaydi
  - Xavfsizlik va ma'lumotlarni himoya qilish

## Tezkor Amalga Oshirish Uchun Tavsiya Etilgan Bosqichlar

### 1. Birinchi Bosqich (1-2 kun)
- Buyurtmalar uchun batafsil ko'rinish
- Avtomatik summa hisoblash tizimi
- Telefon raqami orqali tezkor qidiruv
- Buyurtma holatlarini ranglar bilan ajratish

### 2. Keyingi Bosqichlar
- Ehtiyot qismlar moduli
- Ustalar bo'yicha ish yuklanishi
- To'lov tizimini ishlab chiqish
- Telegram orqali bildirishnomalar

5. Telegram orqali bildirishnoma mijozni telegram username bor bo'lsa va bot ga start bosgan bo'lsa 
Buyurtma holati o‘zgarganda mijozga avto-xabar
Masalan: “Sizning Malibu mashinangiz tayyor, umumiy summa 1 500 000 so‘m”
6. Qidiruv va filtrlar (hammayoqda)
Mijozlar bo‘yicha: telefon orqali tezkor qidiruv
Sana bo‘yicha buyurtmalar filtri
7. Tarix (History)
Har bir mashinaning oldingi servis tarixi
Qachon qanday xizmat qilingan, qancha pul to‘langan
8. Foto qo‘shish imkoniyati
Buyurtmaga oldin/keyin fotosuratlar yuklash
Zarur bo‘lsa mijozga ko‘rsatish uchun
9. Excel/CSV export
Kunlik, oylik hisobotlarni Excelga chiqarish
10. Foydalanuvchi tizimi (Login)
Admin, usta, qabulxona xodimi – turli huquqlar
Hozircha hammaga ochiq, keyin yopish kerak
Tez orada qo‘shish uchun eng oson va foydali 3 ta narsa (1-2 kun ichida):
1.Buyurtma detail sahifasi + avtomatik summa hisoblash
2.Telefon bo‘yicha tezkor qidiruv (mijoz va mashina)
3.Buyurtma holatini o‘zgartirishda rang (Jarayonda – sariq, Yakunlangan – yashil)
# Avtoservis
