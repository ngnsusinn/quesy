# Sơ đồ tuần tự từng chức năng

> Quesy · Bản phân tích nghiệp vụ 1.0 · Ngày 17/11/2026
> Trạng thái: bản đặc tả đề xuất, không phải báo cáo chức năng đã triển khai.

## Quy ước và mức thiết kế

SEQ-nn tương ứng UC-nn và ACT-nn. `A` là tác nhân khởi tạo, `UI` là giao diện Quesy, `S` là trách nhiệm điều phối nghiệp vụ logic, `D` là kho dữ liệu Quesy, `E` là dịch vụ ngoài khi có. Lifeline là đối tượng cộng tác phân tích, không mô tả cấu trúc lớp mã nguồn hay khẳng định có một máy chủ riêng cho mỗi đối tượng.

Mũi tên liền là thông điệp/yêu cầu; mũi tên đứt là kết quả. `alt/else` là lựa chọn loại trừ, `opt` là phần có điều kiện, `loop` là lặp, `ref` là tham chiếu một Use Case đã đặc tả. Tác vụ số hóa trả tiếp nhận trước và cho xem tiến độ sau; thông điệp được diễn đạt ở mức nghiệp vụ, chưa chốt HTTP hay giao thức hàng đợi. Ghi dữ liệu được mô tả thành công giả định giao dịch đạt; lỗi lưu phải giữ các bảo đảm của UC và NFR-04.


<a id="seq-01"></a>
## SEQ-01 — Đăng ký tài khoản giáo viên

Đối chiếu: [UC-01](08_MO_TA_USE_CASE.md#uc-01); dữ liệu TaiKhoan, KhongGian.

```plantuml
@startuml SEQ_01
skinparam defaultFontName Segoe UI
skinparam shadowing false
skinparam defaultFontSize 13
title SEQ-01 / UC-01 — Đăng ký tài khoản giáo viên
actor "Khách chưa đăng nhập" as A
boundary "Giao diện Quesy" as UI
control "Quản lý tài khoản và phiên" as S
database "Kho dữ liệu Quesy" as D
autonumber
A -> UI: Nhập thông tin đăng ký
UI -> S: Yêu cầu đăng ký giáo viên
S -> D: Kiểm tra định danh và chính sách
D --> S: Kết quả kiểm tra
alt Được đăng ký và dữ liệu hợp lệ
  S -> D: Tạo tài khoản + không gian (nguyên tử)
  D --> S: Mã tài khoản và không gian
  S --> UI: Đăng ký thành công
else Bị từ chối hoặc trùng định danh
  S --> UI: Lỗi trường nhập; không tạo dữ liệu
end
UI --> A: Hiển thị kết quả
@enduml
```


<a id="seq-02"></a>
## SEQ-02 — Đăng nhập

Đối chiếu: [UC-02](08_MO_TA_USE_CASE.md#uc-02); dữ liệu TaiKhoan, PhienDangNhap.

```plantuml
@startuml SEQ_02
skinparam defaultFontName Segoe UI
skinparam shadowing false
skinparam defaultFontSize 13
title SEQ-02 / UC-02 — Đăng nhập
actor "Khách chưa đăng nhập" as A
boundary "Giao diện Quesy" as UI
control "Quản lý tài khoản và phiên" as S
database "Kho dữ liệu Quesy" as D
autonumber
A -> UI: Gửi định danh và mật khẩu
UI -> S: Xác thực
S -> D: Đọc tài khoản và trạng thái
D --> S: Thông tin xác thực được bảo vệ
alt Hợp lệ, hoạt động và chưa vượt giới hạn
  S -> D: Tạo phiên gắn vai trò
  D --> S: Định danh phiên
  S --> UI: Phiên và quyền truy cập
else Đăng nhập bị từ chối
  S --> UI: Thông báo chung; không cấp phiên
end
UI --> A: Kết quả đăng nhập
@enduml
```


<a id="seq-03"></a>
## SEQ-03 — Đăng xuất

Đối chiếu: [UC-03](08_MO_TA_USE_CASE.md#uc-03); dữ liệu PhienDangNhap.

```plantuml
@startuml SEQ_03
skinparam defaultFontName Segoe UI
skinparam shadowing false
skinparam defaultFontSize 13
title SEQ-03 / UC-03 — Đăng xuất
actor "Người dùng đã xác thực" as A
boundary "Giao diện Quesy" as UI
control "Quản lý tài khoản và phiên" as S
database "Kho dữ liệu Quesy" as D
autonumber
A -> UI: Đăng xuất sau khi lưu hoặc bỏ bản nháp
UI -> S: Thu hồi phiên hiện tại
alt Máy chủ phản hồi
  S -> D: Đánh dấu phiên đã thu hồi
  D --> S: Đã thu hồi hoặc đã hết hạn
  S --> UI: Xác nhận đăng xuất
else Mất kết nối
  UI -> UI: Xóa phiên cục bộ; đánh dấu chưa xác nhận
end
UI --> A: Trang đăng nhập và trạng thái thu hồi
@enduml
```


<a id="seq-04"></a>
## SEQ-04 — Cập nhật hồ sơ và đổi mật khẩu

Đối chiếu: [UC-04](08_MO_TA_USE_CASE.md#uc-04); dữ liệu TaiKhoan, PhienDangNhap.

```plantuml
@startuml SEQ_04
skinparam defaultFontName Segoe UI
skinparam shadowing false
skinparam defaultFontSize 13
title SEQ-04 / UC-04 — Cập nhật hồ sơ và đổi mật khẩu
actor "Người dùng đã xác thực" as A
boundary "Giao diện Quesy" as UI
control "Quản lý tài khoản và phiên" as S
database "Kho dữ liệu Quesy" as D
autonumber
A -> UI: Gửi thay đổi hồ sơ hoặc mật khẩu
UI -> S: Cập nhật chính chủ kèm phiên bản
S -> D: Đọc tài khoản và phiên bản hiện hành
D --> S: Thông tin cần đối chiếu
alt Đủ quyền, đúng phiên bản và xác minh hợp lệ
  S -> D: Cập nhật; thu hồi phiên nếu đổi mật khẩu
  D --> S: Phiên bản mới
  S --> UI: Hoàn tất; trạng thái phiên
else Sai xác minh hoặc xung đột
  S --> UI: Từ chối; giữ hồ sơ cũ
end
UI --> A: Kết quả cập nhật
@enduml
```


<a id="seq-05"></a>
## SEQ-05 — Tổ chức cây kiến thức cá nhân

Đối chiếu: [UC-05](08_MO_TA_USE_CASE.md#uc-05); dữ liệu NutKienThuc, KhongGian.

```plantuml
@startuml SEQ_05
skinparam defaultFontName Segoe UI
skinparam shadowing false
skinparam defaultFontSize 13
title SEQ-05 / UC-05 — Tổ chức cây kiến thức cá nhân
actor "Giáo viên" as A
boundary "Giao diện Quesy" as UI
control "Quản lý ngân hàng câu hỏi" as S
database "Kho dữ liệu Quesy" as D
autonumber
A -> UI: Gửi thay đổi nhánh cá nhân
UI -> S: Kiểm tra cây và quyền sở hữu
S -> D: Đọc cha, mã và tham chiếu
D --> S: Cấu trúc và mức sử dụng
alt Cây hợp lệ và thuộc không gian
  S -> D: Lưu phiên bản hoặc ngừng dùng nhánh
  D --> S: Cây cập nhật
  S --> UI: Kết quả và bộ lọc mới
else Sai cấu trúc hoặc sửa danh mục chung
  S --> UI: Báo lỗi; đề nghị sao chép nhánh chung
end
UI --> A: Hiển thị cây
@enduml
```


<a id="seq-06"></a>
## SEQ-06 — Tra cứu và xem câu hỏi

Đối chiếu: [UC-06](08_MO_TA_USE_CASE.md#uc-06); dữ liệu CauHoi, PhienBanCauHoi, TaiSan.

```plantuml
@startuml SEQ_06
skinparam defaultFontName Segoe UI
skinparam shadowing false
skinparam defaultFontSize 13
title SEQ-06 / UC-06 — Tra cứu và xem câu hỏi
actor "Giáo viên" as A
boundary "Giao diện Quesy" as UI
control "Quản lý ngân hàng câu hỏi" as S
database "Kho dữ liệu Quesy" as D
autonumber
A -> UI: Nhập từ khóa và bộ lọc
UI -> S: Tra cứu trong phạm vi phiên
S -> D: Truy vấn theo chủ sở hữu, bộ lọc và trang
D --> S: Danh sách, tổng số và phiên bản
alt Có quyền xem
  S --> UI: Nội dung được phép và liên kết tài sản
else Ngoài quyền
  S --> UI: Không cung cấp nội dung
end
UI --> A: Danh sách hoặc trạng thái rỗng
@enduml
```


<a id="seq-07"></a>
## SEQ-07 — Tạo và chỉnh sửa câu hỏi

Đối chiếu: [UC-07](08_MO_TA_USE_CASE.md#uc-07); dữ liệu CauHoi, PhienBanCauHoi, PhuongAn, MenhDe, KetQuaTuongDong.

```plantuml
@startuml SEQ_07
skinparam defaultFontName Segoe UI
skinparam shadowing false
skinparam defaultFontSize 13
title SEQ-07 / UC-07 — Tạo và chỉnh sửa câu hỏi
actor "Giáo viên" as A
boundary "Giao diện Quesy" as UI
control "Quản lý ngân hàng câu hỏi" as S
database "Kho dữ liệu Quesy" as D
autonumber
A -> UI: Gửi câu hỏi và phiên bản kỳ vọng
UI -> S: Kiểm tra cấu trúc, quyền và trạng thái
S -> D: Đọc phiên bản hiện hành và câu tương đồng
D --> S: Câu đối chiếu và phiên bản
S --> UI: Lỗi và cảnh báo tương đồng
A -> UI: Sửa lỗi hoặc chọn lưu nháp / sẵn sàng
UI -> S: Xác nhận lưu với trạng thái đã chọn
alt Đúng phiên bản; trạng thái đáp ứng điều kiện
  S -> D: Lưu phiên bản bất biến mới và nguồn
  D --> S: Mã phiên bản mới
  S --> UI: Lưu thành công
else Xung đột hoặc còn lỗi chặn trạng thái
  S --> UI: Giữ nội dung soạn; trả danh sách lỗi
end
UI --> A: Kết quả lưu
@enduml
```


<a id="seq-08"></a>
## SEQ-08 — Ngừng dùng và khôi phục câu hỏi

Đối chiếu: [UC-08](08_MO_TA_USE_CASE.md#uc-08); dữ liệu CauHoi, PhienBanCauHoi, NhatKy.

```plantuml
@startuml SEQ_08
skinparam defaultFontName Segoe UI
skinparam shadowing false
skinparam defaultFontSize 13
title SEQ-08 / UC-08 — Ngừng dùng và khôi phục câu hỏi
actor "Giáo viên" as A
boundary "Giao diện Quesy" as UI
control "Quản lý ngân hàng câu hỏi" as S
database "Kho dữ liệu Quesy" as D
autonumber
A -> UI: Yêu cầu ngừng dùng hoặc khôi phục
UI -> S: Xem tác động tồn kho và tham chiếu
S -> D: Đọc quyền, phiên bản và trạng thái
D --> S: Tác động và trạng thái
S --> UI: Yêu cầu xác nhận
A -> UI: Xác nhận thay đổi
UI -> S: Gửi xác nhận kèm phiên bản
alt Được phép và phiên bản còn đúng
  S -> D: Đổi trạng thái; giữ nguyên các bản chụp đề
  D --> S: Trạng thái mới
  S --> UI: Hoàn tất
else Xung đột hoặc hủy
  S --> UI: Không thay đổi
end
UI --> A: Kết quả
@enduml
```


<a id="seq-09"></a>
## SEQ-09 — Nhập ngân hàng từ dữ liệu có cấu trúc

Đối chiếu: [UC-09](08_MO_TA_USE_CASE.md#uc-09); dữ liệu LoNhap, DongNhap, PhienBanCauHoi.

```plantuml
@startuml SEQ_09
skinparam defaultFontName Segoe UI
skinparam shadowing false
skinparam defaultFontSize 13
title SEQ-09 / UC-09 — Nhập ngân hàng từ dữ liệu có cấu trúc
actor "Giáo viên" as A
boundary "Giao diện Quesy" as UI
control "Quản lý ngân hàng câu hỏi" as S
database "Kho dữ liệu Quesy" as D
autonumber
A -> UI: Tải bảng dữ liệu và ánh xạ cột
UI -> S: Kiểm tra lô nhập
S -> D: Đối chiếu nhãn, câu tương đồng và lô cũ
D --> S: Kết quả đối chiếu
S --> UI: Bản xem trước và lỗi theo dòng
A -> UI: Chọn dòng hợp lệ; xác nhận
UI -> S: Nhập lô với khóa chống lặp
loop Mỗi dòng được chọn
  S -> D: Lưu dòng nếu chưa có kết quả nhập
  D --> S: Đã nhập hoặc lỗi riêng của dòng
end
S --> UI: Báo cáo theo dòng
UI --> A: Số nhập thành công và dòng cần sửa
@enduml
```


<a id="seq-10"></a>
## SEQ-10 — Xuất tập câu hỏi ngân hàng

Đối chiếu: [UC-10](08_MO_TA_USE_CASE.md#uc-10); dữ liệu PhienBanCauHoi, AnPham, TacVu.

```plantuml
@startuml SEQ_10
skinparam defaultFontName Segoe UI
skinparam shadowing false
skinparam defaultFontSize 13
title SEQ-10 / UC-10 — Xuất tập câu hỏi ngân hàng
actor "Giáo viên" as A
boundary "Giao diện Quesy" as UI
control "Quản lý ngân hàng câu hỏi" as S
database "Kho dữ liệu Quesy" as D
participant "Bộ biên dịch tài liệu ngoài Quesy" as E
autonumber
A -> UI: Chọn tập câu và định dạng
UI -> S: Xuất tập phiên bản có quyền
S -> D: Chốt danh sách phiên bản và tài sản
D --> S: Nội dung được phép
alt Định dạng PDF
  S -> E: Biên dịch nội dung đã chốt
  E --> S: Tệp hoặc lỗi theo vị trí
else Định dạng LaTeX hoặc bảng dữ liệu
  S -> S: Tạo tệp và kiểm tra cấu trúc
end
alt Tệp hợp lệ
  S -> D: Lưu ấn phẩm riêng tư và danh mục nguồn
  D --> S: Mã tệp tải
  S --> UI: Liên kết tải theo quyền
else Lỗi xuất
  S --> UI: Báo câu hoặc tài sản lỗi
end
UI --> A: Tệp hoặc hướng dẫn sửa
@enduml
```


<a id="seq-11"></a>
## SEQ-11 — Số hóa tài liệu nguồn bằng AI

Đối chiếu: [UC-11](08_MO_TA_USE_CASE.md#uc-11); dữ liệu TaiLieuNguon, VungNguon, TaiSan, TacVu, BanTrichXuat.

```plantuml
@startuml SEQ_11
skinparam defaultFontName Segoe UI
skinparam shadowing false
skinparam defaultFontSize 13
title SEQ-11 / UC-11 — Số hóa tài liệu nguồn bằng AI
actor "Giáo viên" as A
boundary "Giao diện Quesy" as UI
control "Điều phối số hóa và hậu kiểm" as S
database "Kho dữ liệu Quesy" as D
participant "Dịch vụ AI/OCR ngoài Quesy" as E
autonumber
A -> UI: Tải tài liệu và chọn trang
UI -> S: Kiểm tra và khởi tạo số hóa
S -> D: Lưu nguồn và tác vụ có khóa chống lặp
D --> S: Mã tác vụ
S --> UI: Đã tiếp nhận; trạng thái đang chờ
S -> S: Pass 1: phân đoạn, cắt hình, cải thiện ảnh
loop Mỗi vùng nguồn cần trích xuất
  S -> E: Pass 2: trích nội dung và chuẩn hóa toán
  alt AI trả kết quả
    E --> S: Nội dung và gợi ý nhãn
    S -> D: Lưu nháp kèm trang, vùng và cảnh báo
    D --> S: Mã bản trích xuất
  else AI lỗi hoặc quá hạn
    E --> S: Lỗi xử lý
    S -> D: Đánh dấu vùng lỗi; giữ vùng đã xong
  end
end
UI -> S: Xem tiến độ tác vụ
S --> UI: Kết quả nháp và vùng cần thử lại
UI --> A: Mở hậu kiểm
@enduml
```


<a id="seq-12"></a>
## SEQ-12 — Hậu kiểm và đưa câu số hóa vào kho

Đối chiếu: [UC-12](08_MO_TA_USE_CASE.md#uc-12); dữ liệu BanTrichXuat, VungNguon, PhienBanCauHoi.

```plantuml
@startuml SEQ_12
skinparam defaultFontName Segoe UI
skinparam shadowing false
skinparam defaultFontSize 13
title SEQ-12 / UC-12 — Hậu kiểm và đưa câu số hóa vào kho
actor "Giáo viên" as A
boundary "Giao diện Quesy" as UI
control "Điều phối số hóa và hậu kiểm" as S
database "Kho dữ liệu Quesy" as D
autonumber
A -> UI: Mở đối chiếu nguồn và bản trích xuất
UI -> S: Lấy câu và vùng nguồn có quyền
S -> D: Đọc bản trích xuất và nguồn
D --> S: Nội dung và vị trí nguồn
S --> UI: Hai khung đối chiếu
A -> UI: Sửa; chọn lưu nháp hoặc xác nhận
UI -> S: Kiểm tra và nhập với khóa chống lặp
S -> D: Đối chiếu tương đồng và trạng thái đã nhập
D --> S: Cảnh báo và kết quả nhập cũ nếu có
alt Đủ điều kiện trạng thái và đã xử lý cảnh báo
  S -> D: Lưu phiên bản, nguồn và kết quả nhập nguyên tử
  D --> S: Mã câu mới hoặc đã nhập trước
  S --> UI: Thành công
else Còn lỗi chặn
  S --> UI: Chỉ cho lưu nháp; liệt kê lỗi
end
UI --> A: Kết quả hậu kiểm
@enduml
```


<a id="seq-13"></a>
## SEQ-13 — Thiết lập ma trận đặc tả

Đối chiếu: [UC-13](08_MO_TA_USE_CASE.md#uc-13); dữ liệu MaTran, PhienBanMaTran, OMaTran, HoSoDe.

```plantuml
@startuml SEQ_13
skinparam defaultFontName Segoe UI
skinparam shadowing false
skinparam defaultFontSize 13
title SEQ-13 / UC-13 — Thiết lập ma trận đặc tả
actor "Giáo viên" as A
boundary "Giao diện Quesy" as UI
control "Lập ma trận và quản lý đề" as S
database "Kho dữ liệu Quesy" as D
autonumber
A -> UI: Nhập cấu trúc và các ô ma trận
UI -> S: Kiểm tra tọa độ và tổng hợp
S -> D: Đọc phiên bản cây và hồ sơ đề
D --> S: Các ràng buộc đang chọn
S -> S: Tính tổng câu, điểm và tỷ lệ
alt Cấu hình hợp lệ hoặc chỉ lưu nháp
  S --> UI: Tổng hợp và cảnh báo
  A -> UI: Xác nhận lưu
  UI -> S: Lưu phiên bản ma trận
  S -> D: Lưu ô và hồ sơ được ghim phiên bản
  D --> S: Phiên bản ma trận
  S --> UI: Lưu thành công
else Mâu thuẫn chưa xử lý
  S --> UI: Chỉ rõ ô sai; không chốt ma trận
end
UI --> A: Kết quả thiết lập
@enduml
```


<a id="seq-14"></a>
## SEQ-14 — Kiểm tra khả năng đáp ứng ma trận

Đối chiếu: [UC-14](08_MO_TA_USE_CASE.md#uc-14); dữ liệu OMaTran, PhienBanCauHoi, BaoCaoThieu.

```plantuml
@startuml SEQ_14
skinparam defaultFontName Segoe UI
skinparam shadowing false
skinparam defaultFontSize 13
title SEQ-14 / UC-14 — Kiểm tra khả năng đáp ứng ma trận
actor "Giáo viên" as A
boundary "Giao diện Quesy" as UI
control "Lập ma trận và quản lý đề" as S
database "Kho dữ liệu Quesy" as D
autonumber
A -> UI: Kiểm tra đáp ứng ma trận
UI -> S: Đánh giá phiên bản ma trận
S -> D: Lấy câu sẵn sàng và lịch sử dùng được phép
D --> S: Tập ứng viên theo ô
S -> S: Đếm ô; thử phân bổ toàn cục không trùng câu
alt Có phân bổ đáp ứng toàn bộ
  S --> UI: Đạt tại thời điểm kiểm tra
else Thiếu hoặc xung đột ứng viên giữa ô
  S --> UI: Tọa độ ô, cần/có/thiếu và nhóm xung đột
end
UI --> A: Báo cáo tồn kho
@enduml
```


<a id="seq-15"></a>
## SEQ-15 — Sinh đề gốc theo ma trận

Đối chiếu: [UC-15](08_MO_TA_USE_CASE.md#uc-15); dữ liệu DeGoc, PhienBanDe, MucDe, BanChupCauHoi, PhienBanMaTran.

```plantuml
@startuml SEQ_15
skinparam defaultFontName Segoe UI
skinparam shadowing false
skinparam defaultFontSize 13
title SEQ-15 / UC-15 — Sinh đề gốc theo ma trận
actor "Giáo viên" as A
boundary "Giao diện Quesy" as UI
control "Lập ma trận và quản lý đề" as S
database "Kho dữ liệu Quesy" as D
autonumber
A -> UI: Sinh đề từ phiên bản ma trận
UI -> S: Yêu cầu sinh đề có khóa chống lặp
S -> D: Đọc ma trận và câu sẵn sàng hiện tại
D --> S: Tập ứng viên có phiên bản
ref over S: UC-14: kiểm tra tồn kho và phân bổ toàn cục
alt Đáp ứng đủ mọi ô
  S -> S: Chọn câu; giữ nhóm ngữ liệu và phần
  S -> S: Kiểm chứng phân bổ, tổng câu và điểm
  S -> D: Chốt đề nháp và bản chụp nguyên tử
  D --> S: Phiên bản đề gốc
  S --> UI: Đề nháp và đối chiếu ma trận
else Thiếu hoặc dữ liệu đã thay đổi
  S --> UI: Thiếu theo tọa độ; không tạo đề một phần
end
UI --> A: Kết quả sinh đề
@enduml
```


<a id="seq-16"></a>
## SEQ-16 — Biên soạn và xem trước đề

Đối chiếu: [UC-16](08_MO_TA_USE_CASE.md#uc-16); dữ liệu PhienBanDe, MucDe, TaiSan.

```plantuml
@startuml SEQ_16
skinparam defaultFontName Segoe UI
skinparam shadowing false
skinparam defaultFontSize 13
title SEQ-16 / UC-16 — Biên soạn và xem trước đề
actor "Giáo viên" as A
boundary "Giao diện Quesy" as UI
control "Biên soạn và kiểm định đề" as S
database "Kho dữ liệu Quesy" as D
participant "Bộ biên dịch tài liệu ngoài Quesy" as E
autonumber
A -> UI: Sửa đề và yêu cầu xem trước
UI -> S: Lưu nháp kèm phiên bản kỳ vọng
S -> D: Kiểm tra quyền và lưu phiên bản mới
D --> S: Phiên bản nháp hoặc xung đột
alt Lưu thành công
  S -> E: Biên dịch đúng phiên bản nháp
  alt Biên dịch thành công
    E --> S: PDF xem trước và phiên bản nguồn
    S --> UI: Bản xem trước có nhãn phiên bản
  else Có lỗi
    E --> S: Vị trí và thông tin lỗi
    S --> UI: Giữ nháp; đánh dấu lỗi biên dịch
  end
else Xung đột phiên bản
  S --> UI: Yêu cầu đối chiếu; không ghi đè
end
UI --> A: Nội dung và trạng thái xem trước
@enduml
```


<a id="seq-17"></a>
## SEQ-17 — Nhận và duyệt đề xuất của Copilot

Đối chiếu: [UC-17](08_MO_TA_USE_CASE.md#uc-17); dữ liệu DeXuatAI, PhienBanDe, TacVu.

```plantuml
@startuml SEQ_17
skinparam defaultFontName Segoe UI
skinparam shadowing false
skinparam defaultFontSize 13
title SEQ-17 / UC-17 — Nhận và duyệt đề xuất của Copilot
actor "Giáo viên" as A
boundary "Giao diện Quesy" as UI
control "Biên soạn và kiểm định đề" as S
database "Kho dữ liệu Quesy" as D
participant "Dịch vụ AI/OCR ngoài Quesy" as E
autonumber
A -> UI: Gửi yêu cầu và phạm vi câu
UI -> S: Chốt ngữ cảnh theo phiên bản
S -> D: Đọc nội dung có quyền và hạn mức
D --> S: Ngữ cảnh tối thiểu
S -> E: Yêu cầu gợi ý hoặc giải thích
alt AI phản hồi
  E --> S: Đề xuất hoặc câu trả lời
  S --> UI: So sánh trước/sau; chưa áp dụng
  A -> UI: Chấp nhận phần sửa hoặc từ chối
  UI -> S: Quyết định kèm phiên bản nền
  alt Chấp nhận và phiên bản nền còn đúng
    S -> D: Lưu phiên bản nháp mới
    D --> S: Phiên bản mới
    S --> UI: Đã áp dụng phần chấp nhận
  else Từ chối, hỏi đáp hoặc xung đột
    S --> UI: Giữ nguyên đề; báo lý do nếu xung đột
  end
else AI lỗi
  E --> S: Lỗi hoặc quá hạn
  S --> UI: Giữ nguyên nháp
end
UI --> A: Kết quả trợ lý
@enduml
```


<a id="seq-18"></a>
## SEQ-18 — Thay câu bằng đối chiếu song song

Đối chiếu: [UC-18](08_MO_TA_USE_CASE.md#uc-18); dữ liệu PhienBanDe, MucDe, BanChupCauHoi, DeXuatAI.

```plantuml
@startuml SEQ_18
skinparam defaultFontName Segoe UI
skinparam shadowing false
skinparam defaultFontSize 13
title SEQ-18 / UC-18 — Thay câu bằng đối chiếu song song
actor "Giáo viên" as A
boundary "Giao diện Quesy" as UI
control "Biên soạn và kiểm định đề" as S
database "Kho dữ liệu Quesy" as D
autonumber
A -> UI: Chọn câu cần thay
UI -> S: Tìm ứng viên tương đương
S -> D: Tìm cùng ô, loại câu đã dùng và ngoài quyền
D --> S: Tập ứng viên
S --> UI: So sánh song song với câu hiện tại
opt Giáo viên yêu cầu sinh ứng viên AI
  ref over A,S: UC-17: sinh đề xuất và giáo viên duyệt
end
A -> UI: Chọn ứng viên và xác nhận
UI -> S: Thay câu kèm phiên bản nền
S -> S: Kiểm tra ô, điểm, nhóm và không trùng
alt Đúng ràng buộc và phiên bản
  S -> D: Lưu bản chụp thay thế trong phiên bản mới
  D --> S: Phiên bản đề mới
  S --> UI: Đã thay câu
else Không còn phù hợp
  S --> UI: Giữ câu cũ; nêu lý do
end
UI --> A: Kết quả thay thế
@enduml
```


<a id="seq-19"></a>
## SEQ-19 — Kiểm định đề và chốt phiên bản

Đối chiếu: [UC-19](08_MO_TA_USE_CASE.md#uc-19); dữ liệu BaoCaoQA, PhienBanDe.

```plantuml
@startuml SEQ_19
skinparam defaultFontName Segoe UI
skinparam shadowing false
skinparam defaultFontSize 13
title SEQ-19 / UC-19 — Kiểm định đề và chốt phiên bản
actor "Giáo viên" as A
boundary "Giao diện Quesy" as UI
control "Biên soạn và kiểm định đề" as S
database "Kho dữ liệu Quesy" as D
autonumber
A -> UI: Yêu cầu QA phiên bản đề
UI -> S: Kiểm định cấu trúc và ma trận
S -> D: Lấy bản chụp, tài sản và hồ sơ đã ghim
D --> S: Dữ liệu phiên bản
S -> S: Kiểm tra cấu trúc, công thức, lời giải và phân bổ
S -> D: Lưu báo cáo QA gắn phiên bản
D --> S: Mã báo cáo
S --> UI: Lỗi theo câu; đáp án ẩn ở bước rà soát mù
A -> UI: Xác nhận chốt sau khi rà soát chuyên môn
UI -> S: Chốt đúng phiên bản đã QA
alt Không có lỗi chặn và phiên bản không đổi
  S -> D: Đánh dấu phiên bản đã chốt
  D --> S: Xác nhận
  S --> UI: Đề đủ điều kiện trộn / xuất
else Lỗi chặn hoặc phiên bản đã đổi
  S --> UI: Không chốt; yêu cầu sửa và QA lại
end
UI --> A: Báo cáo và trạng thái đề
@enduml
```


<a id="seq-20"></a>
## SEQ-20 — Sinh các mã đề hoán vị an toàn

Đối chiếu: [UC-20](08_MO_TA_USE_CASE.md#uc-20); dữ liệu PhienBanDe, MaDe, AnhXaCau, AnhXaLuaChon.

```plantuml
@startuml SEQ_20
skinparam defaultFontName Segoe UI
skinparam shadowing false
skinparam defaultFontSize 13
title SEQ-20 / UC-20 — Sinh các mã đề hoán vị an toàn
actor "Giáo viên" as A
boundary "Giao diện Quesy" as UI
control "Lập ma trận và quản lý đề" as S
database "Kho dữ liệu Quesy" as D
autonumber
A -> UI: Yêu cầu sinh bộ mã đề
UI -> S: Trộn phiên bản đề đã chốt
S -> D: Đọc đề, báo cáo QA và quy tắc
D --> S: Bản chụp bất biến
alt QA còn hiệu lực và cấu hình hợp lệ
  loop Mỗi mã đề
    S -> S: Trộn trong phần; giữ nhóm và phương án neo
    S -> S: Tạo ánh xạ câu, lựa chọn và ý Đúng/Sai
    S -> S: Kiểm chứng song ánh và đáp án
  end
  alt Tất cả mã đạt bất biến
    S -> D: Lưu cả bộ mã và ánh xạ nguyên tử
    D --> S: Bộ mã đã kiểm chứng
    S --> UI: Mã đề và bảng đáp án
  else Có vi phạm
    S --> UI: Không công bố bộ; trả vi phạm
  end
else Đề chưa đủ điều kiện
  S --> UI: Yêu cầu QA hoặc sửa cấu hình
end
UI --> A: Kết quả trộn
@enduml
```


<a id="seq-21"></a>
## SEQ-21 — Xuất bản bộ ấn phẩm khảo thí

Đối chiếu: [UC-21](08_MO_TA_USE_CASE.md#uc-21); dữ liệu AnPham, PhienBanDe, MaDe, HoSoDe, TacVu.

```plantuml
@startuml SEQ_21
skinparam defaultFontName Segoe UI
skinparam shadowing false
skinparam defaultFontSize 13
title SEQ-21 / UC-21 — Xuất bản bộ ấn phẩm khảo thí
actor "Giáo viên" as A
boundary "Giao diện Quesy" as UI
control "Xuất bản ấn phẩm" as S
database "Kho dữ liệu Quesy" as D
participant "Bộ biên dịch tài liệu ngoài Quesy" as E
autonumber
A -> UI: Chọn đề, mã và loại ấn phẩm
UI -> S: Xuất bản đúng phiên bản đã chốt
S -> D: Đọc QA, ánh xạ và tài sản
D --> S: Bộ dữ liệu đã kiểm chứng
S -> E: Biên dịch đề / đáp án / lời giải riêng
alt Biên dịch thành công
  E --> S: Các tệp cùng mã đề và phiên bản
  S -> S: Kiểm tra tệp, tách đáp án và lập danh mục gói
  alt Mọi ấn phẩm hợp lệ
    S -> D: Lưu gói hoàn tất và phạm vi tải
    D --> S: Mã gói tải riêng tư
    S --> UI: Tệp và danh mục phiên bản
  else Sai mã hoặc lẫn đáp án
    S --> UI: Chặn công bố; báo tệp lỗi
  end
else Có lỗi biên dịch
  E --> S: Lỗi theo câu hoặc mã đề
  S --> UI: Chưa hoàn tất; hướng dẫn sửa
end
UI --> A: Kết quả xuất bản
@enduml
```


<a id="seq-22"></a>
## SEQ-22 — Quản lý danh sách lớp và kỳ chấm

Đối chiếu: [UC-22](08_MO_TA_USE_CASE.md#uc-22); dữ liệu LopHoc, HocSinh, DangKyLop, KyCham.

```plantuml
@startuml SEQ_22
skinparam defaultFontName Segoe UI
skinparam shadowing false
skinparam defaultFontSize 13
title SEQ-22 / UC-22 — Quản lý danh sách lớp và kỳ chấm
actor "Giáo viên" as A
boundary "Giao diện Quesy" as UI
control "Chấm và phân tích" as S
database "Kho dữ liệu Quesy" as D
autonumber
A -> UI: Nhập danh sách lớp và chọn bộ đề
UI -> S: Kiểm tra danh sách
S -> D: Đối chiếu mã trong lớp và phiên bản đề
D --> S: Trùng lặp và tham chiếu điểm
alt Danh sách hợp lệ
  S --> UI: Bản xem trước
  A -> UI: Xác nhận danh sách và kỳ chấm
  UI -> S: Lưu cấu hình kỳ chấm
  S -> D: Lưu lớp, học sinh, đăng ký và kỳ chấm
  D --> S: Mã kỳ chấm
  S --> UI: Hoàn tất
else Có dòng lỗi
  S --> UI: Báo từng dòng; chưa nhập
end
UI --> A: Danh sách và kỳ chấm
@enduml
```


<a id="seq-23"></a>
## SEQ-23 — Nhập bài và chấm theo đúng mã đề

Đối chiếu: [UC-23](08_MO_TA_USE_CASE.md#uc-23); dữ liệu BaiLam, TraLoi, KetQuaCham, DiemThanhPhan, KyCham, HoSoCham.

```plantuml
@startuml SEQ_23
skinparam defaultFontName Segoe UI
skinparam shadowing false
skinparam defaultFontSize 13
title SEQ-23 / UC-23 — Nhập bài và chấm theo đúng mã đề
actor "Giáo viên" as A
boundary "Giao diện Quesy" as UI
control "Chấm và phân tích" as S
database "Kho dữ liệu Quesy" as D
autonumber
A -> UI: Nhập bài, ảnh phiếu và kỳ chấm
UI -> S: Tiếp nhận câu trả lời
opt Nguồn là ảnh phiếu
  S -> S: Nhận dạng ô và đánh dấu mơ hồ
end
S -> D: Lấy danh sách, đúng mã đề và hồ sơ chấm đã ghim
D --> S: Ánh xạ đáp án và học sinh
S --> UI: Các ô cần xác minh
A -> UI: Sửa ô mờ; xác nhận mã và điểm tự luận
UI -> S: Yêu cầu tính điểm
alt Mã đề xác định và hết dữ liệu mơ hồ
  S -> S: Tính điểm theo hồ sơ và từng dạng câu
  S --> UI: Điểm thành phần để rà soát
  A -> UI: Chốt kết quả
  UI -> S: Lưu kết quả kèm phiên bản
  S -> D: Lưu bài, điểm và lịch sử nguyên tử
  D --> S: Phiên bản kết quả
  S --> UI: Kết quả đã chốt
else Thiếu mã hoặc còn ô chưa xác minh
  S --> UI: Giữ bài chờ; không công bố điểm
end
UI --> A: Kết quả hoặc yêu cầu xác minh
@enduml
```


<a id="seq-24"></a>
## SEQ-24 — Phân tích kết quả và chất lượng câu hỏi

Đối chiếu: [UC-24](08_MO_TA_USE_CASE.md#uc-24); dữ liệu KetQuaCham, BaoCaoPhanTich, AnhXaCau.

```plantuml
@startuml SEQ_24
skinparam defaultFontName Segoe UI
skinparam shadowing false
skinparam defaultFontSize 13
title SEQ-24 / UC-24 — Phân tích kết quả và chất lượng câu hỏi
actor "Giáo viên" as A
boundary "Giao diện Quesy" as UI
control "Chấm và phân tích" as S
database "Kho dữ liệu Quesy" as D
autonumber
A -> UI: Chọn kỳ chấm và mẫu phân tích
UI -> S: Tổng hợp kết quả có quyền
S -> D: Đọc điểm đã chốt và ánh xạ câu gốc
D --> S: Mẫu hợp lệ và phiên bản chấm
S -> S: Quy về câu gốc; tính phổ điểm và kích thước mẫu
alt Mẫu đủ theo quy tắc chỉ số
  S -> S: Tính p, D cho MCQ; tách các dạng còn lại
  S -> D: Lưu báo cáo và quy tắc chọn mẫu
  D --> S: Mã báo cáo
  S --> UI: Chỉ số, mẫu số và giới hạn diễn giải
else Không đủ dữ liệu
  S --> UI: Phổ điểm nếu có; chỉ số chưa xác định
end
UI --> A: Báo cáo hoặc thông báo thiếu mẫu
@enduml
```


<a id="seq-25"></a>
## SEQ-25 — Quản lý tài khoản và quyền truy cập

Đối chiếu: [UC-25](08_MO_TA_USE_CASE.md#uc-25); dữ liệu TaiKhoan, VaiTro, PhienDangNhap, NhatKy.

```plantuml
@startuml SEQ_25
skinparam defaultFontName Segoe UI
skinparam shadowing false
skinparam defaultFontSize 13
title SEQ-25 / UC-25 — Quản lý tài khoản và quyền truy cập
actor "Quản trị viên kỹ thuật" as A
boundary "Giao diện Quesy" as UI
control "Quản trị vận hành" as S
database "Kho dữ liệu Quesy" as D
autonumber
A -> UI: Chọn tài khoản và thay đổi quyền
UI -> S: Kiểm tra tác động quản trị
S -> D: Đọc vai trò, phiên bản và quản trị viên còn hoạt động
D --> S: Trạng thái và điều kiện bảo vệ
S --> UI: Bản xem trước tác động
A -> UI: Xác minh và xác nhận lý do
UI -> S: Áp dụng thay đổi
alt Đủ quyền và còn quản trị viên hoạt động
  S -> D: Cập nhật quyền; thu hồi phiên; ghi nhật ký
  D --> S: Hoàn tất
  S --> UI: Kết quả thay đổi
else Vi phạm điều kiện bảo vệ
  S --> UI: Từ chối; không thay đổi quyền
end
UI --> A: Kết quả quản trị
@enduml
```


<a id="seq-26"></a>
## SEQ-26 — Quản lý danh mục kiến thức dùng chung

Đối chiếu: [UC-26](08_MO_TA_USE_CASE.md#uc-26); dữ liệu PhienBanDanhMuc, NutKienThuc, NhatKy.

```plantuml
@startuml SEQ_26
skinparam defaultFontName Segoe UI
skinparam shadowing false
skinparam defaultFontSize 13
title SEQ-26 / UC-26 — Quản lý danh mục kiến thức dùng chung
actor "Quản trị viên kỹ thuật" as A
boundary "Giao diện Quesy" as UI
control "Quản trị vận hành" as S
database "Kho dữ liệu Quesy" as D
autonumber
A -> UI: Soạn bản danh mục chung và nguồn
UI -> S: Kiểm tra cấu trúc và tác động
S -> D: Đọc danh mục và tham chiếu hiện hành
D --> S: Cây, mã và số tham chiếu
S --> UI: Khác biệt và cảnh báo di chuyển nhãn
A -> UI: Xác nhận công bố
UI -> S: Phát hành phiên bản danh mục
alt Hợp lệ và có nguồn tham chiếu
  S -> D: Lưu phiên bản mới và nhật ký; giữ bản cũ
  D --> S: Mã phiên bản mới
  S --> UI: Đã công bố
else Thiếu nguồn hoặc sai cấu trúc
  S --> UI: Không công bố; chỉ rõ lỗi
end
UI --> A: Trạng thái danh mục
@enduml
```


<a id="seq-27"></a>
## SEQ-27 — Quản lý hồ sơ đề và quy tắc chấm

Đối chiếu: [UC-27](08_MO_TA_USE_CASE.md#uc-27); dữ liệu HoSoDe, HoSoCham, NhatKy.

```plantuml
@startuml SEQ_27
skinparam defaultFontName Segoe UI
skinparam shadowing false
skinparam defaultFontSize 13
title SEQ-27 / UC-27 — Quản lý hồ sơ đề và quy tắc chấm
actor "Quản trị viên kỹ thuật" as A
boundary "Giao diện Quesy" as UI
control "Quản trị vận hành" as S
database "Kho dữ liệu Quesy" as D
autonumber
A -> UI: Nhập hồ sơ cấu trúc và chấm
UI -> S: Kiểm tra quy tắc và ca mẫu
S -> S: Kiểm tra 0..4 ý đúng, dấu thập phân và tổng điểm
S --> UI: Kết quả ca mẫu và nguồn tham chiếu
A -> UI: Xác nhận phát hành
UI -> S: Công bố hồ sơ mới
alt Quy tắc nhất quán và ca mẫu đạt
  S -> D: Lưu phiên bản hồ sơ và nhật ký
  D --> S: Mã hồ sơ mới
  S --> UI: Được chọn cho đề mới
else Có ca mẫu sai
  S --> UI: Chặn công bố; chỉ rõ trường sai
end
UI --> A: Kết quả cấu hình
@enduml
```


<a id="seq-28"></a>
## SEQ-28 — Cấu hình dịch vụ AI và biên dịch

Đối chiếu: [UC-28](08_MO_TA_USE_CASE.md#uc-28); dữ liệu CauHinhDichVu, TacVu, NhatKy.

```plantuml
@startuml SEQ_28
skinparam defaultFontName Segoe UI
skinparam shadowing false
skinparam defaultFontSize 13
title SEQ-28 / UC-28 — Cấu hình dịch vụ AI và biên dịch
actor "Quản trị viên kỹ thuật" as A
boundary "Giao diện Quesy" as UI
control "Quản trị vận hành" as S
database "Kho dữ liệu Quesy" as D
participant "Dịch vụ AI hoặc biên dịch được thử" as E
autonumber
A -> UI: Nhập cấu hình và chính sách dữ liệu
UI -> S: Lưu bản cấu hình chờ kiểm tra
S -> D: Lưu bí mật được bảo vệ và phiên bản nháp
D --> S: Tham chiếu bí mật
S -> E: Thử AI / biên dịch bằng dữ liệu mẫu
alt Thử kết nối đạt
  E --> S: Năng lực và trạng thái dịch vụ
  S --> UI: Kết quả thử; bí mật đã che
  A -> UI: Xác nhận kích hoạt
  UI -> S: Kích hoạt phiên bản đã thử
  S -> D: Đổi bản hoạt động; lưu nhật ký và bản trước
  D --> S: Cấu hình hoạt động mới
  S --> UI: Hoàn tất
else Kết nối lỗi
  E --> S: Lỗi hoặc quá hạn
  S --> UI: Giữ cấu hình hoạt động cũ
end
UI --> A: Trạng thái cấu hình
@enduml
```


<a id="seq-29"></a>
## SEQ-29 — Giám sát tác vụ, nhật ký và xử lý lỗi

Đối chiếu: [UC-29](08_MO_TA_USE_CASE.md#uc-29); dữ liệu TacVu, LanChay, NhatKy.

```plantuml
@startuml SEQ_29
skinparam defaultFontName Segoe UI
skinparam shadowing false
skinparam defaultFontSize 13
title SEQ-29 / UC-29 — Giám sát tác vụ, nhật ký và xử lý lỗi
actor "Quản trị viên kỹ thuật" as A
boundary "Giao diện Quesy" as UI
control "Quản trị vận hành" as S
database "Kho dữ liệu Quesy" as D
autonumber
A -> UI: Lọc lỗi và chọn tác vụ
UI -> S: Lấy trạng thái vận hành
S -> D: Đọc tác vụ và nhật ký đã che
D --> S: Tiến độ, lỗi và các lần chạy
S --> UI: Thông tin chẩn đoán
A -> UI: Hủy hoặc thử lại phần lỗi
UI -> S: Gửi lệnh kèm trạng thái kỳ vọng
alt Trạng thái cho phép và đủ quyền
  S -> D: Ghi lệnh và lần chạy có khóa chống lặp
  D --> S: Trạng thái mới
  S --> UI: Đã tiếp nhận lệnh
else Trạng thái không còn phù hợp
  S --> UI: Không chạy lặp; trả trạng thái hiện hành
end
UI --> A: Kết quả xử lý
@enduml
```


<a id="seq-30"></a>
## SEQ-30 — Sao lưu và khôi phục hệ thống

Đối chiếu: [UC-30](08_MO_TA_USE_CASE.md#uc-30); dữ liệu BanSaoLuu, NhatKy, TacVu.

```plantuml
@startuml SEQ_30
skinparam defaultFontName Segoe UI
skinparam shadowing false
skinparam defaultFontSize 13
title SEQ-30 / UC-30 — Sao lưu và khôi phục hệ thống
actor "Quản trị viên kỹ thuật" as A
boundary "Giao diện Quesy" as UI
control "Quản trị vận hành" as S
database "Kho dữ liệu Quesy" as D
participant "Kho sao lưu ngoài Quesy" as E
autonumber
A -> UI: Chọn sao lưu hoặc phục hồi
UI -> S: Kiểm tra quyền và phạm vi
S -> D: Đọc danh mục dữ liệu và điểm quay lui
D --> S: Tham chiếu dữ liệu và tài sản
alt Sao lưu
  S -> E: Ghi ảnh chụp nhất quán đã bảo vệ
  E --> S: Mã bản sao và mã kiểm tra
else Phục hồi
  S -> E: Đọc bản sao vào vùng kiểm tra
  E --> S: Dữ liệu và danh mục tài sản
end
S -> S: Kiểm tra tính toàn vẹn và tương thích
alt Toàn vẹn đạt
  S --> UI: Báo cáo kiểm tra
  opt Đang phục hồi
    A -> UI: Xác minh; xác nhận chuyển hoạt động
    UI -> S: Chuyển trong cửa sổ bảo trì
    S -> D: Chuyển dữ liệu; quay lui nếu chuyển lỗi
    D --> S: Kết quả chuyển hoặc quay lui
  end
  S -> D: Ghi bản sao / kết quả phục hồi và nhật ký
  S --> UI: Kết quả có đối soát
else Sai toàn vẹn
  S --> UI: Không chuyển; giữ dữ liệu hoạt động
end
UI --> A: Trạng thái sao lưu / phục hồi
@enduml
```
