# Truy vết và tiêu chí nghiệm thu tài liệu

> Quesy · Bản phân tích nghiệp vụ 1.0 · Ngày 17/11/2026
> Trạng thái: bản đặc tả đề xuất, không phải báo cáo chức năng đã triển khai.

## Phạm vi truy vết

Mỗi dòng dưới đây có đúng một FR, một UC và sơ đồ Activity/Sequence riêng. Sơ đồ Use Case chi tiết nằm trong tài liệu 07; lớp miền có thể tham gia nhiều mục tiêu. Không có mã Use Case ngầm cho các bước nội bộ; các bước như chuẩn hóa toán hoặc tính tổng nằm trong mục tiêu nghiệp vụ bao chứa.

| FR | Use Case | Use Case Diagram | Activity | Sequence | Lớp miền chính |
|---|---|---|---|---|---|
| [FR-01](02_YEU_CAU_CHUC_NANG.md#fr-01) | [UC-01](08_MO_TA_USE_CASE.md#uc-01) | [UCD-01](07_SO_DO_USE_CASE.md#ucd-01) | [ACT-01](09_SO_DO_HOAT_DONG.md#act-01) | [SEQ-01](11_SO_DO_TUAN_TU.md#seq-01) | TaiKhoan, KhongGian |
| [FR-02](02_YEU_CAU_CHUC_NANG.md#fr-02) | [UC-02](08_MO_TA_USE_CASE.md#uc-02) | [UCD-02](07_SO_DO_USE_CASE.md#ucd-02) | [ACT-02](09_SO_DO_HOAT_DONG.md#act-02) | [SEQ-02](11_SO_DO_TUAN_TU.md#seq-02) | TaiKhoan, PhienDangNhap |
| [FR-03](02_YEU_CAU_CHUC_NANG.md#fr-03) | [UC-03](08_MO_TA_USE_CASE.md#uc-03) | [UCD-03](07_SO_DO_USE_CASE.md#ucd-03) | [ACT-03](09_SO_DO_HOAT_DONG.md#act-03) | [SEQ-03](11_SO_DO_TUAN_TU.md#seq-03) | PhienDangNhap |
| [FR-04](02_YEU_CAU_CHUC_NANG.md#fr-04) | [UC-04](08_MO_TA_USE_CASE.md#uc-04) | [UCD-04](07_SO_DO_USE_CASE.md#ucd-04) | [ACT-04](09_SO_DO_HOAT_DONG.md#act-04) | [SEQ-04](11_SO_DO_TUAN_TU.md#seq-04) | TaiKhoan, PhienDangNhap |
| [FR-05](02_YEU_CAU_CHUC_NANG.md#fr-05) | [UC-05](08_MO_TA_USE_CASE.md#uc-05) | [UCD-05](07_SO_DO_USE_CASE.md#ucd-05) | [ACT-05](09_SO_DO_HOAT_DONG.md#act-05) | [SEQ-05](11_SO_DO_TUAN_TU.md#seq-05) | NutKienThuc, KhongGian |
| [FR-06](02_YEU_CAU_CHUC_NANG.md#fr-06) | [UC-06](08_MO_TA_USE_CASE.md#uc-06) | [UCD-06](07_SO_DO_USE_CASE.md#ucd-06) | [ACT-06](09_SO_DO_HOAT_DONG.md#act-06) | [SEQ-06](11_SO_DO_TUAN_TU.md#seq-06) | CauHoi, PhienBanCauHoi, TaiSan |
| [FR-07](02_YEU_CAU_CHUC_NANG.md#fr-07) | [UC-07](08_MO_TA_USE_CASE.md#uc-07) | [UCD-07](07_SO_DO_USE_CASE.md#ucd-07) | [ACT-07](09_SO_DO_HOAT_DONG.md#act-07) | [SEQ-07](11_SO_DO_TUAN_TU.md#seq-07) | CauHoi, PhienBanCauHoi, PhuongAn, MenhDe, KetQuaTuongDong |
| [FR-08](02_YEU_CAU_CHUC_NANG.md#fr-08) | [UC-08](08_MO_TA_USE_CASE.md#uc-08) | [UCD-08](07_SO_DO_USE_CASE.md#ucd-08) | [ACT-08](09_SO_DO_HOAT_DONG.md#act-08) | [SEQ-08](11_SO_DO_TUAN_TU.md#seq-08) | CauHoi, PhienBanCauHoi, NhatKy |
| [FR-09](02_YEU_CAU_CHUC_NANG.md#fr-09) | [UC-09](08_MO_TA_USE_CASE.md#uc-09) | [UCD-09](07_SO_DO_USE_CASE.md#ucd-09) | [ACT-09](09_SO_DO_HOAT_DONG.md#act-09) | [SEQ-09](11_SO_DO_TUAN_TU.md#seq-09) | LoNhap, DongNhap, PhienBanCauHoi |
| [FR-10](02_YEU_CAU_CHUC_NANG.md#fr-10) | [UC-10](08_MO_TA_USE_CASE.md#uc-10) | [UCD-10](07_SO_DO_USE_CASE.md#ucd-10) | [ACT-10](09_SO_DO_HOAT_DONG.md#act-10) | [SEQ-10](11_SO_DO_TUAN_TU.md#seq-10) | PhienBanCauHoi, AnPham, TacVu |
| [FR-11](02_YEU_CAU_CHUC_NANG.md#fr-11) | [UC-11](08_MO_TA_USE_CASE.md#uc-11) | [UCD-11](07_SO_DO_USE_CASE.md#ucd-11) | [ACT-11](09_SO_DO_HOAT_DONG.md#act-11) | [SEQ-11](11_SO_DO_TUAN_TU.md#seq-11) | TaiLieuNguon, VungNguon, TaiSan, TacVu, BanTrichXuat |
| [FR-12](02_YEU_CAU_CHUC_NANG.md#fr-12) | [UC-12](08_MO_TA_USE_CASE.md#uc-12) | [UCD-12](07_SO_DO_USE_CASE.md#ucd-12) | [ACT-12](09_SO_DO_HOAT_DONG.md#act-12) | [SEQ-12](11_SO_DO_TUAN_TU.md#seq-12) | BanTrichXuat, VungNguon, PhienBanCauHoi |
| [FR-13](02_YEU_CAU_CHUC_NANG.md#fr-13) | [UC-13](08_MO_TA_USE_CASE.md#uc-13) | [UCD-13](07_SO_DO_USE_CASE.md#ucd-13) | [ACT-13](09_SO_DO_HOAT_DONG.md#act-13) | [SEQ-13](11_SO_DO_TUAN_TU.md#seq-13) | MaTran, PhienBanMaTran, OMaTran, HoSoDe |
| [FR-14](02_YEU_CAU_CHUC_NANG.md#fr-14) | [UC-14](08_MO_TA_USE_CASE.md#uc-14) | [UCD-14](07_SO_DO_USE_CASE.md#ucd-14) | [ACT-14](09_SO_DO_HOAT_DONG.md#act-14) | [SEQ-14](11_SO_DO_TUAN_TU.md#seq-14) | OMaTran, PhienBanCauHoi, BaoCaoThieu |
| [FR-15](02_YEU_CAU_CHUC_NANG.md#fr-15) | [UC-15](08_MO_TA_USE_CASE.md#uc-15) | [UCD-15](07_SO_DO_USE_CASE.md#ucd-15) | [ACT-15](09_SO_DO_HOAT_DONG.md#act-15) | [SEQ-15](11_SO_DO_TUAN_TU.md#seq-15) | DeGoc, PhienBanDe, MucDe, BanChupCauHoi, PhienBanMaTran |
| [FR-16](02_YEU_CAU_CHUC_NANG.md#fr-16) | [UC-16](08_MO_TA_USE_CASE.md#uc-16) | [UCD-16](07_SO_DO_USE_CASE.md#ucd-16) | [ACT-16](09_SO_DO_HOAT_DONG.md#act-16) | [SEQ-16](11_SO_DO_TUAN_TU.md#seq-16) | PhienBanDe, MucDe, TaiSan |
| [FR-17](02_YEU_CAU_CHUC_NANG.md#fr-17) | [UC-17](08_MO_TA_USE_CASE.md#uc-17) | [UCD-17](07_SO_DO_USE_CASE.md#ucd-17) | [ACT-17](09_SO_DO_HOAT_DONG.md#act-17) | [SEQ-17](11_SO_DO_TUAN_TU.md#seq-17) | DeXuatAI, PhienBanDe, TacVu |
| [FR-18](02_YEU_CAU_CHUC_NANG.md#fr-18) | [UC-18](08_MO_TA_USE_CASE.md#uc-18) | [UCD-18](07_SO_DO_USE_CASE.md#ucd-18) | [ACT-18](09_SO_DO_HOAT_DONG.md#act-18) | [SEQ-18](11_SO_DO_TUAN_TU.md#seq-18) | PhienBanDe, MucDe, BanChupCauHoi, DeXuatAI |
| [FR-19](02_YEU_CAU_CHUC_NANG.md#fr-19) | [UC-19](08_MO_TA_USE_CASE.md#uc-19) | [UCD-19](07_SO_DO_USE_CASE.md#ucd-19) | [ACT-19](09_SO_DO_HOAT_DONG.md#act-19) | [SEQ-19](11_SO_DO_TUAN_TU.md#seq-19) | BaoCaoQA, PhienBanDe |
| [FR-20](02_YEU_CAU_CHUC_NANG.md#fr-20) | [UC-20](08_MO_TA_USE_CASE.md#uc-20) | [UCD-20](07_SO_DO_USE_CASE.md#ucd-20) | [ACT-20](09_SO_DO_HOAT_DONG.md#act-20) | [SEQ-20](11_SO_DO_TUAN_TU.md#seq-20) | PhienBanDe, MaDe, AnhXaCau, AnhXaLuaChon |
| [FR-21](02_YEU_CAU_CHUC_NANG.md#fr-21) | [UC-21](08_MO_TA_USE_CASE.md#uc-21) | [UCD-21](07_SO_DO_USE_CASE.md#ucd-21) | [ACT-21](09_SO_DO_HOAT_DONG.md#act-21) | [SEQ-21](11_SO_DO_TUAN_TU.md#seq-21) | AnPham, PhienBanDe, MaDe, HoSoDe, TacVu |
| [FR-22](02_YEU_CAU_CHUC_NANG.md#fr-22) | [UC-22](08_MO_TA_USE_CASE.md#uc-22) | [UCD-22](07_SO_DO_USE_CASE.md#ucd-22) | [ACT-22](09_SO_DO_HOAT_DONG.md#act-22) | [SEQ-22](11_SO_DO_TUAN_TU.md#seq-22) | LopHoc, HocSinh, DangKyLop, KyCham |
| [FR-23](02_YEU_CAU_CHUC_NANG.md#fr-23) | [UC-23](08_MO_TA_USE_CASE.md#uc-23) | [UCD-23](07_SO_DO_USE_CASE.md#ucd-23) | [ACT-23](09_SO_DO_HOAT_DONG.md#act-23) | [SEQ-23](11_SO_DO_TUAN_TU.md#seq-23) | BaiLam, TraLoi, KetQuaCham, DiemThanhPhan, KyCham, HoSoCham |
| [FR-24](02_YEU_CAU_CHUC_NANG.md#fr-24) | [UC-24](08_MO_TA_USE_CASE.md#uc-24) | [UCD-24](07_SO_DO_USE_CASE.md#ucd-24) | [ACT-24](09_SO_DO_HOAT_DONG.md#act-24) | [SEQ-24](11_SO_DO_TUAN_TU.md#seq-24) | KetQuaCham, BaoCaoPhanTich, AnhXaCau |
| [FR-25](02_YEU_CAU_CHUC_NANG.md#fr-25) | [UC-25](08_MO_TA_USE_CASE.md#uc-25) | [UCD-25](07_SO_DO_USE_CASE.md#ucd-25) | [ACT-25](09_SO_DO_HOAT_DONG.md#act-25) | [SEQ-25](11_SO_DO_TUAN_TU.md#seq-25) | TaiKhoan, VaiTro, PhienDangNhap, NhatKy |
| [FR-26](02_YEU_CAU_CHUC_NANG.md#fr-26) | [UC-26](08_MO_TA_USE_CASE.md#uc-26) | [UCD-26](07_SO_DO_USE_CASE.md#ucd-26) | [ACT-26](09_SO_DO_HOAT_DONG.md#act-26) | [SEQ-26](11_SO_DO_TUAN_TU.md#seq-26) | PhienBanDanhMuc, NutKienThuc, NhatKy |
| [FR-27](02_YEU_CAU_CHUC_NANG.md#fr-27) | [UC-27](08_MO_TA_USE_CASE.md#uc-27) | [UCD-27](07_SO_DO_USE_CASE.md#ucd-27) | [ACT-27](09_SO_DO_HOAT_DONG.md#act-27) | [SEQ-27](11_SO_DO_TUAN_TU.md#seq-27) | HoSoDe, HoSoCham, NhatKy |
| [FR-28](02_YEU_CAU_CHUC_NANG.md#fr-28) | [UC-28](08_MO_TA_USE_CASE.md#uc-28) | [UCD-28](07_SO_DO_USE_CASE.md#ucd-28) | [ACT-28](09_SO_DO_HOAT_DONG.md#act-28) | [SEQ-28](11_SO_DO_TUAN_TU.md#seq-28) | CauHinhDichVu, TacVu, NhatKy |
| [FR-29](02_YEU_CAU_CHUC_NANG.md#fr-29) | [UC-29](08_MO_TA_USE_CASE.md#uc-29) | [UCD-29](07_SO_DO_USE_CASE.md#ucd-29) | [ACT-29](09_SO_DO_HOAT_DONG.md#act-29) | [SEQ-29](11_SO_DO_TUAN_TU.md#seq-29) | TacVu, LanChay, NhatKy |
| [FR-30](02_YEU_CAU_CHUC_NANG.md#fr-30) | [UC-30](08_MO_TA_USE_CASE.md#uc-30) | [UCD-30](07_SO_DO_USE_CASE.md#ucd-30) | [ACT-30](09_SO_DO_HOAT_DONG.md#act-30) | [SEQ-30](11_SO_DO_TUAN_TU.md#seq-30) | BanSaoLuu, NhatKy, TacVu |

## Truy vết nhu cầu, nguồn phương pháp và chất lượng

| Mục tiêu | Phương pháp áp dụng | Use Case | NFR tiêu biểu |
|---|---|---|---|
| G01 Kho truy nguyên và tái sử dụng | M01 tr. 1–3; M03 tr. 4–5 | UC-05–UC-12 | NFR-01, 04, 11–14 |
| G02 Đề đúng đặc tả và bảo toàn | M01 tr. 3–4; M04 tr. 3–5 | UC-13–UC-20 | NFR-03–07, 10–11 |
| G03 Xuất/chấm cùng phiên bản | M03 tr. 10–13 | UC-21–UC-24 | NFR-03–04, 11–12 |
| G04 Kiểm soát dữ liệu và vận hành | M02 tr. 3–6; M05 tr. 1–5 | UC-01–UC-04, UC-25–UC-30 | NFR-01–02, 08–09, 12–15 |

M01–M05 là căn cứ phương pháp, không chứng minh các FR đã được người dùng nghiệm thu từng chi tiết. Bảng căn cứ BC/XN/SL tại tài liệu 02 và các giả định AS tại tài liệu 01 là nơi kiểm tra phần nào cần quyết định nghiệp vụ tiếp theo.

## Kịch bản nghiệm thu tài liệu

| Mã | Kiểm tra | Tiêu chí đạt |
|---|---|---|
| DOC-01 | Nguồn PDF | Đọc đủ 5 tệp/38 trang; có mục sử dụng và giới hạn nguồn; giữ nguyên bản PDF |
| DOC-02 | Đủ bộ | Có đủ yêu cầu, actor, 2 danh mục Use Case, sơ đồ Use Case, mô tả, Activity, Class và Sequence |
| DOC-03 | Độ phủ | FR-01–30, UC-01–30, UCD-01–30, ACT-01–30 và SEQ-01–30 không thiếu/trùng |
| DOC-04 | Ký pháp | Mọi khối PlantUML có tên duy nhất, đóng mở đúng và kết xuất cục bộ không báo lỗi cú pháp |
| DOC-05 | Quan hệ Use Case | Include/extend đúng hướng; không dùng để mô tả thứ tự thời gian; actor ngoài ranh giới |
| DOC-06 | Nhất quán quyền | GV/QT tách quyền; học sinh không là actor đăng nhập; ND chỉ khái quát tài khoản chung |
| DOC-07 | Nhất quán dữ liệu | Có bản nguồn, phiên bản, bản chụp, ánh xạ, hồ sơ và lịch sử chấm; lớp tham chiếu được định nghĩa |
| DOC-08 | Luồng lỗi | Có thiếu kho toàn cục, nguồn thiếu đáp án, lỗi AI, xung đột phiên bản, lỗi QA/trộn/xuất và bài chưa rõ mã |
| DOC-09 | Liên kết | Mọi liên kết Markdown nội bộ và anchor truy vết tới được đích; PDF có mã kiểm tra nguồn |
| DOC-10 | Giới hạn phân tích | Không khẳng định đã khảo sát, triển khai, đạt hiệu năng hoặc tuân thủ văn bản pháp lý hiện hành khi chưa có bằng chứng |

Các kiểm tra DOC là kiểm tra **tài liệu**, tách khỏi kiểm thử chạy Quesy. Các ca trong từng UC và ngưỡng NFR là đầu vào kiểm thử sản phẩm tương lai, không được ghi nhận là đã pass.

## Danh mục nguồn được đối chiếu

| Mã PDF | SHA-256 |
|---|---|
| M01 | `26b6b629693cb3757ecf93dcb97f4bf2a1c25fa0a9e666cba25a1b05338e1319` |
| M02 | `89acf8943dd4d989bafc3c6c36b846f1329952e80962234b71e9f4ce24a35ad5` |
| M03 | `9644d088c5d331db1bade8f3ffb88d3b6c5e6ec76bfcc32b45b6be08eeed043a` |
| M04 | `f71e32c8c9f1f6faf92baa9754d67e78374bc2e33e5071e0e40ad22e35a56c2e` |
| M05 | `4b79a6a3aa22835390caf43a1b2bbe7b837d0cc03b91c30b21697345333b051a` |

## Cách rà soát khi thay đổi

Khi đổi một FR: xác định UC tương ứng, cập nhật mô tả, sơ đồ mục tiêu, Activity và Sequence; kiểm tra lớp và BR/NFR có liên quan. Khi đổi phạm vi actor: cập nhật ma trận quyền và cả sơ đồ dùng chung. Khi có số liệu khảo sát thật: thay giả thuyết hiện trạng, duyệt ngưỡng NFR và ghi nguồn/ngày; giữ phân biệt đặc tả mong muốn với báo cáo trạng thái phần mềm.

## Kết quả kiểm tra bộ tài liệu ngày 17/11/2026

| Hạng mục | Kết quả |
|---|---|
| Nguồn phương pháp | Đã đọc 5 PDF, tổng 38 trang; kiểm tra trực quan các trang minh họa quy trình và quan hệ Use Case |
| Bộ bàn giao chính | 13 Markdown; 30 FR, 30 UC và 16 NFR; mỗi UC có luồng chính, ngoại lệ và truy vết |
| Sơ đồ | 99 khối: 30 Use Case chi tiết + 3 tổng quan theo actor + 1 quan hệ actor + 30 Activity + 5 Class + 30 Sequence |
| Kết xuất cú pháp | 99/99 khối kết xuất SVG thành công bằng PlantUML 1.2026.10 chạy cục bộ; không gửi nội dung tới máy chủ kết xuất ngoài |
| Liên kết/anchor | 441 liên kết nội bộ trong bộ 13 tài liệu đã đối chiếu, không có đích thiếu |
| Lớp | 48 tên lớp khái niệm; mọi lớp được tham chiếu trong danh mục Use Case đều được khai báo |
| Kiểm tra tự động tài liệu | 886/886 điều kiện đạt: số lượng/độ phủ mã, tên sơ đồ duy nhất, Unicode, khối mã, liên kết, quy tắc/lớp tham chiếu và đầu ra SVG |
| Rà soát hình đại diện | Đã xem sơ đồ Use Case có include, tổng quan giáo viên, Activity hậu kiểm/chấm, mô hình lớp đề và Sequence trộn; đã chỉnh lỗi ký pháp và đường nối phát hiện khi xem hình |
| Mã nguồn và kiểm thử ứng dụng | Không thay mã nguồn; không chạy lại bộ test Quesy. Các FR, NFR và ca UC mới là tiêu chí đề xuất, chưa được coi là chức năng đã triển khai hoặc kiểm thử đạt |

Các tệp `.puml`, SVG/PNG và công cụ kiểm tra trung gian chỉ phục vụ kiểm tra cục bộ; mã PlantUML hoàn chỉnh đã được giữ trong Markdown để có thể kết xuất lại. Kết quả trên kiểm tra cấu trúc và tính nhất quán tài liệu, không thay việc giáo viên/chủ dự án thẩm định các giả định AS và chi tiết suy luận SL.
