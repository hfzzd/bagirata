"""Ekspor data BagiRata ke CSV.

CSV dipilih karena bisa dibuka di spreadsheet (LibreOffice, Excel,
Google Sheets) tanpa alat tambahan — berguna untuk arsip bulanan
atau dibagikan ke teman serumah yang tidak memakai CLI.

Kolom tagihan: nomor, nama, pembayar, jumlah, tanggal, peserta.
Peserta digabung dengan ";" agar tetap satu kolom.
Kolom pembayaran: nomor, dari, ke, jumlah, tanggal.
Kolom rencana pelunasan (lunas): nomor, dari, ke, jumlah.
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


def ekspor_csv_lunas(data):
    """Kembalikan teks CSV berisi rencana pelunasan (transfer minimal).

    Kolom: nomor, dari, ke, jumlah. Bila semua sudah lunas, hanya
    header yang dihasilkan — tidak ada transfer yang perlu dicatat.
    """
    from .settle import rencana_pelunasan
    from .split import hitung_saldo

    rencana = rencana_pelunasan(hitung_saldo(data))
    baris = [["nomor", "dari", "ke", "jumlah"]]
    for i, (dari, ke, jumlah) in enumerate(rencana, 1):
        baris.append([i, dari, ke, jumlah])
    return _ke_csv(baris)


def ekspor_csv_pembayaran(data):
    """Kembalikan teks CSV berisi semua pembayaran."""
    baris = [["nomor", "dari", "ke", "jumlah", "tanggal"]]
    for i, p in enumerate(data["pembayaran"], 1):
        baris.append([i, p["dari"], p["ke"], p["jumlah"], p["tanggal"]])
    return _ke_csv(baris)


def ekspor_csv_laporan(data, bulan):
    """Kembalikan teks CSV berisi laporan bulanan per anggota.

    Kolom: anggota, dibayar (membayar tagihan), ditanggung (bagian
    tagihan), membayar (ke teman), menerima (dari teman), saldo_akhir.
    Saldo akhir positif = berhak menerima, negatif = berutang.
    """
    from .report import laporan_bulanan

    lap = laporan_bulanan(data, bulan)
    baris = [["bulan", "anggota", "dibayar", "ditanggung", "membayar",
              "menerima", "saldo_akhir"]]
    for nama, r in lap["per_anggota"].items():
        baris.append([
            bulan, nama, r["dibayar"], r["ditanggung"], r["membayar"],
            r["menerima"], lap["saldo_akhir"][nama],
        ])
    return _ke_csv(baris)
