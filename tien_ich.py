# -*- coding: utf-8 -*-
"""
tien_ich.py - Các hàm tiện ích dùng chung cho toàn bộ chương trình.

Gồm có:
  1. Màu sắc và các hàm in thông báo (thành công / lỗi / cảnh báo).
  2. Các hàm nhập dữ liệu có kiểm tra (nhập lại khi sai, không thoát chương trình).
  3. Xử lý ngày tháng, tính số ngày quá hạn và tiền phạt.
  4. Hàm in bảng dữ liệu căn chỉnh đẹp.
  5. Hàm so sánh chuỗi không phân biệt hoa/thường, không dấu, hỗ trợ tìm gần đúng.
"""

import os
import re
import sys
import difflib
import unicodedata
from datetime import date, datetime, timedelta

# ----------------------------------------------------------------------
# 1. MÀU SẮC (dùng thư viện colorama nếu có, không có thì in chữ thường)
# ----------------------------------------------------------------------
try:
    from colorama import init as colorama_init, Fore, Style
    colorama_init()
    XANH_LA = Fore.GREEN
    DO = Fore.RED
    VANG = Fore.YELLOW
    XANH_DUONG = Fore.CYAN
    DAM = Style.BRIGHT
    TAT = Style.RESET_ALL
except ImportError:
    # Chưa cài colorama: chương trình vẫn chạy bình thường nhưng không có màu
    XANH_LA = DO = VANG = XANH_DUONG = DAM = TAT = ""

# ----------------------------------------------------------------------
# HẰNG SỐ CỦA CHƯƠNG TRÌNH
# ----------------------------------------------------------------------
DINH_DANG_NGAY = "%d/%m/%Y"        # Định dạng ngày: dd/mm/yyyy
TIEN_PHAT_MOI_NGAY = 5000          # Phạt 5.000 VNĐ cho mỗi ngày quá hạn
SO_NGAY_MUON_MAC_DINH = 14         # Mặc định cho mượn 14 ngày
DO_RONG = 70                       # Độ rộng của đường kẻ và tiêu đề

TT_DANG_MUON = "Đang mượn"
TT_DA_TRA = "Đã trả"
TT_QUA_HAN = "Quá hạn"


# ----------------------------------------------------------------------
# CÀI ĐẶT CONSOLE (hiển thị tiếng Việt trên Windows)
# ----------------------------------------------------------------------
def cai_dat_console():
    """Chuyển console sang UTF-8 để không bị lỗi hiển thị tiếng Việt."""
    if os.name == "nt":                      # Đang chạy trên Windows
        os.system("chcp 65001 > nul")
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError, OSError):
        pass                                 # Môi trường không hỗ trợ thì bỏ qua


# ----------------------------------------------------------------------
# 2. CÁC HÀM IN RA MÀN HÌNH
# ----------------------------------------------------------------------
def in_duong_ke(ky_tu="-", do_rong=DO_RONG):
    """In một đường kẻ phân cách."""
    print(ky_tu * do_rong)


def in_tieu_de(tieu_de):
    """In tiêu đề của một chức năng, nằm giữa hai đường kẻ."""
    print()
    print(XANH_DUONG + DAM + "=" * DO_RONG)
    print(tieu_de.center(DO_RONG))
    print("=" * DO_RONG + TAT)


def thong_bao_thanh_cong(noi_dung):
    print(f"{XANH_LA}[THÀNH CÔNG]{TAT} {noi_dung}")


def thong_bao_loi(noi_dung):
    print(f"{DO}[LỖI]{TAT} {noi_dung}")


def thong_bao_canh_bao(noi_dung):
    print(f"{VANG}[CHÚ Ý]{TAT} {noi_dung}")


def thong_bao_thong_tin(noi_dung):
    print(f"{XANH_DUONG}[THÔNG TIN]{TAT} {noi_dung}")


def tam_dung():
    """Dừng màn hình để người dùng đọc kết quả."""
    input("\nNhấn Enter để tiếp tục...")


# ----------------------------------------------------------------------
# 3. XỬ LÝ CHUỖI
# ----------------------------------------------------------------------
def chuan_hoa_chuoi(chuoi):
    """Bỏ khoảng trắng thừa ở đầu, cuối, giữa và chuẩn hóa Unicode (NFC)."""
    chuoi = unicodedata.normalize("NFC", chuoi)
    return " ".join(chuoi.split())


def bo_dau(chuoi):
    """Bỏ dấu tiếng Việt: 'Nguyễn Văn Đạt' -> 'Nguyen Van Dat'."""
    chuoi = unicodedata.normalize("NFD", chuoi)
    ket_qua = ""
    for ky_tu in chuoi:
        if unicodedata.category(ky_tu) != "Mn":   # Mn = dấu kết hợp
            ket_qua += ky_tu
    return ket_qua.replace("đ", "d").replace("Đ", "D")


def khoa_so_sanh(chuoi):
    """Chuỗi dùng để so sánh/sắp xếp: không dấu và viết thường."""
    return bo_dau(chuoi).lower()


def khop_ma(tu_khoa, ma):
    """Tìm theo mã: không phân biệt hoa/thường, chỉ cần chứa từ khóa."""
    return khoa_so_sanh(tu_khoa) in khoa_so_sanh(ma)


def khop_gan_dung(tu_khoa, van_ban):
    """
    Tìm kiếm gần đúng, không phân biệt hoa/thường và không phân biệt dấu.
    - Nếu từ khóa nằm trong văn bản -> khớp.
    - Nếu không, mỗi từ của từ khóa phải giống (>= 80%) một từ nào đó trong văn bản
      (để chịu được lỗi gõ sai nhẹ, ví dụ 'pyton' vẫn tìm ra 'python').
      Từ quá ngắn (dưới 5 ký tự) chỉ tìm đúng, vì sai 1 chữ cái đã thành từ khác
      (ví dụ 'hung' và 'tung' là hai tên khác nhau).
    """
    tk = khoa_so_sanh(tu_khoa)
    vb = khoa_so_sanh(van_ban)
    if tk == "":
        return False
    if tk in vb:
        return True
    cac_tu_van_ban = vb.split()
    for tu in tk.split():
        tim_thay = False
        for tu_vb in cac_tu_van_ban:
            if tu in tu_vb:
                tim_thay = True
                break
            if len(tu) >= 5 and difflib.SequenceMatcher(None, tu, tu_vb).ratio() >= 0.8:
                tim_thay = True
                break
        if not tim_thay:
            return False
    return True


# ----------------------------------------------------------------------
# 4. NHẬP DỮ LIỆU CÓ KIỂM TRA (sai thì báo lỗi và cho nhập lại)
# ----------------------------------------------------------------------
def nhap_lua_chon(thong_bao="Nhập lựa chọn: "):
    """Nhập lựa chọn trong menu."""
    return input(thong_bao).strip()


def nhap_chuoi(thong_bao, bat_buoc=True, mac_dinh=None):
    """
    Nhập một chuỗi.
    - bat_buoc=True: không cho bỏ trống.
    - mac_dinh: nếu người dùng chỉ nhấn Enter thì trả về giá trị này (dùng khi cập nhật).
    """
    while True:
        gia_tri = chuan_hoa_chuoi(input(thong_bao))
        if gia_tri == "":
            if mac_dinh is not None:
                return mac_dinh
            if not bat_buoc:
                return ""
            thong_bao_loi("Thông tin này không được bỏ trống. Vui lòng nhập lại.")
            continue
        if "|" in gia_tri:
            thong_bao_loi("Không được dùng ký tự '|' (đây là ký tự ngăn cách trong file dữ liệu).")
            continue
        return gia_tri


def nhap_ma(thong_bao):
    """
    Nhập một mã (mã sách, mã độc giả, mã phiếu). Mã được viết hoa và không chứa khoảng trắng.
    Nhập 0 để hủy -> trả về None.
    """
    while True:
        gia_tri = nhap_chuoi(thong_bao).upper()
        if gia_tri == "0":
            return None
        if " " in gia_tri:
            thong_bao_loi("Mã không được chứa khoảng trắng. Vui lòng nhập lại.")
            continue
        return gia_tri


def nhap_so_nguyen(thong_bao, nho_nhat=None, lon_nhat=None, mac_dinh=None, ten_truong="Giá trị"):
    """Nhập một số nguyên trong khoảng [nho_nhat, lon_nhat]."""
    while True:
        chuoi = input(thong_bao).strip()
        if chuoi == "":
            if mac_dinh is not None:
                return mac_dinh
            thong_bao_loi(f"{ten_truong} không được bỏ trống. Vui lòng nhập lại.")
            continue
        try:
            so = int(chuoi)
        except ValueError:
            thong_bao_loi(f"{ten_truong} phải là một số nguyên hợp lệ. Vui lòng nhập lại.")
            continue
        if nho_nhat is not None and so < nho_nhat:
            thong_bao_loi(f"{ten_truong} phải lớn hơn hoặc bằng {nho_nhat}. Vui lòng nhập lại.")
            continue
        if lon_nhat is not None and so > lon_nhat:
            thong_bao_loi(f"{ten_truong} phải nhỏ hơn hoặc bằng {lon_nhat}. Vui lòng nhập lại.")
            continue
        return so


def nhap_so_dien_thoai(thong_bao, mac_dinh=None):
    """Nhập số điện thoại: chỉ gồm chữ số, dài 9 đến 11 ký tự."""
    while True:
        chuoi = input(thong_bao).strip()
        if chuoi == "":
            if mac_dinh is not None:
                return mac_dinh
            thong_bao_loi("Số điện thoại không được bỏ trống. Vui lòng nhập lại.")
            continue
        if chuoi.isascii() and chuoi.isdigit() and 9 <= len(chuoi) <= 11:
            return chuoi
        thong_bao_loi("Số điện thoại phải gồm 9 đến 11 chữ số. Vui lòng nhập lại.")


def nhap_email(thong_bao, mac_dinh=None):
    """Nhập email, kiểm tra định dạng cơ bản (có @ và có dấu chấm sau @)."""
    mau_email = r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9-]+(\.[A-Za-z0-9-]+)+$"
    while True:
        chuoi = input(thong_bao).strip()
        if chuoi == "":
            if mac_dinh is not None:
                return mac_dinh
            thong_bao_loi("Email không được bỏ trống. Vui lòng nhập lại.")
            continue
        if re.match(mau_email, chuoi):
            return chuoi
        thong_bao_loi("Email không hợp lệ (ví dụ đúng: ten@gmail.com). Vui lòng nhập lại.")


def xac_nhan(cau_hoi):
    """Hỏi xác nhận Có/Không. Trả về True nếu chọn Có."""
    while True:
        tra_loi = input(f"{cau_hoi} (c/k): ").strip().lower()
        if tra_loi in ("c", "co", "có", "y", "yes"):
            return True
        if tra_loi in ("k", "khong", "không", "n", "no"):
            return False
        thong_bao_loi("Vui lòng nhập 'c' (có) hoặc 'k' (không).")


# ----------------------------------------------------------------------
# 5. NGÀY THÁNG
# ----------------------------------------------------------------------
def chuyen_chuoi_thanh_ngay(chuoi):
    """Đổi chuỗi 'dd/mm/yyyy' thành đối tượng date. Sai định dạng -> trả về None."""
    try:
        ngay = datetime.strptime(chuoi.strip(), DINH_DANG_NGAY).date()
    except ValueError:
        return None
    if ngay.year < 1900:
        return None
    return ngay


def dinh_dang_ngay(ngay):
    """Đổi date thành chuỗi dd/mm/yyyy. Nếu chưa có ngày (None) thì trả về chuỗi rỗng."""
    if ngay is None:
        return ""
    return ngay.strftime(DINH_DANG_NGAY)


def nhap_ngay(thong_bao, mac_dinh=None):
    """Nhập ngày theo định dạng dd/mm/yyyy, sai thì nhập lại."""
    while True:
        chuoi = input(thong_bao).strip()
        if chuoi == "":
            if mac_dinh is not None:
                return mac_dinh
            thong_bao_loi("Ngày không được bỏ trống. Vui lòng nhập lại.")
            continue
        ngay = chuyen_chuoi_thanh_ngay(chuoi)
        if ngay is None:
            thong_bao_loi("Ngày không hợp lệ. Hãy nhập theo dạng dd/mm/yyyy (ví dụ 25/12/2026).")
            continue
        return ngay


# ----------------------------------------------------------------------
# 6. TÍNH QUÁ HẠN VÀ TIỀN PHẠT
# ----------------------------------------------------------------------
def tinh_so_ngay_qua_han(han_tra, ngay_moc):
    """
    Số ngày quá hạn = Ngày trả thực tế - Hạn trả.
    (ngay_moc là ngày trả thực tế, hoặc ngày hiện tại nếu chưa trả)
    Nếu không muộn hơn hạn trả thì bằng 0.
    """
    so_ngay = (ngay_moc - han_tra).days
    if so_ngay < 0:
        so_ngay = 0
    return so_ngay


def tinh_tien_phat(so_ngay_qua_han):
    """Tiền phạt = số ngày quá hạn x 5.000 VNĐ, không bao giờ âm."""
    if so_ngay_qua_han < 0:
        so_ngay_qua_han = 0
    return so_ngay_qua_han * TIEN_PHAT_MOI_NGAY


def dinh_dang_tien(so_tien):
    """5000 -> '5.000'."""
    return f"{so_tien:,}".replace(",", ".")


def cap_nhat_trang_thai_phieu(ds_phieu, hom_nay=None):
    """
    Tính lại trạng thái, số ngày quá hạn và tiền phạt cho mọi phiếu:
      - Phiếu đã trả: tính theo ngày trả thực tế, trạng thái 'Đã trả'.
      - Phiếu chưa trả: tính theo ngày hiện tại; quá hạn > 0 ngày thì là 'Quá hạn',
        ngược lại là 'Đang mượn'.
    """
    if hom_nay is None:
        hom_nay = date.today()
    for phieu in ds_phieu:
        if phieu["ngay_tra"] is not None:
            ngay_moc = phieu["ngay_tra"]
        else:
            ngay_moc = hom_nay
        so_ngay = tinh_so_ngay_qua_han(phieu["han_tra"], ngay_moc)
        phieu["so_ngay_qua_han"] = so_ngay
        phieu["tien_phat"] = tinh_tien_phat(so_ngay)
        if phieu["ngay_tra"] is not None:
            phieu["trang_thai"] = TT_DA_TRA
        elif so_ngay > 0:
            phieu["trang_thai"] = TT_QUA_HAN
        else:
            phieu["trang_thai"] = TT_DANG_MUON


# ----------------------------------------------------------------------
# 7. TÌM BẢN GHI THEO MÃ
# ----------------------------------------------------------------------
def tim_ban_ghi_theo_ma(danh_sach, ten_khoa, ma):
    """Tìm đúng 1 bản ghi có danh_sach[i][ten_khoa] == ma (không phân biệt hoa/thường)."""
    for ban_ghi in danh_sach:
        if ban_ghi[ten_khoa].upper() == ma.upper():
            return ban_ghi
    return None


def dem_phieu_chua_tra_theo(ds_phieu, ten_khoa, ma):
    """Đếm số phiếu CHƯA TRẢ của một sách ('ma_sach') hoặc một độc giả ('ma_doc_gia')."""
    so_luong = 0
    for phieu in ds_phieu:
        if phieu[ten_khoa].upper() == ma.upper() and phieu["ngay_tra"] is None:
            so_luong += 1
    return so_luong


# ----------------------------------------------------------------------
# 8. IN BẢNG DỮ LIỆU
# ----------------------------------------------------------------------
def _cat_chuoi(chuoi, do_dai_toi_da):
    """Cắt chuỗi quá dài và thêm '..' ở cuối."""
    if len(chuoi) <= do_dai_toi_da:
        return chuoi
    return chuoi[:do_dai_toi_da - 2] + ".."


def in_bang(tieu_de_cot, cac_hang, cot_can_phai=(), cot_toi_da=None):
    """
    In bảng căn chỉnh đẹp.
      tieu_de_cot : list tên các cột.
      cac_hang    : list các hàng, mỗi hàng là một list giá trị.
      cot_can_phai: chỉ số các cột căn lề phải (thường là cột số).
      cot_toi_da  : dict {chỉ số cột: độ rộng tối đa}, chuỗi dài hơn sẽ bị cắt.
    """
    if cot_toi_da is None:
        cot_toi_da = {}
    so_cot = len(tieu_de_cot)
    hang_chuoi = []
    for hang in cac_hang:
        hang_chuoi.append([str(o) for o in hang])

    # Tính độ rộng từng cột = độ dài lớn nhất trong cột (có giới hạn)
    do_rong = []
    for i in range(so_cot):
        rong = len(tieu_de_cot[i])
        for hang in hang_chuoi:
            if len(hang[i]) > rong:
                rong = len(hang[i])
        if i in cot_toi_da and rong > cot_toi_da[i]:
            rong = cot_toi_da[i]
        do_rong.append(rong)

    def tao_dong(cac_o):
        phan = []
        for i in range(so_cot):
            o = _cat_chuoi(cac_o[i], do_rong[i])
            if i in cot_can_phai:
                o = o.rjust(do_rong[i])
            else:
                o = o.ljust(do_rong[i])
            phan.append(" " + o + " ")
        return "|" + "|".join(phan) + "|"

    duong_ngang = "+" + "+".join("-" * (r + 2) for r in do_rong) + "+"
    print(duong_ngang)
    print(DAM + VANG + tao_dong(tieu_de_cot) + TAT)
    print(duong_ngang)
    for hang in hang_chuoi:
        print(tao_dong(hang))
    print(duong_ngang)
