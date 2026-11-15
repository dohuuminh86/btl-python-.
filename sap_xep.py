# -*- coding: utf-8 -*-
"""
sap_xep.py - Chức năng SẮP XẾP danh sách sách và phiếu mượn.

  - Sách: theo tên sách (A-Z hoặc Z-A).
  - Phiếu mượn: theo tên sách hoặc theo ngày mượn (tăng dần hoặc giảm dần).
Việc sắp xếp chỉ thay đổi thứ tự hiển thị (làm trên bản sao), không làm thay đổi dữ liệu đã lưu.
Tên được so sánh không dấu và không phân biệt hoa/thường để thứ tự A-Z gần đúng bảng chữ cái.
"""

from tien_ich import (
    in_tieu_de, in_duong_ke, nhap_lua_chon, tam_dung, khoa_so_sanh,
    cap_nhat_trang_thai_phieu, thong_bao_loi, thong_bao_thong_tin,
)
from quan_ly_sach import hien_thi_ds_sach
from quan_ly_muon_tra import hien_thi_ds_phieu, lay_ten_sach


def sap_xep_sach_theo_ten(ds_sach, tang_dan=True):
    """Trả về list sách mới đã sắp xếp theo tên sách."""
    return sorted(ds_sach, key=lambda s: khoa_so_sanh(s["ten_sach"]), reverse=not tang_dan)


def sap_xep_phieu_theo_ten_sach(ds_phieu, ds_sach, tang_dan=True):
    """Trả về list phiếu mới đã sắp xếp theo tên sách được mượn."""
    return sorted(ds_phieu,
                  key=lambda p: khoa_so_sanh(lay_ten_sach(ds_sach, p["ma_sach"])),
                  reverse=not tang_dan)


def sap_xep_phieu_theo_ngay_muon(ds_phieu, tang_dan=True):
    """Trả về list phiếu mới đã sắp xếp theo ngày mượn (cũ -> mới nếu tang_dan=True)."""
    return sorted(ds_phieu, key=lambda p: (p["ngay_muon"], p["ma_phieu"]), reverse=not tang_dan)


def hoi_chieu_sap_xep(nhan_tang, nhan_giam):
    """Hỏi tăng dần hay giảm dần. Trả về True (tăng), False (giảm) hoặc None (hủy)."""
    print(f"1. Tăng dần ({nhan_tang})")
    print(f"2. Giảm dần ({nhan_giam})")
    print("0. Quay lại")
    lua_chon = nhap_lua_chon()
    if lua_chon == "1":
        return True
    if lua_chon == "2":
        return False
    if lua_chon != "0":
        thong_bao_loi("Lựa chọn không hợp lệ.")
    return None


def menu_sap_xep(du_lieu):
    """Menu con của chức năng sắp xếp."""
    while True:
        in_tieu_de("SẮP XẾP")
        print("1. Sắp xếp danh sách sách theo tên sách")
        print("2. Sắp xếp phiếu mượn theo tên sách")
        print("3. Sắp xếp phiếu mượn theo ngày mượn")
        print("0. Quay lại menu chính")
        in_duong_ke()
        lua_chon = nhap_lua_chon()
        if lua_chon == "1":
            chieu = hoi_chieu_sap_xep("A -> Z", "Z -> A")
            if chieu is None:
                continue
            in_tieu_de("SÁCH SẮP XẾP THEO TÊN SÁCH")
            hien_thi_ds_sach(sap_xep_sach_theo_ten(du_lieu["sach"], chieu))
        elif lua_chon == "2":
            chieu = hoi_chieu_sap_xep("A -> Z", "Z -> A")
            if chieu is None:
                continue
            cap_nhat_trang_thai_phieu(du_lieu["phieu"])
            in_tieu_de("PHIẾU MƯỢN SẮP XẾP THEO TÊN SÁCH")
            hien_thi_ds_phieu(
                sap_xep_phieu_theo_ten_sach(du_lieu["phieu"], du_lieu["sach"], chieu),
                du_lieu["sach"])
        elif lua_chon == "3":
            chieu = hoi_chieu_sap_xep("cũ nhất -> mới nhất", "mới nhất -> cũ nhất")
            if chieu is None:
                continue
            cap_nhat_trang_thai_phieu(du_lieu["phieu"])
            in_tieu_de("PHIẾU MƯỢN SẮP XẾP THEO NGÀY MƯỢN")
            hien_thi_ds_phieu(sap_xep_phieu_theo_ngay_muon(du_lieu["phieu"], chieu),
                              du_lieu["sach"])
        elif lua_chon == "0":
            break
        else:
            thong_bao_loi("Lựa chọn không hợp lệ. Vui lòng chọn lại.")
            continue
        thong_bao_thong_tin("Sắp xếp chỉ thay đổi thứ tự hiển thị, dữ liệu đã lưu không bị đổi.")
        tam_dung()
