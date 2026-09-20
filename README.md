# Celengan (Pencatat & Pemantau Target Tabungan)

Aplikasi pencatat dan pemantau target tabungan personal yang terinspirasi dari konsep aplikasi Celenganku, dibangun menggunakan arsitektur **Modern Monolith / HTML-over-the-Wire** dengan **DATH Stack** (Django, Alpine.js, Tailwind CSS, HTMX) dan desain visual **Google Material Design 3 (Dark Theme First)**.

Aplikasi dirancang khusus untuk kebutuhan tugas UTS, fokus pada pengalaman pengguna mobile-first, tanpa kerumitan autentikasi login/register, payment gateway, atau integrasi perbankan.

---

## 🛠️ Tech Stack: DATH Stack
- **D**jango 5 (Python 3.14): Backend framework, ORM, business logic, template rendering.
- **A**lpine.js 3: Interaktivitas mikro sisi klien (modal transitions, reactive icon selection, instant client-side updates).
- **T**ailwind CSS: Desain mobile-first dengan token Google Material Design 3 (*Surface Container*, *Primary*, *Secondary*, *Tertiary*, *Dark Theme*).
- **H**TMX 2: Interaksi dinamis tanpa full page-reload (*HTML-over-the-Wire* untuk filter tab, partial update saldo, live calculator, dan toggle pengingat).

---

## ✨ Fitur Utama
1. **Dashboard Metrik Finansial**:
   - Total tabungan terkumpul dan total target.
   - Indikator persentase penyelesaian keseluruhan secara visual.
   - Ringkasan jumlah target aktif dan target tercapai.
   - Banner jadwal pengingat menabung hari ini.
   - Daftar riwayat 5 transaksi mutasi terakhir.
2. **Manajemen Target Tabungan**:
   - Pembuatan target tabungan baru dengan nama, icon, palet warna, nominal target, tenggat waktu, dan frekuensi.
   - Status target otomatis berubah menjadi **Tercapai** 🎉 saat saldo $\ge$ nominal target.
   - Filter kartu target: *Semua*, *Aktif*, dan *Tercapai* via HTMX partial swap.
3. **Kalkulator & Rencana Tabungan**:
   - Perhitungan otomatis sisa periode dan rekomendasi nominal yang harus disisihkan per hari/minggu/bulan.
   - Halaman simulator kalkulator interaktif dengan input *live calculation* HTMX.
4. **Pencatatan Mutasi Tabungan Cepat**:
   - Modal setoran (*Deposit / Tambah*) dan penarikan (*Withdraw / Kurang*).
   - Chip nominal cepat (+10rb, +20rb, +50rb, +100rb, +250rb, +500rb).
   - Riwayat mutasi lengkap dengan tanggal dan keterangan.
   - Penghapusan catatan transaksi dengan penyesuaian saldo otomatis.
5. **Pengingat Menabung (Reminders)**:
   - Pengingat periodik menabung dengan jam dan frekuensi.
   - Toggle status aktif/mati secara instan dengan HTMX.
   - Integrasi Web Notification API peramban lokal.
6. **Setelan & Utilitas Demonstrasi UTS**:
   - Pengaturan nama panggilan pengguna dan simbol mata uang.
   - Tombol **Isi Sampel Data Tabungan (Demo)** untuk langsung mempopulasikan data uji siap pakai.
   - Tombol **Reset Semua Data** untuk mengosongkan kembali basis data.

---

## 🚀 Cara Menjalankan Aplikasi

1. **Jalankan Server Django**:
   ```bash
   python3 manage.py runserver 0.0.0.0:8000
   ```

2. **Akses Aplikasi melalui Browser**:
   - Buka: `http://localhost:8000` atau `http://127.0.0.1:8000`
   - Buka melalui browser smartphone atau aktifkan *Device Mode (Mobile View)* di Inspect Element browser laptop/PC untuk pengalaman optimal sesuai desain mobile-first Material Design 3.

3. **Menjalankan Pengujian Unit Otomatis (Tests)**:
   ```bash
   python3 manage.py test
   ```

4. **Seed Ulang Data Sampel (Jika Diperlukan)**:
   ```bash
   python3 manage.py seed_data
   ```

---

## 📂 Struktur Direktori Proyek
```text
celengan/
├── config/                      # Django configuration & routing
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── savings/                     # App utama pencatat tabungan
│   ├── models.py                # AppSetting, SavingsGoal, Transaction, SavingsReminder
│   ├── views.py                 # Controller & HTMX partial views
│   ├── forms.py                 # Form input dengan styling MD3
│   ├── urls.py                  # Endpoint routing
│   ├── context_processors.py    # Context processor profil & preferensi
│   ├── templatetags/            # Filter mata uang rupiah & pemformat angka
│   ├── management/commands/     # CLI seed_data untuk demo UTS
│   └── tests.py                 # Automated unit tests
├── templates/                   # Template engine HTML-over-the-Wire
│   ├── base.html                # Kerangka mobile-frame & Material Design 3 theme
│   ├── components/              # Bottom navigation bar & header
│   └── savings/                 # Dashboard, Goals, Detail, Calculator, Settings
│       └── partials/            # HTMX dynamic partials (cards, modals, lists)
├── static/                      # Asset statis offline (HTMX, Alpine.js)
├── PRD_AND_ERD.md               # Dokumen spesifikasi PRD & diagram ERD
└── README.md                    # Dokumentasi proyek
```
