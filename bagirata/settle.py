"""Rencana pelunasan dengan transfer sesedikit mungkin.

Dari saldo tiap anggota (positif = berhak menerima, negatif = berutang),
susun daftar transfer supaya semua lunas. Algoritma greedy: pasangkan
pengutang terbesar dengan penerima terbesar berulang kali. Jumlah
transfer tidak pernah melebihi (jumlah anggota - 1) — jauh lebih
sedikit daripada "semua orang transfer ke semua orang".
"""


def rencana_pelunasan(saldo):
    """Kembalikan daftar (dari, ke, jumlah) untuk melunasi semua saldo.

    Saldo nol diabaikan. Total semua saldo diasumsikan 0; bila tidak,
    kelebihan/kekurangan dibebankan ke transfer terakhir.
    """
    pengutang = sorted(
        ((nama, -nilai) for nama, nilai in saldo.items() if nilai < 0),
        key=lambda x: x[1], reverse=True,
    )
    penerima = sorted(
        ((nama, nilai) for nama, nilai in saldo.items() if nilai > 0),
        key=lambda x: x[1], reverse=True,
    )
    rencana = []
    i = j = 0
    while i < len(pengutang) and j < len(penerima):
        nama_utang, utang = pengutang[i]
        nama_terima, terima = penerima[j]
        jumlah = min(utang, terima)
        rencana.append((nama_utang, nama_terima, jumlah))
        utang -= jumlah
        terima -= jumlah
        if utang == 0:
            i += 1
        else:
            pengutang[i] = (nama_utang, utang)
        if terima == 0:
            j += 1
        else:
            penerima[j] = (nama_terima, terima)
    return rencana
