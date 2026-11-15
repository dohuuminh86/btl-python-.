# -*- coding: utf-8 -*-
"""
quan_ly_doc_gia.py - Chức năng QUẢN LÝ ĐỘC GIẢ.

Mỗi độc giả là một dictionary:
  {"ma_doc_gia", "ho_ten", "ngay_sinh" (kiểu date), "so_dien_thoai", "dia_chi", "email"}
"""

from datetime import date

from tien_ich import (
    in_tieu_de, in_duong_ke, in_bang, nhap_lua_chon, nhap_chuoi, nhap_ma, nhap_ngay,
    nhap_so_dien_thoai, nhap_email, xac_nhan, tam_dung, dinh_dang_ngay,
    thong_bao_thanh_cong, thong_bao_loi, thong_bao_canh_bao, thong_bao_thong_tin,
    tim_ban_ghi_theo_ma, dem_phieu_chua_tra_theo,
)
import xu_ly_file


def tim_doc_gia_theo_ma(ds_doc_gia, ma_doc_gia):
    """Trả về dictionary độc giả có mã tương ứng, không có thì trả về None."""
    return tim_ban_ghi_theo_ma(ds_doc_gia, "ma_doc_gia", ma_doc_gia)


def kiem_tra_trung_ma_doc_gia(ds_doc_gia, ma_doc_gia):
    """True nếu mã độc giả đã tồn tại."""
    return tim_doc_gia_theo_ma(ds_doc_gia, ma_doc_gia) is not None


def hien_thi_ds_doc_gia(ds_doc_gia):
    """In danh sách độc giả dạng bảng."""
    if len(ds_doc_gia) == 0:
        thong_bao_canh_bao("Chưa có độc giả nào để hiển thị.")
        return
    cac_hang = []
    for dg in ds_doc_gia:
        cac_hang.append([dg["ma_doc_gia"], dg["ho_ten"], dinh_dang_ngay(dg["ngay_sinh"]),
                         dg["so_dien_thoai"], dg["dia_chi"], dg["email"]])
    in_bang(["Mã ĐG", "Họ và tên", "Ngày sinh", "Điện thoại", "Địa chỉ", "Email"],
            cac_hang, cot_toi_da={1: 26, 4: 24, 5: 28})
    print(f"Tổng cộng: {len(ds_doc_gia)} độc giả.")


def nhap_ngay_sinh(thong_bao, mac_dinh=None):
    """Nhập ngày sinh: đúng định dạng và phải trước ngày hôm nay."""
    while True:
        ngay_sinh = nhap_ngay(thong_bao, mac_dinh)
        if ngay_sinh >= date.today():
            thong_bao_loi("Ngày sinh phải trước ngày hôm nay. Vui lòng nhập lại.")
            continue
        return ngay_sinh


def them_doc_gia(du_lieu):
    """Thêm độc giả mới: kiểm tra trùng mã, bỏ trống, ngày sinh, điện thoại, email."""
    in_tieu_de("THÊM ĐỘC GIẢ MỚI")
    print("(Nhập 0 ở ô Mã độc giả để hủy)")
    while True:
        ma_doc_gia = nhap_ma("Mã độc giả: ")
        if ma_doc_gia is None:
            thong_bao_thong_tin("Đã hủy thêm độc giả.")
            return
        if kiem_tra_trung_ma_doc_gia(du_lieu["doc_gia"], ma_doc_gia):
            thong_bao_loi(f"Mã độc giả '{ma_doc_gia}' đã tồn tại. Vui lòng nhập mã khác.")
            continue
        break
    ho_ten = nhap_chuoi("Họ và tên: ")
    ngay_sinh = nhap_ngay_sinh("Ngày sinh (dd/mm/yyyy): ")
    so_dien_thoai = nhap_so_dien_thoai("Số điện thoại: ")
    dia_chi = nhap_chuoi("Địa chỉ: ")
    email = nhap_email("Email: ")

    doc_gia_moi = {"ma_doc_gia": ma_doc_gia, "ho_ten": ho_ten, "ngay_sinh": ngay_sinh,
                   "so_dien_thoai": so_dien_thoai, "dia_chi": dia_chi, "email": email}
    du_lieu["doc_gia"].append(doc_gia_moi)
    thong_bao_thanh_cong(f"Đã thêm độc giả '{ho_ten}' (mã {ma_doc_gia}).")
    xu_ly_file.tu_dong_luu(du_lieu)


def cap_nhat_doc_gia(du_lieu):
    """Cập nhật thông tin độc giả. Nhấn Enter để giữ nguyên giá trị cũ."""
    in_tieu_de("CẬP NHẬT THÔNG TIN ĐỘC GIẢ")
    ma_doc_gia = nhap_ma("Nhập mã độc giả cần cập nhật (0 để hủy): ")
    if ma_doc_gia is None:
        thong_bao_thong_tin("Đã hủy cập nhật.")
        return
    doc_gia = tim_doc_gia_theo_ma(du_lieu["doc_gia"], ma_doc_gia)
    if doc_gia is None:
        thong_bao_loi(f"Không tìm thấy độc giả có mã '{ma_doc_gia}'.")
        return

    hien_thi_ds_doc_gia([doc_gia])
    print("Nhấn Enter để giữ nguyên giá trị hiện tại.")
    ho_ten_moi = nhap_chuoi(f"Họ và tên [{doc_gia['ho_ten']}]: ", mac_dinh=doc_gia["ho_ten"])
    ngay_sinh_moi = nhap_ngay_sinh(
        f"Ngày sinh [{dinh_dang_ngay(doc_gia['ngay_sinh'])}]: ", mac_dinh=doc_gia["ngay_sinh"])
    sdt_moi = nhap_so_dien_thoai(f"Số điện thoại [{doc_gia['so_dien_thoai']}]: ",
                                 mac_dinh=doc_gia["so_dien_thoai"])
    dia_chi_moi = nhap_chuoi(f"Địa chỉ [{doc_gia['dia_chi']}]: ", mac_dinh=doc_gia["dia_chi"])
    email_moi = nhap_email(f"Email [{doc_gia['email']}]: ", mac_dinh=doc_gia["email"])

    doc_gia["ho_ten"] = ho_ten_moi
    doc_gia["ngay_sinh"] = ngay_sinh_moi
    doc_gia["so_dien_thoai"] = sdt_moi
    doc_gia["dia_chi"] = dia_chi_moi
    doc_gia["email"] = email_moi

    # Phiếu mượn có lưu họ tên độc giả nên phải cập nhật cho đồng bộ
    for phieu in du_lieu["phieu"]:
        if phieu["ma_doc_gia"].upper() == ma_doc_gia.upper():
            phieu["ho_ten"] = ho_ten_moi

    thong_bao_thanh_cong(f"Đã cập nhật độc giả mã {ma_doc_gia}.")
    hien_thi_ds_doc_gia([doc_gia])
    xu_ly_file.tu_dong_luu(du_lieu)


def xoa_doc_gia(du_lieu):
    """Xóa độc giả (có xác nhận). Không cho xóa nếu còn sách chưa trả."""
    in_tieu_de("XÓA ĐỘC GIẢ")
    ma_doc_gia = nhap_ma("Nhập mã độc giả cần xóa (0 để hủy): ")
    if ma_doc_gia is None:
        thong_bao_thong_tin("Đã hủy xóa độc giả.")
        return
    doc_gia = tim_doc_gia_theo_ma(du_lieu["doc_gia"], ma_doc_gia)
    if doc_gia is None:
        thong_bao_loi(f"Không tìm thấy độc giả có mã '{ma_doc_gia}'.")
        return

    hien_thi_ds_doc_gia([doc_gia])
    so_phieu = dem_phieu_chua_tra_theo(du_lieu["phieu"], "ma_doc_gia", ma_doc_gia)
    if so_phieu > 0:
        thong_bao_loi(f"Không thể xóa: độc giả này đang mượn {so_phieu} cuốn sách chưa trả.")
        return
    if not xac_nhan(f"Bạn có chắc chắn muốn xóa độc giả '{doc_gia['ho_ten']}'?"):
        thong_bao_thong_tin("Đã hủy, dữ liệu không thay đổi.")
        return
    du_lieu["doc_gia"].remove(doc_gia)
    thong_bao_thanh_cong(f"Đã xóa độc giả mã {ma_doc_gia}.")
    xu_ly_file.tu_dong_luu(du_lieu)


def kiem_tra_ma_doc_gia(du_lieu):
    """Tìm độc giả theo mã và cho biết mã đó đã được dùng hay chưa."""
    in_tieu_de("TÌM ĐỘC GIẢ / KIỂM TRA MÃ ĐỘC GIẢ")
    ma_doc_gia = nhap_ma("Nhập mã độc giả cần kiểm tra (0 để hủy): ")
    if ma_doc_gia is None:
        return
    doc_gia = tim_doc_gia_theo_ma(du_lieu["doc_gia"], ma_doc_gia)
    if doc_gia is None:
        thong_bao_thong_tin(f"Mã '{ma_doc_gia}' CHƯA tồn tại, có thể dùng để thêm độc giả mới.")
    else:
        thong_bao_canh_bao(f"Mã '{ma_doc_gia}' ĐÃ tồn tại, thông tin độc giả:")
        hien_thi_ds_doc_gia([doc_gia])


def menu_quan_ly_doc_gia(du_lieu):
    """Menu con của chức năng quản lý độc giả."""
    while True:
        in_tieu_de("QUẢN LÝ ĐỘC GIẢ")
        print("1. Thêm độc giả")
        print("2. Hiển thị danh sách độc giả")
        print("3. Cập nhật thông tin độc giả")
        print("4. Xóa độc giả")
        print("5. Tìm độc giả / kiểm tra mã độc giả trùng")
        print("0. Quay lại menu chính")
        in_duong_ke()
        lua_chon = nhap_lua_chon()
        if lua_chon == "1":
            them_doc_gia(du_lieu)
        elif lua_chon == "2":
            in_tieu_de("DANH SÁCH ĐỘC GIẢ")
            hien_thi_ds_doc_gia(du_lieu["doc_gia"])
        elif lua_chon == "3":
            cap_nhat_doc_gia(du_lieu)
        elif lua_chon == "4":
            xoa_doc_gia(du_lieu)
        elif lua_chon == "5":
            kiem_tra_ma_doc_gia(du_lieu)
        elif lua_chon == "0":
            break
        else:
            thong_bao_loi("Lựa chọn không hợp lệ. Vui lòng chọn lại.")
            continue
        tam_dung()
