# Use Case người dùng

> Quesy · Bản phân tích nghiệp vụ 1.0 · Ngày 17/11/2026
> Trạng thái: bản đặc tả đề xuất, không phải báo cáo chức năng đã triển khai.

## Danh mục mục tiêu người dùng

Người dùng nghiệp vụ là giáo viên. Khách chỉ tham gia trước khi xác thực; UC-03–UC-04 dùng chung cho giáo viên và quản trị viên. Các thao tác thêm/sửa/xem theo cùng mục tiêu được gom trong một Use Case khi chia sẻ đầu vào, quy tắc và hậu điều kiện; nhánh thay thế được mô tả ở tài liệu 08.

| Mã | Mục tiêu | Tác nhân chính | Nhóm | Căn cứ |
|---|---|---|---|---|
| [UC-01](08_MO_TA_USE_CASE.md#uc-01) | Đăng ký tài khoản giáo viên | Khách chưa đăng nhập | Tài khoản | SL |
| [UC-02](08_MO_TA_USE_CASE.md#uc-02) | Đăng nhập | Khách chưa đăng nhập | Tài khoản | SL |
| [UC-03](08_MO_TA_USE_CASE.md#uc-03) | Đăng xuất | Người dùng đã xác thực | Tài khoản | SL |
| [UC-04](08_MO_TA_USE_CASE.md#uc-04) | Cập nhật hồ sơ và đổi mật khẩu | Người dùng đã xác thực | Tài khoản | SL |
| [UC-05](08_MO_TA_USE_CASE.md#uc-05) | Tổ chức cây kiến thức cá nhân | Giáo viên | Ngân hàng | BC |
| [UC-06](08_MO_TA_USE_CASE.md#uc-06) | Tra cứu và xem câu hỏi | Giáo viên | Ngân hàng | BC |
| [UC-07](08_MO_TA_USE_CASE.md#uc-07) | Tạo và chỉnh sửa câu hỏi | Giáo viên | Ngân hàng | BC |
| [UC-08](08_MO_TA_USE_CASE.md#uc-08) | Ngừng dùng và khôi phục câu hỏi | Giáo viên | Ngân hàng | SL |
| [UC-09](08_MO_TA_USE_CASE.md#uc-09) | Nhập ngân hàng từ dữ liệu có cấu trúc | Giáo viên | Ngân hàng | SL |
| [UC-10](08_MO_TA_USE_CASE.md#uc-10) | Xuất tập câu hỏi ngân hàng | Giáo viên | Ngân hàng | SL |
| [UC-11](08_MO_TA_USE_CASE.md#uc-11) | Số hóa tài liệu nguồn bằng AI | Giáo viên | Số hóa | BC |
| [UC-12](08_MO_TA_USE_CASE.md#uc-12) | Hậu kiểm và đưa câu số hóa vào kho | Giáo viên | Số hóa | BC |
| [UC-13](08_MO_TA_USE_CASE.md#uc-13) | Thiết lập ma trận đặc tả | Giáo viên | Ma trận và đề | BC |
| [UC-14](08_MO_TA_USE_CASE.md#uc-14) | Kiểm tra khả năng đáp ứng ma trận | Giáo viên | Ma trận và đề | BC |
| [UC-15](08_MO_TA_USE_CASE.md#uc-15) | Sinh đề gốc theo ma trận | Giáo viên | Ma trận và đề | BC |
| [UC-16](08_MO_TA_USE_CASE.md#uc-16) | Biên soạn và xem trước đề | Giáo viên | Biên soạn | BC |
| [UC-17](08_MO_TA_USE_CASE.md#uc-17) | Nhận và duyệt đề xuất của Copilot | Giáo viên | Biên soạn | BC |
| [UC-18](08_MO_TA_USE_CASE.md#uc-18) | Thay câu bằng đối chiếu song song | Giáo viên | Biên soạn | BC |
| [UC-19](08_MO_TA_USE_CASE.md#uc-19) | Kiểm định đề và chốt phiên bản | Giáo viên | Biên soạn | BC |
| [UC-20](08_MO_TA_USE_CASE.md#uc-20) | Sinh các mã đề hoán vị an toàn | Giáo viên | Ma trận và đề | BC |
| [UC-21](08_MO_TA_USE_CASE.md#uc-21) | Xuất bản bộ ấn phẩm khảo thí | Giáo viên | Xuất bản | BC |
| [UC-22](08_MO_TA_USE_CASE.md#uc-22) | Quản lý danh sách lớp và kỳ chấm | Giáo viên | Chấm và phân tích | SL |
| [UC-23](08_MO_TA_USE_CASE.md#uc-23) | Nhập bài và chấm theo đúng mã đề | Giáo viên | Chấm và phân tích | BC |
| [UC-24](08_MO_TA_USE_CASE.md#uc-24) | Phân tích kết quả và chất lượng câu hỏi | Giáo viên | Chấm và phân tích | SL |

## Chuỗi sử dụng thông thường

**Luồng nhập nguồn:** UC-02 → UC-05 → UC-11 → UC-12 → UC-06. Có thể thay số hóa bằng UC-07 nhập tay hoặc UC-09 nhập bảng. UC-11 hoàn tất không tự kích hoạt nhập kho; UC-12 là mục tiêu do giáo viên khởi tạo riêng.

**Luồng tạo đề:** UC-13 → UC-14 → UC-15 → UC-16 → UC-19 → UC-20 → UC-21. UC-15 bắt buộc kiểm tra lại UC-14 vì kho có thể đổi. Trong UC-16 có thể gọi UC-17 nhận gợi ý hoặc UC-18 thay câu. QA phải gắn đúng phiên bản được trộn và xuất.

**Luồng chấm:** UC-22 → UC-23 → UC-24. Học sinh làm bài ngoài hệ thống; giáo viên nhập câu trả lời/phiếu, xác minh mã và chốt điểm. Điểm tự luận do giáo viên nhập theo rubric; chỉ số thống kê được trình bày theo đúng dạng câu.

Mũi tên trên diễn tả thứ tự công việc điển hình, không phải quan hệ `include` hay `extend`. Giáo viên có thể soạn đề mới trực tiếp bằng UC-16; một đề không bắt buộc đi qua số hóa hoặc sinh từ ma trận.

## Hành vi khi chưa hoàn tất

Thiếu câu ở ma trận phải quay lại bổ sung hoặc điều chỉnh; không tự hạ mục tiêu đánh giá. Câu thiếu đáp án/lời giải giữ nháp. AI và bản xem trước lỗi giữ nội dung đã lưu. Bản QA không còn hiệu lực nếu sửa đề. Bài không xác định mã hoặc có ô mơ hồ giữ chờ xác minh, không dùng mã mặc định để cho ra điểm.
