# BagiRata

**Pembagi tagihan untuk anak kos & teman serumah — tanpa aplikasi berat, tanpa akun, tanpa biaya.**

Tinggal serumah itu gampang. Yang ribet: siapa yang sudah bayar listrik, siapa yang
nombok WiFi bulan lalu, dan siapa yang masih berutang ke siapa. BagiRata mencatat
tagihan bersama, menghitung pembagian yang adil, dan menunjukkan cara melunasi
dengan transfer sesedikit mungkin.

## Masalah yang diselesaikan

- Tagihan bersama (listrik, WiFi, air galon, iuran kebersihan) sering dicatat di
  chat — tercecer dan sulit dilacak.
- Pembagian yang "kira-kira" bikin ada yang merasa dirugikan.
- Saat melunasi, transfer bolak-balik yang sebenarnya bisa dipersingkat.

## Fitur

- **Anggota** — tambah & lihat daftar penghuni rumah/kos.
- **Tagihan** — catat tagihan bersama: siapa yang membayar, berapa, untuk siapa saja.
- **Bagi rata & proporsional** — bagi sama rata, atau berdasarkan bobot (mis. kamar
  besar bayar lebih).
- **Pembayaran & settlement** — catat pembayaran antar anggota; BagiRata menghitung
  transfer seminimal mungkin supaya semua lunas.
- **Laporan bulanan** — ringkasan tagihan & saldo tiap anggota per bulan.
- **Data lokal** — semua tersimpan di satu file JSON (`bagirata.json`) di komputermu.
  Tidak ada server, tidak ada akun, tidak ada data yang keluar.

## Cara pakai

Butuh Python 3.10+ saja, tanpa dependensi tambahan.

```bash
# Instal (opsional — bisa juga langsung pakai python -m bagirata)
pip install -e .

# 1. Daftarkan penghuni
bagirata anggota tambah "Rani"
bagirata anggota tambah "Budi"
bagirata anggota tambah "Sinta"

# 2. Catat tagihan (Rani membayar listrik Rp300.000 untuk ketiganya)
bagirata tagihan tambah --nama "Listrik Oktober" --pembayar Rani \
    --jumlah 300000 --peserta Rani Budi Sinta

# 3. Lihat saldo — siapa berutang ke siapa
bagirata saldo

# 4. Catat pembayaran (Budi membayar Rp100.000 ke Rani)
bagirata bayar --dari Budi --ke Rani --jumlah 100000

# 5. Lihat transfer seminimal mungkin supaya semua lunas
bagirata lunas

# 6. Laporan bulan berjalan
bagirata laporan
```

Jalankan `bagirata --help` untuk daftar perintah lengkap. Data bisa dipindah ke file
lain dengan `--data` atau variabel lingkungan `BAGIRATA_DATA`.

## Format data

`bagirata.json` berisi tiga daftar: `anggota`, `tagihan`, dan `pembayaran`.
File ini sengaja dibuat mudah dibaca manusia — silakan dibuka dan diperiksa.
Contoh lengkap ada di [`contoh/bagirata-contoh.json`](contoh/bagirata-contoh.json).
Coba langsung tanpa membuat data sendiri:

```bash
bagirata --data contoh/bagirata-contoh.json saldo
bagirata --data contoh/bagirata-contoh.json lunas
bagirata --data contoh/bagirata-contoh.json laporan --bulan 2026-11
```

## Pengembangan

```bash
python -m unittest discover -s tests -v   # jalankan test
```

## Lisensi

MIT — lihat [`LICENSE`](LICENSE).
