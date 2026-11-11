"""Pengingat tagihan jatuh tempo.

Tagihan yang punya `jatuh_tempo` (lihat `model.tambah_tagihan`)
diingatkan di sini: yang sudah lewat, yang jatuh hari ini, dan yang
jatuh dalam `ambang_hari` hari ke depan. Tagihan tanpa jatuh tempo
tidak pernah muncul — tidak ada tanggal, tidak ada pengingat.
"""

from datetime import date, datetime


def daftar_pengingat(data, hari_ini=None, ambang_hari=7):
    """Kembalikan pengingat terurut berdasarkan jatuh tempo.

    Setiap butir: {"nomor", "nama", "pembayar", "jumlah",
    "jatuh_tempo", "sisa_hari", "status"} dengan `sisa_hari` negatif
    bila sudah lewat. `status` salah satu dari "TERLAMBAT",
    "HARI INI", atau "n HARI LAGI".
    """
    hari_ini = hari_ini or date.today()
    hasil = []
    for i, t in enumerate(data["tagihan"], 1):
        jatuh = t.get("jatuh_tempo")
        if not jatuh:
            continue
        sisa = (datetime.strptime(jatuh, "%Y-%m-%d").date() - hari_ini).days
        if sisa < 0:
            status = "TERLAMBAT"
        elif sisa == 0:
            status = "HARI INI"
        else:
            status = f"{sisa} HARI LAGI"
        if sisa < 0 or sisa <= ambang_hari:
            hasil.append({
                "nomor": i,
                "nama": t["nama"],
                "pembayar": t["pembayar"],
                "jumlah": t["jumlah"],
                "jatuh_tempo": jatuh,
                "sisa_hari": sisa,
                "status": status,
            })
    hasil.sort(key=lambda p: p["jatuh_tempo"])
    return hasil
