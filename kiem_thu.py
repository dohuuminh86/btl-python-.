# -*- coding: utf-8 -*-
"""
kiem_thu.py - Bộ kiểm thử tự động cho chương trình quản lý thư viện.

Chạy:  python kiem_thu.py
Kiểm thử làm việc trên THƯ MỤC TẠM, không làm thay đổi thư mục data/ của bạn.

Cách hoạt động:
  - Các hàm nhập liệu (input) được thay bằng một danh sách câu trả lời viết sẵn.
  - Sau mỗi hàm, kiểm tra dữ liệu trong bộ nhớ, trong file TXT và nội dung đã in ra.
  - Cuối cùng chạy main.py như một tiến trình thật (subprocess) với đầu vào giả lập.
"""

import contextlib
import io
import os
import shutil
import subprocess
import sys
import tempfile
from datetime import date, timedelta
from unittest import mock

THU_MUC_DU_AN = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, THU_MUC_DU_AN)

import tien_ich
import xu_ly_file
import tao_du_lieu_mau
import quan_ly_sach
import quan_ly_doc_gia
import quan_ly_muon_tra
import tim_kiem
import sap_xep
import thong_ke

SO_DAT = 0
SO_HONG = 0
DS_HONG = []


def kiem_tra(ten, dieu_kien):
    """Ghi nhận một phép kiểm tra đạt hay không đạt."""
    global SO_DAT, SO_HONG
    if dieu_kien:
        SO_DAT += 1
        print(f"  [ĐẠT]     {ten}")
    else:
        SO_HONG += 1
        DS_HONG.append(ten)
        print(f"  [KHÔNG ĐẠT] {ten}")


def nhom(ten):
    print(f"\n=== {ten} ===")


class DauVao:
    """Giả lập input(): lần lượt trả về từng câu trả lời viết sẵn."""
    def __init__(self, cac_dong):
        self.cac_dong = list(cac_dong)
        self.vi_tri = 0

    def __call__(self, thong_bao=""):
        if self.vi_tri >= len(self.cac_dong):
            raise EOFError("hết dữ liệu nhập giả lập")
        gia_tri = self.cac_dong[self.vi_tri]
        self.vi_tri += 1
        return gia_tri

    def da_dung_het(self):
        return self.vi_tri == len(self.cac_dong)


def chay(ham, du_lieu, cac_dong, ten_phep=None):
    """Chạy một hàm tương tác với đầu vào giả lập, trả về toàn bộ chữ đã in ra màn hình."""
    dau_vao = DauVao(cac_dong)
    bo_dem = io.StringIO()
    het_dau_vao = False
    with mock.patch("builtins.input", dau_vao), contextlib.redirect_stdout(bo_dem):
        try:
            ham(du_lieu)
        except EOFError:
            het_dau_vao = True
    if ten_phep is not None:
        kiem_tra(f"{ten_phep}: dùng đúng và đủ các dòng nhập giả lập",
                 dau_vao.da_dung_het() and not het_dau_vao)
    return bo_dem.getvalue()


def ngay_chuoi(so_ngay_lech):
    """Chuỗi dd/mm/yyyy của (hôm nay + so_ngay_lech)."""
    return tien_ich.dinh_dang_ngay(date.today() + timedelta(days=so_ngay_lech))


def tao_moi_truong():
    """Tạo thư mục data tạm, trỏ xu_ly_file vào đó, ghi dữ liệu mẫu, trả về du_lieu."""
    thu_muc = tempfile.mkdtemp(prefix="thuvien_test_")
    xu_ly_file.THU_MUC_DATA = thu_muc
    xu_ly_file.FILE_SACH = os.path.join(thu_muc, "sach.txt")
    xu_ly_file.FILE_DOC_GIA = os.path.join(thu_muc, "docgia.txt")
    xu_ly_file.FILE_PHIEU = os.path.join(thu_muc, "phieumuon.txt")
    du_lieu = tao_du_lieu_mau.tao_du_lieu()
    with contextlib.redirect_stdout(io.StringIO()):
        xu_ly_file.luu_tat_ca(du_lieu, False)
    return du_lieu


def doc_lai_tu_file():
    """Đọc lại 3 file TXT vào một dictionary mới (để so sánh với bộ nhớ)."""
    moi = {"sach": [], "doc_gia": [], "phieu": []}
    with contextlib.redirect_stdout(io.StringIO()):
        xu_ly_file.doc_tat_ca(moi)
    return moi


def sach(du_lieu, ma):
    return quan_ly_sach.tim_sach_theo_ma(du_lieu["sach"], ma)


def phieu(du_lieu, ma):
    return quan_ly_muon_tra.tim_phieu_theo_ma(du_lieu["phieu"], ma)


# ----------------------------------------------------------------------
def kt_du_lieu_mau():
    nhom("1. Dữ liệu mẫu và đọc file")
    du_lieu = tao_moi_truong()
    moi = doc_lai_tu_file()
    kiem_tra("Đọc file: 16 sách, 11 độc giả, 18 phiếu",
             len(moi["sach"]) == 16 and len(moi["doc_gia"]) == 11 and len(moi["phieu"]) == 18)
    trang_thai = [p["trang_thai"] for p in moi["phieu"]]
    kiem_tra("Có đủ phiếu Đang mượn / Đã trả / Quá hạn",
             trang_thai.count("Đang mượn") == 5 and trang_thai.count("Đã trả") == 9
             and trang_thai.count("Quá hạn") == 4)
    dung = True
    for s in moi["sach"]:
        chua_tra = 0
        luot = 0
        for p in moi["phieu"]:
            if p["ma_sach"] == s["ma_sach"]:
                luot += 1
                if p["ngay_tra"] is None:
                    chua_tra += 1
        if s["con_lai"] != s["tong_so"] - chua_tra or s["luot_muon"] != luot:
            dung = False
    kiem_tra("Số lượng còn lại và lượt mượn của mọi sách khớp với phiếu mượn", dung)
    ma_sach = [s["ma_sach"] for s in moi["sach"]]
    ma_dg = [d["ma_doc_gia"] for d in moi["doc_gia"]]
    lien_ket = True
    for p in moi["phieu"]:
        if p["ma_sach"] not in ma_sach or p["ma_doc_gia"] not in ma_dg:
            lien_ket = False
        dg = quan_ly_doc_gia.tim_doc_gia_theo_ma(moi["doc_gia"], p["ma_doc_gia"])
        if dg is None or dg["ho_ten"] != p["ho_ten"]:
            lien_ket = False
    kiem_tra("Mọi phiếu liên kết hợp lệ với sách và độc giả (kể cả họ tên)", lien_ket)
    kiem_tra("Kiểu dữ liệu đúng sau khi đọc (int và date)",
             isinstance(moi["sach"][0]["tong_so"], int)
             and isinstance(moi["phieu"][0]["ngay_muon"], date)
             and isinstance(moi["doc_gia"][0]["ngay_sinh"], date)
             and moi["phieu"][-1]["ngay_tra"] is None)
    with open(xu_ly_file.FILE_SACH, "rb") as f:
        noi_dung = f.read().decode("utf-8")
    kiem_tra("File lưu UTF-8, giữ nguyên tiếng Việt", "Dế Mèn phiêu lưu ký" in noi_dung)
    # Dữ liệu mẫu thật trong thư mục data/ của dự án
    thu_muc_data_that = os.path.join(THU_MUC_DU_AN, "data")
    kiem_tra("Các file dữ liệu mẫu thật tồn tại trong data/",
             all(os.path.exists(os.path.join(thu_muc_data_that, t))
                 for t in ("sach.txt", "docgia.txt", "phieumuon.txt")))


def kt_tinh_phat():
    nhom("2. Tính số ngày quá hạn và tiền phạt")
    han = date(2026, 1, 10)
    kiem_tra("Trả muộn 5 ngày -> quá hạn 5", tien_ich.tinh_so_ngay_qua_han(han, date(2026, 1, 15)) == 5)
    kiem_tra("Trả đúng hạn -> 0", tien_ich.tinh_so_ngay_qua_han(han, han) == 0)
    kiem_tra("Trả sớm -> 0 (không âm)", tien_ich.tinh_so_ngay_qua_han(han, date(2026, 1, 1)) == 0)
    kiem_tra("Phạt 5 ngày = 25.000", tien_ich.tinh_tien_phat(5) == 25000)
    kiem_tra("Phạt 0 ngày = 0 và số âm vẫn không âm",
             tien_ich.tinh_tien_phat(0) == 0 and tien_ich.tinh_tien_phat(-3) == 0)
    kiem_tra("Định dạng tiền 25000 -> '25.000'", tien_ich.dinh_dang_tien(25000) == "25.000")
    ds = [{"ngay_tra": None, "han_tra": date(2026, 1, 10), "ngay_muon": date(2026, 1, 1),
           "trang_thai": "", "so_ngay_qua_han": 0, "tien_phat": 0}]
    tien_ich.cap_nhat_trang_thai_phieu(ds, date(2026, 1, 14))
    kiem_tra("Phiếu chưa trả: tính theo ngày hiện tại (4 ngày, 20.000, Quá hạn)",
             ds[0]["so_ngay_qua_han"] == 4 and ds[0]["tien_phat"] == 20000
             and ds[0]["trang_thai"] == "Quá hạn")
    tien_ich.cap_nhat_trang_thai_phieu(ds, date(2026, 1, 10))
    kiem_tra("Phiếu chưa trả, đúng hạn chót: Đang mượn, 0 đồng",
             ds[0]["trang_thai"] == "Đang mượn" and ds[0]["tien_phat"] == 0)


def kt_nhap_lieu():
    nhom("3. Hàm nhập liệu và kiểm tra đầu vào")
    with mock.patch("builtins.input", DauVao(["", "  ", "Xin  chào"])), \
            contextlib.redirect_stdout(io.StringIO()):
        ket_qua = tien_ich.nhap_chuoi("x: ")
    kiem_tra("Bỏ trống bị từ chối, khoảng trắng thừa được gọt", ket_qua == "Xin chào")
    with mock.patch("builtins.input", DauVao(["abc", "1.5", "-2", "7"])), \
            contextlib.redirect_stdout(io.StringIO()):
        so = tien_ich.nhap_so_nguyen("x: ", nho_nhat=0)
    kiem_tra("Số nguyên: sai kiểu, số thực, số âm đều bị từ chối", so == 7)
    with mock.patch("builtins.input", DauVao(["31/02/2026", "2026-01-01", "1/1/26", "05/03/2026"])), \
            contextlib.redirect_stdout(io.StringIO()):
        ngay = tien_ich.nhap_ngay("x: ")
    kiem_tra("Ngày sai định dạng / không tồn tại bị từ chối", ngay == date(2026, 3, 5))
    kiem_tra("Tìm gần đúng: 'pyton' khớp 'Python Crash Course'",
             tien_ich.khop_gan_dung("pyton", "Python Crash Course"))
    kiem_tra("Tìm không phân biệt hoa/thường và dấu: 'DE MEN' khớp 'Dế Mèn'",
             tien_ich.khop_gan_dung("DE MEN", "Dế Mèn phiêu lưu ký"))
    kiem_tra("Từ khóa không liên quan không khớp",
             not tien_ich.khop_gan_dung("zzzzqq", "Dế Mèn phiêu lưu ký"))
    kiem_tra("Từ ngắn chỉ tìm đúng: 'hung' không khớp 'Tùng'",
             not tien_ich.khop_gan_dung("hung", "Đỗ Thanh Tùng")
             and tien_ich.khop_gan_dung("hung", "Nguyễn Văn Hùng"))


def kt_quan_ly_sach():
    nhom("4. Quản lý sách (thêm, sửa, xóa, kiểm tra)")
    du_lieu = tao_moi_truong()

    chay(quan_ly_sach.them_sach, du_lieu, ["S100", "Sách thử", "Tác giả A", "Thể loại B", "3"],
         "Thêm sách hợp lệ")
    s = sach(du_lieu, "S100")
    kiem_tra("Sách mới có trong bộ nhớ, còn lại = tổng = 3, lượt mượn = 0",
             s is not None and s["tong_so"] == 3 and s["con_lai"] == 3 and s["luot_muon"] == 0)
    moi = doc_lai_tu_file()
    kiem_tra("Thêm sách tự động lưu ra file", quan_ly_sach.tim_sach_theo_ma(moi["sach"], "S100") is not None)

    so_luong_truoc = len(du_lieu["sach"])
    ra = chay(quan_ly_sach.them_sach, du_lieu,
              ["S001", "S101", "", "Tên B", "TG", "TL", "-5", "abc", "0", "4"],
              "Thêm sách với mã trùng, bỏ trống, số âm, sai kiểu")
    kiem_tra("Báo lỗi mã sách trùng", "đã tồn tại" in ra)
    kiem_tra("Báo lỗi bỏ trống", "không được bỏ trống" in ra)
    kiem_tra("Báo lỗi số âm / sai kiểu / bằng 0", "lớn hơn hoặc bằng 1" in ra and "số nguyên hợp lệ" in ra)
    kiem_tra("Chỉ thêm đúng 1 sách (S101), S001 không bị nhân đôi",
             len(du_lieu["sach"]) == so_luong_truoc + 1 and sach(du_lieu, "S101")["tong_so"] == 4)

    chay(quan_ly_sach.them_sach, du_lieu, ["0"], "Hủy thêm sách bằng 0")
    kiem_tra("Hủy thêm sách: không đổi", len(du_lieu["sach"]) == so_luong_truoc + 1)

    ra = chay(quan_ly_sach.cap_nhat_sach, du_lieu,
              ["S100", "", "Tác giả mới", "", "5", "9", "4"], "Cập nhật sách")
    s = sach(du_lieu, "S100")
    kiem_tra("Enter giữ nguyên tên và thể loại; đổi tác giả, tổng = 5, còn lại = 4",
             s["ten_sach"] == "Sách thử" and s["tac_gia"] == "Tác giả mới"
             and s["the_loai"] == "Thể loại B" and s["tong_so"] == 5 and s["con_lai"] == 4)
    kiem_tra("Không cho số còn lại lớn hơn tổng (nhập 9 bị từ chối)", "nhỏ hơn hoặc bằng 5" in ra)
    moi = doc_lai_tu_file()
    kiem_tra("Cập nhật sách đã lưu ra file",
             quan_ly_sach.tim_sach_theo_ma(moi["sach"], "S100")["con_lai"] == 4)
    ra = chay(quan_ly_sach.cap_nhat_sach, du_lieu, ["S777"], "Cập nhật sách không tồn tại")
    kiem_tra("Báo không tìm thấy sách", "Không tìm thấy sách" in ra)

    chay(quan_ly_sach.xoa_sach, du_lieu, ["S100", "k"], "Xóa sách nhưng chọn không xác nhận")
    kiem_tra("Từ chối xác nhận: sách vẫn còn", sach(du_lieu, "S100") is not None)
    ra = chay(quan_ly_sach.xoa_sach, du_lieu, ["S004"], "Xóa sách đang có phiếu chưa trả")
    kiem_tra("Không cho xóa sách đang được mượn", "Không thể xóa" in ra and sach(du_lieu, "S004") is not None)
    chay(quan_ly_sach.xoa_sach, du_lieu, ["S100", "c"], "Xóa sách có xác nhận")
    kiem_tra("Xóa xong: sách biến mất khỏi bộ nhớ và file",
             sach(du_lieu, "S100") is None
             and quan_ly_sach.tim_sach_theo_ma(doc_lai_tu_file()["sach"], "S100") is None)
    ra = chay(quan_ly_sach.kiem_tra_ma_sach, du_lieu, ["s001"], "Kiểm tra mã đã tồn tại (gõ thường)")
    kiem_tra("Nhận ra mã S001 đã tồn tại", "ĐÃ tồn tại" in ra)
    ra = chay(quan_ly_sach.kiem_tra_ma_sach, du_lieu, ["S555"], "Kiểm tra mã chưa dùng")
    kiem_tra("Nhận ra mã S555 chưa tồn tại", "CHƯA tồn tại" in ra)

    ra = chay(quan_ly_sach.menu_quan_ly_sach, du_lieu, ["x", "2", "", "5", "S001", "", "0"],
              "Menu quản lý sách")
    kiem_tra("Menu: báo lựa chọn sai, vẫn chạy tiếp và hiển thị danh sách",
             "Lựa chọn không hợp lệ" in ra and "Dế Mèn phiêu lưu ký" in ra)


def kt_quan_ly_doc_gia():
    nhom("5. Quản lý độc giả (thêm, sửa, xóa)")
    du_lieu = tao_moi_truong()
    ra = chay(quan_ly_doc_gia.them_doc_gia, du_lieu,
              ["DG001", "DG100", "Nguyễn Test", "abc", "01/01/2999", "20/05/2000",
               "123", "0987654321", "Hà Nội", "sai-email", "test@example.com"],
              "Thêm độc giả (mã trùng, ngày sinh sai/tương lai, sdt sai, email sai)")
    dg = quan_ly_doc_gia.tim_doc_gia_theo_ma(du_lieu["doc_gia"], "DG100")
    kiem_tra("Độc giả DG100 được thêm với dữ liệu đúng kiểu",
             dg is not None and dg["ngay_sinh"] == date(2000, 5, 20)
             and dg["so_dien_thoai"] == "0987654321" and dg["email"] == "test@example.com")
    kiem_tra("Báo lỗi mã độc giả trùng", "đã tồn tại" in ra)
    kiem_tra("Báo lỗi ngày sinh sai định dạng và ngày sinh ở tương lai",
             "dd/mm/yyyy" in ra and "trước ngày hôm nay" in ra)
    kiem_tra("Báo lỗi số điện thoại và email sai", "9 đến 11 chữ số" in ra and "Email không hợp lệ" in ra)
    kiem_tra("DG001 không bị nhân đôi", len([d for d in du_lieu["doc_gia"] if d["ma_doc_gia"] == "DG001"]) == 1)
    kiem_tra("Thêm độc giả tự động lưu file",
             quan_ly_doc_gia.tim_doc_gia_theo_ma(doc_lai_tu_file()["doc_gia"], "DG100") is not None)

    chay(quan_ly_doc_gia.cap_nhat_doc_gia, du_lieu,
         ["DG001", "Nguyễn Văn Hùng Mới", "", "", "", ""], "Cập nhật họ tên độc giả")
    kiem_tra("Họ tên mới được lưu", quan_ly_doc_gia.tim_doc_gia_theo_ma(du_lieu["doc_gia"], "DG001")["ho_ten"]
             == "Nguyễn Văn Hùng Mới")
    kiem_tra("Họ tên trong các phiếu của độc giả được đồng bộ",
             phieu(du_lieu, "PM001")["ho_ten"] == "Nguyễn Văn Hùng Mới"
             and phieu(du_lieu, "PM018")["ho_ten"] == "Nguyễn Văn Hùng Mới")

    ra = chay(quan_ly_doc_gia.xoa_doc_gia, du_lieu, ["DG002"], "Xóa độc giả đang mượn sách chưa trả")
    kiem_tra("Không cho xóa độc giả đang có sách chưa trả",
             "Không thể xóa" in ra and quan_ly_doc_gia.tim_doc_gia_theo_ma(du_lieu["doc_gia"], "DG002"))
    chay(quan_ly_doc_gia.xoa_doc_gia, du_lieu, ["DG100", "k"], "Xóa độc giả, không xác nhận")
    kiem_tra("Từ chối xác nhận: độc giả vẫn còn",
             quan_ly_doc_gia.tim_doc_gia_theo_ma(du_lieu["doc_gia"], "DG100") is not None)
    chay(quan_ly_doc_gia.xoa_doc_gia, du_lieu, ["DG100", "c"], "Xóa độc giả có xác nhận")
    kiem_tra("Xóa độc giả xong: mất khỏi bộ nhớ và file",
             quan_ly_doc_gia.tim_doc_gia_theo_ma(du_lieu["doc_gia"], "DG100") is None
             and quan_ly_doc_gia.tim_doc_gia_theo_ma(doc_lai_tu_file()["doc_gia"], "DG100") is None)
    chay(quan_ly_doc_gia.xoa_doc_gia, du_lieu, ["DG008", "c"], "Xóa độc giả chỉ có phiếu đã trả")
    kiem_tra("Độc giả không còn sách chưa trả thì xóa được",
             quan_ly_doc_gia.tim_doc_gia_theo_ma(du_lieu["doc_gia"], "DG008") is None)
    ra = chay(quan_ly_doc_gia.menu_quan_ly_doc_gia, du_lieu, ["9", "2", "", "5", "DG001", "", "0"],
              "Menu quản lý độc giả")
    kiem_tra("Menu độc giả chạy tốt", "Lựa chọn không hợp lệ" in ra and "Nguyễn Văn Hùng Mới" in ra)


def kt_muon_sach():
    nhom("6. Tạo phiếu mượn")
    du_lieu = tao_moi_truong()
    s3_truoc = dict(sach(du_lieu, "S003"))
    so_phieu_truoc = len(du_lieu["phieu"])

    ra = chay(quan_ly_muon_tra.tao_phieu_muon, du_lieu,
              ["S999", "S004", "S003", "DG999", "DG005", "", "", "c"],
              "Tạo phiếu: sách không tồn tại, sách hết, độc giả không tồn tại")
    kiem_tra("Báo mã sách không tồn tại", "Mã sách 'S999' không tồn tại" in ra)
    kiem_tra("Không cho mượn khi sách hết (S004 còn 0)", "đã hết" in ra)
    kiem_tra("Báo mã độc giả không tồn tại", "Mã độc giả 'DG999' không tồn tại" in ra)
    kiem_tra("Tự hiển thị tên sách và họ tên độc giả",
             "Tắt đèn" in ra and "Hoàng Đức Anh" in ra)
    p = phieu(du_lieu, "PM019")
    kiem_tra("Mã phiếu tự tạo là PM019 và duy nhất",
             p is not None and len(du_lieu["phieu"]) == so_phieu_truoc + 1)
    kiem_tra("Phiếu mới đúng sách, độc giả, họ tên, ngày mượn hôm nay, hạn +14 ngày, chưa trả",
             p["ma_sach"] == "S003" and p["ma_doc_gia"] == "DG005" and p["ho_ten"] == "Hoàng Đức Anh"
             and p["ngay_muon"] == date.today() and p["han_tra"] == date.today() + timedelta(days=14)
             and p["ngay_tra"] is None and p["trang_thai"] == "Đang mượn")
    s3 = sach(du_lieu, "S003")
    kiem_tra("Số lượng còn lại giảm 1", s3["con_lai"] == s3_truoc["con_lai"] - 1)
    kiem_tra("Lượt mượn tăng 1", s3["luot_muon"] == s3_truoc["luot_muon"] + 1)
    moi = doc_lai_tu_file()
    kiem_tra("Phiếu mới và số lượng sách đã được lưu ra file",
             quan_ly_muon_tra.tim_phieu_theo_ma(moi["phieu"], "PM019") is not None
             and quan_ly_sach.tim_sach_theo_ma(moi["sach"], "S003")["con_lai"] == s3["con_lai"])

    ra = chay(quan_ly_muon_tra.tao_phieu_muon, du_lieu,
              ["S003", "DG005", ngay_chuoi(-5), "32/13/2026", ngay_chuoi(-10), ngay_chuoi(3), "c"],
              "Tạo phiếu: ngày sai định dạng và hạn trả trước ngày mượn")
    kiem_tra("Báo lỗi ngày không hợp lệ", "dd/mm/yyyy" in ra)
    kiem_tra("Báo lỗi hạn trả trước ngày mượn", "Hạn trả không được trước ngày mượn" in ra)
    p = phieu(du_lieu, "PM020")
    kiem_tra("Phiếu PM020 tạo với ngày mượn/hạn trả đã nhập",
             p is not None and p["ngay_muon"] == date.today() - timedelta(days=5)
             and p["han_tra"] == date.today() + timedelta(days=3))

    ra = chay(quan_ly_muon_tra.tao_phieu_muon, du_lieu, ["S003", "0"],
              "Mượn S003 khi đã hết")
    s3 = sach(du_lieu, "S003")
    kiem_tra("Sau 2 lần mượn, S003 đã hết (còn lại 0) và bị chặn", s3["con_lai"] == 0 and "đã hết" in ra)

    con_lai_s5 = sach(du_lieu, "S005")["con_lai"]
    so_phieu = len(du_lieu["phieu"])
    chay(quan_ly_muon_tra.tao_phieu_muon, du_lieu, ["S001", "DG001", "", "", "k"],
         "Tạo phiếu nhưng không xác nhận")
    kiem_tra("Không xác nhận: không tạo phiếu, không đổi số lượng",
             len(du_lieu["phieu"]) == so_phieu and sach(du_lieu, "S001")["con_lai"] == 5)
    chay(quan_ly_muon_tra.tao_phieu_muon, du_lieu, ["0"], "Hủy tạo phiếu")
    kiem_tra("Hủy bằng 0: không đổi", len(du_lieu["phieu"]) == so_phieu)
    ra = chay(quan_ly_muon_tra.tao_phieu_muon, du_lieu,
              ["S002", "DG003", ngay_chuoi(-30), ngay_chuoi(-20), "c"],
              "Tạo phiếu với hạn trả đã qua (quá hạn ngay)")
    kiem_tra("Phiếu có hạn trả đã qua tự được tính Quá hạn 20 ngày = 100.000",
             phieu(du_lieu, "PM021")["trang_thai"] == "Quá hạn"
             and phieu(du_lieu, "PM021")["so_ngay_qua_han"] == 20
             and phieu(du_lieu, "PM021")["tien_phat"] == 100000)
    ma_phieu = [p["ma_phieu"] for p in du_lieu["phieu"]]
    kiem_tra("Mã phiếu không trùng nhau", len(ma_phieu) == len(set(ma_phieu)))
    ra = chay(quan_ly_muon_tra.menu_muon_sach, du_lieu, ["z", "2", "", "3", "", "0"], "Menu mượn sách")
    kiem_tra("Menu mượn: danh sách phiếu và kiểm tra quá hạn hoạt động",
             "DANH SÁCH PHIẾU MƯỢN" in ra and "PHIẾU MƯỢN QUÁ HẠN" in ra and "PM018" in ra)


def kt_tra_sach():
    nhom("7. Trả sách, cập nhật số lượng, tính tiền phạt")
    du_lieu = tao_moi_truong()

    ra = chay(quan_ly_muon_tra.tra_sach, du_lieu, ["PM999", "PM001", "0"],
              "Trả sách: phiếu không tồn tại, phiếu đã trả")
    kiem_tra("Báo phiếu không tồn tại", "Phiếu mượn 'PM999' không tồn tại" in ra)
    kiem_tra("Không cho trả phiếu đã trả trước đó", "không thể trả lần nữa" in ra)

    s2_truoc = sach(du_lieu, "S002")["con_lai"]
    ra = chay(quan_ly_muon_tra.tra_sach, du_lieu, ["PM015", "", "c"], "Trả PM015 (quá hạn 11 ngày)")
    p = phieu(du_lieu, "PM015")
    kiem_tra("Trả PM015: ngày trả hôm nay, trạng thái Đã trả",
             p["ngay_tra"] == date.today() and p["trang_thai"] == "Đã trả")
    kiem_tra("Quá hạn 11 ngày, tiền phạt 55.000", p["so_ngay_qua_han"] == 11 and p["tien_phat"] == 55000)
    kiem_tra("Hiển thị tiền phạt khi trả sách", "55.000" in ra)
    kiem_tra("Số lượng còn lại của S002 tăng 1", sach(du_lieu, "S002")["con_lai"] == s2_truoc + 1)
    moi = doc_lai_tu_file()
    p_file = quan_ly_muon_tra.tim_phieu_theo_ma(moi["phieu"], "PM015")
    kiem_tra("Đã lưu file: PM015 có ngày trả, Đã trả, phạt 55000",
             p_file["ngay_tra"] == date.today() and p_file["tien_phat"] == 55000
             and p_file["trang_thai"] == "Đã trả")
    ra = chay(quan_ly_muon_tra.tra_sach, du_lieu, ["PM015", "0"], "Trả PM015 lần thứ hai")
    kiem_tra("Trả lần hai bị chặn, số lượng không đổi",
             "không thể trả lần nữa" in ra and sach(du_lieu, "S002")["con_lai"] == s2_truoc + 1)

    s3_truoc = sach(du_lieu, "S003")["con_lai"]
    ra = chay(quan_ly_muon_tra.tra_sach, du_lieu, ["PM010", "01/01/2020", "", "c"],
              "Trả sách với ngày trả trước ngày mượn")
    kiem_tra("Báo lỗi ngày trả trước ngày mượn", "Ngày trả không được trước ngày mượn" in ra)
    p = phieu(du_lieu, "PM010")
    kiem_tra("Trả trong hạn: quá hạn 0 ngày, phạt 0",
             p["trang_thai"] == "Đã trả" and p["so_ngay_qua_han"] == 0 and p["tien_phat"] == 0)
    kiem_tra("S003 tăng 1 cuốn", sach(du_lieu, "S003")["con_lai"] == s3_truoc + 1)

    chay(quan_ly_muon_tra.tra_sach, du_lieu, ["PM011", "", "k"], "Trả sách nhưng không xác nhận")
    kiem_tra("Không xác nhận: phiếu vẫn chưa trả", phieu(du_lieu, "PM011")["ngay_tra"] is None
             and phieu(du_lieu, "PM011")["trang_thai"] == "Đang mượn")

    s6_truoc = sach(du_lieu, "S006")["con_lai"]
    ra = chay(quan_ly_muon_tra.tra_sach, du_lieu, ["PM016", ngay_chuoi(-2), "c"],
              "Trả PM016 với ngày trả nhập tay (hạn trả cách đây 6 ngày)")
    p = phieu(du_lieu, "PM016")
    kiem_tra("Trả ngày hôm kia: quá hạn 4 ngày, phạt 20.000",
             p["so_ngay_qua_han"] == 4 and p["tien_phat"] == 20000 and "20.000" in ra)
    kiem_tra("S006 tăng 1 cuốn", sach(du_lieu, "S006")["con_lai"] == s6_truoc + 1)

    ra = chay(quan_ly_muon_tra.xem_thong_tin_phieu, du_lieu, ["PM018"], "Xem thông tin phiếu chưa trả")
    kiem_tra("Phiếu chưa trả quá hạn: tính theo ngày hiện tại (16 ngày, 80.000)",
             "16" in ra and "80.000" in ra and "tạm tính" in ra)
    ra = chay(quan_ly_muon_tra.xem_thong_tin_phieu, du_lieu, ["PM888"], "Xem phiếu không tồn tại")
    kiem_tra("Báo phiếu không tồn tại", "không tồn tại" in ra)
    ra = chay(quan_ly_muon_tra.menu_tra_sach, du_lieu, ["8", "3", "", "4", "", "2", "PM002", "", "0"],
              "Menu trả sách")
    kiem_tra("Menu trả: danh sách chưa trả / đã trả / xem phiếu",
             "PHIẾU CHƯA TRẢ" in ra and "PHIẾU ĐÃ TRẢ" in ra and "30.000" in ra)

    # Mượn rồi trả: số lượng trở lại như ban đầu
    du_lieu2 = tao_moi_truong()
    truoc = dict(sach(du_lieu2, "S001"))
    chay(quan_ly_muon_tra.tao_phieu_muon, du_lieu2, ["S001", "DG001", "", "", "c"])
    chay(quan_ly_muon_tra.tra_sach, du_lieu2, ["PM019", "", "c"])
    sau = sach(du_lieu2, "S001")
    kiem_tra("Mượn rồi trả: còn lại trở về ban đầu, lượt mượn tăng 1",
             sau["con_lai"] == truoc["con_lai"] and sau["luot_muon"] == truoc["luot_muon"] + 1)


def kt_tim_kiem():
    nhom("8. Tìm kiếm")
    du_lieu = tao_moi_truong()
    ds_sach, ds_dg, ds_phieu = du_lieu["sach"], du_lieu["doc_gia"], du_lieu["phieu"]
    ma = lambda ds, k: sorted(x[k] for x in ds)
    kiem_tra("Sách theo tên 'python' (thường) tìm S010, S012",
             ma(tim_kiem.tim_sach(ds_sach, "ten", "python"), "ma_sach") == ["S010", "S012"])
    kiem_tra("Sách theo tên 'PYTHON' (hoa) cho cùng kết quả",
             ma(tim_kiem.tim_sach(ds_sach, "ten", "PYTHON"), "ma_sach") == ["S010", "S012"])
    kiem_tra("Sách theo tên gần đúng 'pyton'",
             "S012" in ma(tim_kiem.tim_sach(ds_sach, "ten", "pyton"), "ma_sach"))
    kiem_tra("Sách theo tên không dấu 'de men'",
             ma(tim_kiem.tim_sach(ds_sach, "ten", "de men"), "ma_sach") == ["S001"])
    kiem_tra("Sách theo tác giả 'nguyen nhat anh'",
             ma(tim_kiem.tim_sach(ds_sach, "tac_gia", "nguyen nhat anh"), "ma_sach") == ["S014", "S015"])
    kiem_tra("Sách theo mã 's00' (không phân biệt hoa/thường)",
             len(tim_kiem.tim_sach(ds_sach, "ma", "s00")) == 9)
    kiem_tra("Sách theo mã đầy đủ 'S010'", ma(tim_kiem.tim_sach(ds_sach, "ma", "S010"), "ma_sach") == ["S010"])
    kiem_tra("Sách không có kết quả -> list rỗng", tim_kiem.tim_sach(ds_sach, "ten", "zzzzqqq") == [])
    kiem_tra("Độc giả theo họ tên 'hung'",
             ma(tim_kiem.tim_doc_gia(ds_dg, "ten", "hung"), "ma_doc_gia") == ["DG001"])
    kiem_tra("Độc giả theo mã 'dg00' ", len(tim_kiem.tim_doc_gia(ds_dg, "ma", "dg00")) == 9)
    kiem_tra("Độc giả không có kết quả", tim_kiem.tim_doc_gia(ds_dg, "ten", "xyzxyz") == [])
    kiem_tra("Phiếu theo mã phiếu 'pm015'", ma(tim_kiem.tim_phieu(ds_phieu, "ma_phieu", "pm015"), "ma_phieu") == ["PM015"])
    kiem_tra("Phiếu theo mã sách 'S001' có 2 phiếu",
             ma(tim_kiem.tim_phieu(ds_phieu, "ma_sach", "S001"), "ma_phieu") == ["PM001", "PM007"])
    kiem_tra("Phiếu theo mã độc giả 'DG001' có 3 phiếu",
             ma(tim_kiem.tim_phieu(ds_phieu, "ma_doc_gia", "DG001"), "ma_phieu") == ["PM001", "PM004", "PM018"])
    kiem_tra("Phiếu theo trạng thái Quá hạn = 4, Đang mượn = 5, Đã trả = 9",
             len(tim_kiem.tim_phieu(ds_phieu, "trang_thai", "Quá hạn")) == 4
             and len(tim_kiem.tim_phieu(ds_phieu, "trang_thai", "Đang mượn")) == 5
             and len(tim_kiem.tim_phieu(ds_phieu, "trang_thai", "Đã trả")) == 9)
    ra = chay(tim_kiem.menu_tim_sach, du_lieu, ["2", "zzzzqqq"], "Menu tìm sách không có kết quả")
    kiem_tra("Thông báo rõ ràng khi không tìm thấy", "Không tìm thấy sách nào" in ra)
    ra = chay(tim_kiem.menu_tim_doc_gia, du_lieu, ["2", "HÙNG"], "Menu tìm độc giả theo tên có dấu")
    kiem_tra("Menu tìm độc giả hiển thị kết quả", "Nguyễn Văn Hùng" in ra and "Tìm thấy 1" in ra)
    ra = chay(tim_kiem.menu_tim_phieu, du_lieu, ["4", "3"], "Menu tìm phiếu theo trạng thái")
    kiem_tra("Menu tìm phiếu quá hạn hiển thị 4 phiếu", "Tìm thấy 4" in ra)
    ra = chay(tim_kiem.menu_tim_kiem, du_lieu, ["1", "1", "S001", "", "7", "0"], "Menu tìm kiếm tổng")
    kiem_tra("Menu tìm kiếm tổng hoạt động và báo lựa chọn sai", "Lựa chọn không hợp lệ" in ra)


def kt_sap_xep():
    nhom("9. Sắp xếp")
    du_lieu = tao_moi_truong()
    thu_tu_goc = [s["ma_sach"] for s in du_lieu["sach"]]
    tang = sap_xep.sap_xep_sach_theo_ten(du_lieu["sach"], True)
    giam = sap_xep.sap_xep_sach_theo_ten(du_lieu["sach"], False)
    kiem_tra("Sách A-Z: đầu 'Automate...', cuối 'Tuổi trẻ...'",
             tang[0]["ma_sach"] == "S010" and tang[-1]["ma_sach"] == "S016")
    kiem_tra("Sách Z-A là đảo ngược của A-Z", [s["ma_sach"] for s in giam] == [s["ma_sach"] for s in reversed(tang)])
    kiem_tra("Sắp xếp không làm thay đổi danh sách gốc", [s["ma_sach"] for s in du_lieu["sach"]] == thu_tu_goc)
    cu_moi = sap_xep.sap_xep_phieu_theo_ngay_muon(du_lieu["phieu"], True)
    moi_cu = sap_xep.sap_xep_phieu_theo_ngay_muon(du_lieu["phieu"], False)
    kiem_tra("Phiếu theo ngày mượn cũ -> mới: PM001 đầu, PM014 cuối",
             cu_moi[0]["ma_phieu"] == "PM001" and cu_moi[-1]["ma_phieu"] == "PM014")
    kiem_tra("Phiếu theo ngày mượn mới -> cũ: PM014 đầu, PM001 cuối",
             moi_cu[0]["ma_phieu"] == "PM014" and moi_cu[-1]["ma_phieu"] == "PM001")
    ngay_tang = all(cu_moi[i]["ngay_muon"] <= cu_moi[i + 1]["ngay_muon"] for i in range(len(cu_moi) - 1))
    kiem_tra("Dãy ngày mượn thực sự tăng dần", ngay_tang)
    theo_ten = sap_xep.sap_xep_phieu_theo_ten_sach(du_lieu["phieu"], du_lieu["sach"], True)
    kiem_tra("Phiếu theo tên sách A-Z: đầu là sách 'Automate...' (PM006)", theo_ten[0]["ma_phieu"] == "PM006")
    ra = chay(sap_xep.menu_sap_xep, du_lieu,
              ["1", "2", "", "2", "1", "", "3", "2", "", "1", "0", "9", "0"], "Menu sắp xếp")
    kiem_tra("Menu sắp xếp: có cả 3 kiểu sắp xếp và báo lựa chọn sai",
             "THEO TÊN SÁCH" in ra and "THEO NGÀY MƯỢN" in ra and "Lựa chọn không hợp lệ" in ra)


def kt_thong_ke():
    nhom("10. Thống kê")
    du_lieu = tao_moi_truong()
    tk = thong_ke.tinh_thong_ke(du_lieu)
    kiem_tra("Tổng đầu sách 16, tổng số lượng 50, kho còn 41",
             tk["tong_dau_sach"] == 16 and tk["tong_so_luong"] == 50 and tk["tong_con_lai"] == 41)
    kiem_tra("Tổng độc giả 11, tổng phiếu 18", tk["tong_doc_gia"] == 11 and tk["tong_phieu"] == 18)
    kiem_tra("Đang mượn 5, đã trả 9, quá hạn 4",
             tk["so_dang_muon"] == 5 and tk["so_da_tra"] == 9 and tk["so_qua_han"] == 4)
    kiem_tra("Danh sách đang mượn gồm 9 phiếu chưa trả, quá hạn gồm 4",
             len(tk["ds_dang_muon"]) == 9 and len(tk["ds_qua_han"]) == 4)
    kiem_tra("Sách mượn nhiều nhất: S001, S002, S006, S009 (2 lượt)",
             sorted(s["ma_sach"] for s in tk["sach_nhieu_nhat"]) == ["S001", "S002", "S006", "S009"])
    kiem_tra("Sách mượn ít nhất: S015, S016 (0 lượt)",
             sorted(s["ma_sach"] for s in tk["sach_it_nhat"]) == ["S015", "S016"])
    kiem_tra("Tổng tiền phạt 280.000", tk["tong_tien_phat"] == 280000)
    ra = chay(thong_ke.thong_ke_day_du, du_lieu, [], "Báo cáo thống kê đầy đủ")
    kiem_tra("Báo cáo in đủ các mục", "THỐNG KÊ TỔNG QUAN" in ra and "ĐANG ĐƯỢC MƯỢN" in ra
             and "ĐÃ QUÁ HẠN" in ra and "NHIỀU NHẤT" in ra and "ÍT NHẤT" in ra)
    ra = chay(thong_ke.menu_thong_ke, du_lieu, ["2", "", "3", "", "4", "", "5", "", "8", "0"], "Menu thống kê")
    kiem_tra("Menu thống kê chạy đủ các mục", "Tổng số đầu sách" in ra and "Lựa chọn không hợp lệ" in ra)

    rong = {"sach": [], "doc_gia": [], "phieu": []}
    ra = chay(thong_ke.thong_ke_day_du, rong, [], "Thống kê khi chưa có dữ liệu")
    kiem_tra("Dữ liệu rỗng: thông báo phù hợp, không lỗi", "Chưa có dữ liệu" in ra)
    ra = chay(thong_ke.menu_thong_ke, rong, ["1", "", "2", "", "5", "", "0"], "Menu thống kê dữ liệu rỗng")
    kiem_tra("Menu thống kê với dữ liệu rỗng không bị lỗi", "Chưa có dữ liệu" in ra)
    ra = chay(lambda d: thong_ke.in_ds_muon_nhieu_it(thong_ke.tinh_thong_ke(d)), rong, [], "Mượn nhiều/ít khi rỗng")
    kiem_tra("Báo chưa có sách", "Chưa có sách" in ra)
    chua_muon = {"sach": [dict(tao_du_lieu_mau.tao_du_lieu()["sach"][0], luot_muon=0)], "doc_gia": [], "phieu": []}
    ra = chay(lambda d: thong_ke.in_ds_muon_nhieu_it(thong_ke.tinh_thong_ke(d)), chua_muon, [], "Chưa ai mượn")
    kiem_tra("Có sách nhưng chưa có lượt mượn: thông báo phù hợp", "Chưa có lượt mượn nào" in ra)
    ra = chay(lambda d: quan_ly_sach.hien_thi_ds_sach(d["sach"]), rong, [], "Hiển thị danh sách sách rỗng")
    kiem_tra("Danh sách sách rỗng: thông báo, không lỗi", "Chưa có sách nào" in ra)
    ra = chay(lambda d: quan_ly_muon_tra.hien_thi_ds_phieu(d["phieu"], d["sach"]), rong, [], "Danh sách phiếu rỗng")
    kiem_tra("Danh sách phiếu rỗng: thông báo, không lỗi", "Không có phiếu mượn nào" in ra)


def kt_file():
    nhom("11. Lưu / đọc file và xử lý file lỗi")
    du_lieu = tao_moi_truong()
    chay(quan_ly_sach.them_sach, du_lieu, ["S200", "Sách Lưu Thử", "Tác giả", "TL", "2"])
    chay(quan_ly_muon_tra.tao_phieu_muon, du_lieu, ["S200", "DG001", "", "", "c"])
    with contextlib.redirect_stdout(io.StringIO()):
        luu_ok = xu_ly_file.luu_tat_ca(du_lieu)
    kiem_tra("Lưu thủ công thành công", luu_ok)
    moi = doc_lai_tu_file()
    kiem_tra("Đọc lại giống hệt dữ liệu trong bộ nhớ",
             moi["sach"] == du_lieu["sach"] and moi["doc_gia"] == du_lieu["doc_gia"]
             and moi["phieu"] == du_lieu["phieu"])
    con_tmp = [t for t in os.listdir(xu_ly_file.THU_MUC_DATA) if t.endswith(".tmp")]
    kiem_tra("Không còn file .tmp sau khi lưu", con_tmp == [])

    # Mất dữ liệu trong bộ nhớ rồi đọc lại
    du_lieu["sach"].clear()
    with contextlib.redirect_stdout(io.StringIO()):
        xu_ly_file.doc_tat_ca(du_lieu)
    kiem_tra("Chức năng đọc lại dữ liệu khôi phục được danh sách", len(du_lieu["sach"]) == 17)

    # File chưa tồn tại
    for duong_dan in (xu_ly_file.FILE_SACH, xu_ly_file.FILE_DOC_GIA, xu_ly_file.FILE_PHIEU):
        os.remove(duong_dan)
    rong = {"sach": [1], "doc_gia": [1], "phieu": [1]}
    ra = chay(lambda d: xu_ly_file.doc_tat_ca(d), rong, [], "Đọc khi file chưa tồn tại")
    kiem_tra("File chưa tồn tại: trả về danh sách rỗng, tạo file mới, không lỗi",
             rong["sach"] == [] and rong["doc_gia"] == [] and rong["phieu"] == []
             and os.path.exists(xu_ly_file.FILE_SACH) and "Chưa có file" in ra)

    # File có dòng lỗi
    with open(xu_ly_file.FILE_SACH, "w", encoding="utf-8") as f:
        f.write("# tiêu đề\n"
                "S001|Sách A|TG|TL|5|3|2\n"
                "S002|Sách B|TG|TL|abc|3|2\n"
                "S003|Sách C|TG|TL|2|5|0\n"
                "S004|Sách D|TG|TL|-1|0|0\n"
                "S001|Trùng mã|TG|TL|1|1|0\n"
                "S005|Thiếu trường|TG\n"
                "|Thiếu mã|TG|TL|1|1|0\n"
                "\n"
                "S006|Sách E|TG|TL|4|4|0\n")
    with open(xu_ly_file.FILE_DOC_GIA, "w", encoding="utf-8") as f:
        f.write("DG001|An|01/01/2000|0900000001|HN|an@example.com\n"
                "DG002|Bình|31/02/2000|0900000002|HN|binh@example.com\n")
    with open(xu_ly_file.FILE_PHIEU, "w", encoding="utf-8") as f:
        f.write("PM001|S001|DG001|An|01/01/2026|15/01/2026||Đang mượn|0|0\n"
                "PM002|S001|DG001|An|10/01/2026|01/01/2026||Đang mượn|0|0\n"
                "PM003|S001|DG001|An|01/01/2026|15/01/2026|xx/yy/zzzz|Đã trả|0|0\n"
                "PM004|S001|DG001|An|01/01/2026|15/01/2026|20/01/2026|Đã trả|5|25000\n")
    loi = {"sach": [], "doc_gia": [], "phieu": []}
    ra = chay(lambda d: xu_ly_file.doc_tat_ca(d), loi, [], "Đọc file có dòng lỗi")
    kiem_tra("Chỉ đọc các dòng hợp lệ của sach.txt (S001, S006)",
             sorted(s["ma_sach"] for s in loi["sach"]) == ["S001", "S006"])
    kiem_tra("Thông báo rõ dòng nào bị bỏ qua và vì sao",
             "dòng 3" in ra and "dòng 4" in ra and "còn lại lớn hơn tổng" in ra and "trùng mã" in ra)
    kiem_tra("Dòng ngày sinh sai bị bỏ qua (chỉ còn DG001)", [d["ma_doc_gia"] for d in loi["doc_gia"]] == ["DG001"])
    kiem_tra("Phiếu hạn trả trước ngày mượn / ngày trả sai bị bỏ qua (còn PM001, PM004)",
             sorted(p["ma_phieu"] for p in loi["phieu"]) == ["PM001", "PM004"])
    kiem_tra("Phiếu đã trả muộn 5 ngày vẫn giữ phạt 25.000",
             [p for p in loi["phieu"] if p["ma_phieu"] == "PM004"][0]["tien_phat"] == 25000)
    kiem_tra("File gốc bị lỗi được sao lưu thành .loi.bak (không mất dữ liệu cũ)",
             os.path.exists(xu_ly_file.FILE_SACH + ".loi.bak")
             and "Thiếu trường" in open(xu_ly_file.FILE_SACH + ".loi.bak", encoding="utf-8").read())

    # File không phải UTF-8 / hỏng
    with open(xu_ly_file.FILE_SACH, "wb") as f:
        f.write(b"\xff\xfe\x00S001|\x80\x81|bad")
    hong = {"sach": [], "doc_gia": [], "phieu": []}
    ra = chay(lambda d: d.update(sach=xu_ly_file.doc_sach()), hong, [], "Đọc file hỏng (không phải UTF-8)")
    kiem_tra("File hỏng: báo lỗi, trả về danh sách rỗng, không văng lỗi", hong["sach"] == [] and "Không thể đọc" in ra)

    # File có BOM
    with open(xu_ly_file.FILE_SACH, "w", encoding="utf-8-sig") as f:
        f.write("S001|Sách BOM|TG|TL|1|1|0\n")
    kiem_tra("File UTF-8 có BOM đọc bình thường", xu_ly_file.doc_sach()[0]["ma_sach"] == "S001")

    # Ghi lỗi
    with contextlib.redirect_stdout(io.StringIO()) as bo_dem:
        ok = xu_ly_file.ghi_file("/proc/khong_ton_tai/x.txt", "#", [])
    kiem_tra("Không ghi được file: trả về False, có thông báo, không văng lỗi",
             ok is False and "Không thể ghi file" in bo_dem.getvalue())


def kt_tien_trinh_that():
    nhom("12. Chạy main.py như người dùng thật (tiến trình riêng, đầu vào giả lập)")
    thu_muc = tempfile.mkdtemp(prefix="thuvien_e2e_")
    du_an = os.path.join(thu_muc, "QuanLyThuVien")
    shutil.copytree(THU_MUC_DU_AN, du_an, ignore=shutil.ignore_patterns("__pycache__", "*.bak", "*.tmp"))
    # Tạo dữ liệu mẫu mới trong bản sao để mốc ngày luôn đúng với hôm nay
    mt = dict(os.environ, PYTHONIOENCODING="utf-8")
    subprocess.run([sys.executable, "tao_du_lieu_mau.py"], cwd=du_an, env=mt,
                   capture_output=True, check=True)

    def chay_main(dong, cwd=du_an, duong_dan_main=None):
        return subprocess.run([sys.executable, duong_dan_main or "main.py"], cwd=cwd, env=mt,
                              input="\n".join(dong) + "\n", capture_output=True,
                              text=True, encoding="utf-8", timeout=60)

    # Kịch bản: mượn S003 cho DG005, trả phiếu mới, lưu, thoát
    kich_ban = ["abc", "99",                       # lựa chọn sai ở menu chính
                "3", "1", "S003", "DG005", "", "", "c", "", "0",      # mượn sách
                "4", "1", "PM019", "", "c", "", "0",                   # trả sách
                "8", "",                                               # lưu thủ công
                "0", "c"]                                              # thoát
    kq = chay_main(kich_ban)
    kiem_tra("main.py chạy xong với mã thoát 0", kq.returncode == 0)
    kiem_tra("Không có lỗi Python (Traceback)", "Traceback" not in kq.stderr and "Traceback" not in kq.stdout)
    kiem_tra("Menu chính hiển thị tiếng Việt đủ 10 mục",
             "PHẦN MỀM QUẢN LÝ THƯ VIỆN" in kq.stdout and "9. ĐỌC DỮ LIỆU" in kq.stdout
             and "0. THOÁT CHƯƠNG TRÌNH" in kq.stdout)
    kiem_tra("Lựa chọn sai ở menu chính không làm thoát chương trình",
             kq.stdout.count("Lựa chọn không hợp lệ") >= 2)
    kiem_tra("Đã tạo phiếu và trả sách trong cùng phiên", "Đã tạo phiếu mượn PM019" in kq.stdout
             and "Đã ghi nhận trả sách cho phiếu PM019" in kq.stdout)
    with open(os.path.join(du_an, "data", "phieumuon.txt"), encoding="utf-8") as f:
        dong_phieu = [d for d in f.read().splitlines() if d.startswith("PM019|")]
    kiem_tra("phieumuon.txt có PM019 trạng thái Đã trả, tiền phạt 0",
             len(dong_phieu) == 1 and "|Đã trả|0|0" in dong_phieu[0])
    with open(os.path.join(du_an, "data", "sach.txt"), encoding="utf-8") as f:
        dong_s3 = [d for d in f.read().splitlines() if d.startswith("S003|")][0]
    kiem_tra("sach.txt: S003 còn lại 2/3 và lượt mượn 2 sau khi mượn rồi trả", dong_s3.endswith("|3|2|2"))

    # Chạy từ thư mục khác (như khi mở bằng VS Code ở thư mục khác)
    kq = chay_main(["7", "2", "", "0", "0", "c"], cwd=thu_muc,
                   duong_dan_main=os.path.join(du_an, "main.py"))
    kiem_tra("Chạy main.py từ thư mục khác vẫn tìm đúng thư mục data/",
             kq.returncode == 0 and "Đã đọc dữ liệu: 16 đầu sách, 11 độc giả, 19 phiếu mượn" in kq.stdout)

    # Đọc dữ liệu (chức năng 9) và nhập sai toàn bộ
    kq = chay_main(["9", "x", "k", "", "9", "c", "", "0", "c"])
    kiem_tra("Chức năng 9 có xác nhận (nhập sai được hỏi lại), đọc lại dữ liệu thành công",
             "Vui lòng nhập 'c'" in kq.stdout and kq.stdout.count("Đã đọc dữ liệu") >= 2)

    # Hết đầu vào / Ctrl+D: thoát nhẹ nhàng, có lưu
    kq = chay_main(["1"])
    kiem_tra("Hết dữ liệu nhập giữa chừng: không văng lỗi, tự lưu và thoát",
             kq.returncode == 0 and "Traceback" not in kq.stderr and "Đang lưu dữ liệu" in kq.stdout)

    # Không có thư mục data (lần chạy đầu tiên)
    shutil.rmtree(os.path.join(du_an, "data"))
    kq = chay_main(["0", "c"])
    kiem_tra("Chưa có thư mục data/: chương trình tự tạo file rỗng và vẫn chạy",
             kq.returncode == 0 and os.path.exists(os.path.join(du_an, "data", "sach.txt"))
             and "Chưa có dữ liệu" in kq.stdout)
    shutil.rmtree(thu_muc, ignore_errors=True)


def main():
    kt_du_lieu_mau()
    kt_tinh_phat()
    kt_nhap_lieu()
    kt_quan_ly_sach()
    kt_quan_ly_doc_gia()
    kt_muon_sach()
    kt_tra_sach()
    kt_tim_kiem()
    kt_sap_xep()
    kt_thong_ke()
    kt_file()
    kt_tien_trinh_that()
    print("\n" + "=" * 60)
    print(f"KẾT QUẢ: {SO_DAT} đạt, {SO_HONG} không đạt (tổng {SO_DAT + SO_HONG} phép kiểm tra)")
    if SO_HONG > 0:
        print("Các phép kiểm tra không đạt:")
        for ten in DS_HONG:
            print("  -", ten)
        sys.exit(1)


if __name__ == "__main__":
    main()
