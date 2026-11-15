# -*- coding: utf-8 -*-
"""
thong_ke.py - Chức năng THỐNG KÊ THƯ VIỆN.

Hàm tinh_thong_ke() chỉ tính toán và trả về một dictionary kết quả (dễ kiểm thử),
các hàm in_... chịu trách nhiệm hiển thị.
Quy ước:
  - "Đang mượn (còn hạn)": phiếu chưa trả và chưa quá hạn.
  - "Quá hạn": phiếu chưa trả và đã quá hạn tính đến hôm nay.
  - "Danh sách sách đang được mượn": mọi phiếu chưa trả (gồm cả còn hạn và quá hạn).
"""

from tien_ich import (
    in_tieu_de, in_duong_ke, in_bang, nhap_lua_chon, tam_dung, dinh_dang_tien,
    cap_nhat_trang_thai_phieu, thong_bao_loi, thong_bao_canh_bao, thong_bao_thanh_cong,
    TT_DANG_MUON, TT_DA_TRA, TT_QUA_HAN,
)
from quan_ly_muon_tra import hien_thi_ds_phieu


def tinh_thong_ke(du_lieu):
    """Tính toàn bộ số liệu thống kê và trả về dictionary."""
    ds_sach = du_lieu["sach"]
    ds_phieu = du_lieu["phieu"]
    cap_nhat_trang_thai_phieu(ds_phieu)          # Tính lại quá hạn theo ngày hôm nay

    tk = {}
    tk["tong_dau_sach"] = len(ds_sach)
    tk["tong_so_luong"] = 0
    tk["tong_con_lai"] = 0
    for sach in ds_sach:
        tk["tong_so_luong"] += sach["tong_so"]
        tk["tong_con_lai"] += sach["con_lai"]
    tk["tong_doc_gia"] = len(du_lieu["doc_gia"])
    tk["tong_phieu"] = len(ds_phieu)

    tk["so_dang_muon"] = 0
    tk["so_da_tra"] = 0
    tk["so_qua_han"] = 0
    tk["tong_tien_phat"] = 0
    tk["ds_dang_muon"] = []     # Mọi phiếu chưa trả
    tk["ds_qua_han"] = []       # Phiếu chưa trả và đã quá hạn
    for phieu in ds_phieu:
        tk["tong_tien_phat"] += phieu["tien_phat"]
        if phieu["trang_thai"] == TT_DANG_MUON:
            tk["so_dang_muon"] += 1
            tk["ds_dang_muon"].append(phieu)
        elif phieu["trang_thai"] == TT_QUA_HAN:
            tk["so_qua_han"] += 1
            tk["ds_dang_muon"].append(phieu)
            tk["ds_qua_han"].append(phieu)
        elif phieu["trang_thai"] == TT_DA_TRA:
            tk["so_da_tra"] += 1

    # Sách được mượn nhiều nhất / ít nhất (có thể nhiều sách bằng nhau)
    tk["sach_nhieu_nhat"] = []
    tk["sach_it_nhat"] = []
    if len(ds_sach) > 0:
        luot_max = ds_sach[0]["luot_muon"]
        luot_min = ds_sach[0]["luot_muon"]
        for sach in ds_sach:
            if sach["luot_muon"] > luot_max:
                luot_max = sach["luot_muon"]
            if sach["luot_muon"] < luot_min:
                luot_min = sach["luot_muon"]
        for sach in ds_sach:
            if sach["luot_muon"] == luot_max:
                tk["sach_nhieu_nhat"].append(sach)
            if sach["luot_muon"] == luot_min:
                tk["sach_it_nhat"].append(sach)
    return tk


def in_thong_ke_tong_quan(tk):
    in_tieu_de("THỐNG KÊ TỔNG QUAN")
    cac_hang = [
        ["Tổng số đầu sách", tk["tong_dau_sach"]],
        ["Tổng số lượng sách trong thư viện", tk["tong_so_luong"]],
        ["Số lượng sách hiện còn trong kho", tk["tong_con_lai"]],
        ["Tổng số độc giả", tk["tong_doc_gia"]],
        ["Tổng số phiếu mượn", tk["tong_phieu"]],
        ["Số phiếu đang mượn (còn hạn)", tk["so_dang_muon"]],
        ["Số phiếu đã trả", tk["so_da_tra"]],
        ["Số phiếu quá hạn (chưa trả)", tk["so_qua_han"]],
        ["Tổng tiền phạt (VNĐ)", dinh_dang_tien(tk["tong_tien_phat"])],
    ]
    in_bang(["Chỉ tiêu", "Giá trị"], cac_hang, cot_can_phai=(1,))


def in_sach_dang_muon(tk, du_lieu):
    in_tieu_de("DANH SÁCH SÁCH ĐANG ĐƯỢC MƯỢN")
    if len(tk["ds_dang_muon"]) == 0:
        thong_bao_thanh_cong("Hiện không có sách nào đang được mượn.")
    else:
        hien_thi_ds_phieu(tk["ds_dang_muon"], du_lieu["sach"])


def in_sach_qua_han(tk, du_lieu):
    in_tieu_de("DANH SÁCH SÁCH ĐÃ QUÁ HẠN")
    if len(tk["ds_qua_han"]) == 0:
        thong_bao_thanh_cong("Hiện không có sách nào quá hạn.")
    else:
        hien_thi_ds_phieu(tk["ds_qua_han"], du_lieu["sach"])


def in_ds_muon_nhieu_it(tk):
    in_tieu_de("SÁCH ĐƯỢC MƯỢN NHIỀU NHẤT / ÍT NHẤT")
    if tk["tong_dau_sach"] == 0:
        thong_bao_canh_bao("Chưa có sách nào trong thư viện.")
        return
    luot_max = tk["sach_nhieu_nhat"][0]["luot_muon"]
    luot_min = tk["sach_it_nhat"][0]["luot_muon"]
    if luot_max == 0:
        thong_bao_canh_bao("Chưa có lượt mượn nào, chưa thể xác định sách mượn nhiều nhất.")
    else:
        print(f"Sách được mượn NHIỀU NHẤT ({luot_max} lượt):")
        for sach in tk["sach_nhieu_nhat"]:
            print(f"  - {sach['ma_sach']}: {sach['ten_sach']} ({sach['tac_gia']})")
    print()
    print(f"Sách được mượn ÍT NHẤT ({luot_min} lượt):")
    for sach in tk["sach_it_nhat"]:
        print(f"  - {sach['ma_sach']}: {sach['ten_sach']} ({sach['tac_gia']})")


def thong_ke_day_du(du_lieu):
    """In toàn bộ báo cáo thống kê."""
    tk = tinh_thong_ke(du_lieu)
    if tk["tong_dau_sach"] == 0 and tk["tong_doc_gia"] == 0 and tk["tong_phieu"] == 0:
        in_tieu_de("THỐNG KÊ THƯ VIỆN")
        thong_bao_canh_bao("Chưa có dữ liệu để thống kê. Hãy thêm sách, độc giả hoặc đọc dữ liệu.")
        return
    in_thong_ke_tong_quan(tk)
    in_sach_dang_muon(tk, du_lieu)
    in_sach_qua_han(tk, du_lieu)
    in_ds_muon_nhieu_it(tk)


def menu_thong_ke(du_lieu):
    """Menu con của chức năng thống kê."""
    while True:
        in_tieu_de("THỐNG KÊ THƯ VIỆN")
        print("1. Báo cáo thống kê đầy đủ")
        print("2. Thống kê tổng quan")
        print("3. Danh sách sách đang được mượn")
        print("4. Danh sách sách đã quá hạn")
        print("5. Sách được mượn nhiều nhất / ít nhất")
        print("0. Quay lại menu chính")
        in_duong_ke()
        lua_chon = nhap_lua_chon()
        if lua_chon == "0":
            break
        if lua_chon not in ("1", "2", "3", "4", "5"):
            thong_bao_loi("Lựa chọn không hợp lệ. Vui lòng chọn lại.")
            continue
        if lua_chon == "1":
            thong_ke_day_du(du_lieu)
        else:
            tk = tinh_thong_ke(du_lieu)
            if tk["tong_dau_sach"] == 0 and tk["tong_doc_gia"] == 0 and tk["tong_phieu"] == 0:
                thong_bao_canh_bao("Chưa có dữ liệu để thống kê.")
            elif lua_chon == "2":
                in_thong_ke_tong_quan(tk)
            elif lua_chon == "3":
                in_sach_dang_muon(tk, du_lieu)
            elif lua_chon == "4":
                in_sach_qua_han(tk, du_lieu)
            elif lua_chon == "5":
                in_ds_muon_nhieu_it(tk)
        tam_dung()
