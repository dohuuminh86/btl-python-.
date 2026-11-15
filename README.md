# Phần mềm quản lý thư viện và mượn trả sách (Python, giao diện Console)

Bài tập lớn học phần Lập trình Python - Trường Đại học Đại Nam.
Ngôn ngữ: Python 3. Lưu trữ: file TXT (UTF-8), không dùng cơ sở dữ liệu SQL.

## 1. Cài đặt

1. Cài Python 3.8 trở lên từ https://www.python.org (khi cài nhớ tick **Add Python to PATH**).
2. Cài thư viện màu sắc `colorama` (không bắt buộc, không cài vẫn chạy nhưng không có màu):

```
pip install -r requirements.txt
```

## 2. Chạy chương trình trên Visual Studio Code

1. Giải nén file ZIP, trong VS Code chọn **File > Open Folder...** và mở thư mục `QuanLyThuVien`.
2. Mở terminal: **Terminal > New Terminal** (phím tắt Ctrl + `).
3. Chạy:

```
python main.py
```

(Nếu lệnh `python` không chạy, thử `py main.py`.) Hoặc mở `main.py` rồi nhấn nút **Run Python File** góc trên bên phải.

Lưu ý hiển thị:
- Bảng phiếu mượn khá rộng (khoảng 130-150 ký tự). Hãy kéo rộng khung terminal hoặc bấm nút phóng to panel Terminal để bảng không bị xuống dòng.
- Chương trình tự chuyển console sang UTF-8 (`chcp 65001`) nên hiển thị đúng tiếng Việt trên Windows.

## 3. Dữ liệu mẫu

Thư mục `data/` đã có sẵn dữ liệu mẫu: 16 đầu sách, 11 độc giả, 18 phiếu mượn (9 đã trả, 5 đang mượn, 4 quá hạn). Một cuốn (S004) đã hết sách để thử chức năng chặn mượn.

Muốn đưa dữ liệu về trạng thái ban đầu (ngày mượn/hạn trả được tính lùi từ ngày chạy, nên luôn có phiếu quá hạn):

```
python tao_du_lieu_mau.py
```

Cảnh báo: lệnh này ghi đè dữ liệu hiện có trong `data/`.

## 4. Cấu trúc dự án

```
QuanLyThuVien/
├── main.py               Chương trình chính, menu chính
├── tien_ich.py           Màu sắc, nhập liệu có kiểm tra, ngày tháng, tính phạt, in bảng, so khớp chuỗi
├── xu_ly_file.py         Đọc / ghi 3 file TXT
├── quan_ly_sach.py       Quản lý sách
├── quan_ly_doc_gia.py    Quản lý độc giả
├── quan_ly_muon_tra.py   Quản lý mượn sách và trả sách
├── tim_kiem.py           Tìm kiếm sách, độc giả, phiếu mượn
├── sap_xep.py            Sắp xếp sách và phiếu mượn
├── thong_ke.py           Thống kê thư viện
├── tao_du_lieu_mau.py    Tạo dữ liệu mẫu
├── kiem_thu.py           Bộ kiểm thử tự động
├── data/
│   ├── sach.txt
│   ├── docgia.txt
│   └── phieumuon.txt
├── README.md
└── requirements.txt
```

So với cấu trúc đề xuất, có thêm 3 file: `sap_xep.py` (chức năng Sắp xếp), `tao_du_lieu_mau.py` và `kiem_thu.py`.

## 5. Tổ chức dữ liệu

Toàn chương trình dùng một dictionary `du_lieu` gồm 3 list; mỗi bản ghi là một dictionary:

| Khóa | Nội dung của mỗi phần tử |
|---|---|
| `du_lieu["sach"]` | `ma_sach, ten_sach, tac_gia, the_loai, tong_so (int), con_lai (int), luot_muon (int)` |
| `du_lieu["doc_gia"]` | `ma_doc_gia, ho_ten, ngay_sinh (date), so_dien_thoai, dia_chi, email` |
| `du_lieu["phieu"]` | `ma_phieu, ma_sach, ma_doc_gia, ho_ten, ngay_muon (date), han_tra (date), ngay_tra (date hoặc None), trang_thai, so_ngay_qua_han (int), tien_phat (int)` |

Mỗi phiếu quản lý một cuốn sách. Một độc giả có thể có nhiều phiếu.

### Định dạng file TXT

Mỗi dòng là một bản ghi, các trường ngăn cách bằng dấu `|`. Dòng bắt đầu bằng `#` là tiêu đề cột, khi đọc bị bỏ qua. Ngày dạng `dd/mm/yyyy`; ngày trả để trống nếu chưa trả.

```
sach.txt      : ma_sach|ten_sach|tac_gia|the_loai|tong_so|con_lai|luot_muon
docgia.txt    : ma_doc_gia|ho_ten|ngay_sinh|so_dien_thoai|dia_chi|email
phieumuon.txt : ma_phieu|ma_sach|ma_doc_gia|ho_ten|ngay_muon|han_tra|ngay_tra|trang_thai|so_ngay_qua_han|tien_phat
```

Vì `|` là ký tự ngăn cách nên khi nhập liệu chương trình không cho dùng ký tự này.

## 6. Quy tắc nghiệp vụ

- Phạt **5.000 VNĐ/ngày** quá hạn. Số ngày quá hạn = ngày trả thực tế - hạn trả, nếu không muộn thì bằng 0, tiền phạt không bao giờ âm.
- Phiếu chưa trả: số ngày quá hạn và tiền phạt được **tính lại theo ngày hiện tại của máy** mỗi lần đọc file, hiển thị, tìm kiếm hoặc thống kê. Phiếu quá hạn khi ngày hôm nay muộn hơn hạn trả.
- Phiếu đã trả: số ngày quá hạn và tiền phạt tính theo ngày trả thực tế.
- Mượn thành công: `con_lai` giảm 1, `luot_muon` tăng 1. Trả sách: `con_lai` tăng 1 (không vượt quá tổng).
- Mã phiếu tự tạo dạng `PM001, PM002, ...` (lấy số lớn nhất hiện có cộng 1, kiểm tra lại để không trùng).
- Mã sách, mã độc giả, mã phiếu được tự viết hoa, không chứa khoảng trắng. Nhập `0` ở ô mã để hủy thao tác.
- Danh sách "Sách đang được mượn" trong thống kê gồm mọi phiếu chưa trả (cả còn hạn và quá hạn); "Số phiếu đang mượn" chỉ đếm phiếu còn hạn.

## 7. Hướng dẫn sử dụng từng chức năng

Menu chính có 10 lựa chọn; chọn số rồi nhấn Enter. Mỗi nhóm có menu con và lựa chọn `0` để quay lại.

**1. Quản lý sách**: thêm sách (kiểm tra trùng mã, không bỏ trống, tổng số lượng ≥ 1); hiển thị danh sách; cập nhật (Enter để giữ nguyên giá trị cũ; số còn lại phải từ 0 đến tổng và không vượt quá số cuốn đang không bị mượn); xóa (có xác nhận, bị chặn nếu sách còn phiếu chưa trả); tìm sách / kiểm tra mã trùng.

**2. Quản lý độc giả**: thêm (kiểm tra trùng mã, ngày sinh đúng định dạng và trước hôm nay, điện thoại 9-11 chữ số, email hợp lệ); hiển thị; cập nhật (đổi họ tên sẽ cập nhật cả trong các phiếu mượn); xóa (có xác nhận, bị chặn nếu độc giả còn sách chưa trả); tìm độc giả / kiểm tra mã.

**3. Quản lý mượn sách**: tạo phiếu mượn: nhập mã sách (hiện tên sách và số còn lại), mã độc giả (hiện họ tên), ngày mượn (Enter = hôm nay), hạn trả (Enter = +14 ngày), xem tóm tắt rồi xác nhận. Ngoài ra có xem tất cả phiếu và kiểm tra phiếu quá hạn.

**4. Quản lý trả sách**: nhập mã phiếu, xem thông tin phiếu, nhập ngày trả thực tế (Enter = hôm nay), xem số ngày quá hạn và tiền phạt, xác nhận. Phiếu đã trả không thể trả lần hai. Có thêm: xem thông tin phiếu và tiền phạt tạm tính, danh sách phiếu chưa trả / đã trả.

**5. Tìm kiếm**: sách (mã, tên, tác giả); độc giả (mã, họ tên); phiếu (mã phiếu, mã sách, mã độc giả, trạng thái). Tìm tên không phân biệt hoa thường, không phân biệt dấu, hỗ trợ gõ sai nhẹ (ví dụ `pyton` tìm ra `Python`; từ dưới 5 ký tự chỉ tìm đúng). Không có kết quả thì có thông báo.

**6. Sắp xếp**: sách theo tên (A-Z / Z-A); phiếu mượn theo tên sách hoặc theo ngày mượn (cũ → mới / mới → cũ). Sắp xếp chỉ đổi thứ tự hiển thị, không đổi file. Thứ tự A-Z so sánh khi đã bỏ dấu nên gần đúng với bảng chữ cái tiếng Việt.

**7. Thống kê thư viện**: tổng đầu sách, tổng số lượng, số còn trong kho, tổng độc giả, tổng phiếu, số phiếu đang mượn / đã trả / quá hạn, tổng tiền phạt, danh sách sách đang mượn, danh sách quá hạn, sách mượn nhiều nhất / ít nhất (liệt kê tất cả sách bằng nhau). Dữ liệu rỗng thì báo "chưa có dữ liệu".

**8. Lưu dữ liệu**: lưu thủ công cả 3 file. Ngoài ra chương trình **tự lưu** sau mỗi thao tác thêm / sửa / xóa / mượn / trả và khi thoát.

**9. Đọc dữ liệu**: đọc lại 3 file TXT (có xác nhận vì dữ liệu trong bộ nhớ sẽ bị thay). Khi khởi động chương trình cũng tự đọc.

**0. Thoát**: có xác nhận, lưu dữ liệu lần cuối.

## 8. An toàn dữ liệu và xử lý lỗi

- File chưa tồn tại: tự tạo file rỗng, chương trình vẫn chạy.
- Dòng lỗi (sai số trường, sai kiểu số, số âm, còn lại > tổng, ngày sai, trùng mã, hạn trả trước ngày mượn): bị bỏ qua và thông báo rõ **dòng nào, vì sao**. File gốc được sao lưu thành `*.loi.bak` để không mất dữ liệu.
- File không đọc được (hỏng, sai mã hóa) hoặc không ghi được (thiếu quyền): thông báo lỗi, không văng chương trình.
- Khi ghi, chương trình ghi ra file `.tmp` rồi mới thay file thật, nên nếu ghi lỗi giữa chừng thì file cũ vẫn còn nguyên.
- Nhập sai: luôn báo lỗi bằng tiếng Việt và cho nhập lại. Ctrl+C hoặc hết dữ liệu nhập: chương trình lưu dữ liệu rồi thoát nhẹ nhàng.

## 9. Kiểm thử

```
python kiem_thu.py
```

Bộ kiểm thử chạy trên thư mục tạm (không đụng vào `data/` của bạn), gồm 205 phép kiểm tra: đọc/ghi file và dòng lỗi, thêm / sửa / xóa sách và độc giả, tạo phiếu mượn, số lượng sau khi mượn / trả, trả hai lần, tính phạt, tìm kiếm, sắp xếp, thống kê (kể cả dữ liệu rỗng), nhập sai, và chạy `main.py` thật bằng đầu vào giả lập. Chỉ khi in ra `0 không đạt` thì mới đạt toàn bộ.

## 10. Giải thích chương trình để thuyết trình và vấn đáp

### Luồng chạy tổng quát

`main()` → `cai_dat_console()` → `doc_tat_ca(du_lieu)` đọc 3 file → vòng lặp `while True` hiện menu chính, gọi menu con tương ứng → khi chọn 0 thì `luu_tat_ca()` và thoát. Mỗi menu con cũng là một vòng `while True`, chọn 0 thì `break` để quay lại.

### Các hàm quan trọng

| Hàm | File | Vai trò |
|---|---|---|
| `nhap_chuoi`, `nhap_so_nguyen`, `nhap_ngay`, `nhap_ma` | tien_ich | Vòng `while True` nhập đến khi hợp lệ, dùng `try/except ValueError` để bắt nhập sai kiểu, không thoát chương trình |
| `chuyen_chuoi_thanh_ngay` | tien_ich | `datetime.strptime` đổi `dd/mm/yyyy` thành `date`; sai thì trả `None` |
| `tinh_so_ngay_qua_han`, `tinh_tien_phat` | tien_ich | Số ngày quá hạn = ngày mốc - hạn trả (nhỏ nhất 0); phạt = số ngày × 5.000 |
| `cap_nhat_trang_thai_phieu` | tien_ich | Duyệt từng phiếu, tính lại trạng thái / số ngày quá hạn / tiền phạt theo ngày trả hoặc ngày hôm nay |
| `khop_gan_dung` | tien_ich | Tìm tên không phân biệt hoa thường và dấu (`bo_dau`), thêm so khớp gần đúng bằng `difflib` |
| `in_bang` | tien_ich | Tính độ rộng từng cột rồi in bảng bằng `ljust` / `rjust` |
| `doc_file_chung`, `phan_tich_dong_*` | xu_ly_file | Đọc từng dòng, `split("|")`, ép kiểu `int` / `date`; dòng lỗi gây `ValueError` và bị bỏ qua có thông báo |
| `ghi_file`, `luu_tat_ca`, `tu_dong_luu` | xu_ly_file | Ghi file tạm rồi `os.replace`; `tu_dong_luu` gọi sau mỗi thay đổi |
| `them_sach`, `cap_nhat_sach`, `xoa_sach` | quan_ly_sach | Kiểm tra trùng mã, số lượng, phiếu chưa trả; xác nhận trước khi xóa |
| `tao_ma_phieu_moi` | quan_ly_muon_tra | Sinh mã `PMxxx` duy nhất |
| `tao_phieu_muon` | quan_ly_muon_tra | Kiểm tra sách/độc giả tồn tại, sách còn, hạn trả ≥ ngày mượn; tạo phiếu, `con_lai -= 1`, `luot_muon += 1` |
| `tra_sach` | quan_ly_muon_tra | Chặn phiếu không tồn tại / đã trả; tính phạt; cập nhật phiếu; `con_lai += 1` |
| `tim_sach`, `tim_doc_gia`, `tim_phieu` | tim_kiem | Duyệt list bằng `for` và trả về list kết quả |
| `sap_xep_*` | sap_xep | `sorted(..., key=..., reverse=...)` trên bản sao |
| `tinh_thong_ke` | thong_ke | Duyệt các list, đếm và cộng dồn, trả về dictionary kết quả |

### Kiến thức Python được thể hiện

Biến và kiểu dữ liệu (`int`, `str`, `date`, `list`, `dict`); `if/elif/else`; vòng lặp `for` và `while`; hàm chia nhỏ chương trình, nhiều module; list và dictionary; đọc/ghi file UTF-8; `try/except`; menu điều khiển; chú thích tiếng Việt.

### Câu hỏi giảng viên có thể hỏi

- **Vì sao dùng list các dictionary?** Mỗi bản ghi truy cập theo tên trường (`sach["con_lai"]`) dễ đọc hơn theo chỉ số, và dễ ghi ra dòng TXT.
- **Vì sao phiếu lưu cả họ tên độc giả?** Theo yêu cầu đề bài; vì vậy khi sửa họ tên độc giả, chương trình cập nhật lại họ tên trong các phiếu để dữ liệu đồng bộ.
- **Tiền phạt tính thế nào cho sách chưa trả?** Tính theo ngày hiện tại của máy mỗi khi đọc / hiển thị, không cần lưu cố định.
- **Làm sao không mất dữ liệu khi ghi lỗi?** Ghi file tạm rồi mới thay file thật; file lỗi được sao lưu `.loi.bak`.
- **Làm sao chặn trả sách hai lần?** Phiếu đã trả có `ngay_tra` khác `None`, `tra_sach` kiểm tra và báo lỗi.
- **Vì sao tìm tên không dấu vẫn ra?** `bo_dau` dùng `unicodedata.normalize("NFD")` tách dấu rồi loại bỏ ký tự dấu.
- **Hạn chế?** Dữ liệu nằm trong file TXT nên chỉ phù hợp quy mô nhỏ; không có phân quyền; thứ tự A-Z là gần đúng theo bảng chữ cái không dấu; ngày quá hạn phụ thuộc đồng hồ máy.
