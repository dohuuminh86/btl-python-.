# -*- coding: utf-8 -*-
"""
quan_ly_muon_tra.py - Chức năng QUẢN LÝ MƯỢN SÁCH và QUẢN LÝ TRẢ SÁCH.

Mỗi phiếu mượn là một dictionary:
  {"ma_phieu", "ma_sach", "ma_doc_gia", "ho_ten", "ngay_muon", "han_tra",
   "ngay_tra" (None nếu chưa trả), "trang_thai", "so_ngay_qua_han", "tien_phat"}
Mỗi phiếu quản lý đúng một cuốn sách.
"""

from datetime import date, timedelta

from tien_ich import (
    in_tieu_de, in_duong_ke, in_bang, nhap_lua_chon, nhap_ma, nhap_ngay, xac_nhan, tam_dung,
    dinh_dang_ngay, dinh_dang_tien, cap_nhat_trang_thai_phieu, tinh_so_ngay_qua_han,
    tinh_tien_phat, tim_ban_ghi_theo_ma, thong_bao_thanh_cong, thong_bao_loi,
    thong_bao_canh_bao, thong_bao_thong_tin, SO_NGAY_MUON_MAC_DINH,
    TT_DANG_MUON, TT_DA_TRA, TT_QUA_HAN,
)
from quan_ly_sach import tim_sach_theo_ma, hien_thi_ds_sach
from quan_ly_doc_gia import tim_doc_gia_theo_ma
import xu_ly_file


# ----------------------------------------------------------------------
# CÁC HÀM HỖ TRỢ
# ----------------------------------------------------------------------
def tim_phieu_theo_ma(ds_phieu, ma_phieu):
    """Trả về dictionary phiếu có mã tương ứng, không có thì trả về None."""
    return tim_ban_ghi_theo_ma(ds_phieu, "ma_phieu", ma_phieu)


def tao_ma_phieu_moi(ds_phieu):
    """
    Tự động tạo mã phiếu duy nhất dạng PM001, PM002, ...
    Lấy số lớn nhất đang có cộng thêm 1, rồi kiểm tra lại để chắc chắn không trùng.
    """
    so_lon_nhat = 0
    for phieu in ds_phieu:
        ma = phieu["ma_phieu"].upper()
        if ma.startswith("PM") and ma[2:].isdigit():
            if int(ma[2:]) > so_lon_nhat:
                so_lon_nhat = int(ma[2:])
    so_moi = so_lon_nhat + 1
    while True:
        ma_moi = f"PM{so_moi:03d}"
        if tim_phieu_theo_ma(ds_phieu, ma_moi) is None:
            return ma_moi
        so_moi += 1


def lay_ten_sach(ds_sach, ma_sach):
    """Lấy tên sách theo mã (phòng khi sách đã bị xóa khỏi danh sách)."""
    sach = tim_sach_theo_ma(ds_sach, ma_sach)
    if sach is None:
        return "(sách đã bị xóa)"
    return sach["ten_sach"]


def hien_thi_ds_phieu(ds_phieu, ds_sach):
    """In danh sách phiếu mượn dạng bảng."""
    if len(ds_phieu) == 0:
        thong_bao_canh_bao("Không có phiếu mượn nào để hiển thị.")
        return
    cac_hang = []
    for p in ds_phieu:
        ngay_tra = dinh_dang_ngay(p["ngay_tra"])
        if ngay_tra == "":
            ngay_tra = "-"
        cac_hang.append([p["ma_phieu"], p["ma_sach"], lay_ten_sach(ds_sach, p["ma_sach"]),
                         p["ma_doc_gia"], p["ho_ten"], dinh_dang_ngay(p["ngay_muon"]),
                         dinh_dang_ngay(p["han_tra"]), ngay_tra, p["trang_thai"],
                         p["so_ngay_qua_han"], dinh_dang_tien(p["tien_phat"])])
    in_bang(["Mã phiếu", "Mã sách", "Tên sách", "Mã ĐG", "Họ tên", "Ngày mượn",
             "Hạn trả", "Ngày trả", "Trạng thái", "Quá hạn", "Tiền phạt"],
            cac_hang, cot_can_phai=(9, 10), cot_toi_da={2: 20, 4: 16})
    print(f"Tổng cộng: {len(ds_phieu)} phiếu mượn.  (Quá hạn: số ngày | Tiền phạt: VNĐ)")


def in_thong_tin_phieu(phieu, ds_sach):
    """In chi tiết một phiếu mượn."""
    ngay_tra = dinh_dang_ngay(phieu["ngay_tra"])
    if ngay_tra == "":
        ngay_tra = "(chưa trả)"
    in_duong_ke()
    print(f"Mã phiếu mượn     : {phieu['ma_phieu']}")
    print(f"Sách              : {phieu['ma_sach']} - {lay_ten_sach(ds_sach, phieu['ma_sach'])}")
    print(f"Độc giả           : {phieu['ma_doc_gia']} - {phieu['ho_ten']}")
    print(f"Ngày mượn         : {dinh_dang_ngay(phieu['ngay_muon'])}")
    print(f"Hạn trả           : {dinh_dang_ngay(phieu['han_tra'])}")
    print(f"Ngày trả thực tế  : {ngay_tra}")
    print(f"Trạng thái        : {phieu['trang_thai']}")
    if phieu["ngay_tra"] is None:
        print(f"Số ngày quá hạn   : {phieu['so_ngay_qua_han']} (tính đến hôm nay)")
        print(f"Tiền phạt tạm tính: {dinh_dang_tien(phieu['tien_phat'])} VNĐ")
    else:
        print(f"Số ngày quá hạn   : {phieu['so_ngay_qua_han']}")
        print(f"Tiền phạt         : {dinh_dang_tien(phieu['tien_phat'])} VNĐ")
    in_duong_ke()


# ----------------------------------------------------------------------
# QUẢN LÝ MƯỢN SÁCH
# ----------------------------------------------------------------------
def tao_phieu_muon(du_lieu):
    """Tạo phiếu mượn mới và cập nhật số lượng sách."""
    in_tieu_de("TẠO PHIẾU MƯỢN MỚI")
    cap_nhat_trang_thai_phieu(du_lieu["phieu"])
    print("(Nhập 0 ở ô Mã sách / Mã độc giả để hủy)")

    # Bước 1: chọn sách theo mã (phải tồn tại và còn sách)
    while True:
        ma_sach = nhap_ma("Mã sách cần mượn: ")
        if ma_sach is None:
            thong_bao_thong_tin("Đã hủy tạo phiếu mượn.")
            return
        sach = tim_sach_theo_ma(du_lieu["sach"], ma_sach)
        if sach is None:
            thong_bao_loi(f"Mã sách '{ma_sach}' không tồn tại. Vui lòng nhập lại.")
            continue
        print(f"  -> Tên sách: {sach['ten_sach']} | Tác giả: {sach['tac_gia']} "
              f"| Còn lại: {sach['con_lai']}/{sach['tong_so']}")
        if sach["con_lai"] <= 0:
            thong_bao_loi("Sách này đã hết (số lượng còn lại = 0), không thể cho mượn. "
                          "Vui lòng chọn sách khác.")
            continue
        break

    # Bước 2: chọn độc giả theo mã (phải tồn tại)
    while True:
        ma_doc_gia = nhap_ma("Mã độc giả: ")
        if ma_doc_gia is None:
            thong_bao_thong_tin("Đã hủy tạo phiếu mượn.")
            return
        doc_gia = tim_doc_gia_theo_ma(du_lieu["doc_gia"], ma_doc_gia)
        if doc_gia is None:
            thong_bao_loi(f"Mã độc giả '{ma_doc_gia}' không tồn tại. Vui lòng nhập lại.")
            continue
        print(f"  -> Họ tên độc giả: {doc_gia['ho_ten']}")
        break

    # Bước 3: nhập ngày mượn và hạn trả (hạn trả không được trước ngày mượn)
    hom_nay = date.today()
    ngay_muon = nhap_ngay(
        f"Ngày mượn (dd/mm/yyyy) [Enter = hôm nay {dinh_dang_ngay(hom_nay)}]: ", mac_dinh=hom_nay)
    han_tra_mac_dinh = ngay_muon + timedelta(days=SO_NGAY_MUON_MAC_DINH)
    while True:
        han_tra = nhap_ngay(
            f"Hạn trả (dd/mm/yyyy) [Enter = {dinh_dang_ngay(han_tra_mac_dinh)}]: ",
            mac_dinh=han_tra_mac_dinh)
        if han_tra < ngay_muon:
            thong_bao_loi("Hạn trả không được trước ngày mượn. Vui lòng nhập lại.")
            continue
        break

    ma_phieu = tao_ma_phieu_moi(du_lieu["phieu"])
    print()
    print(f"Mã phiếu mượn mới : {ma_phieu}")
    print(f"Sách              : {sach['ma_sach']} - {sach['ten_sach']}")
    print(f"Độc giả           : {doc_gia['ma_doc_gia']} - {doc_gia['ho_ten']}")
    print(f"Ngày mượn / Hạn   : {dinh_dang_ngay(ngay_muon)} / {dinh_dang_ngay(han_tra)}")
    if not xac_nhan("Xác nhận tạo phiếu mượn?"):
        thong_bao_thong_tin("Đã hủy, dữ liệu không thay đổi.")
        return

    phieu_moi = {"ma_phieu": ma_phieu, "ma_sach": sach["ma_sach"],
                 "ma_doc_gia": doc_gia["ma_doc_gia"], "ho_ten": doc_gia["ho_ten"],
                 "ngay_muon": ngay_muon, "han_tra": han_tra, "ngay_tra": None,
                 "trang_thai": TT_DANG_MUON, "so_ngay_qua_han": 0, "tien_phat": 0}
    du_lieu["phieu"].append(phieu_moi)
    sach["con_lai"] = sach["con_lai"] - 1          # Giảm số lượng còn lại đi 1
    sach["luot_muon"] = sach["luot_muon"] + 1      # Tăng số lượt mượn lên 1
    cap_nhat_trang_thai_phieu(du_lieu["phieu"])
    thong_bao_thanh_cong(f"Đã tạo phiếu mượn {ma_phieu}. Sách '{sach['ten_sach']}' "
                         f"còn lại {sach['con_lai']} cuốn.")
    xu_ly_file.tu_dong_luu(du_lieu)


def menu_muon_sach(du_lieu):
    """Menu con của chức năng quản lý mượn sách."""
    while True:
        in_tieu_de("QUẢN LÝ MƯỢN SÁCH")
        print("1. Tạo phiếu mượn mới")
        print("2. Hiển thị tất cả phiếu mượn")
        print("3. Kiểm tra phiếu quá hạn (tính theo ngày hôm nay)")
        print("0. Quay lại menu chính")
        in_duong_ke()
        lua_chon = nhap_lua_chon()
        if lua_chon == "1":
            tao_phieu_muon(du_lieu)
        elif lua_chon == "2":
            in_tieu_de("DANH SÁCH PHIẾU MƯỢN")
            cap_nhat_trang_thai_phieu(du_lieu["phieu"])
            hien_thi_ds_phieu(du_lieu["phieu"], du_lieu["sach"])
        elif lua_chon == "3":
            in_tieu_de("PHIẾU MƯỢN QUÁ HẠN")
            cap_nhat_trang_thai_phieu(du_lieu["phieu"])
            ds_qua_han = []
            for p in du_lieu["phieu"]:
                if p["trang_thai"] == TT_QUA_HAN:
                    ds_qua_han.append(p)
            if len(ds_qua_han) == 0:
                thong_bao_thanh_cong("Hiện không có phiếu mượn nào quá hạn.")
            else:
                hien_thi_ds_phieu(ds_qua_han, du_lieu["sach"])
        elif lua_chon == "0":
            break
        else:
            thong_bao_loi("Lựa chọn không hợp lệ. Vui lòng chọn lại.")
            continue
        tam_dung()


# ----------------------------------------------------------------------
# QUẢN LÝ TRẢ SÁCH
# ----------------------------------------------------------------------
def tra_sach(du_lieu):
    """Trả sách: tính quá hạn, tiền phạt, cập nhật phiếu và số lượng sách."""
    in_tieu_de("TRẢ SÁCH")
    cap_nhat_trang_thai_phieu(du_lieu["phieu"])
    print("(Nhập 0 ở ô Mã phiếu để hủy)")

    # Bước 1: tìm phiếu (phải tồn tại và chưa được trả)
    while True:
        ma_phieu = nhap_ma("Mã phiếu mượn: ")
        if ma_phieu is None:
            thong_bao_thong_tin("Đã hủy trả sách.")
            return
        phieu = tim_phieu_theo_ma(du_lieu["phieu"], ma_phieu)
        if phieu is None:
            thong_bao_loi(f"Phiếu mượn '{ma_phieu}' không tồn tại. Vui lòng nhập lại.")
            continue
        in_thong_tin_phieu(phieu, du_lieu["sach"])
        if phieu["ngay_tra"] is not None:
            thong_bao_loi(f"Phiếu {phieu['ma_phieu']} đã được trả vào ngày "
                          f"{dinh_dang_ngay(phieu['ngay_tra'])}, không thể trả lần nữa.")
            continue
        break

    # Bước 2: nhập ngày trả thực tế (không được trước ngày mượn)
    hom_nay = date.today()
    while True:
        ngay_tra = nhap_ngay(
            f"Ngày trả thực tế (dd/mm/yyyy) [Enter = hôm nay {dinh_dang_ngay(hom_nay)}]: ",
            mac_dinh=hom_nay)
        if ngay_tra < phieu["ngay_muon"]:
            thong_bao_loi("Ngày trả không được trước ngày mượn "
                          f"({dinh_dang_ngay(phieu['ngay_muon'])}). Vui lòng nhập lại.")
            continue
        break

    # Bước 3: tính số ngày quá hạn và tiền phạt, cho người quản lý xem trước khi xác nhận
    so_ngay_qua_han = tinh_so_ngay_qua_han(phieu["han_tra"], ngay_tra)
    tien_phat = tinh_tien_phat(so_ngay_qua_han)
    print(f"Số ngày quá hạn : {so_ngay_qua_han} ngày")
    print(f"Tiền phạt       : {dinh_dang_tien(tien_phat)} VNĐ "
          f"({so_ngay_qua_han} ngày x {dinh_dang_tien(5000)} VNĐ)")
    if not xac_nhan("Xác nhận trả sách?"):
        thong_bao_thong_tin("Đã hủy, dữ liệu không thay đổi.")
        return

    # Bước 4: cập nhật phiếu và cộng lại số lượng sách còn lại
    phieu["ngay_tra"] = ngay_tra
    phieu["trang_thai"] = TT_DA_TRA
    phieu["so_ngay_qua_han"] = so_ngay_qua_han
    phieu["tien_phat"] = tien_phat
    sach = tim_sach_theo_ma(du_lieu["sach"], phieu["ma_sach"])
    if sach is not None and sach["con_lai"] < sach["tong_so"]:
        sach["con_lai"] = sach["con_lai"] + 1      # Không để còn lại vượt quá tổng
    cap_nhat_trang_thai_phieu(du_lieu["phieu"])
    thong_bao_thanh_cong(f"Đã ghi nhận trả sách cho phiếu {phieu['ma_phieu']}. "
                         f"Tiền phạt: {dinh_dang_tien(tien_phat)} VNĐ.")
    xu_ly_file.tu_dong_luu(du_lieu)


def xem_thong_tin_phieu(du_lieu):
    """Xem thông tin một phiếu theo mã, kèm số ngày quá hạn và tiền phạt."""
    in_tieu_de("XEM THÔNG TIN PHIẾU MƯỢN")
    cap_nhat_trang_thai_phieu(du_lieu["phieu"])
    ma_phieu = nhap_ma("Nhập mã phiếu mượn (0 để hủy): ")
    if ma_phieu is None:
        return
    phieu = tim_phieu_theo_ma(du_lieu["phieu"], ma_phieu)
    if phieu is None:
        thong_bao_loi(f"Phiếu mượn '{ma_phieu}' không tồn tại.")
        return
    in_thong_tin_phieu(phieu, du_lieu["sach"])


def menu_tra_sach(du_lieu):
    """Menu con của chức năng quản lý trả sách."""
    while True:
        in_tieu_de("QUẢN LÝ TRẢ SÁCH")
        print("1. Trả sách")
        print("2. Xem thông tin phiếu mượn và tiền phạt")
        print("3. Danh sách phiếu chưa trả")
        print("4. Danh sách phiếu đã trả")
        print("0. Quay lại menu chính")
        in_duong_ke()
        lua_chon = nhap_lua_chon()
        if lua_chon == "1":
            tra_sach(du_lieu)
        elif lua_chon == "2":
            xem_thong_tin_phieu(du_lieu)
        elif lua_chon == "3" or lua_chon == "4":
            cap_nhat_trang_thai_phieu(du_lieu["phieu"])
            ket_qua = []
            for p in du_lieu["phieu"]:
                if lua_chon == "3" and p["ngay_tra"] is None:
                    ket_qua.append(p)
                elif lua_chon == "4" and p["ngay_tra"] is not None:
                    ket_qua.append(p)
            if lua_chon == "3":
                in_tieu_de("DANH SÁCH PHIẾU CHƯA TRẢ")
            else:
                in_tieu_de("DANH SÁCH PHIẾU ĐÃ TRẢ")
            hien_thi_ds_phieu(ket_qua, du_lieu["sach"])
        elif lua_chon == "0":
            break
        else:
            thong_bao_loi("Lựa chọn không hợp lệ. Vui lòng chọn lại.")
            continue
        tam_dung()
