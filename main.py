# -*- coding: utf-8 -*-
"""
main.py - Chương trình chính: PHẦN MỀM QUẢN LÝ THƯ VIỆN VÀ MƯỢN TRẢ SÁCH.

Cách chạy:  python main.py
Dữ liệu dùng chung của toàn chương trình là dictionary du_lieu gồm 3 list:
  du_lieu["sach"], du_lieu["doc_gia"], du_lieu["phieu"]
"""

from tien_ich import (
    cai_dat_console, in_duong_ke, in_tieu_de, nhap_lua_chon, xac_nhan,
    thong_bao_loi, thong_bao_canh_bao, thong_bao_thong_tin, tam_dung, XANH_DUONG, DAM, TAT,
)
import xu_ly_file
from quan_ly_sach import menu_quan_ly_sach
from quan_ly_doc_gia import menu_quan_ly_doc_gia
from quan_ly_muon_tra import menu_muon_sach, menu_tra_sach
from tim_kiem import menu_tim_kiem
from sap_xep import menu_sap_xep
from thong_ke import menu_thong_ke


def hien_thi_menu_chinh():
    """In menu chính của chương trình."""
    print()
    print(XANH_DUONG + DAM + "=" * 47)
    print("PHẦN MỀM QUẢN LÝ THƯ VIỆN".center(47))
    print("=" * 47 + TAT)
    print()
    print("1. QUẢN LÝ SÁCH")
    print("2. QUẢN LÝ ĐỘC GIẢ")
    print("3. QUẢN LÝ MƯỢN SÁCH")
    print("4. QUẢN LÝ TRẢ SÁCH")
    print("5. TÌM KIẾM")
    print("6. SẮP XẾP")
    print("7. THỐNG KÊ THƯ VIỆN")
    print("8. LƯU DỮ LIỆU")
    print("9. ĐỌC DỮ LIỆU")
    print("0. THOÁT CHƯƠNG TRÌNH")
    print()
    in_duong_ke("=", 47)


def main():
    cai_dat_console()
    du_lieu = {"sach": [], "doc_gia": [], "phieu": []}

    in_tieu_de("CHÀO MỪNG ĐẾN VỚI PHẦN MỀM QUẢN LÝ THƯ VIỆN")
    xu_ly_file.doc_tat_ca(du_lieu)               # Tự động đọc dữ liệu khi khởi động
    if len(du_lieu["sach"]) == 0 and len(du_lieu["doc_gia"]) == 0 and len(du_lieu["phieu"]) == 0:
        thong_bao_thong_tin("Chưa có dữ liệu. Chạy 'python tao_du_lieu_mau.py' để tạo dữ liệu mẫu, "
                            "hoặc tự thêm dữ liệu trong chương trình.")

    try:
        while True:
            hien_thi_menu_chinh()
            lua_chon = nhap_lua_chon("Nhập lựa chọn: ")
            if lua_chon == "1":
                menu_quan_ly_sach(du_lieu)
            elif lua_chon == "2":
                menu_quan_ly_doc_gia(du_lieu)
            elif lua_chon == "3":
                menu_muon_sach(du_lieu)
            elif lua_chon == "4":
                menu_tra_sach(du_lieu)
            elif lua_chon == "5":
                menu_tim_kiem(du_lieu)
            elif lua_chon == "6":
                menu_sap_xep(du_lieu)
            elif lua_chon == "7":
                menu_thong_ke(du_lieu)
            elif lua_chon == "8":
                in_tieu_de("LƯU DỮ LIỆU")
                xu_ly_file.luu_tat_ca(du_lieu)
                tam_dung()
            elif lua_chon == "9":
                in_tieu_de("ĐỌC LẠI DỮ LIỆU")
                thong_bao_canh_bao("Dữ liệu đang có trong bộ nhớ sẽ được thay bằng dữ liệu trong file.")
                if xac_nhan("Bạn có chắc chắn muốn đọc lại dữ liệu từ file?"):
                    xu_ly_file.doc_tat_ca(du_lieu)
                else:
                    thong_bao_thong_tin("Đã hủy đọc dữ liệu.")
                tam_dung()
            elif lua_chon == "0":
                if xac_nhan("Bạn có chắc chắn muốn thoát chương trình?"):
                    xu_ly_file.luu_tat_ca(du_lieu)       # Lưu lần cuối trước khi thoát
                    print("Cảm ơn bạn đã sử dụng chương trình. Hẹn gặp lại!")
                    break
            else:
                thong_bao_loi("Lựa chọn không hợp lệ. Vui lòng nhập số từ 0 đến 9.")
    except (EOFError, KeyboardInterrupt):
        # Người dùng nhấn Ctrl+C / Ctrl+Z hoặc hết dữ liệu nhập: lưu rồi thoát nhẹ nhàng
        print()
        thong_bao_canh_bao("Chương trình bị ngắt. Đang lưu dữ liệu trước khi thoát...")
        xu_ly_file.luu_tat_ca(du_lieu)


if __name__ == "__main__":
    main()
