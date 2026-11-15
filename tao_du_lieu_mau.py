# -*- coding: utf-8 -*-
"""
tao_du_lieu_mau.py - Tạo dữ liệu mẫu và ghi ra 3 file TXT trong thư mục data/.

Chạy:  python tao_du_lieu_mau.py
CẢNH BÁO: lệnh này ghi đè dữ liệu hiện có trong data/.

Dữ liệu mẫu: 16 đầu sách, 11 độc giả, 18 phiếu mượn (9 đã trả, 5 đang mượn, 4 quá hạn).
Ngày mượn / hạn trả được tính lùi từ ngày chạy script nên luôn có đủ 3 loại trạng thái.
Số lượng còn lại và lượt mượn của mỗi sách được TÍNH TỪ các phiếu nên luôn khớp nhau.
"""

import sys
from datetime import date, timedelta

import xu_ly_file
from tien_ich import cap_nhat_trang_thai_phieu, thong_bao_thanh_cong, thong_bao_canh_bao

# (mã sách, tên sách, tác giả, thể loại, tổng số lượng)
SACH_MAU = [
    ("S001", "Dế Mèn phiêu lưu ký", "Tô Hoài", "Thiếu nhi", 5),
    ("S002", "Số đỏ", "Vũ Trọng Phụng", "Văn học", 4),
    ("S003", "Tắt đèn", "Ngô Tất Tố", "Văn học", 3),
    ("S004", "Truyện Kiều", "Nguyễn Du", "Văn học", 1),
    ("S005", "Chí Phèo", "Nam Cao", "Văn học", 3),
    ("S006", "Nhà giả kim", "Paulo Coelho", "Tiểu thuyết", 4),
    ("S007", "Đắc nhân tâm", "Dale Carnegie", "Kỹ năng sống", 3),
    ("S008", "Sapiens: Lược sử loài người", "Yuval Noah Harari", "Lịch sử", 2),
    ("S009", "Clean Code", "Robert C. Martin", "Công nghệ thông tin", 4),
    ("S010", "Automate the Boring Stuff with Python", "Al Sweigart", "Công nghệ thông tin", 3),
    ("S011", "Introduction to Algorithms", "Thomas H. Cormen", "Công nghệ thông tin", 2),
    ("S012", "Python Crash Course", "Eric Matthes", "Công nghệ thông tin", 3),
    ("S013", "Lược sử thời gian", "Stephen Hawking", "Khoa học", 2),
    ("S014", "Mắt biếc", "Nguyễn Nhật Ánh", "Tiểu thuyết", 3),
    ("S015", "Cho tôi xin một vé đi tuổi thơ", "Nguyễn Nhật Ánh", "Thiếu nhi", 5),
    ("S016", "Tuổi trẻ đáng giá bao nhiêu", "Rosie Nguyễn", "Kỹ năng sống", 3),
]

# (mã độc giả, họ tên, ngày sinh, điện thoại, địa chỉ, email) - thông tin hoàn toàn giả định
DOC_GIA_MAU = [
    ("DG001", "Nguyễn Văn Hùng", date(2003, 5, 14), "0912345601", "12 Nguyễn Trãi, Hà Đông, Hà Nội", "hung.nv@example.com"),
    ("DG002", "Trần Thị Mai", date(2004, 8, 22), "0912345602", "45 Lê Lợi, Hoàn Kiếm, Hà Nội", "mai.tt@example.com"),
    ("DG003", "Lê Minh Quân", date(2002, 12, 3), "0912345603", "8 Trần Phú, Ba Đình, Hà Nội", "quan.lm@example.com"),
    ("DG004", "Phạm Thu Hà", date(2003, 1, 30), "0912345604", "21 Cầu Giấy, Cầu Giấy, Hà Nội", "ha.pt@example.com"),
    ("DG005", "Hoàng Đức Anh", date(2001, 7, 9), "0912345605", "67 Giải Phóng, Hai Bà Trưng, Hà Nội", "anh.hd@example.com"),
    ("DG006", "Vũ Thị Lan", date(2004, 3, 18), "0912345606", "5 Xuân Thủy, Cầu Giấy, Hà Nội", "lan.vt@example.com"),
    ("DG007", "Đặng Quốc Bảo", date(2002, 10, 27), "0912345607", "90 Nguyễn Chí Thanh, Đống Đa, Hà Nội", "bao.dq@example.com"),
    ("DG008", "Bùi Ngọc Linh", date(2003, 6, 6), "0912345608", "33 Phố Huế, Hai Bà Trưng, Hà Nội", "linh.bn@example.com"),
    ("DG009", "Đỗ Thanh Tùng", date(2001, 11, 11), "0912345609", "14 Tây Sơn, Đống Đa, Hà Nội", "tung.dt@example.com"),
    ("DG010", "Ngô Phương Thảo", date(2004, 2, 25), "0912345610", "72 Kim Mã, Ba Đình, Hà Nội", "thao.np@example.com"),
    ("DG011", "Dương Hải Đăng", date(2002, 9, 15), "0912345611", "28 Hoàng Quốc Việt, Cầu Giấy, Hà Nội", "dang.dh@example.com"),
]

# (mã phiếu, mã sách, mã độc giả, ngày mượn, hạn trả, ngày trả)
# Các con số là SỐ NGÀY so với hôm nay (âm = trong quá khứ); ngày trả None = chưa trả.
PHIEU_MAU = [
    # --- 9 phiếu ĐÃ TRẢ (6 đúng hạn, 3 trả muộn bị phạt) ---
    ("PM001", "S001", "DG001", -60, -46, -48),
    ("PM002", "S002", "DG002", -55, -41, -35),   # trả muộn 6 ngày
    ("PM003", "S006", "DG003", -50, -36, -40),
    ("PM004", "S007", "DG001", -45, -31, -31),   # trả đúng ngày hạn
    ("PM005", "S009", "DG004", -40, -26, -20),   # trả muộn 6 ngày
    ("PM006", "S010", "DG005", -35, -21, -25),
    ("PM007", "S001", "DG006", -30, -16, -9),    # trả muộn 7 ngày
    ("PM008", "S012", "DG007", -28, -14, -15),
    ("PM009", "S008", "DG008", -25, -11, -12),
    # --- 5 phiếu ĐANG MƯỢN (còn hạn) ---
    ("PM010", "S003", "DG002", -5, 9, None),
    ("PM011", "S005", "DG009", -3, 11, None),
    ("PM012", "S009", "DG010", -2, 12, None),
    ("PM013", "S014", "DG003", -1, 13, None),
    ("PM014", "S004", "DG011", 0, 14, None),     # S004 chỉ có 1 cuốn -> hết sách
    # --- 4 phiếu QUÁ HẠN (chưa trả, hạn trả đã qua) ---
    ("PM015", "S002", "DG004", -25, -11, None),
    ("PM016", "S006", "DG005", -20, -6, None),
    ("PM017", "S011", "DG006", -18, -4, None),
    ("PM018", "S013", "DG001", -30, -16, None),
]


def tao_du_lieu():
    """Dựng dictionary du_lieu từ các bảng mẫu ở trên."""
    hom_nay = date.today()
    ds_doc_gia = []
    ten_theo_ma = {}
    for ma, ho_ten, ngay_sinh, sdt, dia_chi, email in DOC_GIA_MAU:
        ds_doc_gia.append({"ma_doc_gia": ma, "ho_ten": ho_ten, "ngay_sinh": ngay_sinh,
                           "so_dien_thoai": sdt, "dia_chi": dia_chi, "email": email})
        ten_theo_ma[ma] = ho_ten

    ds_phieu = []
    for ma_phieu, ma_sach, ma_dg, muon, han, tra in PHIEU_MAU:
        ngay_tra = None
        if tra is not None:
            ngay_tra = hom_nay + timedelta(days=tra)
        ds_phieu.append({"ma_phieu": ma_phieu, "ma_sach": ma_sach, "ma_doc_gia": ma_dg,
                         "ho_ten": ten_theo_ma[ma_dg],
                         "ngay_muon": hom_nay + timedelta(days=muon),
                         "han_tra": hom_nay + timedelta(days=han),
                         "ngay_tra": ngay_tra, "trang_thai": "", "so_ngay_qua_han": 0,
                         "tien_phat": 0})
    cap_nhat_trang_thai_phieu(ds_phieu, hom_nay)

    # Lượt mượn = số phiếu của sách; còn lại = tổng - số phiếu chưa trả
    ds_sach = []
    for ma, ten, tac_gia, the_loai, tong in SACH_MAU:
        luot_muon = 0
        chua_tra = 0
        for p in ds_phieu:
            if p["ma_sach"] == ma:
                luot_muon += 1
                if p["ngay_tra"] is None:
                    chua_tra += 1
        ds_sach.append({"ma_sach": ma, "ten_sach": ten, "tac_gia": tac_gia,
                        "the_loai": the_loai, "tong_so": tong, "con_lai": tong - chua_tra,
                        "luot_muon": luot_muon})
    return {"sach": ds_sach, "doc_gia": ds_doc_gia, "phieu": ds_phieu}


def main():
    du_lieu = tao_du_lieu()
    for s in du_lieu["sach"]:
        if s["con_lai"] < 0:
            thong_bao_canh_bao(f"Sách {s['ma_sach']} có số lượng còn lại âm, hãy kiểm tra bảng mẫu.")
            sys.exit(1)
    if xu_ly_file.luu_tat_ca(du_lieu, False):
        thong_bao_thanh_cong(
            f"Đã tạo dữ liệu mẫu: {len(du_lieu['sach'])} sách, {len(du_lieu['doc_gia'])} độc giả, "
            f"{len(du_lieu['phieu'])} phiếu mượn trong thư mục data/.")


if __name__ == "__main__":
    main()
