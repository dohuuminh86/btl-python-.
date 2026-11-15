# -*- coding: utf-8 -*-
"""
quan_ly_sach.py - Chức năng QUẢN LÝ SÁCH.

Mỗi cuốn sách là một dictionary:
  {"ma_sach", "ten_sach", "tac_gia", "the_loai", "tong_so", "con_lai", "luot_muon"}
Danh sách sách là một list các dictionary đó: du_lieu["sach"].
"""

from tien_ich import (
    in_tieu_de, in_duong_ke, in_bang, nhap_lua_chon, nhap_chuoi, nhap_ma, nhap_so_nguyen,
    xac_nhan, tam_dung, thong_bao_thanh_cong, thong_bao_loi, thong_bao_canh_bao,
    thong_bao_thong_tin, tim_ban_ghi_theo_ma, dem_phieu_chua_tra_theo,
)
import xu_ly_file


def tim_sach_theo_ma(ds_sach, ma_sach):
    """Trả về dictionary sách có mã tương ứng, không có thì trả về None."""
    return tim_ban_ghi_theo_ma(ds_sach, "ma_sach", ma_sach)


def kiem_tra_trung_ma_sach(ds_sach, ma_sach):
    """True nếu mã sách đã tồn tại."""
    return tim_sach_theo_ma(ds_sach, ma_sach) is not None


def hien_thi_ds_sach(ds_sach):
    """In danh sách sách (hoặc một danh sách kết quả tìm kiếm/sắp xếp) dạng bảng."""
    if len(ds_sach) == 0:
        thong_bao_canh_bao("Chưa có sách nào để hiển thị.")
        return
    cac_hang = []
    for s in ds_sach:
        cac_hang.append([s["ma_sach"], s["ten_sach"], s["tac_gia"], s["the_loai"],
                         s["tong_so"], s["con_lai"], s["luot_muon"]])
    in_bang(["Mã sách", "Tên sách", "Tác giả", "Thể loại", "Tổng", "Còn lại", "Lượt mượn"],
            cac_hang, cot_can_phai=(4, 5, 6), cot_toi_da={1: 36, 2: 22, 3: 18})
    print(f"Tổng cộng: {len(ds_sach)} đầu sách.")


def them_sach(du_lieu):
    """Thêm sách mới: kiểm tra trùng mã, không bỏ trống, số lượng phải dương."""
    in_tieu_de("THÊM SÁCH MỚI")
    print("(Nhập 0 ở ô Mã sách để hủy)")
    while True:
        ma_sach = nhap_ma("Mã sách: ")
        if ma_sach is None:
            thong_bao_thong_tin("Đã hủy thêm sách.")
            return
        if kiem_tra_trung_ma_sach(du_lieu["sach"], ma_sach):
            thong_bao_loi(f"Mã sách '{ma_sach}' đã tồn tại. Vui lòng nhập mã khác.")
            continue
        break
    ten_sach = nhap_chuoi("Tên sách: ")
    tac_gia = nhap_chuoi("Tác giả: ")
    the_loai = nhap_chuoi("Thể loại: ")
    tong_so = nhap_so_nguyen("Tổng số lượng: ", nho_nhat=1, ten_truong="Tổng số lượng")

    # Sách mới chưa có ai mượn nên số lượng còn lại = tổng số lượng, lượt mượn = 0
    sach_moi = {"ma_sach": ma_sach, "ten_sach": ten_sach, "tac_gia": tac_gia,
                "the_loai": the_loai, "tong_so": tong_so, "con_lai": tong_so, "luot_muon": 0}
    du_lieu["sach"].append(sach_moi)
    thong_bao_thanh_cong(f"Đã thêm sách '{ten_sach}' (mã {ma_sach}).")
    xu_ly_file.tu_dong_luu(du_lieu)


def cap_nhat_sach(du_lieu):
    """Cập nhật thông tin sách. Nhấn Enter để giữ nguyên giá trị cũ."""
    in_tieu_de("CẬP NHẬT THÔNG TIN SÁCH")
    ma_sach = nhap_ma("Nhập mã sách cần cập nhật (0 để hủy): ")
    if ma_sach is None:
        thong_bao_thong_tin("Đã hủy cập nhật.")
        return
    sach = tim_sach_theo_ma(du_lieu["sach"], ma_sach)
    if sach is None:
        thong_bao_loi(f"Không tìm thấy sách có mã '{ma_sach}'.")
        return

    hien_thi_ds_sach([sach])
    print("Nhấn Enter để giữ nguyên giá trị hiện tại.")
    ten_moi = nhap_chuoi(f"Tên sách [{sach['ten_sach']}]: ", mac_dinh=sach["ten_sach"])
    tac_gia_moi = nhap_chuoi(f"Tác giả [{sach['tac_gia']}]: ", mac_dinh=sach["tac_gia"])
    the_loai_moi = nhap_chuoi(f"Thể loại [{sach['the_loai']}]: ", mac_dinh=sach["the_loai"])

    # Số cuốn đang được mượn (phiếu chưa trả) -> tổng số lượng không được nhỏ hơn số này
    dang_muon = dem_phieu_chua_tra_theo(du_lieu["phieu"], "ma_sach", ma_sach)
    tong_nho_nhat = max(1, dang_muon)
    tong_moi = nhap_so_nguyen(
        f"Tổng số lượng [{sach['tong_so']}] (tối thiểu {tong_nho_nhat}): ",
        nho_nhat=tong_nho_nhat, mac_dinh=sach["tong_so"], ten_truong="Tổng số lượng")

    # Số lượng còn lại tối đa = tổng - số cuốn đang cho mượn, và không bao giờ lớn hơn tổng
    con_lai_toi_da = max(0, tong_moi - dang_muon)
    con_lai_mac_dinh = con_lai_toi_da
    con_lai_moi = nhap_so_nguyen(
        f"Số lượng còn lại [{con_lai_mac_dinh}] (từ 0 đến {con_lai_toi_da}): ",
        nho_nhat=0, lon_nhat=con_lai_toi_da, mac_dinh=con_lai_mac_dinh,
        ten_truong="Số lượng còn lại")

    sach["ten_sach"] = ten_moi
    sach["tac_gia"] = tac_gia_moi
    sach["the_loai"] = the_loai_moi
    sach["tong_so"] = tong_moi
    sach["con_lai"] = con_lai_moi
    thong_bao_thanh_cong(f"Đã cập nhật sách mã {ma_sach}.")
    hien_thi_ds_sach([sach])
    xu_ly_file.tu_dong_luu(du_lieu)


def xoa_sach(du_lieu):
    """Xóa sách (có xác nhận). Không cho xóa nếu còn phiếu mượn chưa trả."""
    in_tieu_de("XÓA SÁCH")
    ma_sach = nhap_ma("Nhập mã sách cần xóa (0 để hủy): ")
    if ma_sach is None:
        thong_bao_thong_tin("Đã hủy xóa sách.")
        return
    sach = tim_sach_theo_ma(du_lieu["sach"], ma_sach)
    if sach is None:
        thong_bao_loi(f"Không tìm thấy sách có mã '{ma_sach}'.")
        return

    hien_thi_ds_sach([sach])
    so_phieu = dem_phieu_chua_tra_theo(du_lieu["phieu"], "ma_sach", ma_sach)
    if so_phieu > 0:
        thong_bao_loi(f"Không thể xóa: sách này đang có {so_phieu} phiếu mượn chưa trả.")
        return
    if not xac_nhan(f"Bạn có chắc chắn muốn xóa sách '{sach['ten_sach']}'?"):
        thong_bao_thong_tin("Đã hủy, dữ liệu không thay đổi.")
        return
    du_lieu["sach"].remove(sach)
    thong_bao_thanh_cong(f"Đã xóa sách mã {ma_sach}.")
    xu_ly_file.tu_dong_luu(du_lieu)


def kiem_tra_ma_sach(du_lieu):
    """Tìm sách theo mã và cho biết mã đó đã được dùng hay chưa."""
    in_tieu_de("TÌM SÁCH / KIỂM TRA MÃ SÁCH")
    ma_sach = nhap_ma("Nhập mã sách cần kiểm tra (0 để hủy): ")
    if ma_sach is None:
        return
    sach = tim_sach_theo_ma(du_lieu["sach"], ma_sach)
    if sach is None:
        thong_bao_thong_tin(f"Mã '{ma_sach}' CHƯA tồn tại, có thể dùng để thêm sách mới.")
    else:
        thong_bao_canh_bao(f"Mã '{ma_sach}' ĐÃ tồn tại, thông tin sách:")
        hien_thi_ds_sach([sach])


def menu_quan_ly_sach(du_lieu):
    """Menu con của chức năng quản lý sách."""
    while True:
        in_tieu_de("QUẢN LÝ SÁCH")
        print("1. Thêm sách mới")
        print("2. Hiển thị danh sách sách")
        print("3. Cập nhật thông tin sách")
        print("4. Xóa sách")
        print("5. Tìm sách / kiểm tra mã sách trùng")
        print("0. Quay lại menu chính")
        in_duong_ke()
        lua_chon = nhap_lua_chon()
        if lua_chon == "1":
            them_sach(du_lieu)
        elif lua_chon == "2":
            in_tieu_de("DANH SÁCH SÁCH")
            hien_thi_ds_sach(du_lieu["sach"])
        elif lua_chon == "3":
            cap_nhat_sach(du_lieu)
        elif lua_chon == "4":
            xoa_sach(du_lieu)
        elif lua_chon == "5":
            kiem_tra_ma_sach(du_lieu)
        elif lua_chon == "0":
            break
        else:
            thong_bao_loi("Lựa chọn không hợp lệ. Vui lòng chọn lại.")
            continue
        tam_dung()
