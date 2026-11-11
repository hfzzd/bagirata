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
- **Jatuh tempo & pengingat** — tagihan bisa diberi batas bayar; perintah
  `pengingat` menampilkan yang terlambat, jatuh hari ini, atau jatuh dalam
  N hari ke depan (bawaan 7 hari).
- **Tagihan berulang** — tagihan bulanan (mis. WiFi) ditandai `--berulang
  bulanan` lalu disalin ke bulan berjalan dengan `tagihan perpanjang`.
- **Ekspor CSV** — ekspor tagihan, pembayaran, laporan bulanan, dan rencana
  pelunasan (`lunas`) ke CSV, siap dibuka di spreadsheet atau dibagikan ke
  teman serumah yang tidak memakai CLI.
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

# 7. Tagihan berulang dengan jatuh tempo, lalu cek pengingat
bagirata tagihan tambah --nama "WiFi" --pembayar Budi --jumlah 150000 \
    --peserta Rani Budi Sinta --jatuh-tempo 2026-11-10 --berulang bulanan
bagirata pengingat             # jatuh tempo ≤ 7 hari lagi (bawaan)
bagirata pengingat --dalam 1   # hanya yang jatuh besok / hari ini / terlambat

# 8. Perpanjang tagihan berulang ke bulan berjalan
bagirata tagihan perpanjang --bulan 2026-12

# 9. Ekspor ke CSV (buka di spreadsheet)
bagirata ekspor --jenis tagihan --keluar tagihan.csv
bagirata ekspor --jenis lunas
```

Jalankan `bagirata --help` untuk daftar perintah lengkap. Data bisa dipindah ke file
lain dengan `--data` atau variabel lingkungan `BAGIRATA_DATA`.

## Contoh ekspor CSV

Jenis yang tersedia: `tagihan`, `pembayaran`, `laporan` (tambah `--bulan`),
dan `lunas` (rencana pelunasan: transfer seminimal mungkin supaya semua
lunas). Tanpa `--keluar`, hasil CSV tampil di layar.

`bagirata --data contoh/bagirata-contoh.json ekspor --jenis lunas`:

```csv
nomor,dari,ke,jumlah
1,Sinta,Rani,80000
2,Sinta,Budi,30000
```

`bagirata --data contoh/bagirata-contoh.json ekspor --jenis tagihan`:

```csv
nomor,nama,pembayar,jumlah,tanggal,peserta
1,Listrik November,Rani,300000,2026-11-03,Rani;Budi;Sinta
2,WiFi November,Budi,150000,2026-11-05,Rani;Budi;Sinta
3,Air galon,Sinta,60000,2026-11-08,Rani;Budi;Sinta
```

## Format data

`bagirata.json` berisi tiga daftar: `anggota`, `tagihan`, dan `pembayaran`.
Tagihan bisa punya field opsional `jatuh_tempo` (YYYY-MM-DD) dan `berulang`
(`"bulanan"`).
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
