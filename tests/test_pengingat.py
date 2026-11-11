"""Unit test jatuh tempo & pengingat BagiRata.

Model: jatuh tempo tersimpan di tagihan, tanggal tidak valid ditolak,
`perpanjang` menggeser tanggal + jatuh tempo sebulan tanpa duplikasi.
Modul pengingat: TERLAMBAT / HARI INI / N HARI LAGI, ambang hari,
tagihan tanpa jatuh tempo tidak pernah muncul, terurut jatuh tempo.
"""

import io
import os
import tempfile
import unittest
from contextlib import redirect_stdout
from datetime import date

from bagirata import model
from bagirata import pengingat as pengingat_mod
from bagirata.cli import main


def data_contoh():
    data = model.data_kosong()
    for nama in ("Rani", "Budi"):
        model.tambah_anggota(data, nama)
    return data


class TestJatuhTempoModel(unittest.TestCase):
    def test_jatuh_tempo_tersimpan(self):
        data = data_contoh()
        t = model.tambah_tagihan(data, "WiFi", "Rani", 200000,
                                 ["Rani", "Budi"], "2026-11-01",
                                 jatuh_tempo="2026-11-10")
        self.assertEqual(t["jatuh_tempo"], "2026-11-10")

    def test_tanpa_jatuh_tempo_tidak_ada_field(self):
        data = data_contoh()
        t = model.tambah_tagihan(data, "WiFi", "Rani", 200000,
                                 ["Rani", "Budi"], "2026-11-01")
        self.assertNotIn("jatuh_tempo", t)

    def test_jatuh_tempo_tidak_valid_ditolak(self):
        data = data_contoh()
        with self.assertRaises(model.BagiRataError):
            model.tambah_tagihan(data, "WiFi", "Rani", 200000,
                                 ["Rani", "Budi"], "2026-11-01",
                                 jatuh_tempo="2026-02-30")
        with self.assertRaises(model.BagiRataError):
            model.tambah_tagihan(data, "WiFi", "Rani", 200000,
                                 ["Rani", "Budi"], "2026-11-01",
                                 jatuh_tempo="10-11-2026")


class TestPerpanjangModel(unittest.TestCase):
    def setUp(self):
        self.data = data_contoh()
        model.tambah_tagihan(self.data, "WiFi", "Rani", 200000,
                             ["Rani", "Budi"], "2026-10-05",
                             jatuh_tempo="2026-10-10", berulang="bulanan")
        model.tambah_tagihan(self.data, "Galon", "Budi", 25000,
                             ["Rani", "Budi"], "2026-10-07")

    def test_salin_tanggal_dan_jatuh_tempo_digeser_sebulan(self):
        baru = model.perpanjang_tagihan_berulang(self.data, "2026-11")
        self.assertEqual(len(baru), 1)
        self.assertEqual(baru[0]["nama"], "WiFi")
        self.assertEqual(baru[0]["tanggal"], "2026-11-05")
        self.assertEqual(baru[0]["jatuh_tempo"], "2026-11-10")
        self.assertEqual(baru[0]["berulang"], "bulanan")
        self.assertEqual(baru[0]["jumlah"], 200000)
        self.assertEqual(baru[0]["peserta"], ["Rani", "Budi"])

    def test_tidak_berulang_tidak_disalin(self):
        model.perpanjang_tagihan_berulang(self.data, "2026-11")
        nama = [t["nama"] for t in model.daftar_tagihan(self.data)]
        self.assertEqual(nama.count("Galon"), 1)

    def test_perpanjang_kedua_tidak_menduplikasi(self):
        model.perpanjang_tagihan_berulang(self.data, "2026-11")
        kedua = model.perpanjang_tagihan_berulang(self.data, "2026-11")
        self.assertEqual(kedua, [])
        nama = [t["nama"] for t in model.daftar_tagihan(self.data)]
        self.assertEqual(nama.count("WiFi"), 2)

    def test_tanggal_31_dijepit_ke_hari_terakhir_bulan(self):
        data = data_contoh()
        model.tambah_tagihan(data, "Sewa", "Rani", 1000000,
                             ["Rani", "Budi"], "2026-01-31",
                             jatuh_tempo="2026-01-31", berulang="bulanan")
        baru = model.perpanjang_tagihan_berulang(data, "2026-02")
        self.assertEqual(baru[0]["tanggal"], "2026-02-28")
        self.assertEqual(baru[0]["jatuh_tempo"], "2026-02-28")

    def test_bulan_tidak_valid_ditolak(self):
        with self.assertRaises(model.BagiRataError):
            model.perpanjang_tagihan_berulang(self.data, "2026-13")
        with self.assertRaises(model.BagiRataError):
            model.perpanjang_tagihan_berulang(self.data, "Nov-2026")


class TestPengingat(unittest.TestCase):
    HARI_INI = date(2026, 11, 11)

    def setUp(self):
        self.data = data_contoh()
        model.tambah_tagihan(self.data, "Terlambat", "Rani", 100000,
                             ["Rani", "Budi"], "2026-11-01",
                             jatuh_tempo="2026-11-05")
        model.tambah_tagihan(self.data, "HariIni", "Rani", 200000,
                             ["Rani", "Budi"], "2026-11-02",
                             jatuh_tempo="2026-11-11")
        model.tambah_tagihan(self.data, "TigaHari", "Budi", 50000,
                             ["Rani", "Budi"], "2026-11-03",
                             jatuh_tempo="2026-11-14")
        model.tambah_tagihan(self.data, "SembilanHari", "Budi", 75000,
                             ["Rani", "Budi"], "2026-11-04",
                             jatuh_tempo="2026-11-20")
        model.tambah_tagihan(self.data, "TanpaJatuhTempo", "Rani", 30000,
                             ["Rani", "Budi"], "2026-11-05")

    def test_status_terlambat_hari_ini_dan_n_hari_lagi(self):
        daftar = pengingat_mod.daftar_pengingat(self.data,
                                                hari_ini=self.HARI_INI,
                                                ambang_hari=30)
        per_nama = {p["nama"]: p for p in daftar}
        self.assertEqual(per_nama["Terlambat"]["status"], "TERLAMBAT")
        self.assertEqual(per_nama["Terlambat"]["sisa_hari"], -6)
        self.assertEqual(per_nama["HariIni"]["status"], "HARI INI")
        self.assertEqual(per_nama["HariIni"]["sisa_hari"], 0)
        self.assertEqual(per_nama["TigaHari"]["status"], "3 HARI LAGI")
        self.assertEqual(per_nama["TigaHari"]["sisa_hari"], 3)
        self.assertEqual(per_nama["SembilanHari"]["status"], "9 HARI LAGI")
        self.assertEqual(per_nama["SembilanHari"]["sisa_hari"], 9)

    def test_ambang_menyaring_yang_masih_jauh(self):
        # Ambang bawaan 7: yang jatuh 9 hari lagi tidak muncul.
        daftar = pengingat_mod.daftar_pengingat(self.data,
                                                hari_ini=self.HARI_INI,
                                                ambang_hari=7)
        nama = [p["nama"] for p in daftar]
        self.assertIn("Terlambat", nama)
        self.assertIn("HariIni", nama)
        self.assertIn("TigaHari", nama)
        self.assertNotIn("SembilanHari", nama)

    def test_terlambat_selalu_muncul_walau_ambang_nol(self):
        daftar = pengingat_mod.daftar_pengingat(self.data,
                                                hari_ini=self.HARI_INI,
                                                ambang_hari=0)
        nama = [p["nama"] for p in daftar]
        self.assertEqual(nama, ["Terlambat", "HariIni"])

    def test_tanpa_jatuh_tempo_tidak_pernah_muncul(self):
        daftar = pengingat_mod.daftar_pengingat(self.data,
                                                hari_ini=self.HARI_INI,
                                                ambang_hari=30)
        nama = [p["nama"] for p in daftar]
        self.assertNotIn("TanpaJatuhTempo", nama)
        self.assertEqual(len(daftar), 4)

    def test_terurut_berdasarkan_jatuh_tempo(self):
        daftar = pengingat_mod.daftar_pengingat(self.data,
                                                hari_ini=self.HARI_INI,
                                                ambang_hari=30)
        jatuh = [p["jatuh_tempo"] for p in daftar]
        self.assertEqual(jatuh, sorted(jatuh))


class TestPerpanjangCLI(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.data = os.path.join(self.tmp.name, "data.json")

    def tearDown(self):
        self.tmp.cleanup()

    def jalan(self, *args):
        out = io.StringIO()
        with redirect_stdout(out):
            kode = main(["--data", self.data, *args])
        return kode, out.getvalue()

    def test_perpanjang_lewat_cli(self):
        self.jalan("anggota", "tambah", "Rani")
        self.jalan("anggota", "tambah", "Budi")
        kode, _ = self.jalan("tagihan", "tambah", "--nama", "WiFi",
                             "--pembayar", "Rani", "--jumlah", "200000",
                             "--peserta", "Rani", "Budi",
                             "--tanggal", "2026-10-05",
                             "--jatuh-tempo", "2026-10-10",
                             "--berulang", "bulanan")
        self.assertEqual(kode, 0)
        kode, out = self.jalan("tagihan", "perpanjang", "--bulan", "2026-11")
        self.assertEqual(kode, 0)
        self.assertIn("1 tagihan berulang diperpanjang ke 2026-11", out)
        self.assertIn("2026-11-05", out)
        self.assertIn("jatuh tempo 2026-11-10", out)
        kode, out = self.jalan("tagihan", "perpanjang", "--bulan", "2026-11")
        self.assertIn("Tidak ada tagihan berulang", out)


if __name__ == "__main__":
    unittest.main()
