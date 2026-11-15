# -*- coding: utf-8 -*-
"""
tim_kiem.py - Chức năng TÌM KIẾM sách, độc giả, phiếu mượn.

  - Tìm theo tên / tác giả / họ tên: không phân biệt hoa thường, không phân biệt dấu,
    hỗ trợ tìm gần đúng (xem hàm khop_gan_dung trong tien_ich.py).
  - Tìm theo mã: không phân biệt hoa thường, chỉ cần mã chứa từ khóa.
  - Không có kết quả thì thông báo rõ ràng.
Các hàm tim_... trả về một list kết quả để dễ kiểm thử.
"""

from tien_ich import (
    in_tieu_de, in_duong_ke, nhap_lua_chon, nhap_chuoi, tam_dung, khop_ma, khop_gan_dung,
    khoa_so_sanh, cap_nhat_trang_thai_phieu, thong_bao_loi, thong_bao_canh_bao,
    thong_bao_thanh_cong, TT_DANG_MUON, TT_DA_TRA, TT_QUA_HAN,
)
from quan_ly_sach import hien_thi_ds_sach
from quan_ly_doc_gia import hien_thi_ds_doc_gia
from quan_ly_muon_tra import hien_thi_ds_phieu


# ----------------------------------------------------------------------
# CÁC HÀM TÌM KIẾM (trả về list kết quả)
# ----------------------------------------------------------------------
def tim_sach(ds_sach, cach_tim, tu_khoa):
    """cach_tim: 'ma' (mã sách), 'ten' (tên sách) hoặc 'tac_gia'."""
    ket_qua = []
    for sach in ds_sach:
        if cach_tim == "ma" and khop_ma(tu_khoa, sach["ma_sach"]):
            ket_qua.append(sach)
        elif cach_tim == "ten" and khop_gan_dung(tu_khoa, sach["ten_sach"]):
            ket_qua.append(sach)
        elif cach_tim == "tac_gia" and khop_gan_dung(tu_khoa, sach["tac_gia"]):
            ket_qua.append(sach)
    return ket_qua


def tim_doc_gia(ds_doc_gia, cach_tim, tu_khoa):
    """cach_tim: 'ma' (mã độc giả) hoặc 'ten' (họ tên)."""
    ket_qua = []
    for doc_gia in ds_doc_gia:
        if cach_tim == "ma" and khop_ma(tu_khoa, doc_gia["ma_doc_gia"]):
            ket_qua.append(doc_gia)
        elif cach_tim == "ten" and khop_gan_dung(tu_khoa, doc_gia["ho_ten"]):
            ket_qua.append(doc_gia)
    return ket_qua


def tim_phieu(ds_phieu, cach_tim, tu_khoa):
    """cach_tim: 'ma_phieu', 'ma_sach', 'ma_doc_gia' hoặc 'trang_thai'."""
    ket_qua = []
    for phieu in ds_phieu:
        if cach_tim == "ma_phieu" and khop_ma(tu_khoa, phieu["ma_phieu"]):
            ket_qua.append(phieu)
        elif cach_tim == "ma_sach" and khop_ma(tu_khoa, phieu["ma_sach"]):
            ket_qua.append(phieu)
        elif cach_tim == "ma_doc_gia" and khop_ma(tu_khoa, phieu["ma_doc_gia"]):
            ket_qua.append(phieu)
        elif cach_tim == "trang_thai" and khoa_so_sanh(tu_khoa) == khoa_so_sanh(phieu["trang_thai"]):
            ket_qua.append(phieu)
    return ket_qua


# ----------------------------------------------------------------------
# CÁC MENU TÌM KIẾM
# ----------------------------------------------------------------------
def menu_tim_sach(du_lieu):
    in_tieu_de("TÌM KIẾM SÁCH")
    print("1. Theo mã sách")
    print("2. Theo tên sách")
    print("3. Theo tác giả")
    print("0. Quay lại")
    in_duong_ke()
    lua_chon = nhap_lua_chon()
    if lua_chon == "0":
        return
    if lua_chon == "1":
        cach_tim = "ma"
    elif lua_chon == "2":
        cach_tim = "ten"
    elif lua_chon == "3":
        cach_tim = "tac_gia"
    else:
        thong_bao_loi("Lựa chọn không hợp lệ.")
        return
    tu_khoa = nhap_chuoi("Nhập từ khóa tìm kiếm: ")
    ket_qua = tim_sach(du_lieu["sach"], cach_tim, tu_khoa)
    if len(ket_qua) == 0:
        thong_bao_canh_bao(f"Không tìm thấy sách nào phù hợp với '{tu_khoa}'.")
    else:
        thong_bao_thanh_cong(f"Tìm thấy {len(ket_qua)} kết quả.")
        hien_thi_ds_sach(ket_qua)


def menu_tim_doc_gia(du_lieu):
    in_tieu_de("TÌM KIẾM ĐỘC GIẢ")
    print("1. Theo mã độc giả")
    print("2. Theo họ tên")
    print("0. Quay lại")
    in_duong_ke()
    lua_chon = nhap_lua_chon()
    if lua_chon == "0":
        return
    if lua_chon == "1":
        cach_tim = "ma"
    elif lua_chon == "2":
        cach_tim = "ten"
    else:
        thong_bao_loi("Lựa chọn không hợp lệ.")
        return
    tu_khoa = nhap_chuoi("Nhập từ khóa tìm kiếm: ")
    ket_qua = tim_doc_gia(du_lieu["doc_gia"], cach_tim, tu_khoa)
    if len(ket_qua) == 0:
        thong_bao_canh_bao(f"Không tìm thấy độc giả nào phù hợp với '{tu_khoa}'.")
    else:
        thong_bao_thanh_cong(f"Tìm thấy {len(ket_qua)} kết quả.")
        hien_thi_ds_doc_gia(ket_qua)


def menu_tim_phieu(du_lieu):
    in_tieu_de("TÌM KIẾM PHIẾU MƯỢN")
    cap_nhat_trang_thai_phieu(du_lieu["phieu"])
    print("1. Theo mã phiếu mượn")
    print("2. Theo mã sách")
    print("3. Theo mã độc giả")
    print("4. Theo trạng thái (Đang mượn / Đã trả / Quá hạn)")
    print("0. Quay lại")
    in_duong_ke()
    lua_chon = nhap_lua_chon()
    if lua_chon == "0":
        return
    if lua_chon == "1":
        cach_tim = "ma_phieu"
    elif lua_chon == "2":
        cach_tim = "ma_sach"
    elif lua_chon == "3":
        cach_tim = "ma_doc_gia"
    elif lua_chon == "4":
        cach_tim = "trang_thai"
    else:
        thong_bao_loi("Lựa chọn không hợp lệ.")
        return

    if cach_tim == "trang_thai":
        print(f"1. {TT_DANG_MUON}   2. {TT_DA_TRA}   3. {TT_QUA_HAN}")
        chon_tt = nhap_lua_chon("Chọn trạng thái: ")
        if chon_tt == "1":
            tu_khoa = TT_DANG_MUON
        elif chon_tt == "2":
            tu_khoa = TT_DA_TRA
        elif chon_tt == "3":
            tu_khoa = TT_QUA_HAN
        else:
            thong_bao_loi("Lựa chọn không hợp lệ.")
            return
    else:
        tu_khoa = nhap_chuoi("Nhập từ khóa tìm kiếm: ")

    ket_qua = tim_phieu(du_lieu["phieu"], cach_tim, tu_khoa)
    if len(ket_qua) == 0:
        thong_bao_canh_bao(f"Không tìm thấy phiếu mượn nào phù hợp với '{tu_khoa}'.")
    else:
        thong_bao_thanh_cong(f"Tìm thấy {len(ket_qua)} kết quả.")
        hien_thi_ds_phieu(ket_qua, du_lieu["sach"])


def menu_tim_kiem(du_lieu):
    """Menu con của chức năng tìm kiếm."""
    while True:
        in_tieu_de("TÌM KIẾM")
        print("1. Tìm kiếm sách")
        print("2. Tìm kiếm độc giả")
        print("3. Tìm kiếm phiếu mượn")
        print("0. Quay lại menu chính")
        in_duong_ke()
        lua_chon = nhap_lua_chon()
        if lua_chon == "1":
            menu_tim_sach(du_lieu)
        elif lua_chon == "2":
            menu_tim_doc_gia(du_lieu)
        elif lua_chon == "3":
            menu_tim_phieu(du_lieu)
        elif lua_chon == "0":
            break
        else:
            thong_bao_loi("Lựa chọn không hợp lệ. Vui lòng chọn lại.")
            continue
        tam_dung()
