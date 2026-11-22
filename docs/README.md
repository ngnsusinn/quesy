# Tài liệu Quesy

## Báo cáo hiện trạng 22/11/2026

Ba báo cáo Word đối chiếu với bản mã `557cb3f` trên `main`:

- [Kiến trúc hệ thống Quesy](bao_cao_hien_trang/01_kien_truc_he_thong_quesy.docx)
- [Lược đồ Use Case Quesy](bao_cao_hien_trang/02_luoc_do_use_case_quesy.docx)
- [Lược đồ lớp Quesy](bao_cao_hien_trang/03_luoc_do_lop_quesy.docx)

Bản tài liệu 2.0 dùng 15 sơ đồ [PlantUML](https://plantuml.com/) và lưu [mã nguồn sơ đồ](bao_cao_hien_trang/plantuml/) để chỉnh sửa. Các tệp có tiền tố **arch** cho kiến trúc, **uc** cho Use Case, **class** cho lược đồ lớp. Báo cáo Use Case đặc tả 23 mục tiêu theo 13 trường và rà soát theo checklist C1–C20 của *use-case-writer* (Phúc NT, BA Zone).

Khi đã có Java, PlantUML và Graphviz, có thể kết xuất lại các sơ đồ bằng lệnh sau từ thư mục gốc của dự án.

~~~shell
java -jar plantuml.jar -charset UTF-8 -failfast2 -tpng -o render docs/bao_cao_hien_trang/plantuml
~~~

## Bộ phân tích nghiệp vụ 17/11/2026

Bắt đầu tại [Bộ phân tích hệ thống từ PDF](phan_tich_he_thong/00_MUC_LUC_VA_CO_SO_PHAN_TICH.md).

Bộ ngày 17/11/2026 gồm yêu cầu chức năng/phi chức năng, tác nhân, Use Case người dùng và quản trị, mô tả Use Case, cùng sơ đồ PlantUML Use Case, Activity, Class và Sequence. Bản phân tích dựa trên bối cảnh nghiệp vụ và phương pháp của 5 PDF trong `pdf/`, không đọc mã nguồn để suy ra yêu cầu.

Phạm vi đã xác nhận: giáo viên quản lý kho cá nhân; quản trị viên quản lý tài khoản, cấu hình và vận hành kỹ thuật. Các đề xuất chưa được duyệt chi tiết có nhãn và giả định rõ trong bộ mới.

Các đặc tả cũ tại thư mục này được giữ để đối chiếu lịch sử. [Hướng dẫn ex_test](GUIDELINE_EX_TEST.md) vẫn là tài liệu chuyên biệt. Báo cáo kiểm thử cũ mô tả lần kiểm thử trước, không chứng minh bộ yêu cầu mới đã được triển khai.
