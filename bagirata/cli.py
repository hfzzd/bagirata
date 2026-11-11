"""Antarmuka baris perintah (CLI) BagiRata.

Contoh pemakaian:
    bagirata anggota tambah "Rani"
    bagirata anggota daftar
    bagirata tagihan tambah --nama "Listrik" --pembayar Rani \\
        --jumlah 300000 --peserta Rani Budi Sinta
    bagirata tagihan daftar
"""

import argparse
import os
import sys
from datetime import datetime

from . import __version__, model
from . import export as export_mod
from . import pengingat as pengingat_mod
from . import report as report_mod
from . import settle as settle_mod
from . import split as split_mod


def _parser():
    p = argparse.ArgumentParser(
        prog="bagirata",
        description="Pembagi tagihan untuk anak kos & teman serumah.",
    )
    p.add_argument(
        "--data",
        default=os.environ.get("BAGIRATA_DATA", model.DEFAULT_DATA_FILE),
        help="File data JSON (bawaan: bagirata.json atau $BAGIRATA_DATA).",
    )
    p.add_argument("--version", action="version",
                   version=f"bagirata {__version__}")
    sub = p.add_subparsers(dest="perintah", required=True)

    anggota = sub.add_parser("anggota", help="Kelola daftar anggota.")
    anggota_sub = anggota.add_subparsers(dest="aksi", required=True)
    tambah = anggota_sub.add_parser("tambah", help="Tambah satu anggota.")
    tambah.add_argument("nama", help="Nama anggota, mis. \"Rani\".")
    anggota_sub.add_parser("daftar", help="Tampilkan semua anggota.")

    tagihan = sub.add_parser("tagihan", help="Kelola tagihan bersama.")
    tagihan_sub = tagihan.add_subparsers(dest="aksi", required=True)
    t_tambah = tagihan_sub.add_parser("tambah", help="Catat satu tagihan.")
    t_tambah.add_argument("--nama", required=True, help="Nama tagihan.")
    t_tambah.add_argument("--pembayar", required=True,
                          help="Anggota yang membayar dulu.")
    t_tambah.add_argument("--jumlah", required=True, type=int,
                          help="Jumlah tagihan dalam rupiah.")
    t_tambah.add_argument("--peserta", required=True, nargs="+",
                          help="Anggota yang ikut menanggung.")
    t_tambah.add_argument("--tanggal", default=None,
                          help="Tanggal YYYY-MM-DD (bawaan: hari ini).")
    t_tambah.add_argument("--jatuh-tempo", default=None,
                          help="Batas bayar YYYY-MM-DD (opsional, untuk "
                               "pengingat).")
    tagihan_sub.add_parser("daftar", help="Tampilkan semua tagihan.")
    t_hapus = tagihan_sub.add_parser("hapus", help="Hapus satu tagihan.")
    t_hapus.add_argument("nomor", type=int,
                         help="Nomor tagihan dari 'tagihan daftar'.")

    sub.add_parser("saldo", help="Tampilkan saldo tiap anggota.")

    bayar = sub.add_parser("bayar", help="Catat pembayaran antar anggota.")
    bayar.add_argument("--dari", required=True, help="Anggota yang membayar.")
    bayar.add_argument("--ke", required=True, help="Anggota yang menerima.")
    bayar.add_argument("--jumlah", required=True, type=int,
                       help="Jumlah pembayaran dalam rupiah.")
    bayar.add_argument("--tanggal", default=None,
                       help="Tanggal YYYY-MM-DD (bawaan: hari ini).")

    sub.add_parser("lunas",
                   help="Tampilkan transfer seminimal mungkin supaya lunas.")

    laporan = sub.add_parser("laporan", help="Tampilkan laporan bulanan.")
    laporan.add_argument("--bulan", default=None,
                         help="Bulan YYYY-MM (bawaan: bulan berjalan).")

    ekspor = sub.add_parser(
        "ekspor", help="Ekspor data ke CSV (untuk spreadsheet).")
    ekspor.add_argument("--jenis", required=True,
                        choices=["tagihan", "pembayaran", "laporan"],
                        help="Data yang diekspor.")
    ekspor.add_argument("--keluar", default=None,
                        help="File CSV tujuan (bawaan: tampilkan di layar).")
    ekspor.add_argument("--bulan", default=None,
                        help="Bulan YYYY-MM untuk jenis laporan "
                             "(bawaan: bulan berjalan).")

    pengingat = sub.add_parser(
        "pengingat", help="Ingatkan tagihan yang jatuh tempo.")
    pengingat.add_argument("--dalam", default=7, type=int,
                           help="Ingatkan tagihan yang jatuh dalam N hari "
                                "ke depan (bawaan: 7). Tagihan terlambat "
                                "selalu diingatkan.")
    return p


def _rupiah(n):
    return f"Rp{n:,}".replace(",", ".")


def main(argv=None):
    args = _parser().parse_args(argv)
    try:
        data = model.muat(args.data)
        if args.perintah == "anggota":
            if args.aksi == "tambah":
                nama = model.tambah_anggota(data, args.nama)
                model.simpan(args.data, data)
                print(f"Anggota '{nama}' ditambahkan.")
            else:
                anggota = model.daftar_anggota(data)
                if not anggota:
                    print("Belum ada anggota. Tambah dengan "
                          "'bagirata anggota tambah <nama>'.")
                for i, nama in enumerate(anggota, 1):
                    print(f"{i}. {nama}")
        elif args.perintah == "tagihan":
            if args.aksi == "tambah":
                t = model.tambah_tagihan(
                    data, args.nama, args.pembayar, args.jumlah,
                    args.peserta, args.tanggal, args.jatuh_tempo,
                )
                model.simpan(args.data, data)
                pesan = (f"Tagihan '{t['nama']}' {_rupiah(t['jumlah'])} "
                         f"dicatat, dibayar {t['pembayar']} untuk "
                         f"{len(t['peserta'])} peserta.")
                if t.get("jatuh_tempo"):
                    pesan += f" Jatuh tempo {t['jatuh_tempo']}."
                print(pesan)
            elif args.aksi == "hapus":
                t = model.hapus_tagihan(data, args.nomor)
                model.simpan(args.data, data)
                print(f"Tagihan '{t['nama']}' {_rupiah(t['jumlah'])} dihapus.")
            else:
                tagihan = model.daftar_tagihan(data)
                if not tagihan:
                    print("Belum ada tagihan.")
                for i, t in enumerate(tagihan, 1):
                    baris = (f"{i}. {t['nama']} — {_rupiah(t['jumlah'])} "
                             f"(dibayar {t['pembayar']}, {t['tanggal']})")
                    if t.get("jatuh_tempo"):
                        baris += f" — jatuh tempo {t['jatuh_tempo']}"
                    print(baris)
        elif args.perintah == "saldo":
            saldo = split_mod.hitung_saldo(data)
            if not saldo:
                print("Belum ada anggota.")
            for nama, nilai in saldo.items():
                if nilai > 0:
                    print(f"{nama}: berhak menerima {_rupiah(nilai)}")
                elif nilai < 0:
                    print(f"{nama}: berutang {_rupiah(-nilai)}")
                else:
                    print(f"{nama}: lunas")
        elif args.perintah == "bayar":
            p = model.tambah_pembayaran(
                data, args.dari, args.ke, args.jumlah, args.tanggal)
            model.simpan(args.data, data)
            print(f"Pembayaran {_rupiah(p['jumlah'])} dari {p['dari']} "
                  f"ke {p['ke']} dicatat.")
        elif args.perintah == "lunas":
            saldo = split_mod.hitung_saldo(data)
            rencana = settle_mod.rencana_pelunasan(saldo)
            if not rencana:
                print("Semua sudah lunas — tidak ada transfer yang perlu "
                      "dilakukan.")
            else:
                print("Supaya semua lunas, cukup lakukan transfer ini:")
                for dari, ke, jumlah in rencana:
                    print(f"  {dari} -> {ke}: {_rupiah(jumlah)}")
        elif args.perintah == "laporan":
            from datetime import date as _date
            bulan = args.bulan or _date.today().strftime("%Y-%m")
            try:
                datetime.strptime(bulan, "%Y-%m")
            except ValueError:
                raise model.BagiRataError(
                    f"Bulan '{bulan}' tidak valid (pakai format YYYY-MM).")
            lap = report_mod.laporan_bulanan(data, bulan)
            print(f"Laporan {lap['bulan']}: {lap['jumlah_tagihan']} tagihan, "
                  f"total {_rupiah(lap['total_tagihan'])}, "
                  f"{lap['jumlah_pembayaran']} pembayaran.")
            for nama, r in lap["per_anggota"].items():
                print(f"  {nama}: membayar tagihan {_rupiah(r['dibayar'])}, "
                      f"menanggung {_rupiah(r['ditanggung'])}, "
                      f"membayar ke teman {_rupiah(r['membayar'])}, "
                      f"menerima {_rupiah(r['menerima'])}")
            print("Saldo akhir:")
            for nama, nilai in lap["saldo_akhir"].items():
                status = (f"berhak menerima {_rupiah(nilai)}" if nilai > 0
                          else f"berutang {_rupiah(-nilai)}" if nilai < 0
                          else "lunas")
                print(f"  {nama}: {status}")
        elif args.perintah == "ekspor":
            if args.jenis == "tagihan":
                teks = export_mod.ekspor_csv_tagihan(data)
            elif args.jenis == "pembayaran":
                teks = export_mod.ekspor_csv_pembayaran(data)
            else:
                from datetime import date as _date
                bulan = args.bulan or _date.today().strftime("%Y-%m")
                try:
                    datetime.strptime(bulan, "%Y-%m")
                except ValueError:
                    raise model.BagiRataError(
                        f"Bulan '{bulan}' tidak valid "
                        "(pakai format YYYY-MM).")
                teks = export_mod.ekspor_csv_laporan(data, bulan)
            if args.keluar:
                with open(args.keluar, "w", encoding="utf-8",
                          newline="") as f:
                    f.write(teks)
                print(f"Data {args.jenis} diekspor ke {args.keluar}.")
            else:
                print(teks, end="")
        elif args.perintah == "pengingat":
            daftar = pengingat_mod.daftar_pengingat(data,
                                                    ambang_hari=args.dalam)
            if not daftar:
                print("Tidak ada tagihan yang jatuh tempo dalam "
                      f"{args.dalam} hari ke depan. Aman.")
            else:
                for p in daftar:
                    if p["sisa_hari"] < 0:
                        kapan = f"terlambat {-p['sisa_hari']} hari"
                    elif p["sisa_hari"] == 0:
                        kapan = "jatuh hari ini"
                    else:
                        kapan = f"{p['sisa_hari']} hari lagi"
                    print(f"[{p['status']}] {p['nama']} — "
                          f"{_rupiah(p['jumlah'])} (dibayar {p['pembayar']}, "
                          f"jatuh tempo {p['jatuh_tempo']}, {kapan})")
        return 0
    except model.BagiRataError as e:
        print(f"Galat: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
