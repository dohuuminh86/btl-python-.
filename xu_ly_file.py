# -*- coding: utf-8 -*-
"""
xu_ly_file.py - Đọc và ghi dữ liệu từ/vào file TXT (mã hóa UTF-8).

Mỗi file TXT lưu một bản ghi trên một dòng, các trường ngăn cách bởi dấu '|'.
Dòng bắt đầu bằng '#' là dòng chú thích (tiêu đề cột), khi đọc sẽ bị bỏ qua.

  sach.txt     : ma_sach|ten_sach|tac_gia|the_loai|tong_so|con_lai|luot_muon
  docgia.txt   : ma_doc_gia|ho_ten|ngay_sinh|so_dien_thoai|dia_chi|email
  phieumuon.txt: ma_phieu|ma_sach|ma_doc_gia|ho_ten|ngay_muon|han_tra|ngay_tra|
                 trang_thai|so_ngay_qua_han|tien_phat

Cách tránh mất dữ liệu cũ:
  - Khi ghi, chương trình ghi ra file tạm (.tmp) trước, thành công mới thay thế file thật.
    Nếu ghi lỗi giữa chừng thì file cũ vẫn còn nguyên.
  - Khi đọc gặp dòng lỗi, file gốc được sao lưu thành *.loi.bak trước khi chương trình lưu đè.
"""

import os
import shutil

from tien_ich import (
    chuyen_chuoi_thanh_ngay, dinh_dang_ngay, cap_nhat_trang_thai_phieu,
    thong_bao_thanh_cong, thong_bao_loi, thong_bao_canh_bao, thong_bao_thong_tin,
    TT_DANG_MUON, TT_DA_TRA, TT_QUA_HAN,
)

# Đường dẫn tính theo vị trí file này, nên chạy từ thư mục nào cũng được
THU_MUC_GOC = os.path.dirname(os.path.abspath(__file__))
THU_MUC_DATA = os.path.join(THU_MUC_GOC, "data")
FILE_SACH = os.path.join(THU_MUC_DATA, "sach.txt")
FILE_DOC_GIA = os.path.join(THU_MUC_DATA, "docgia.txt")
FILE_PHIEU = os.path.join(THU_MUC_DATA, "phieumuon.txt")

TIEU_DE_SACH = "# ma_sach|ten_sach|tac_gia|the_loai|tong_so|con_lai|luot_muon"
TIEU_DE_DOC_GIA = "# ma_doc_gia|ho_ten|ngay_sinh|so_dien_thoai|dia_chi|email"
TIEU_DE_PHIEU = ("# ma_phieu|ma_sach|ma_doc_gia|ho_ten|ngay_muon|han_tra|ngay_tra|"
                 "trang_thai|so_ngay_qua_han|tien_phat")


# ----------------------------------------------------------------------
# GHI FILE
# ----------------------------------------------------------------------
def ghi_file(duong_dan, tieu_de, cac_dong):
    """Ghi danh sách dòng vào file UTF-8. Trả về True nếu thành công."""
    try:
        os.makedirs(os.path.dirname(duong_dan), exist_ok=True)
        file_tam = duong_dan + ".tmp"
        with open(file_tam, "w", encoding="utf-8", newline="\n") as f:
            f.write(tieu_de + "\n")
            for dong in cac_dong:
                f.write(dong + "\n")
        os.replace(file_tam, duong_dan)       # Thay file thật bằng file tạm (an toàn)
        return True
    except OSError as loi:
        thong_bao_loi(f"Không thể ghi file {os.path.basename(duong_dan)}: {loi}")
        return False


def sach_thanh_dong(s):
    return "|".join([s["ma_sach"], s["ten_sach"], s["tac_gia"], s["the_loai"],
                     str(s["tong_so"]), str(s["con_lai"]), str(s["luot_muon"])])


def doc_gia_thanh_dong(dg):
    return "|".join([dg["ma_doc_gia"], dg["ho_ten"], dinh_dang_ngay(dg["ngay_sinh"]),
                     dg["so_dien_thoai"], dg["dia_chi"], dg["email"]])


def phieu_thanh_dong(p):
    return "|".join([p["ma_phieu"], p["ma_sach"], p["ma_doc_gia"], p["ho_ten"],
                     dinh_dang_ngay(p["ngay_muon"]), dinh_dang_ngay(p["han_tra"]),
                     dinh_dang_ngay(p["ngay_tra"]), p["trang_thai"],
                     str(p["so_ngay_qua_han"]), str(p["tien_phat"])])


def luu_sach(ds_sach):
    cac_dong = []
    for s in ds_sach:
        cac_dong.append(sach_thanh_dong(s))
    return ghi_file(FILE_SACH, TIEU_DE_SACH, cac_dong)


def luu_doc_gia(ds_doc_gia):
    cac_dong = []
    for dg in ds_doc_gia:
        cac_dong.append(doc_gia_thanh_dong(dg))
    return ghi_file(FILE_DOC_GIA, TIEU_DE_DOC_GIA, cac_dong)


def luu_phieu(ds_phieu):
    cac_dong = []
    for p in ds_phieu:
        cac_dong.append(phieu_thanh_dong(p))
    return ghi_file(FILE_PHIEU, TIEU_DE_PHIEU, cac_dong)


def luu_tat_ca(du_lieu, hien_thong_bao=True, loi_nhan="Đã lưu dữ liệu vào thư mục data/."):
    """Lưu cả 3 file. Trả về True nếu cả 3 đều thành công."""
    ok_sach = luu_sach(du_lieu["sach"])
    ok_doc_gia = luu_doc_gia(du_lieu["doc_gia"])
    ok_phieu = luu_phieu(du_lieu["phieu"])
    thanh_cong = ok_sach and ok_doc_gia and ok_phieu
    if thanh_cong and hien_thong_bao:
        thong_bao_thanh_cong(loi_nhan)
    elif not thanh_cong:
        thong_bao_loi("Lưu dữ liệu chưa hoàn tất. Hãy kiểm tra quyền ghi file trong thư mục data/.")
    return thanh_cong


def tu_dong_luu(du_lieu):
    """Gọi sau mỗi thay đổi quan trọng (thêm/sửa/xóa/mượn/trả)."""
    return luu_tat_ca(du_lieu, True, "Dữ liệu đã được tự động lưu.")


# ----------------------------------------------------------------------
# PHÂN TÍCH TỪNG DÒNG (đổi chuỗi về đúng kiểu dữ liệu)
# Dòng sai sẽ gây ValueError và được bỏ qua kèm thông báo.
# ----------------------------------------------------------------------
def phan_tich_dong_sach(dong):
    truong = dong.split("|")
    if len(truong) != 7:
        raise ValueError(f"cần 7 trường nhưng có {len(truong)}")
    ma, ten, tac_gia, the_loai, tong, con_lai, luot = [t.strip() for t in truong]
    if ma == "" or ten == "":
        raise ValueError("thiếu mã sách hoặc tên sách")
    tong = int(tong)          # Sai kiểu sẽ tự sinh ValueError
    con_lai = int(con_lai)
    luot = int(luot)
    if tong < 0 or con_lai < 0 or luot < 0:
        raise ValueError("số lượng bị âm")
    if con_lai > tong:
        raise ValueError("số lượng còn lại lớn hơn tổng số lượng")
    return {"ma_sach": ma, "ten_sach": ten, "tac_gia": tac_gia, "the_loai": the_loai,
            "tong_so": tong, "con_lai": con_lai, "luot_muon": luot}


def phan_tich_dong_doc_gia(dong):
    truong = dong.split("|")
    if len(truong) != 6:
        raise ValueError(f"cần 6 trường nhưng có {len(truong)}")
    ma, ho_ten, ngay_sinh, sdt, dia_chi, email = [t.strip() for t in truong]
    if ma == "" or ho_ten == "":
        raise ValueError("thiếu mã độc giả hoặc họ tên")
    ngay_sinh = chuyen_chuoi_thanh_ngay(ngay_sinh)
    if ngay_sinh is None:
        raise ValueError("ngày sinh sai định dạng dd/mm/yyyy")
    return {"ma_doc_gia": ma, "ho_ten": ho_ten, "ngay_sinh": ngay_sinh,
            "so_dien_thoai": sdt, "dia_chi": dia_chi, "email": email}


def phan_tich_dong_phieu(dong):
    truong = dong.split("|")
    if len(truong) != 10:
        raise ValueError(f"cần 10 trường nhưng có {len(truong)}")
    (ma_phieu, ma_sach, ma_dg, ho_ten, ngay_muon, han_tra,
     ngay_tra, trang_thai, so_ngay, tien_phat) = [t.strip() for t in truong]
    if ma_phieu == "" or ma_sach == "" or ma_dg == "":
        raise ValueError("thiếu mã phiếu, mã sách hoặc mã độc giả")
    ngay_muon = chuyen_chuoi_thanh_ngay(ngay_muon)
    han_tra = chuyen_chuoi_thanh_ngay(han_tra)
    if ngay_muon is None or han_tra is None:
        raise ValueError("ngày mượn hoặc hạn trả sai định dạng")
    if han_tra < ngay_muon:
        raise ValueError("hạn trả trước ngày mượn")
    if ngay_tra == "":
        ngay_tra = None                       # Chưa trả
    else:
        ngay_tra = chuyen_chuoi_thanh_ngay(ngay_tra)
        if ngay_tra is None:
            raise ValueError("ngày trả sai định dạng")
        if ngay_tra < ngay_muon:
            raise ValueError("ngày trả trước ngày mượn")
    # Số ngày quá hạn, tiền phạt, trạng thái sẽ được tính lại sau khi đọc,
    # nhưng vẫn kiểm tra chúng là số hợp lệ.
    int(so_ngay)
    int(tien_phat)
    return {"ma_phieu": ma_phieu, "ma_sach": ma_sach, "ma_doc_gia": ma_dg, "ho_ten": ho_ten,
            "ngay_muon": ngay_muon, "han_tra": han_tra, "ngay_tra": ngay_tra,
            "trang_thai": trang_thai, "so_ngay_qua_han": 0, "tien_phat": 0}


# ----------------------------------------------------------------------
# ĐỌC FILE
# ----------------------------------------------------------------------
def doc_file_chung(duong_dan, tieu_de, ham_phan_tich, ten_khoa):
    """
    Đọc một file dữ liệu, trả về list các dictionary.
      - File chưa có: tạo file rỗng và trả về list rỗng.
      - Dòng lỗi hoặc trùng mã: bỏ qua và thông báo rõ dòng nào.
    """
    ten_file = os.path.basename(duong_dan)
    if not os.path.exists(duong_dan):
        thong_bao_canh_bao(f"Chưa có file {ten_file}, chương trình tạo file mới (rỗng).")
        ghi_file(duong_dan, tieu_de, [])
        return []

    try:
        with open(duong_dan, "r", encoding="utf-8-sig") as f:
            cac_dong = f.readlines()
    except (OSError, UnicodeDecodeError) as loi:
        thong_bao_loi(f"Không thể đọc file {ten_file}: {loi}")
        return []

    ket_qua = []
    ma_da_co = set()
    so_dong_loi = 0
    for so_dong, dong in enumerate(cac_dong, start=1):
        dong = dong.rstrip("\r\n")
        if dong.strip() == "" or dong.startswith("#"):
            continue                              # Bỏ qua dòng trống và dòng chú thích
        try:
            ban_ghi = ham_phan_tich(dong)
        except ValueError as loi:
            so_dong_loi += 1
            thong_bao_canh_bao(f"{ten_file}, dòng {so_dong}: bỏ qua vì {loi}.")
            continue
        ma = ban_ghi[ten_khoa].upper()
        if ma in ma_da_co:
            so_dong_loi += 1
            thong_bao_canh_bao(f"{ten_file}, dòng {so_dong}: bỏ qua vì trùng mã '{ban_ghi[ten_khoa]}'.")
            continue
        ma_da_co.add(ma)
        ket_qua.append(ban_ghi)

    if so_dong_loi > 0:
        # Sao lưu file gốc để không mất dữ liệu khi chương trình lưu đè bản đã làm sạch
        try:
            shutil.copy2(duong_dan, duong_dan + ".loi.bak")
            thong_bao_thong_tin(f"Đã sao lưu file gốc thành {ten_file}.loi.bak")
        except OSError:
            pass
    return ket_qua


def doc_sach():
    return doc_file_chung(FILE_SACH, TIEU_DE_SACH, phan_tich_dong_sach, "ma_sach")


def doc_doc_gia():
    return doc_file_chung(FILE_DOC_GIA, TIEU_DE_DOC_GIA, phan_tich_dong_doc_gia, "ma_doc_gia")


def doc_phieu():
    ds_phieu = doc_file_chung(FILE_PHIEU, TIEU_DE_PHIEU, phan_tich_dong_phieu, "ma_phieu")
    cap_nhat_trang_thai_phieu(ds_phieu)           # Tính lại quá hạn theo ngày hôm nay
    return ds_phieu


def doc_tat_ca(du_lieu):
    """Đọc cả 3 file vào dictionary du_lieu (thay thế dữ liệu đang có trong bộ nhớ)."""
    du_lieu["sach"] = doc_sach()
    du_lieu["doc_gia"] = doc_doc_gia()
    du_lieu["phieu"] = doc_phieu()
    thong_bao_thanh_cong(
        f"Đã đọc dữ liệu: {len(du_lieu['sach'])} đầu sách, "
        f"{len(du_lieu['doc_gia'])} độc giả, {len(du_lieu['phieu'])} phiếu mượn.")
