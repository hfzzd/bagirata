"""Ekspor data BagiRata ke CSV.

CSV dipilih karena bisa dibuka di spreadsheet (LibreOffice, Excel,
Google Sheets) tanpa alat tambahan — berguna untuk arsip bulanan
atau dibagikan ke teman serumah yang tidak memakai CLI.

Kolom tagihan: nomor, nama, pembayar, jumlah, tanggal, peserta.
Peserta digabung dengan ";" agar tetap satu kolom.
Kolom pembayaran: nomor, dari, ke, jumlah, tanggal.
"""

import csv
import io


def _ke_csv(baris):
    """Ubah daftar baris (daftar kolom) menjadi teks CSV."""
    buf = io.StringIO(newline="")
    penulis = csv.writer(buf)
    penulis.writerows(baris)
    return buf.getvalue()


def ekspor_csv_tagihan(data):
    """Kembalikan teks CSV berisi semua tagihan."""
    baris = [["nomor", "nama", "pembayar", "jumlah", "tanggal", "peserta"]]
    for i, t in enumerate(data["tagihan"], 1):
        baris.append([
            i, t["nama"], t["pembayar"], t["jumlah"], t["tanggal"],
            ";".join(t["peserta"]),
        ])
    return _ke_csv(baris)


def ekspor_csv_pembayaran(data):
    """Kembalikan teks CSV berisi semua pembayaran."""
    baris = [["nomor", "dari", "ke", "jumlah", "tanggal"]]
    for i, p in enumerate(data["pembayaran"], 1):
        baris.append([i, p["dari"], p["ke"], p["jumlah"], p["tanggal"]])
    return _ke_csv(baris)
