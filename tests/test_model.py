"""Unit test model BagiRata: anggota, tagihan, pembayaran, hapus, IO."""

import json
import os
import tempfile
import unittest

from bagirata import model


def data_contoh():
    data = model.data_kosong()
    for nama in ("Rani", "Budi", "Sinta"):
        model.tambah_anggota(data, nama)
    return data


class TestAnggota(unittest.TestCase):
    def test_tambah_dan_daftar(self):
        data = model.data_kosong()
        model.tambah_anggota(data, "Rani")
        model.tambah_anggota(data, "Budi")
        self.assertEqual(model.daftar_anggota(data), ["Rani", "Budi"])

    def test_nama_kosong_ditolak(self):
        with self.assertRaises(model.BagiRataError):
            model.tambah_anggota(model.data_kosong(), "   ")

    def test_duplikat_tanpa_peduli_huruf_ditolak(self):
        data = model.data_kosong()
        model.tambah_anggota(data, "Rani")
        with self.assertRaises(model.BagiRataError):
            model.tambah_anggota(data, "rani")


class TestTagihan(unittest.TestCase):
    def test_tambah_tagihan_valid(self):
        data = data_contoh()
        t = model.tambah_tagihan(data, "Listrik", "Rani", 300000,
                                 ["Rani", "Budi"], "2026-11-01")
        self.assertEqual(t["nama"], "Listrik")
        self.assertEqual(t["tanggal"], "2026-11-01")
        self.assertEqual(len(model.daftar_tagihan(data)), 1)

    def test_pembayar_tidak_dikenal_ditolak(self):
        with self.assertRaises(model.BagiRataError):
            model.tambah_tagihan(data_contoh(), "X", "Dedi", 1000, ["Rani"])

    def test_peserta_tidak_dikenal_ditolak(self):
        with self.assertRaises(model.BagiRataError):
            model.tambah_tagihan(data_contoh(), "X", "Rani", 1000, ["Dedi"])

    def test_jumlah_nol_atau_negatif_ditolak(self):
        for jumlah in (0, -5000):
            with self.assertRaises(model.BagiRataError):
                model.tambah_tagihan(data_contoh(), "X", "Rani", jumlah,
                                     ["Rani"])

    def test_peserta_ganda_ditolak(self):
        with self.assertRaises(model.BagiRataError):
            model.tambah_tagihan(data_contoh(), "X", "Rani", 1000,
                                 ["Rani", "Rani"])

    def test_tanpa_peserta_ditolak(self):
        with self.assertRaises(model.BagiRataError):
            model.tambah_tagihan(data_contoh(), "X", "Rani", 1000, [])


class TestPembayaran(unittest.TestCase):
    def test_tambah_pembayaran_valid(self):
        data = data_contoh()
        p = model.tambah_pembayaran(data, "Budi", "Rani", 100000,
                                    "2026-11-05")
        self.assertEqual((p["dari"], p["ke"]), ("Budi", "Rani"))
        self.assertEqual(len(model.daftar_pembayaran(data)), 1)

    def test_bayar_ke_diri_sendiri_ditolak(self):
        with self.assertRaises(model.BagiRataError):
            model.tambah_pembayaran(data_contoh(), "Rani", "Rani", 1000)

    def test_pembayaran_anggota_tidak_dikenal_ditolak(self):
        with self.assertRaises(model.BagiRataError):
            model.tambah_pembayaran(data_contoh(), "Dedi", "Rani", 1000)


class TestHapusTagihan(unittest.TestCase):
    def test_hapus_mengembalikan_dan_menghapus(self):
        data = data_contoh()
        model.tambah_tagihan(data, "A", "Rani", 1000, ["Rani"])
        model.tambah_tagihan(data, "B", "Rani", 2000, ["Rani"])
        hapus = model.hapus_tagihan(data, 1)
        self.assertEqual(hapus["nama"], "A")
        self.assertEqual([t["nama"] for t in model.daftar_tagihan(data)],
                         ["B"])

    def test_nomor_di_luar_jangkauan_ditolak(self):
        data = data_contoh()
        with self.assertRaises(model.BagiRataError):
            model.hapus_tagihan(data, 1)
        model.tambah_tagihan(data, "A", "Rani", 1000, ["Rani"])
        with self.assertRaises(model.BagiRataError):
            model.hapus_tagihan(data, 2)
        with self.assertRaises(model.BagiRataError):
            model.hapus_tagihan(data, 0)


class TestSimpanMuat(unittest.TestCase):
    def test_roundtrip_json(self):
        data = data_contoh()
        model.tambah_tagihan(data, "Listrik", "Rani", 300000,
                             ["Rani", "Budi"], "2026-11-01")
        with tempfile.TemporaryDirectory() as d:
            path = os.path.join(d, "data.json")
            model.simpan(path, data)
            with open(path, encoding="utf-8") as f:
                mentah = json.load(f)
            self.assertEqual(mentah["anggota"], ["Rani", "Budi", "Sinta"])
            self.assertEqual(model.muat(path), data)

    def test_file_belum_ada_kembalikan_data_kosong(self):
        with tempfile.TemporaryDirectory() as d:
            self.assertEqual(
                model.muat(os.path.join(d, "belum-ada.json")),
                model.data_kosong(),
            )


if __name__ == "__main__":
    unittest.main()
