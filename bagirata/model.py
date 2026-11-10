"""Model data BagiRata: anggota, tagihan, dan pembayaran.

Semua data disimpan dalam satu file JSON agar mudah dibaca, dicadangkan,
dan diperiksa manual oleh pengguna:

    {
      "anggota": ["Rani", "Budi"],
      "tagihan": [
        {"nama": "Listrik", "pembayar": "Rani", "jumlah": 300000,
         "peserta": ["Rani", "Budi"], "tanggal": "2026-11-01"}
      ],
      "pembayaran": [
        {"dari": "Budi", "ke": "Rani", "jumlah": 100000,
         "tanggal": "2026-11-05"}
      ]
    }
"""

import json
import os
from datetime import date, datetime

DEFAULT_DATA_FILE = "bagirata.json"


class BagiRataError(ValueError):
    """Kesalahan input dari pengguna (nama kosong, anggota tidak ada, dst.)."""


def data_kosong():
    """Struktur data awal yang masih kosong."""
    return {"anggota": [], "tagihan": [], "pembayaran": []}


def muat(path):
    """Muat data dari file JSON; kembalikan data kosong bila file belum ada."""
    if not os.path.exists(path):
        return data_kosong()
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    for kunci in ("anggota", "tagihan", "pembayaran"):
        data.setdefault(kunci, [])
    return data


def simpan(path, data):
    """Simpan data ke file JSON (ditulis atomik lewat file sementara)."""
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")
    os.replace(tmp, path)


def _tanggal_valid(tanggal):
    """Pastikan tanggal berformat YYYY-MM-DD yang benar-benar ada."""
    try:
        datetime.strptime(tanggal, "%Y-%m-%d")
    except (ValueError, TypeError):
        raise BagiRataError(
            f"Tanggal '{tanggal}' tidak valid (pakai format YYYY-MM-DD).")
    return tanggal


def _nama_bersih(nama):
    nama = (nama or "").strip()
    if not nama:
        raise BagiRataError("Nama tidak boleh kosong.")
    return nama


def tambah_anggota(data, nama):
    """Tambahkan anggota baru; nama harus unik (tanpa peduli huruf besar-kecil)."""
    nama = _nama_bersih(nama)
    if any(a.lower() == nama.lower() for a in data["anggota"]):
        raise BagiRataError(f"Anggota '{nama}' sudah ada.")
    data["anggota"].append(nama)
    return nama


def daftar_anggota(data):
    """Kembalikan daftar anggota sesuai urutan pendaftaran."""
    return list(data["anggota"])


def _cek_anggota(data, nama):
    if nama not in data["anggota"]:
        raise BagiRataError(
            f"Anggota '{nama}' tidak dikenal. Daftarkan dulu dengan "
            "'bagirata anggota tambah'."
        )


def tambah_tagihan(data, nama, pembayar, jumlah, peserta, tanggal=None):
    """Catat satu tagihan bersama.

    `pembayar` adalah anggota yang membayar dulu (nombok); `peserta` adalah
    anggota yang ikut menanggung tagihan ini (pembayar boleh termasuk).
    """
    nama = _nama_bersih(nama)
    pembayar = _nama_bersih(pembayar)
    _cek_anggota(data, pembayar)
    if jumlah <= 0:
        raise BagiRataError("Jumlah tagihan harus lebih dari 0.")
    peserta = [_nama_bersih(p) for p in peserta]
    if not peserta:
        raise BagiRataError("Tagihan harus punya minimal satu peserta.")
    if len(set(p.lower() for p in peserta)) != len(peserta):
        raise BagiRataError("Peserta tidak boleh ditulis dua kali.")
    for p in peserta:
        _cek_anggota(data, p)
    tagihan = {
        "nama": nama,
        "pembayar": pembayar,
        "jumlah": jumlah,
        "peserta": peserta,
        "tanggal": _tanggal_valid(tanggal) if tanggal else date.today().isoformat(),
    }
    data["tagihan"].append(tagihan)
    return tagihan


def daftar_tagihan(data):
    """Kembalikan daftar tagihan sesuai urutan pencatatan."""
    return list(data["tagihan"])


def hapus_tagihan(data, nomor):
    """Hapus tagihan berdasarkan nomor urut (1-based, sesuai `tagihan daftar`).

    Mengembalikan tagihan yang dihapus. Pembayaran tidak merujuk ke
    tagihan, jadi menghapus tagihan tidak merusak riwayat pembayaran.
    """
    if nomor < 1 or nomor > len(data["tagihan"]):
        raise BagiRataError(
            f"Tidak ada tagihan nomor {nomor} "
            f"(ada {len(data['tagihan'])} tagihan).")
    return data["tagihan"].pop(nomor - 1)


def tambah_pembayaran(data, dari, ke, jumlah, tanggal=None):
    """Catat pembayaran dari satu anggota ke anggota lain.

    Pembayaran mengurangi utang `dari` dan mengurangi hak terima `ke`.
    """
    dari = _nama_bersih(dari)
    ke = _nama_bersih(ke)
    _cek_anggota(data, dari)
    _cek_anggota(data, ke)
    if dari == ke:
        raise BagiRataError("Pembayar dan penerima tidak boleh sama.")
    if jumlah <= 0:
        raise BagiRataError("Jumlah pembayaran harus lebih dari 0.")
    pembayaran = {
        "dari": dari,
        "ke": ke,
        "jumlah": jumlah,
        "tanggal": _tanggal_valid(tanggal) if tanggal else date.today().isoformat(),
    }
    data["pembayaran"].append(pembayaran)
    return pembayaran


def daftar_pembayaran(data):
    """Kembalikan daftar pembayaran sesuai urutan pencatatan."""
    return list(data["pembayaran"])
