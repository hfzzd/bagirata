"""Laporan bulanan: ringkasan tagihan, pembayaran, dan saldo per anggota.

Laporan memfilter tagihan & pembayaran berdasarkan awalan tanggal
"YYYY-MM" (mis. "2026-11"), lalu menghitung total per anggota untuk
bulan itu. Saldo akhir yang ditampilkan adalah saldo keseluruhan
(semua bulan) supaya angka "siapa berutang ke siapa" tetap konsisten
dengan perintah `saldo`.
"""

from .split import bagi_rata, hitung_saldo


def laporan_bulanan(data, bulan):
    """Kembalikan ringkasan bulan `bulan` ("YYYY-MM").

    Hasil: {"bulan", "total_tagihan", "jumlah_tagihan", "jumlah_pembayaran",
            "per_anggota": {nama: {"dibayar", "ditanggung", "membayar",
            "menerima"}}, "saldo_akhir": {nama: saldo}}.
    """
    tagihan = [t for t in data["tagihan"]
               if t["tanggal"].startswith(bulan)]
    pembayaran = [p for p in data["pembayaran"]
                  if p["tanggal"].startswith(bulan)]
    per_anggota = {
        nama: {"dibayar": 0, "ditanggung": 0, "membayar": 0, "menerima": 0}
        for nama in data["anggota"]
    }
    for t in tagihan:
        per_anggota[t["pembayar"]]["dibayar"] += t["jumlah"]
        for peserta, bagian in bagi_rata(t["jumlah"], t["peserta"]).items():
            per_anggota[peserta]["ditanggung"] += bagian
    for p in pembayaran:
        per_anggota[p["dari"]]["membayar"] += p["jumlah"]
        per_anggota[p["ke"]]["menerima"] += p["jumlah"]
    return {
        "bulan": bulan,
        "total_tagihan": sum(t["jumlah"] for t in tagihan),
        "jumlah_tagihan": len(tagihan),
        "jumlah_pembayaran": len(pembayaran),
        "per_anggota": per_anggota,
        "saldo_akhir": hitung_saldo(data),
    }
