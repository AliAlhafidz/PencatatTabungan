# Celengan (Pencatat & Pemantau Target Tabungan)

Aplikasi pencatat dan pemantau target tabungan personal yang terinspirasi dari konsep aplikasi Celenganku, dibangun menggunakan arsitektur **Modern Monolith / HTML-over-the-Wire** dengan **DATH Stack** (Django, Alpine.js, Tailwind CSS, HTMX), desain visual **Google Material Design 3 (Dark Theme First)**, dan dukungan **Progressive Web App (PWA)** dengan ikon celengan babi (*piggy bank*) yang imut.

Aplikasi dirancang khusus untuk kebutuhan tugas UTS, berfokus pada pengalaman pengguna mobile-first yang super ringan (*zero lag*), tanpa kerumitan autentikasi login/register, payment gateway, atau integrasi perbankan.

---

## 🛠️ Tech Stack: DATH Stack & PWA
- **D**jango 5 (Python 3.14): Backend framework, ORM, business logic, template rendering.
- **A**lpine.js 3: Interaktivitas mikro sisi klien (modal transitions, modal picker frekuensi, instant formatting titik ribuan).
- **T**ailwind CSS: Desain mobile-first dengan token Google Material Design 3 (*Surface Container*, *Primary*, *Secondary*, *Tertiary*, *Dark Theme*).
- **H**TMX 2: Interaksi dinamis tanpa full page-reload (*HTML-over-the-Wire* untuk filter tab, partial update saldo, kalkulator live, modal trigger, dan toggle pengingat).
- **PWA (Progressive Web App)**: Service worker caching (`celengan-v2`), manifest, dan ikon aplikasi celengan babi (*piggy bank*) mandiri di homescreen smartphone.

---

## ✨ Fitur Utama & Penyempurnaan Terkini

1. **Dashboard Metrik Finansial Bersih**:
   - Total tabungan terkumpul dan total target finansial dengan format rupiah otomatis.
   - Ringkasan jumlah target aktif dan target tercapai (*achieved*).
   - Banner jadwal pengingat menabung hari ini.
   - Daftar 5 riwayat transaksi mutasi terakhir.

2. **Manajemen Target Tabungan Modern**:
   - Pembuatan target tabungan baru dengan nama, foto impian (opsional), nominal target, frekuensi menabung, dan rencana nominal simpanan.
   - **Form Modal Terpusat & Elevated**: Posisi modal form berada di tengah dan sedikit ke atas (`-translate-y-4`) agar nyaman diisi dan tidak terhimpit keyboard virtual saat mengetik di smartphone.
   - **Modal Picker Frekuensi Khusus**: Menggantikan dropdown `<select>` mentah dengan modal pilihan kartu bergaya MD3 (Harian, Mingguan, Bulanan) lengkap dengan deskripsi dan ikon.
   - **Modal Konfirmasi Hapus Aman**: Menghapus target tabungan kini menggunakan modal konfirmasi bahaya khusus bergaya MD3, menggantikan dialog alert mentah bawaan browser.
   - Status target otomatis berubah menjadi **Tercapai** 🎉 saat saldo $\ge$ nominal target.

3. **Pencatatan Mutasi Tabungan Cepat**:
   - Modal setoran (*Deposit / Tambah*) dan penarikan (*Withdraw / Kurang*) yang terpusat dan ergonomis.
   - Chip nominal cepat (+10rb, +20rb, +50rb, +100rb, +250rb, +500rb).
   - Riwayat mutasi lengkap dengan tanggal dan keterangan.
   - Penghapusan catatan transaksi yang salah dengan penyesuaian saldo otomatis.

4. **Kalkulator & Estimasi Target**:
   - Perhitungan otomatis estimasi waktu tercapainya impian berdasarkan rencana frekuensi dan nominal simpanan.
   - Halaman simulator kalkulator interaktif dengan input *live calculation* HTMX.

5. **Pengingat Menabung (Reminders)**:
   - Pengingat periodik menabung dengan jam dan frekuensi.
   - Toggle status aktif/mati secara instan dengan HTMX.
   - Integrasi Web Notification API peramban lokal.

6. **Optimasi Performa & Animasi Ringan**:
   - **Zero Lag Mobile**: Menonaktifkan komputasi berat `backdrop-filter: blur` pada layar ponsel sehingga rendering sangat cepat dan hemat baterai.
   - **Animasi Mikro GPU**: Transisi pop-in modal (`anim-modal`), efek muncul kartu (`anim-slide-up`), dan tombol kenyal (`touch-bounce`) dengan akselerasi hardware.

7. **Setelan & Utilitas Demonstrasi UTS**:
   - Pengaturan nama panggilan pengguna dan simbol mata uang default.
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
│   ├── base.html                # Kerangka mobile-frame, animations & MD3 theme
│   ├── components/              # Bottom navigation bar & header
│   └── savings/                 # Dashboard, Goals, Detail, Calculator, Settings
│       └── partials/            # HTMX dynamic partials (cards, modals, lists)
│           ├── goal_form_modal.html       # Modal form target + picker frekuensi
│           ├── goal_delete_modal.html     # Modal konfirmasi hapus khusus
│           ├── transaction_form_modal.html# Modal transaksi setor/tarik
│           └── ...
├── static/                      # Asset statis offline (HTMX, Alpine.js, PWA Icons)
│   ├── icons/                   # Piggy bank icons (icon.svg, 192px, 512px)
│   ├── manifest.json            # PWA Manifest configuration
│   └── sw.js                    # PWA Service Worker caching
├── PRD_AND_ERD.md               # Dokumen spesifikasi PRD, User Flow & ERD
└── README.md                    # Dokumentasi proyek
```
