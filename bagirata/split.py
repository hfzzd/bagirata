"""Logika pembagian tagihan dan perhitungan saldo.

Semua jumlah dalam rupiah (bilangan bulat) supaya tidak ada galat
pembulatan uang. Pembagian yang tidak habis dibagi: sisa rupiah
dibebankan ke peserta pertama secara berurutan, sehingga total
bagian selalu tepat sama dengan jumlah tagihan.
"""


def bagi_rata(jumlah, peserta):
    """Bagi `jumlah` sama rata ke `peserta`; kembalikan {nama: bagian}.

    Sisa pembagian (jumlah % len(peserta)) rupiah dibebankan satu per satu
    ke peserta pertama, jadi total bagian == jumlah (tanpa selisih).
    """
    if not peserta:
        raise ValueError("Peserta tidak boleh kosong.")
    if jumlah < 0:
        raise ValueError("Jumlah tidak boleh negatif.")
    n = len(peserta)
    dasar, sisa = divmod(jumlah, n)
    return {
        nama: dasar + (1 if i < sisa else 0)
        for i, nama in enumerate(peserta)
    }


def hitung_saldo(data, bobot=None):
    """Hitung saldo tiap anggota dari semua tagihan.

    Saldo positif = anggota sudah membayar lebih dari bagiannya
    (berhak menerima kembali). Saldo negatif = anggota masih berutang.
    Total semua saldo selalu 0.

    `bobot` (opsional): {nama_tagihan: {nama: bobot}} untuk pembagian
    proporsional; bila tidak ada, tagihan dibagi rata.
    """
    saldo = {nama: 0 for nama in data["anggota"]}
    for t in data["tagihan"]:
        if bobot and t["nama"] in bobot:
            bagian = bagi_proporsional(t["jumlah"], t["peserta"],
                                       bobot[t["nama"]])
        else:
            bagian = bagi_rata(t["jumlah"], t["peserta"])
        saldo[t["pembayar"]] += t["jumlah"]
        for nama, porsi in bagian.items():
            saldo[nama] -= porsi
    return saldo


def bagi_proporsional(jumlah, peserta, bobot):
    """Bagi `jumlah` sebanding dengan `bobot` tiap peserta.

    `bobot` memetakan nama peserta ke angka positif (mis. luas kamar).
    Pembagian memakai pembulatan ke bawah lalu sisa rupiah dibagikan
    satu per satu ke peserta dengan sisa pecahan terbesar (largest
    remainder), sehingga total bagian == jumlah.
    """
    if not peserta:
        raise ValueError("Peserta tidak boleh kosong.")
    if jumlah < 0:
        raise ValueError("Jumlah tidak boleh negatif.")
    for nama in peserta:
        if bobot.get(nama, 0) <= 0:
            raise ValueError(f"Bobot untuk '{nama}' harus lebih dari 0.")
    total = sum(bobot[nama] for nama in peserta)
    mentah = {nama: jumlah * bobot[nama] / total for nama in peserta}
    bagian = {nama: int(mentah[nama]) for nama in peserta}
    sisa = jumlah - sum(bagian.values())
    urutan = sorted(peserta, key=lambda n: (mentah[n] - bagian[n]), reverse=True)
    for nama in urutan[:sisa]:
        bagian[nama] += 1
    return bagian
