# Mô tả Use Case từng chức năng

> Quesy · Bản phân tích nghiệp vụ 1.0 · Ngày 17/11/2026
> Trạng thái: bản đặc tả đề xuất, không phải báo cáo chức năng đã triển khai.

## Quy ước đặc tả

Mỗi Use Case là một mục tiêu đạt giá trị cho tác nhân. Các biến thể CRUD/định dạng cùng mục tiêu được nêu trong luồng chính hoặc luồng thay thế. Tác nhân ND áp dụng cho giáo viên và quản trị đã xác thực. Trừ UC-01–UC-02, quyền phiên và quyền từng đối tượng phải hợp lệ; tiền điều kiện không thay cho kiểm tra quyền tại thời điểm xử lý.

**Bảo đảm tối thiểu chung:** không tiết lộ nội dung ngoài quyền; không làm mất dữ liệu đã lưu; không ghi đè phiên bản khi xung đột; lỗi một tác vụ không được gắn nhãn thành công. Những chức năng cho lưu nháp hoặc kết quả theo dòng phải nêu rõ phạm vi thành công, không gọi là giao dịch hoàn tất toàn bộ. Bước kích hoạt là lựa chọn thao tác đầu tiên trong luồng, không phải lịch nền tự suy ra.


<a id="uc-01"></a>
## UC-01 — Đăng ký tài khoản giáo viên

| Thuộc tính | Mô tả |
|---|---|
| Mục tiêu/đáp ứng | Tài khoản giáo viên và không gian cá nhân được tạo; chưa tự cấp quyền quản trị. |
| Tác nhân chính | Khách chưa đăng nhập |
| Tác nhân hỗ trợ | Không bắt buộc |
| Căn cứ | SL; Đề xuất suy luận nghiệp vụ; cần duyệt khi lập kế hoạch triển khai |
| Tiền điều kiện | Chưa đăng nhập; chính sách đăng ký đang mở. |
| Kích hoạt | Chọn đăng ký và nhập thông tin. |
| Đầu vào | Tên hiển thị, định danh đăng nhập, mật khẩu và chấp nhận chính sách dữ liệu. |
| Dữ liệu/khái niệm liên quan | TaiKhoan, KhongGian |
| Quy tắc | BR-01 |
| Quan hệ | Không có quan hệ include/extend bắt buộc; xem tiền điều kiện và luồng. |

### Luồng thành công chính

1. **Khách chưa đăng nhập:** Chọn đăng ký và nhập thông tin.
2. **Quesy:** Kiểm tra chính sách đăng ký, định danh và mật khẩu.
3. **Quesy:** Tạo tài khoản giáo viên và không gian riêng trong cùng giao dịch.
4. **Quesy:** Thông báo hoàn tất và mời đăng nhập.

### Luồng thay thế và ngoại lệ

- **UC-01-E1:** Định danh đã dùng hoặc đăng ký bị đóng: từ chối tạo, giữ dữ liệu nhập trừ mật khẩu.
- **UC-01-E2:** Ghi dữ liệu thất bại: hoàn tác tài khoản và không gian; cho gửi lại an toàn.

### Hậu điều kiện và nghiệm thu

Khi hoàn tất: Tài khoản giáo viên và không gian cá nhân được tạo; chưa tự cấp quyền quản trị. Khi thất bại, giữ bảo đảm tối thiểu chung và trạng thái trung gian đã mô tả trong nhánh ngoại lệ. Hủy ở bước chưa xác nhận không tạo thay đổi nghiệp vụ mới.

Nghiệm thu dự kiến: luồng chính phải cho đúng đầu ra; chạy riêng các ca UC-01-E1 đến UC-01-E2; đối chiếu quyền và phiên bản tại điểm ghi. Các yêu cầu này chưa phải bằng chứng đã chạy kiểm thử sản phẩm.

Truy vết: [FR-01](02_YEU_CAU_CHUC_NANG.md#fr-01) · [UCD-01](07_SO_DO_USE_CASE.md#ucd-01) · [ACT-01](09_SO_DO_HOAT_DONG.md#act-01) · [SEQ-01](11_SO_DO_TUAN_TU.md#seq-01).


<a id="uc-02"></a>
## UC-02 — Đăng nhập

| Thuộc tính | Mô tả |
|---|---|
| Mục tiêu/đáp ứng | Phiên xác thực mang đúng vai trò được tạo. |
| Tác nhân chính | Khách chưa đăng nhập |
| Tác nhân hỗ trợ | Không bắt buộc |
| Căn cứ | SL; Đề xuất suy luận nghiệp vụ; cần duyệt khi lập kế hoạch triển khai |
| Tiền điều kiện | Có tài khoản đang hoạt động; chưa có phiên hợp lệ. |
| Kích hoạt | Nhập thông tin đăng nhập. |
| Đầu vào | Định danh và mật khẩu. |
| Dữ liệu/khái niệm liên quan | TaiKhoan, PhienDangNhap |
| Quy tắc | BR-01 |
| Quan hệ | Không có quan hệ include/extend bắt buộc; xem tiền điều kiện và luồng. |

### Luồng thành công chính

1. **Khách chưa đăng nhập:** Nhập thông tin đăng nhập.
2. **Quesy:** Kiểm tra thông tin, trạng thái tài khoản và giới hạn thử sai.
3. **Quesy:** Tạo phiên với vai trò và phạm vi được cấp.
4. **Quesy:** Mở không gian giáo viên hoặc trang quản trị theo quyền.

### Luồng thay thế và ngoại lệ

- **UC-02-E1:** Sai thông tin, bị khóa hoặc vượt giới hạn: báo đăng nhập không thành công, không tiết lộ tài khoản tồn tại.
- **UC-02-E2:** Phiên hết hạn ở chức năng khác: yêu cầu đăng nhập lại và giữ bản nháp có thể khôi phục.

### Hậu điều kiện và nghiệm thu

Khi hoàn tất: Phiên xác thực mang đúng vai trò được tạo. Khi thất bại, giữ bảo đảm tối thiểu chung và trạng thái trung gian đã mô tả trong nhánh ngoại lệ. Hủy ở bước chưa xác nhận không tạo thay đổi nghiệp vụ mới.

Nghiệm thu dự kiến: luồng chính phải cho đúng đầu ra; chạy riêng các ca UC-02-E1 đến UC-02-E2; đối chiếu quyền và phiên bản tại điểm ghi. Các yêu cầu này chưa phải bằng chứng đã chạy kiểm thử sản phẩm.

Truy vết: [FR-02](02_YEU_CAU_CHUC_NANG.md#fr-02) · [UCD-02](07_SO_DO_USE_CASE.md#ucd-02) · [ACT-02](09_SO_DO_HOAT_DONG.md#act-02) · [SEQ-02](11_SO_DO_TUAN_TU.md#seq-02).


<a id="uc-03"></a>
## UC-03 — Đăng xuất

| Thuộc tính | Mô tả |
|---|---|
| Mục tiêu/đáp ứng | Phiên hiện tại bị thu hồi; dữ liệu ngân hàng đã lưu vẫn còn. |
| Tác nhân chính | Người dùng đã xác thực |
| Tác nhân hỗ trợ | Không bắt buộc |
| Căn cứ | SL; Đề xuất suy luận nghiệp vụ; cần duyệt khi lập kế hoạch triển khai |
| Tiền điều kiện | Có phiên đăng nhập hoặc phiên vừa hết hạn. |
| Kích hoạt | Chọn đăng xuất sau khi xử lý cảnh báo bản nháp. |
| Đầu vào | Lệnh đăng xuất và lựa chọn xử lý bản nháp chưa lưu. |
| Dữ liệu/khái niệm liên quan | PhienDangNhap |
| Quy tắc | BR-01 |
| Quan hệ | Không có quan hệ include/extend bắt buộc; xem tiền điều kiện và luồng. |

### Luồng thành công chính

1. **Người dùng đã xác thực:** Chọn đăng xuất sau khi xử lý cảnh báo bản nháp.
2. **Quesy:** Xác định phiên hiện tại.
3. **Quesy:** Thu hồi phiên và xóa dữ liệu phiên trên giao diện.
4. **Quesy:** Trở về trang đăng nhập.

### Luồng thay thế và ngoại lệ

- **UC-03-E1:** Hủy tại cảnh báo bản nháp: tiếp tục làm việc, không thu hồi phiên.
- **UC-03-E2:** Không kết nối được máy chủ: xóa phiên phía giao diện và báo chưa xác nhận thu hồi phía máy chủ; phiên vẫn phải hết hạn theo chính sách.

### Hậu điều kiện và nghiệm thu

Khi hoàn tất: Phiên hiện tại bị thu hồi; dữ liệu ngân hàng đã lưu vẫn còn. Khi thất bại, giữ bảo đảm tối thiểu chung và trạng thái trung gian đã mô tả trong nhánh ngoại lệ. Hủy ở bước chưa xác nhận không tạo thay đổi nghiệp vụ mới.

Nghiệm thu dự kiến: luồng chính phải cho đúng đầu ra; chạy riêng các ca UC-03-E1 đến UC-03-E2; đối chiếu quyền và phiên bản tại điểm ghi. Các yêu cầu này chưa phải bằng chứng đã chạy kiểm thử sản phẩm.

Truy vết: [FR-03](02_YEU_CAU_CHUC_NANG.md#fr-03) · [UCD-03](07_SO_DO_USE_CASE.md#ucd-03) · [ACT-03](09_SO_DO_HOAT_DONG.md#act-03) · [SEQ-03](11_SO_DO_TUAN_TU.md#seq-03).


<a id="uc-04"></a>
## UC-04 — Cập nhật hồ sơ và đổi mật khẩu

| Thuộc tính | Mô tả |
|---|---|
| Mục tiêu/đáp ứng | Hồ sơ được cập nhật; đổi mật khẩu thu hồi các phiên cũ theo chính sách. |
| Tác nhân chính | Người dùng đã xác thực |
| Tác nhân hỗ trợ | Không bắt buộc |
| Căn cứ | SL; Đề xuất suy luận nghiệp vụ; cần duyệt khi lập kế hoạch triển khai |
| Tiền điều kiện | Đã đăng nhập; đổi mật khẩu cần xác minh mật khẩu hiện tại. |
| Kích hoạt | Sửa hồ sơ hoặc chọn đổi mật khẩu. |
| Đầu vào | Tên hiển thị hoặc mật khẩu hiện tại và mật khẩu mới. |
| Dữ liệu/khái niệm liên quan | TaiKhoan, PhienDangNhap |
| Quy tắc | BR-01, BR-02 |
| Quan hệ | Không có quan hệ include/extend bắt buộc; xem tiền điều kiện và luồng. |

### Luồng thành công chính

1. **Người dùng đã xác thực:** Sửa hồ sơ hoặc chọn đổi mật khẩu.
2. **Quesy:** Kiểm tra quyền chính chủ và thông tin xác minh khi đổi mật khẩu.
3. **Quesy:** Lưu hồ sơ hoặc thông tin xác thực mới; thu hồi phiên cần thu hồi.
4. **Quesy:** Thông báo thành công và yêu cầu đăng nhập lại nếu phiên hiện tại bị thu hồi.

### Luồng thay thế và ngoại lệ

- **UC-04-E1:** Mật khẩu hiện tại sai hoặc mật khẩu mới không hợp lệ: không thay thông tin xác thực.
- **UC-04-E2:** Hồ sơ bị cập nhật đồng thời: yêu cầu tải lại để tránh ghi đè.

### Hậu điều kiện và nghiệm thu

Khi hoàn tất: Hồ sơ được cập nhật; đổi mật khẩu thu hồi các phiên cũ theo chính sách. Khi thất bại, giữ bảo đảm tối thiểu chung và trạng thái trung gian đã mô tả trong nhánh ngoại lệ. Hủy ở bước chưa xác nhận không tạo thay đổi nghiệp vụ mới.

Nghiệm thu dự kiến: luồng chính phải cho đúng đầu ra; chạy riêng các ca UC-04-E1 đến UC-04-E2; đối chiếu quyền và phiên bản tại điểm ghi. Các yêu cầu này chưa phải bằng chứng đã chạy kiểm thử sản phẩm.

Truy vết: [FR-04](02_YEU_CAU_CHUC_NANG.md#fr-04) · [UCD-04](07_SO_DO_USE_CASE.md#ucd-04) · [ACT-04](09_SO_DO_HOAT_DONG.md#act-04) · [SEQ-04](11_SO_DO_TUAN_TU.md#seq-04).


<a id="uc-05"></a>
## UC-05 — Tổ chức cây kiến thức cá nhân

| Thuộc tính | Mô tả |
|---|---|
| Mục tiêu/đáp ứng | Danh mục cá nhân hợp lệ; tham chiếu của câu hỏi cũ được giữ. |
| Tác nhân chính | Giáo viên |
| Tác nhân hỗ trợ | Không bắt buộc |
| Căn cứ | BC; Bối cảnh Quesy do người dùng cung cấp |
| Tiền điều kiện | Đã đăng nhập với không gian riêng; có môn và khối cần quản lý. |
| Kích hoạt | Chọn nhánh cá nhân và nhập thay đổi. |
| Đầu vào | Môn, khối, chương/chủ đề, bài, yêu cầu cần đạt và dạng bài; thao tác thêm, sửa hoặc ngừng dùng. |
| Dữ liệu/khái niệm liên quan | NutKienThuc, KhongGian |
| Quy tắc | BR-01, BR-03 |
| Quan hệ | Không có quan hệ include/extend bắt buộc; xem tiền điều kiện và luồng. |

### Luồng thành công chính

1. **Giáo viên:** Chọn nhánh cá nhân và nhập thay đổi.
2. **Quesy:** Kiểm tra cấp cha, mã trùng và tham chiếu đang dùng.
3. **Quesy:** Lưu phiên bản nhánh hoặc đánh dấu ngừng dùng.
4. **Quesy:** Cập nhật cây và các bộ lọc của không gian.

### Luồng thay thế và ngoại lệ

- **UC-05-E1:** Nhánh có con hoặc đang được tham chiếu: ngừng dùng thay cho xóa phá hủy.
- **UC-05-E2:** Giáo viên sửa danh mục chuẩn dùng chung: từ chối; cho sao chép thành nhánh cá nhân.

### Hậu điều kiện và nghiệm thu

Khi hoàn tất: Danh mục cá nhân hợp lệ; tham chiếu của câu hỏi cũ được giữ. Khi thất bại, giữ bảo đảm tối thiểu chung và trạng thái trung gian đã mô tả trong nhánh ngoại lệ. Hủy ở bước chưa xác nhận không tạo thay đổi nghiệp vụ mới.

Nghiệm thu dự kiến: luồng chính phải cho đúng đầu ra; chạy riêng các ca UC-05-E1 đến UC-05-E2; đối chiếu quyền và phiên bản tại điểm ghi. Các yêu cầu này chưa phải bằng chứng đã chạy kiểm thử sản phẩm.

Truy vết: [FR-05](02_YEU_CAU_CHUC_NANG.md#fr-05) · [UCD-05](07_SO_DO_USE_CASE.md#ucd-05) · [ACT-05](09_SO_DO_HOAT_DONG.md#act-05) · [SEQ-05](11_SO_DO_TUAN_TU.md#seq-05).


<a id="uc-06"></a>
## UC-06 — Tra cứu và xem câu hỏi

| Thuộc tính | Mô tả |
|---|---|
| Mục tiêu/đáp ứng | Danh sách và chi tiết câu hỏi trong phạm vi được phép, gồm công thức, hình và lời giải. |
| Tác nhân chính | Giáo viên |
| Tác nhân hỗ trợ | Không bắt buộc |
| Căn cứ | BC; Bối cảnh Quesy do người dùng cung cấp |
| Tiền điều kiện | Đã đăng nhập. |
| Kích hoạt | Nhập bộ lọc hoặc chọn câu hỏi. |
| Đầu vào | Từ khóa, môn, khối, nhánh kiến thức, dạng câu hỏi, mức nhận thức và trang kết quả. |
| Dữ liệu/khái niệm liên quan | CauHoi, PhienBanCauHoi, TaiSan |
| Quy tắc | BR-01, BR-02 |
| Quan hệ | Không có quan hệ include/extend bắt buộc; xem tiền điều kiện và luồng. |

### Luồng thành công chính

1. **Giáo viên:** Nhập bộ lọc hoặc chọn câu hỏi.
2. **Quesy:** Giới hạn truy vấn trong không gian được phép.
3. **Quesy:** Tìm kiếm, phân trang và lấy phiên bản câu hỏi.
4. **Quesy:** Hiển thị nội dung, nguồn và trạng thái.

### Luồng thay thế và ngoại lệ

- **UC-06-E1:** Không có kết quả: hiển thị danh sách rỗng và gợi ý giảm điều kiện.
- **UC-06-E2:** Truy cập mã câu hỏi ngoài quyền hoặc đã ngừng dùng: không tiết lộ nội dung trái phép.

### Hậu điều kiện và nghiệm thu

Khi hoàn tất: Danh sách và chi tiết câu hỏi trong phạm vi được phép, gồm công thức, hình và lời giải. Khi thất bại, giữ bảo đảm tối thiểu chung và trạng thái trung gian đã mô tả trong nhánh ngoại lệ. Hủy ở bước chưa xác nhận không tạo thay đổi nghiệp vụ mới.

Nghiệm thu dự kiến: luồng chính phải cho đúng đầu ra; chạy riêng các ca UC-06-E1 đến UC-06-E2; đối chiếu quyền và phiên bản tại điểm ghi. Các yêu cầu này chưa phải bằng chứng đã chạy kiểm thử sản phẩm.

Truy vết: [FR-06](02_YEU_CAU_CHUC_NANG.md#fr-06) · [UCD-06](07_SO_DO_USE_CASE.md#ucd-06) · [ACT-06](09_SO_DO_HOAT_DONG.md#act-06) · [SEQ-06](11_SO_DO_TUAN_TU.md#seq-06).


<a id="uc-07"></a>
## UC-07 — Tạo và chỉnh sửa câu hỏi

| Thuộc tính | Mô tả |
|---|---|
| Mục tiêu/đáp ứng | Bản nháp hoặc phiên bản sẵn sàng được lưu; đề đã chốt không bị đổi nội dung. |
| Tác nhân chính | Giáo viên |
| Tác nhân hỗ trợ | Không bắt buộc |
| Căn cứ | BC; Bối cảnh Quesy do người dùng cung cấp |
| Tiền điều kiện | Đã đăng nhập; sửa câu hỏi cần quyền sở hữu và phiên bản hiện hành. |
| Kích hoạt | Nhập nội dung, đáp án, lời giải và nhãn. |
| Đầu vào | Đề bài, dạng MCQ/Đúng-Sai/trả lời ngắn/tự luận, lựa chọn/ý, đáp án, lời giải, nhãn và hình. |
| Dữ liệu/khái niệm liên quan | CauHoi, PhienBanCauHoi, PhuongAn, MenhDe, KetQuaTuongDong |
| Quy tắc | BR-02, BR-04, BR-05 |
| Quan hệ | Không có quan hệ include/extend bắt buộc; xem tiền điều kiện và luồng. |

### Luồng thành công chính

1. **Giáo viên:** Nhập nội dung, đáp án, lời giải và nhãn.
2. **Quesy:** Kiểm tra cấu trúc theo dạng, công thức và quyền sửa.
3. **Quesy:** So sánh với câu trong kho và trả cảnh báo tương đồng.
4. **Giáo viên:** Sửa lỗi hoặc xác nhận lưu khi cảnh báo đã được xử lý.
5. **Quesy:** Lưu phiên bản mới và trạng thái nháp hoặc sẵn sàng.

### Luồng thay thế và ngoại lệ

- **UC-07-E1:** Thiếu đáp án hoặc lời giải: cho lưu nháp có cờ lỗi; không chuyển sẵn sàng.
- **UC-07-E2:** Nghi trùng: hiển thị cặp câu để giáo viên quyết định; không tự xóa.
- **UC-07-E3:** Phiên bản cũ: báo xung đột, giữ nội dung đang soạn để đối chiếu.

### Hậu điều kiện và nghiệm thu

Khi hoàn tất: Bản nháp hoặc phiên bản sẵn sàng được lưu; đề đã chốt không bị đổi nội dung. Khi thất bại, giữ bảo đảm tối thiểu chung và trạng thái trung gian đã mô tả trong nhánh ngoại lệ. Hủy ở bước chưa xác nhận không tạo thay đổi nghiệp vụ mới.

Nghiệm thu dự kiến: luồng chính phải cho đúng đầu ra; chạy riêng các ca UC-07-E1 đến UC-07-E3; đối chiếu quyền và phiên bản tại điểm ghi. Các yêu cầu này chưa phải bằng chứng đã chạy kiểm thử sản phẩm.

Truy vết: [FR-07](02_YEU_CAU_CHUC_NANG.md#fr-07) · [UCD-07](07_SO_DO_USE_CASE.md#ucd-07) · [ACT-07](09_SO_DO_HOAT_DONG.md#act-07) · [SEQ-07](11_SO_DO_TUAN_TU.md#seq-07).


<a id="uc-08"></a>
## UC-08 — Ngừng dùng và khôi phục câu hỏi

| Thuộc tính | Mô tả |
|---|---|
| Mục tiêu/đáp ứng | Trạng thái sử dụng thay đổi; bản chụp trong các đề cũ còn nguyên. |
| Tác nhân chính | Giáo viên |
| Tác nhân hỗ trợ | Không bắt buộc |
| Căn cứ | SL; Đề xuất suy luận nghiệp vụ; cần duyệt khi lập kế hoạch triển khai |
| Tiền điều kiện | Câu hỏi thuộc không gian cá nhân và vẫn tồn tại. |
| Kích hoạt | Chọn câu và thao tác trạng thái. |
| Đầu vào | Mã câu hỏi, phiên bản, thao tác ngừng dùng hoặc khôi phục và lý do. |
| Dữ liệu/khái niệm liên quan | CauHoi, PhienBanCauHoi, NhatKy |
| Quy tắc | BR-02, BR-06 |
| Quan hệ | Không có quan hệ include/extend bắt buộc; xem tiền điều kiện và luồng. |

### Luồng thành công chính

1. **Giáo viên:** Chọn câu và thao tác trạng thái.
2. **Quesy:** Kiểm tra quyền, phiên bản và ảnh hưởng tới tồn kho.
3. **Giáo viên:** Xác nhận tác động.
4. **Quesy:** Đổi trạng thái và ghi lịch sử; cập nhật tồn kho.

### Luồng thay thế và ngoại lệ

- **UC-08-E1:** Hủy xác nhận: không đổi trạng thái.
- **UC-08-E2:** Khôi phục câu có lỗi: trả về nháp; cần hậu kiểm trước khi sẵn sàng.

### Hậu điều kiện và nghiệm thu

Khi hoàn tất: Trạng thái sử dụng thay đổi; bản chụp trong các đề cũ còn nguyên. Khi thất bại, giữ bảo đảm tối thiểu chung và trạng thái trung gian đã mô tả trong nhánh ngoại lệ. Hủy ở bước chưa xác nhận không tạo thay đổi nghiệp vụ mới.

Nghiệm thu dự kiến: luồng chính phải cho đúng đầu ra; chạy riêng các ca UC-08-E1 đến UC-08-E2; đối chiếu quyền và phiên bản tại điểm ghi. Các yêu cầu này chưa phải bằng chứng đã chạy kiểm thử sản phẩm.

Truy vết: [FR-08](02_YEU_CAU_CHUC_NANG.md#fr-08) · [UCD-08](07_SO_DO_USE_CASE.md#ucd-08) · [ACT-08](09_SO_DO_HOAT_DONG.md#act-08) · [SEQ-08](11_SO_DO_TUAN_TU.md#seq-08).


<a id="uc-09"></a>
## UC-09 — Nhập ngân hàng từ dữ liệu có cấu trúc

| Thuộc tính | Mô tả |
|---|---|
| Mục tiêu/đáp ứng | Các dòng được chọn được nhập; mỗi dòng có kết quả và khóa chống nhập lặp. |
| Tác nhân chính | Giáo viên |
| Tác nhân hỗ trợ | Không bắt buộc |
| Căn cứ | SL; Đề xuất suy luận nghiệp vụ; cần duyệt khi lập kế hoạch triển khai |
| Tiền điều kiện | Đã đăng nhập; có tệp theo mẫu công bố. |
| Kích hoạt | Tải tệp theo mẫu và ánh xạ trường. |
| Đầu vào | Tệp bảng dữ liệu câu hỏi và ánh xạ cột/nhãn. |
| Dữ liệu/khái niệm liên quan | LoNhap, DongNhap, PhienBanCauHoi |
| Quy tắc | BR-04, BR-05, BR-07 |
| Quan hệ | Không có quan hệ include/extend bắt buộc; xem tiền điều kiện và luồng. |

### Luồng thành công chính

1. **Giáo viên:** Tải tệp theo mẫu và ánh xạ trường.
2. **Quesy:** Kiểm tra tệp, từng dòng, nhãn và tương đồng.
3. **Quesy:** Hiển thị bản xem trước với lỗi theo dòng.
4. **Giáo viên:** Chọn các dòng hợp lệ và xác nhận nhập.
5. **Quesy:** Lưu kết quả từng dòng; trả báo cáo nhập.

### Luồng thay thế và ngoại lệ

- **UC-09-E1:** Dòng lỗi: loại khỏi tập được nhập, nêu trường lỗi và giữ số dòng nguồn.
- **UC-09-E2:** Gửi lại cùng lô: trả kết quả cũ cho dòng đã nhập, không tạo bản sao.

### Hậu điều kiện và nghiệm thu

Khi hoàn tất: Các dòng được chọn được nhập; mỗi dòng có kết quả và khóa chống nhập lặp. Khi thất bại, giữ bảo đảm tối thiểu chung và trạng thái trung gian đã mô tả trong nhánh ngoại lệ. Hủy ở bước chưa xác nhận không tạo thay đổi nghiệp vụ mới.

Nghiệm thu dự kiến: luồng chính phải cho đúng đầu ra; chạy riêng các ca UC-09-E1 đến UC-09-E2; đối chiếu quyền và phiên bản tại điểm ghi. Các yêu cầu này chưa phải bằng chứng đã chạy kiểm thử sản phẩm.

Truy vết: [FR-09](02_YEU_CAU_CHUC_NANG.md#fr-09) · [UCD-09](07_SO_DO_USE_CASE.md#ucd-09) · [ACT-09](09_SO_DO_HOAT_DONG.md#act-09) · [SEQ-09](11_SO_DO_TUAN_TU.md#seq-09).


<a id="uc-10"></a>
## UC-10 — Xuất tập câu hỏi ngân hàng

| Thuộc tính | Mô tả |
|---|---|
| Mục tiêu/đáp ứng | Tệp xuất tái hiện đúng tập phiên bản đã chọn, tải được trong phạm vi quyền. |
| Tác nhân chính | Giáo viên |
| Tác nhân hỗ trợ | Bộ biên dịch tài liệu ngoài Quesy |
| Căn cứ | SL; Đề xuất suy luận nghiệp vụ; cần duyệt khi lập kế hoạch triển khai |
| Tiền điều kiện | Có quyền đọc các câu được chọn. |
| Kích hoạt | Chọn câu, định dạng và chế độ đáp án. |
| Đầu vào | Bộ lọc hoặc danh sách câu, định dạng PDF/LaTeX/bảng dữ liệu và lựa chọn kèm đáp án. |
| Dữ liệu/khái niệm liên quan | PhienBanCauHoi, AnPham, TacVu |
| Quy tắc | BR-01, BR-02, BR-12 |
| Quan hệ | Không có quan hệ include/extend bắt buộc; xem tiền điều kiện và luồng. |

### Luồng thành công chính

1. **Giáo viên:** Chọn câu, định dạng và chế độ đáp án.
2. **Quesy:** Kiểm tra quyền và chốt danh sách phiên bản.
3. **Quesy:** Tạo tệp; kiểm tra công thức và tài sản.
4. **Quesy:** Cấp tệp tải riêng tư và báo kết quả.

### Luồng thay thế và ngoại lệ

- **UC-10-E1:** Tập câu rỗng: yêu cầu chọn lại.
- **UC-10-E2:** Biên dịch hoặc tài sản thiếu: báo câu gây lỗi, giữ lựa chọn và không công bố tệp lỗi.

### Hậu điều kiện và nghiệm thu

Khi hoàn tất: Tệp xuất tái hiện đúng tập phiên bản đã chọn, tải được trong phạm vi quyền. Khi thất bại, giữ bảo đảm tối thiểu chung và trạng thái trung gian đã mô tả trong nhánh ngoại lệ. Hủy ở bước chưa xác nhận không tạo thay đổi nghiệp vụ mới.

Nghiệm thu dự kiến: luồng chính phải cho đúng đầu ra; chạy riêng các ca UC-10-E1 đến UC-10-E2; đối chiếu quyền và phiên bản tại điểm ghi. Các yêu cầu này chưa phải bằng chứng đã chạy kiểm thử sản phẩm.

Truy vết: [FR-10](02_YEU_CAU_CHUC_NANG.md#fr-10) · [UCD-10](07_SO_DO_USE_CASE.md#ucd-10) · [ACT-10](09_SO_DO_HOAT_DONG.md#act-10) · [SEQ-10](11_SO_DO_TUAN_TU.md#seq-10).


<a id="uc-11"></a>
## UC-11 — Số hóa tài liệu nguồn bằng AI

| Thuộc tính | Mô tả |
|---|---|
| Mục tiêu/đáp ứng | Bản trích xuất nháp gắn trang, vùng nguồn và tài sản; chưa vào kho sẵn sàng. |
| Tác nhân chính | Giáo viên |
| Tác nhân hỗ trợ | Dịch vụ AI/OCR ngoài Quesy |
| Căn cứ | BC; Bối cảnh Quesy do người dùng cung cấp |
| Tiền điều kiện | Đã đăng nhập; dịch vụ AI được cấu hình; còn hạn mức. |
| Kích hoạt | Tải tài liệu và chọn trang. |
| Đầu vào | PDF/ảnh/Word/LaTeX và phạm vi trang cần xử lý. |
| Dữ liệu/khái niệm liên quan | TaiLieuNguon, VungNguon, TaiSan, TacVu, BanTrichXuat |
| Quy tắc | BR-04, BR-05, BR-07, BR-08 |
| Quan hệ | Không có quan hệ include/extend bắt buộc; xem tiền điều kiện và luồng. |

### Luồng thành công chính

1. **Giáo viên:** Tải tài liệu và chọn trang.
2. **Quesy:** Kiểm tra định dạng, dung lượng, quyền và hạn mức.
3. **Quesy:** Tạo tác vụ; phân đoạn bố cục, cắt hình và cải thiện ảnh (Pass 1).
4. **Dịch vụ AI/OCR bên ngoài:** Trích nội dung, công thức, đáp án, lời giải và gợi ý nhãn (Pass 2).
5. **Quesy:** Lưu nháp, liên kết vùng nguồn và cảnh báo tương đồng; báo trạng thái hậu kiểm.

### Luồng thay thế và ngoại lệ

- **UC-11-E1:** Tệp sai định dạng, không đọc được hoặc vượt hạn mức: từ chối trước xử lý.
- **UC-11-E2:** AI lỗi hoặc hết thời gian: đánh dấu lỗi theo trang, giữ phần thành công; cho thử lại phần lỗi với cùng khóa tác vụ.
- **UC-11-E3:** Nguồn không có đáp án/lời giải: đánh dấu thiếu, không tự khẳng định nội dung suy đoán là dữ liệu gốc.

### Hậu điều kiện và nghiệm thu

Khi hoàn tất: Bản trích xuất nháp gắn trang, vùng nguồn và tài sản; chưa vào kho sẵn sàng. Khi thất bại, giữ bảo đảm tối thiểu chung và trạng thái trung gian đã mô tả trong nhánh ngoại lệ. Hủy ở bước chưa xác nhận không tạo thay đổi nghiệp vụ mới.

Nghiệm thu dự kiến: luồng chính phải cho đúng đầu ra; chạy riêng các ca UC-11-E1 đến UC-11-E3; đối chiếu quyền và phiên bản tại điểm ghi. Các yêu cầu này chưa phải bằng chứng đã chạy kiểm thử sản phẩm.

Truy vết: [FR-11](02_YEU_CAU_CHUC_NANG.md#fr-11) · [UCD-11](07_SO_DO_USE_CASE.md#ucd-11) · [ACT-11](09_SO_DO_HOAT_DONG.md#act-11) · [SEQ-11](11_SO_DO_TUAN_TU.md#seq-11).


<a id="uc-12"></a>
## UC-12 — Hậu kiểm và đưa câu số hóa vào kho

| Thuộc tính | Mô tả |
|---|---|
| Mục tiêu/đáp ứng | Chỉ các câu được giáo viên xác nhận mới vào kho; giữ truy nguyên tới nguồn. |
| Tác nhân chính | Giáo viên |
| Tác nhân hỗ trợ | Không bắt buộc |
| Căn cứ | BC; Bối cảnh Quesy do người dùng cung cấp |
| Tiền điều kiện | Có bản trích xuất thuộc không gian; bản nguồn còn truy cập được. |
| Kích hoạt | Đối chiếu từng câu với trang/vùng nguồn song song. |
| Đầu vào | Bản trích xuất, sửa nội dung/hình/công thức, đáp án, lời giải, nhãn và lựa chọn nhập. |
| Dữ liệu/khái niệm liên quan | BanTrichXuat, VungNguon, PhienBanCauHoi |
| Quy tắc | BR-04, BR-05, BR-07, BR-08 |
| Quan hệ | Không có quan hệ include/extend bắt buộc; xem tiền điều kiện và luồng. |

### Luồng thành công chính

1. **Giáo viên:** Đối chiếu từng câu với trang/vùng nguồn song song.
2. **Giáo viên:** Sửa công thức, hình, đáp án, lời giải và nhãn.
3. **Quesy:** Kiểm tra cấu trúc, thiếu dữ liệu và tương đồng.
4. **Giáo viên:** Chọn lưu nháp hoặc xác nhận câu đủ điều kiện.
5. **Quesy:** Lưu vào kho đúng trạng thái và ghi kết quả nhập để tránh lặp.

### Luồng thay thế và ngoại lệ

- **UC-12-E1:** Thiếu dữ liệu bắt buộc hoặc còn lỗi: chỉ được lưu nháp; chỉ rõ câu và trường cần sửa.
- **UC-12-E2:** Nghi trùng: đối chiếu câu cũ, bỏ nhập hoặc xác nhận lưu phiên bản/câu độc lập kèm lý do.
- **UC-12-E3:** Bấm xác nhận lại: trả mã câu đã nhập, không nhập đôi.

### Hậu điều kiện và nghiệm thu

Khi hoàn tất: Chỉ các câu được giáo viên xác nhận mới vào kho; giữ truy nguyên tới nguồn. Khi thất bại, giữ bảo đảm tối thiểu chung và trạng thái trung gian đã mô tả trong nhánh ngoại lệ. Hủy ở bước chưa xác nhận không tạo thay đổi nghiệp vụ mới.

Nghiệm thu dự kiến: luồng chính phải cho đúng đầu ra; chạy riêng các ca UC-12-E1 đến UC-12-E3; đối chiếu quyền và phiên bản tại điểm ghi. Các yêu cầu này chưa phải bằng chứng đã chạy kiểm thử sản phẩm.

Truy vết: [FR-12](02_YEU_CAU_CHUC_NANG.md#fr-12) · [UCD-12](07_SO_DO_USE_CASE.md#ucd-12) · [ACT-12](09_SO_DO_HOAT_DONG.md#act-12) · [SEQ-12](11_SO_DO_TUAN_TU.md#seq-12).


<a id="uc-13"></a>
## UC-13 — Thiết lập ma trận đặc tả

| Thuộc tính | Mô tả |
|---|---|
| Mục tiêu/đáp ứng | Phiên bản ma trận được lưu; tổng câu, điểm và phân bổ được tính nhất quán. |
| Tác nhân chính | Giáo viên |
| Tác nhân hỗ trợ | Không bắt buộc |
| Căn cứ | BC; Bối cảnh Quesy do người dùng cung cấp |
| Tiền điều kiện | Có cây kiến thức và hồ sơ cấu trúc đề được chọn. |
| Kích hoạt | Chọn hồ sơ đề và cấu hình các ô ma trận. |
| Đầu vào | Môn, khối, thời lượng, phần thi; ô kiến thức × dạng câu × mức nhận thức, số câu và điểm. |
| Dữ liệu/khái niệm liên quan | MaTran, PhienBanMaTran, OMaTran, HoSoDe |
| Quy tắc | BR-03, BR-09, BR-13 |
| Quan hệ | Không có quan hệ include/extend bắt buộc; xem tiền điều kiện và luồng. |

### Luồng thành công chính

1. **Giáo viên:** Chọn hồ sơ đề và cấu hình các ô ma trận.
2. **Quesy:** Kiểm tra tọa độ, số câu nguyên không âm và tổng điểm.
3. **Quesy:** Tính tổng theo phần, mức nhận thức và kiến thức.
4. **Giáo viên:** Xác nhận lưu ma trận.
5. **Quesy:** Lưu phiên bản ma trận cùng hồ sơ chấm và cấu trúc.

### Luồng thay thế và ngoại lệ

- **UC-13-E1:** Tổng điểm hoặc số lượng trái hồ sơ đã chọn: chỉ rõ ô gây sai; cho sửa hoặc lưu nháp.
- **UC-13-E2:** Hai ô chồng miền câu hỏi: cảnh báo khả năng thiếu phân bổ; kiểm tra toàn cục ở UC-14.

### Hậu điều kiện và nghiệm thu

Khi hoàn tất: Phiên bản ma trận được lưu; tổng câu, điểm và phân bổ được tính nhất quán. Khi thất bại, giữ bảo đảm tối thiểu chung và trạng thái trung gian đã mô tả trong nhánh ngoại lệ. Hủy ở bước chưa xác nhận không tạo thay đổi nghiệp vụ mới.

Nghiệm thu dự kiến: luồng chính phải cho đúng đầu ra; chạy riêng các ca UC-13-E1 đến UC-13-E2; đối chiếu quyền và phiên bản tại điểm ghi. Các yêu cầu này chưa phải bằng chứng đã chạy kiểm thử sản phẩm.

Truy vết: [FR-13](02_YEU_CAU_CHUC_NANG.md#fr-13) · [UCD-13](07_SO_DO_USE_CASE.md#ucd-13) · [ACT-13](09_SO_DO_HOAT_DONG.md#act-13) · [SEQ-13](11_SO_DO_TUAN_TU.md#seq-13).


<a id="uc-14"></a>
## UC-14 — Kiểm tra khả năng đáp ứng ma trận

| Thuộc tính | Mô tả |
|---|---|
| Mục tiêu/đáp ứng | Báo cáo tồn kho từng ô và tính khả thi phân bổ toàn cục, không nhân đôi một câu. |
| Tác nhân chính | Giáo viên |
| Tác nhân hỗ trợ | Không bắt buộc |
| Căn cứ | BC; Bối cảnh Quesy do người dùng cung cấp |
| Tiền điều kiện | Có phiên bản ma trận; câu hỏi chỉ lấy từ không gian được phép. |
| Kích hoạt | Yêu cầu kiểm tra ma trận. |
| Đầu vào | Ma trận, quy tắc loại trừ câu đã dùng và tập câu sẵn sàng. |
| Dữ liệu/khái niệm liên quan | OMaTran, PhienBanCauHoi, BaoCaoThieu |
| Quy tắc | BR-06, BR-09 |
| Quan hệ | Không có quan hệ include/extend bắt buộc; xem tiền điều kiện và luồng. |

### Luồng thành công chính

1. **Giáo viên:** Yêu cầu kiểm tra ma trận.
2. **Quesy:** Lấy câu sẵn sàng thỏa nhãn, dạng, mức và quy tắc loại trừ.
3. **Quesy:** Đếm theo ô và kiểm tra khả năng phân bổ không dùng trùng câu.
4. **Quesy:** Trả tọa độ ô, yêu cầu, khả dụng, thiếu và xung đột giữa các ô.

### Luồng thay thế và ngoại lệ

- **UC-14-E1:** Thiếu câu: trả đầy đủ môn/khối/nhánh/dạng/mức/phần và số thiếu; không báo đạt.
- **UC-14-E2:** Từng ô đủ nhưng cùng tranh chấp một tập câu: báo thiếu toàn cục và các ô liên quan.
- **UC-14-E3:** Kho thay đổi sau kiểm tra: kết quả chỉ có giá trị tại thời điểm kiểm tra, UC-15 phải kiểm tra lại.

### Hậu điều kiện và nghiệm thu

Khi hoàn tất: Báo cáo tồn kho từng ô và tính khả thi phân bổ toàn cục, không nhân đôi một câu. Khi thất bại, giữ bảo đảm tối thiểu chung và trạng thái trung gian đã mô tả trong nhánh ngoại lệ. Hủy ở bước chưa xác nhận không tạo thay đổi nghiệp vụ mới.

Nghiệm thu dự kiến: luồng chính phải cho đúng đầu ra; chạy riêng các ca UC-14-E1 đến UC-14-E3; đối chiếu quyền và phiên bản tại điểm ghi. Các yêu cầu này chưa phải bằng chứng đã chạy kiểm thử sản phẩm.

Truy vết: [FR-14](02_YEU_CAU_CHUC_NANG.md#fr-14) · [UCD-14](07_SO_DO_USE_CASE.md#ucd-14) · [ACT-14](09_SO_DO_HOAT_DONG.md#act-14) · [SEQ-14](11_SO_DO_TUAN_TU.md#seq-14).


<a id="uc-15"></a>
## UC-15 — Sinh đề gốc theo ma trận

| Thuộc tính | Mô tả |
|---|---|
| Mục tiêu/đáp ứng | Bản nháp đề gốc đúng ma trận được lưu bằng các bản chụp câu hỏi. |
| Tác nhân chính | Giáo viên |
| Tác nhân hỗ trợ | Không bắt buộc |
| Căn cứ | BC; Bối cảnh Quesy do người dùng cung cấp |
| Tiền điều kiện | Ma trận hợp lệ và được chốt; có quyền sử dụng các câu nguồn. |
| Kích hoạt | Chọn ma trận và yêu cầu sinh đề. |
| Đầu vào | Phiên bản ma trận, điều kiện loại trừ và tiêu chí chọn câu. |
| Dữ liệu/khái niệm liên quan | DeGoc, PhienBanDe, MucDe, BanChupCauHoi, PhienBanMaTran |
| Quy tắc | BR-02, BR-06, BR-09, BR-10 |
| Quan hệ | include UC-14: Bắt buộc kiểm tra lại trước chọn câu |

### Luồng thành công chính

1. **Giáo viên:** Chọn ma trận và yêu cầu sinh đề.
2. **Quesy:** Kiểm tra lại tồn kho và phân bổ toàn cục theo UC-14.
3. **Quesy:** Chọn đủ câu, giữ nhóm ngữ liệu và thứ tự phần.
4. **Quesy:** Kiểm chứng các ô, tổng câu và tổng điểm.
5. **Quesy:** Lưu đề nháp, bản chụp câu và ma trận nguồn nguyên tử.

### Luồng thay thế và ngoại lệ

- **UC-15-E1:** Không còn đủ câu: báo tọa độ và số thiếu; không tạo đề một phần.
- **UC-15-E2:** Có câu đã đổi trạng thái lúc chốt: hủy lưu, kiểm tra lại tập ứng viên.

### Hậu điều kiện và nghiệm thu

Khi hoàn tất: Bản nháp đề gốc đúng ma trận được lưu bằng các bản chụp câu hỏi. Khi thất bại, giữ bảo đảm tối thiểu chung và trạng thái trung gian đã mô tả trong nhánh ngoại lệ. Hủy ở bước chưa xác nhận không tạo thay đổi nghiệp vụ mới.

Nghiệm thu dự kiến: luồng chính phải cho đúng đầu ra; chạy riêng các ca UC-15-E1 đến UC-15-E2; đối chiếu quyền và phiên bản tại điểm ghi. Các yêu cầu này chưa phải bằng chứng đã chạy kiểm thử sản phẩm.

Truy vết: [FR-15](02_YEU_CAU_CHUC_NANG.md#fr-15) · [UCD-15](07_SO_DO_USE_CASE.md#ucd-15) · [ACT-15](09_SO_DO_HOAT_DONG.md#act-15) · [SEQ-15](11_SO_DO_TUAN_TU.md#seq-15).


<a id="uc-16"></a>
## UC-16 — Biên soạn và xem trước đề

| Thuộc tính | Mô tả |
|---|---|
| Mục tiêu/đáp ứng | Bản nháp có phiên bản; bản xem trước ghi đúng phiên bản vừa biên dịch. |
| Tác nhân chính | Giáo viên |
| Tác nhân hỗ trợ | Bộ biên dịch tài liệu ngoài Quesy |
| Căn cứ | BC; Bối cảnh Quesy do người dùng cung cấp |
| Tiền điều kiện | Có đề thuộc không gian hoặc khởi tạo đề mới. |
| Kích hoạt | Tạo hoặc mở đề và chỉnh nội dung. |
| Đầu vào | Thông tin đầu đề, nội dung câu, phần thi, thứ tự, đáp án, lời giải và hình. |
| Dữ liệu/khái niệm liên quan | PhienBanDe, MucDe, TaiSan |
| Quy tắc | BR-02, BR-04, BR-12 |
| Quan hệ | Không có quan hệ include/extend bắt buộc; xem tiền điều kiện và luồng. |

### Luồng thành công chính

1. **Giáo viên:** Tạo hoặc mở đề và chỉnh nội dung.
2. **Quesy:** Kiểm tra quyền và phiên bản; lưu nháp.
3. **Quesy:** Biên dịch xem trước với cấu trúc ex_test và hình được kiểm soát.
4. **Quesy:** Trả bản xem trước hoặc vị trí lỗi, kèm phiên bản đã biên dịch.
5. **Giáo viên:** Đọc bản xem trước và tiếp tục chỉnh khi cần.

### Luồng thay thế và ngoại lệ

- **UC-16-E1:** Lỗi công thức, hình hoặc lệnh không được hỗ trợ: giữ nháp và trả vị trí lỗi; không dùng bản xem trước cũ làm bản mới.
- **UC-16-E2:** Có thay đổi đồng thời: giữ bản đang soạn, yêu cầu so sánh phiên bản.

### Hậu điều kiện và nghiệm thu

Khi hoàn tất: Bản nháp có phiên bản; bản xem trước ghi đúng phiên bản vừa biên dịch. Khi thất bại, giữ bảo đảm tối thiểu chung và trạng thái trung gian đã mô tả trong nhánh ngoại lệ. Hủy ở bước chưa xác nhận không tạo thay đổi nghiệp vụ mới.

Nghiệm thu dự kiến: luồng chính phải cho đúng đầu ra; chạy riêng các ca UC-16-E1 đến UC-16-E2; đối chiếu quyền và phiên bản tại điểm ghi. Các yêu cầu này chưa phải bằng chứng đã chạy kiểm thử sản phẩm.

Truy vết: [FR-16](02_YEU_CAU_CHUC_NANG.md#fr-16) · [UCD-16](07_SO_DO_USE_CASE.md#ucd-16) · [ACT-16](09_SO_DO_HOAT_DONG.md#act-16) · [SEQ-16](11_SO_DO_TUAN_TU.md#seq-16).


<a id="uc-17"></a>
## UC-17 — Nhận và duyệt đề xuất của Copilot

| Thuộc tính | Mô tả |
|---|---|
| Mục tiêu/đáp ứng | Đề xuất được xem xét; chỉ phần giáo viên chấp nhận mới thành phiên bản nháp mới. |
| Tác nhân chính | Giáo viên |
| Tác nhân hỗ trợ | Dịch vụ AI/OCR ngoài Quesy |
| Căn cứ | BC; Bối cảnh Quesy do người dùng cung cấp |
| Tiền điều kiện | Có bản nháp và cấu hình AI sử dụng được. |
| Kích hoạt | Chỉ rõ yêu cầu và phạm vi nội dung cần hỗ trợ. |
| Đầu vào | Yêu cầu tự nhiên, phạm vi câu/đoạn, phiên bản đề và lỗi biên dịch nếu liên quan. |
| Dữ liệu/khái niệm liên quan | DeXuatAI, PhienBanDe, TacVu |
| Quy tắc | BR-02, BR-08, BR-11 |
| Quan hệ | extend UC-16: [Giáo viên yêu cầu AI] điểm: hỗ trợ nội dung |

### Luồng thành công chính

1. **Giáo viên:** Chỉ rõ yêu cầu và phạm vi nội dung cần hỗ trợ.
2. **Quesy:** Kiểm tra quyền, hạn mức và chốt ngữ cảnh tối thiểu.
3. **Dịch vụ AI/OCR bên ngoài:** Sinh đề xuất sửa hoặc trả lời giải thích.
4. **Quesy:** Hiển thị nội dung trước/sau và cảnh báo.
5. **Giáo viên:** Chấp nhận, từ chối hoặc sửa đề xuất.
6. **Quesy:** Đối chiếu phiên bản; chỉ áp dụng phần được chấp nhận.

### Luồng thay thế và ngoại lệ

- **UC-17-E1:** AI lỗi hoặc quá hạn: báo lỗi; giữ nguyên nháp.
- **UC-17-E2:** Nội dung đề đã đổi sau khi gửi: không áp dụng tự động, yêu cầu so sánh lại.
- **UC-17-E3:** Yêu cầu hỏi đáp: trả lời trong khung trợ lý, không thay nội dung đề.

### Hậu điều kiện và nghiệm thu

Khi hoàn tất: Đề xuất được xem xét; chỉ phần giáo viên chấp nhận mới thành phiên bản nháp mới. Khi thất bại, giữ bảo đảm tối thiểu chung và trạng thái trung gian đã mô tả trong nhánh ngoại lệ. Hủy ở bước chưa xác nhận không tạo thay đổi nghiệp vụ mới.

Nghiệm thu dự kiến: luồng chính phải cho đúng đầu ra; chạy riêng các ca UC-17-E1 đến UC-17-E3; đối chiếu quyền và phiên bản tại điểm ghi. Các yêu cầu này chưa phải bằng chứng đã chạy kiểm thử sản phẩm.

Truy vết: [FR-17](02_YEU_CAU_CHUC_NANG.md#fr-17) · [UCD-17](07_SO_DO_USE_CASE.md#ucd-17) · [ACT-17](09_SO_DO_HOAT_DONG.md#act-17) · [SEQ-17](11_SO_DO_TUAN_TU.md#seq-17).


<a id="uc-18"></a>
## UC-18 — Thay câu bằng đối chiếu song song

| Thuộc tính | Mô tả |
|---|---|
| Mục tiêu/đáp ứng | Câu được thay sau xác nhận; đề vẫn đúng ma trận và có phiên bản mới. |
| Tác nhân chính | Giáo viên |
| Tác nhân hỗ trợ | Không bắt buộc |
| Căn cứ | BC; Bối cảnh Quesy do người dùng cung cấp |
| Tiền điều kiện | Có câu trong đề nháp và ô ma trận tương ứng; đề chưa chốt xuất bản. |
| Kích hoạt | Chọn câu cần thay và nguồn ứng viên. |
| Đầu vào | Câu cần thay, tiêu chí cùng ô và lựa chọn tìm kho hoặc đề xuất AI. |
| Dữ liệu/khái niệm liên quan | PhienBanDe, MucDe, BanChupCauHoi, DeXuatAI |
| Quy tắc | BR-02, BR-09, BR-10, BR-11 |
| Quan hệ | extend UC-16: [Giáo viên muốn thay câu] điểm: thay câu đã chọn |

### Luồng thành công chính

1. **Giáo viên:** Chọn câu cần thay và nguồn ứng viên.
2. **Quesy:** Tìm ứng viên cùng kiến thức, dạng, mức và điểm; loại câu đã có.
3. **Quesy:** Hiển thị câu hiện tại và ứng viên song song.
4. **Giáo viên:** Đối chiếu đề, đáp án, lời giải và chọn thay.
5. **Quesy:** Kiểm tra lại ô ma trận và phiên bản; lưu thay thế.

### Luồng thay thế và ngoại lệ

- **UC-18-E1:** Không có ứng viên kho: cho hủy hoặc gọi UC-17 sinh đề xuất AI; ứng viên AI vẫn cần hậu kiểm.
- **UC-18-E2:** Ứng viên đã có trong đề, làm vỡ nhóm ngữ liệu hoặc sai ô: từ chối thay.
- **UC-18-E3:** Đề thay đổi khi đang đối chiếu: yêu cầu chọn lại trên phiên bản mới.

### Hậu điều kiện và nghiệm thu

Khi hoàn tất: Câu được thay sau xác nhận; đề vẫn đúng ma trận và có phiên bản mới. Khi thất bại, giữ bảo đảm tối thiểu chung và trạng thái trung gian đã mô tả trong nhánh ngoại lệ. Hủy ở bước chưa xác nhận không tạo thay đổi nghiệp vụ mới.

Nghiệm thu dự kiến: luồng chính phải cho đúng đầu ra; chạy riêng các ca UC-18-E1 đến UC-18-E3; đối chiếu quyền và phiên bản tại điểm ghi. Các yêu cầu này chưa phải bằng chứng đã chạy kiểm thử sản phẩm.

Truy vết: [FR-18](02_YEU_CAU_CHUC_NANG.md#fr-18) · [UCD-18](07_SO_DO_USE_CASE.md#ucd-18) · [ACT-18](09_SO_DO_HOAT_DONG.md#act-18) · [SEQ-18](11_SO_DO_TUAN_TU.md#seq-18).


<a id="uc-19"></a>
## UC-19 — Kiểm định đề và chốt phiên bản

| Thuộc tính | Mô tả |
|---|---|
| Mục tiêu/đáp ứng | Báo cáo QA gắn phiên bản; chỉ đề không có lỗi chặn mới được chốt. |
| Tác nhân chính | Giáo viên |
| Tác nhân hỗ trợ | Không bắt buộc |
| Căn cứ | BC; Bối cảnh Quesy do người dùng cung cấp |
| Tiền điều kiện | Có phiên bản đề nháp đọc được. |
| Kích hoạt | Chọn kiểm định phiên bản đề. |
| Đầu vào | Phiên bản đề, hồ sơ cấu trúc/chấm và lựa chọn chế độ kiểm định ẩn đáp án trước. |
| Dữ liệu/khái niệm liên quan | BaoCaoQA, PhienBanDe |
| Quy tắc | BR-04, BR-09, BR-11, BR-12 |
| Quan hệ | Không có quan hệ include/extend bắt buộc; xem tiền điều kiện và luồng. |

### Luồng thành công chính

1. **Giáo viên:** Chọn kiểm định phiên bản đề.
2. **Quesy:** Kiểm tra số lựa chọn/ý, đáp án, công thức, hình và lời giải.
3. **Quesy:** Đối chiếu ma trận, phần thi, tổng câu và điểm.
4. **Quesy:** Trả lỗi theo câu và mức nghiêm trọng; cho mở đáp án sau bước rà soát mù.
5. **Giáo viên:** Xác nhận chốt nếu không có lỗi chặn.
6. **Quesy:** Gắn báo cáo đạt vào đúng phiên bản và đánh dấu đã chốt.

### Luồng thay thế và ngoại lệ

- **UC-19-E1:** Có lỗi chặn: không chốt; quay lại sửa rồi chạy QA mới.
- **UC-19-E2:** Phiên bản thay đổi sau QA: báo cáo cũ hết hiệu lực đối với phiên bản mới.
- **UC-19-E3:** QA cấu trúc không chứng minh đáp án đúng về chuyên môn; giáo viên phải rà soát nội dung.

### Hậu điều kiện và nghiệm thu

Khi hoàn tất: Báo cáo QA gắn phiên bản; chỉ đề không có lỗi chặn mới được chốt. Khi thất bại, giữ bảo đảm tối thiểu chung và trạng thái trung gian đã mô tả trong nhánh ngoại lệ. Hủy ở bước chưa xác nhận không tạo thay đổi nghiệp vụ mới.

Nghiệm thu dự kiến: luồng chính phải cho đúng đầu ra; chạy riêng các ca UC-19-E1 đến UC-19-E3; đối chiếu quyền và phiên bản tại điểm ghi. Các yêu cầu này chưa phải bằng chứng đã chạy kiểm thử sản phẩm.

Truy vết: [FR-19](02_YEU_CAU_CHUC_NANG.md#fr-19) · [UCD-19](07_SO_DO_USE_CASE.md#ucd-19) · [ACT-19](09_SO_DO_HOAT_DONG.md#act-19) · [SEQ-19](11_SO_DO_TUAN_TU.md#seq-19).


<a id="uc-20"></a>
## UC-20 — Sinh các mã đề hoán vị an toàn

| Thuộc tính | Mô tả |
|---|---|
| Mục tiêu/đáp ứng | Bộ mã đề và ánh xạ đáp án được lưu sau kiểm chứng đầy đủ bất biến. |
| Tác nhân chính | Giáo viên |
| Tác nhân hỗ trợ | Không bắt buộc |
| Căn cứ | BC; Bối cảnh Quesy do người dùng cung cấp |
| Tiền điều kiện | Đề gốc đã chốt và QA còn hiệu lực. |
| Kích hoạt | Chọn số mã và quy tắc trộn. |
| Đầu vào | Phiên bản đề gốc, số mã đề, mã định danh và cấu hình trộn. |
| Dữ liệu/khái niệm liên quan | PhienBanDe, MaDe, AnhXaCau, AnhXaLuaChon |
| Quy tắc | BR-02, BR-10, BR-13 |
| Quan hệ | Không có quan hệ include/extend bắt buộc; xem tiền điều kiện và luồng. |

### Luồng thành công chính

1. **Giáo viên:** Chọn số mã và quy tắc trộn.
2. **Quesy:** Kiểm tra phiên bản chốt và cấu hình.
3. **Quesy:** Hoán vị trong từng phần; giữ câu chùm, phương án neo và cập nhật đáp án.
4. **Quesy:** Kiểm chứng song ánh câu, phần, nhóm và khóa đáp án cho mọi mã.
5. **Quesy:** Lưu cả bộ mã cùng ánh xạ nguyên tử; cho xem trước.

### Luồng thay thế và ngoại lệ

- **UC-20-E1:** Có phương án phụ thuộc vị trí không thể xử lý an toàn: giữ vị trí phù hợp hoặc từ chối trộn câu đó, nêu lý do.
- **UC-20-E2:** Bất kỳ mã nào vi phạm bất biến: không công bố cả bộ; giữ đề gốc và báo lỗi.

### Hậu điều kiện và nghiệm thu

Khi hoàn tất: Bộ mã đề và ánh xạ đáp án được lưu sau kiểm chứng đầy đủ bất biến. Khi thất bại, giữ bảo đảm tối thiểu chung và trạng thái trung gian đã mô tả trong nhánh ngoại lệ. Hủy ở bước chưa xác nhận không tạo thay đổi nghiệp vụ mới.

Nghiệm thu dự kiến: luồng chính phải cho đúng đầu ra; chạy riêng các ca UC-20-E1 đến UC-20-E2; đối chiếu quyền và phiên bản tại điểm ghi. Các yêu cầu này chưa phải bằng chứng đã chạy kiểm thử sản phẩm.

Truy vết: [FR-20](02_YEU_CAU_CHUC_NANG.md#fr-20) · [UCD-20](07_SO_DO_USE_CASE.md#ucd-20) · [ACT-20](09_SO_DO_HOAT_DONG.md#act-20) · [SEQ-20](11_SO_DO_TUAN_TU.md#seq-20).


<a id="uc-21"></a>
## UC-21 — Xuất bản bộ ấn phẩm khảo thí

| Thuộc tính | Mô tả |
|---|---|
| Mục tiêu/đáp ứng | Ấn phẩm đúng phiên bản và mã đề; đề phát cho học sinh không lộ đáp án. |
| Tác nhân chính | Giáo viên |
| Tác nhân hỗ trợ | Bộ biên dịch tài liệu ngoài Quesy |
| Căn cứ | BC; Bối cảnh Quesy do người dùng cung cấp |
| Tiền điều kiện | Đề gốc đã chốt; các mã đề nếu có đã đạt kiểm chứng; có đủ tài sản. |
| Kích hoạt | Chọn bộ đề và các ấn phẩm cần xuất. |
| Đầu vào | Phiên bản đề/bộ mã, mẫu dàn trang, chế độ đề/đáp án/lời giải và định dạng PDF/LaTeX/ZIP. |
| Dữ liệu/khái niệm liên quan | AnPham, PhienBanDe, MaDe, HoSoDe, TacVu |
| Quy tắc | BR-01, BR-02, BR-10, BR-12 |
| Quan hệ | Không có quan hệ include/extend bắt buộc; xem tiền điều kiện và luồng. |

### Luồng thành công chính

1. **Giáo viên:** Chọn bộ đề và các ấn phẩm cần xuất.
2. **Quesy:** Kiểm tra quyền, QA, ánh xạ và tài sản.
3. **Quesy:** Biên dịch đề, đáp án, lời giải và phiếu trả lời theo mẫu ex_test.
4. **Quesy:** Kiểm tra tệp, mã đề, số trang và tách đáp án; tạo danh mục gói.
5. **Quesy:** Lưu ấn phẩm và cấp tải riêng tư khi cả gói đạt.

### Luồng thay thế và ngoại lệ

- **UC-21-E1:** Biên dịch lỗi: chỉ rõ mã đề/câu, giữ kết quả nháp; không gắn nhãn gói hoàn tất.
- **UC-21-E2:** Tệp đáp án không khớp phiên bản hoặc mã đề: chặn xuất bản.
- **UC-21-E3:** Thay đề sau xuất bản: tạo phiên bản và gói mới, giữ gói cũ để đối chiếu.

### Hậu điều kiện và nghiệm thu

Khi hoàn tất: Ấn phẩm đúng phiên bản và mã đề; đề phát cho học sinh không lộ đáp án. Khi thất bại, giữ bảo đảm tối thiểu chung và trạng thái trung gian đã mô tả trong nhánh ngoại lệ. Hủy ở bước chưa xác nhận không tạo thay đổi nghiệp vụ mới.

Nghiệm thu dự kiến: luồng chính phải cho đúng đầu ra; chạy riêng các ca UC-21-E1 đến UC-21-E3; đối chiếu quyền và phiên bản tại điểm ghi. Các yêu cầu này chưa phải bằng chứng đã chạy kiểm thử sản phẩm.

Truy vết: [FR-21](02_YEU_CAU_CHUC_NANG.md#fr-21) · [UCD-21](07_SO_DO_USE_CASE.md#ucd-21) · [ACT-21](09_SO_DO_HOAT_DONG.md#act-21) · [SEQ-21](11_SO_DO_TUAN_TU.md#seq-21).


<a id="uc-22"></a>
## UC-22 — Quản lý danh sách lớp và kỳ chấm

| Thuộc tính | Mô tả |
|---|---|
| Mục tiêu/đáp ứng | Danh sách lớp và kỳ chấm hợp lệ, không trùng mã trong cùng danh sách. |
| Tác nhân chính | Giáo viên |
| Tác nhân hỗ trợ | Không bắt buộc |
| Căn cứ | SL; Đề xuất suy luận nghiệp vụ; cần duyệt khi lập kế hoạch triển khai |
| Tiền điều kiện | Đã đăng nhập; có mục đích quản lý kết quả học tập. |
| Kích hoạt | Nhập trực tiếp hoặc tải danh sách theo mẫu. |
| Đầu vào | Danh sách học sinh tối thiểu, mã học sinh, lớp và kỳ chấm gắn đề/bộ mã. |
| Dữ liệu/khái niệm liên quan | LopHoc, HocSinh, DangKyLop, KyCham |
| Quy tắc | BR-01, BR-07, BR-14 |
| Quan hệ | Không có quan hệ include/extend bắt buộc; xem tiền điều kiện và luồng. |

### Luồng thành công chính

1. **Giáo viên:** Nhập trực tiếp hoặc tải danh sách theo mẫu.
2. **Quesy:** Kiểm tra cột, mã trùng và phạm vi lớp.
3. **Giáo viên:** Đối chiếu bản xem trước và chọn đề cho kỳ chấm.
4. **Quesy:** Lưu lớp, danh sách và kỳ chấm gắn phiên bản đề.

### Luồng thay thế và ngoại lệ

- **UC-22-E1:** Mã học sinh trùng hoặc thiếu: báo dòng, không tự gộp người.
- **UC-22-E2:** Kỳ đã có điểm: sửa danh sách phải giữ lịch sử và tham chiếu kết quả; không xóa âm thầm.

### Hậu điều kiện và nghiệm thu

Khi hoàn tất: Danh sách lớp và kỳ chấm hợp lệ, không trùng mã trong cùng danh sách. Khi thất bại, giữ bảo đảm tối thiểu chung và trạng thái trung gian đã mô tả trong nhánh ngoại lệ. Hủy ở bước chưa xác nhận không tạo thay đổi nghiệp vụ mới.

Nghiệm thu dự kiến: luồng chính phải cho đúng đầu ra; chạy riêng các ca UC-22-E1 đến UC-22-E2; đối chiếu quyền và phiên bản tại điểm ghi. Các yêu cầu này chưa phải bằng chứng đã chạy kiểm thử sản phẩm.

Truy vết: [FR-22](02_YEU_CAU_CHUC_NANG.md#fr-22) · [UCD-22](07_SO_DO_USE_CASE.md#ucd-22) · [ACT-22](09_SO_DO_HOAT_DONG.md#act-22) · [SEQ-22](11_SO_DO_TUAN_TU.md#seq-22).


<a id="uc-23"></a>
## UC-23 — Nhập bài và chấm theo đúng mã đề

| Thuộc tính | Mô tả |
|---|---|
| Mục tiêu/đáp ứng | Kết quả và chi tiết điểm gắn bài, mã đề và phiên bản hồ sơ chấm; có lịch sử sửa. |
| Tác nhân chính | Giáo viên |
| Tác nhân hỗ trợ | Không bắt buộc |
| Căn cứ | BC; Bối cảnh Quesy do người dùng cung cấp |
| Tiền điều kiện | Có kỳ chấm, bộ mã và hồ sơ chấm đã chốt; học sinh là dữ liệu, không đăng nhập hệ thống. |
| Kích hoạt | Nhập bài trả lời hoặc ảnh phiếu và chọn kỳ chấm. |
| Đầu vào | Câu trả lời nhập tay/bảng dữ liệu/ảnh phiếu; mã học sinh, mã đề; điểm tự luận do giáo viên chấm. |
| Dữ liệu/khái niệm liên quan | BaiLam, TraLoi, KetQuaCham, DiemThanhPhan, KyCham, HoSoCham |
| Quy tắc | BR-10, BR-13, BR-14 |
| Quan hệ | Không có quan hệ include/extend bắt buộc; xem tiền điều kiện và luồng. |

### Luồng thành công chính

1. **Giáo viên:** Nhập bài trả lời hoặc ảnh phiếu và chọn kỳ chấm.
2. **Quesy:** Nhận diện nếu là ảnh; kiểm tra học sinh, mã đề và câu trả lời.
3. **Giáo viên:** Xác minh ô mờ/đa tô, dữ liệu thiếu và điểm tự luận.
4. **Quesy:** Đối chiếu đáp án đúng mã; tính MCQ, Đúng/Sai và trả lời ngắn theo hồ sơ.
5. **Giáo viên:** Rà soát và xác nhận chốt điểm.
6. **Quesy:** Lưu kết quả, chi tiết điểm và lịch sử chỉnh sửa.

### Luồng thay thế và ngoại lệ

- **UC-23-E1:** Không xác định được mã đề hoặc còn ô mờ: giữ bài chờ xác minh; không chấm theo mã mặc định.
- **UC-23-E2:** Đúng/Sai bỏ trống tính là ý không khớp; 0 ý đúng được 0 điểm.
- **UC-23-E3:** Tự luận: chỉ lưu điểm giáo viên nhập theo rubric, không suy ra điểm tự động.
- **UC-23-E4:** Sửa đáp án sau chốt: tạo phiên bản chấm lại, không ghi đè lịch sử.

### Hậu điều kiện và nghiệm thu

Khi hoàn tất: Kết quả và chi tiết điểm gắn bài, mã đề và phiên bản hồ sơ chấm; có lịch sử sửa. Khi thất bại, giữ bảo đảm tối thiểu chung và trạng thái trung gian đã mô tả trong nhánh ngoại lệ. Hủy ở bước chưa xác nhận không tạo thay đổi nghiệp vụ mới.

Nghiệm thu dự kiến: luồng chính phải cho đúng đầu ra; chạy riêng các ca UC-23-E1 đến UC-23-E4; đối chiếu quyền và phiên bản tại điểm ghi. Các yêu cầu này chưa phải bằng chứng đã chạy kiểm thử sản phẩm.

Truy vết: [FR-23](02_YEU_CAU_CHUC_NANG.md#fr-23) · [UCD-23](07_SO_DO_USE_CASE.md#ucd-23) · [ACT-23](09_SO_DO_HOAT_DONG.md#act-23) · [SEQ-23](11_SO_DO_TUAN_TU.md#seq-23).


<a id="uc-24"></a>
## UC-24 — Phân tích kết quả và chất lượng câu hỏi

| Thuộc tính | Mô tả |
|---|---|
| Mục tiêu/đáp ứng | Phổ điểm và chỉ số câu hỏi có mẫu số, nhóm mẫu, phiên bản và cảnh báo giới hạn. |
| Tác nhân chính | Giáo viên |
| Tác nhân hỗ trợ | Không bắt buộc |
| Căn cứ | SL; Đề xuất suy luận nghiệp vụ; cần duyệt khi lập kế hoạch triển khai |
| Tiền điều kiện | Có kết quả đã chốt và ánh xạ về câu gốc. |
| Kích hoạt | Chọn kỳ chấm và tập kết quả. |
| Đầu vào | Kỳ chấm, lớp, bộ lọc kết quả và quy tắc chọn mẫu. |
| Dữ liệu/khái niệm liên quan | KetQuaCham, BaoCaoPhanTich, AnhXaCau |
| Quy tắc | BR-01, BR-10, BR-15 |
| Quan hệ | Không có quan hệ include/extend bắt buộc; xem tiền điều kiện và luồng. |

### Luồng thành công chính

1. **Giáo viên:** Chọn kỳ chấm và tập kết quả.
2. **Quesy:** Lấy kết quả có quyền; ánh xạ mọi mã về câu gốc.
3. **Quesy:** Tổng hợp phổ điểm và tính chỉ số trên mẫu hợp lệ.
4. **Quesy:** Hiển thị số mẫu, dữ liệu thiếu và cảnh báo diễn giải.
5. **Giáo viên:** Xem hoặc xuất báo cáo để điều chỉnh kho.

### Luồng thay thế và ngoại lệ

- **UC-24-E1:** Không có mẫu hợp lệ hoặc không lập được hai nhóm phân biệt: hiển thị không đủ dữ liệu, không chia cho 0.
- **UC-24-E2:** MCQ tính p và D; Đúng/Sai báo từng ý hoặc chỉ số điểm đã chuẩn hóa có nhãn riêng; tự luận không gán p nhị phân tùy tiện.

### Hậu điều kiện và nghiệm thu

Khi hoàn tất: Phổ điểm và chỉ số câu hỏi có mẫu số, nhóm mẫu, phiên bản và cảnh báo giới hạn. Khi thất bại, giữ bảo đảm tối thiểu chung và trạng thái trung gian đã mô tả trong nhánh ngoại lệ. Hủy ở bước chưa xác nhận không tạo thay đổi nghiệp vụ mới.

Nghiệm thu dự kiến: luồng chính phải cho đúng đầu ra; chạy riêng các ca UC-24-E1 đến UC-24-E2; đối chiếu quyền và phiên bản tại điểm ghi. Các yêu cầu này chưa phải bằng chứng đã chạy kiểm thử sản phẩm.

Truy vết: [FR-24](02_YEU_CAU_CHUC_NANG.md#fr-24) · [UCD-24](07_SO_DO_USE_CASE.md#ucd-24) · [ACT-24](09_SO_DO_HOAT_DONG.md#act-24) · [SEQ-24](11_SO_DO_TUAN_TU.md#seq-24).


<a id="uc-25"></a>
## UC-25 — Quản lý tài khoản và quyền truy cập

| Thuộc tính | Mô tả |
|---|---|
| Mục tiêu/đáp ứng | Tài khoản và quyền được cập nhật có nhật ký; không tạo quyền xem kho riêng mặc định. |
| Tác nhân chính | Quản trị viên kỹ thuật |
| Tác nhân hỗ trợ | Không bắt buộc |
| Căn cứ | XN; Phạm vi được người dùng xác nhận ngày 17/11/2026 |
| Tiền điều kiện | Quản trị viên đã đăng nhập; thay quyền cần xác minh tăng cường theo chính sách. |
| Kích hoạt | Tra cứu tài khoản và chọn thay đổi quyền/trạng thái. |
| Đầu vào | Tài khoản, trạng thái mở/khóa, vai trò, hạn mức và lý do thay đổi. |
| Dữ liệu/khái niệm liên quan | TaiKhoan, VaiTro, PhienDangNhap, NhatKy |
| Quy tắc | BR-01, BR-14, BR-16 |
| Quan hệ | Không có quan hệ include/extend bắt buộc; xem tiền điều kiện và luồng. |

### Luồng thành công chính

1. **Quản trị viên kỹ thuật:** Tra cứu tài khoản và chọn thay đổi quyền/trạng thái.
2. **Quesy:** Kiểm tra quyền quản trị, phiên bản và bảo vệ quản trị viên hoạt động cuối cùng.
3. **Quản trị viên kỹ thuật:** Xem tác động và xác nhận lý do.
4. **Quesy:** Cập nhật, thu hồi phiên bị ảnh hưởng và ghi nhật ký.
5. **Quesy:** Thông báo kết quả quản trị.

### Luồng thay thế và ngoại lệ

- **UC-25-E1:** Định khóa/hạ quyền quản trị viên hoạt động cuối cùng: chặn.
- **UC-25-E2:** Quản trị viên yêu cầu mở nội dung kho cá nhân bằng quyền vận hành: từ chối, trừ quy trình hỗ trợ riêng được chủ sở hữu cho phép.

### Hậu điều kiện và nghiệm thu

Khi hoàn tất: Tài khoản và quyền được cập nhật có nhật ký; không tạo quyền xem kho riêng mặc định. Khi thất bại, giữ bảo đảm tối thiểu chung và trạng thái trung gian đã mô tả trong nhánh ngoại lệ. Hủy ở bước chưa xác nhận không tạo thay đổi nghiệp vụ mới.

Nghiệm thu dự kiến: luồng chính phải cho đúng đầu ra; chạy riêng các ca UC-25-E1 đến UC-25-E2; đối chiếu quyền và phiên bản tại điểm ghi. Các yêu cầu này chưa phải bằng chứng đã chạy kiểm thử sản phẩm.

Truy vết: [FR-25](02_YEU_CAU_CHUC_NANG.md#fr-25) · [UCD-25](07_SO_DO_USE_CASE.md#ucd-25) · [ACT-25](09_SO_DO_HOAT_DONG.md#act-25) · [SEQ-25](11_SO_DO_TUAN_TU.md#seq-25).


<a id="uc-26"></a>
## UC-26 — Quản lý danh mục kiến thức dùng chung

| Thuộc tính | Mô tả |
|---|---|
| Mục tiêu/đáp ứng | Danh mục chung có phiên bản được công bố; dữ liệu cá nhân cũ không bị đổi nhãn ngầm. |
| Tác nhân chính | Quản trị viên kỹ thuật |
| Tác nhân hỗ trợ | Không bắt buộc |
| Căn cứ | SL; Đề xuất suy luận nghiệp vụ; cần duyệt khi lập kế hoạch triển khai |
| Tiền điều kiện | Có quyền quản trị danh mục; có nguồn tham chiếu giáo dục được phê duyệt. |
| Kích hoạt | Soạn bản sửa danh mục chung và khai báo nguồn. |
| Đầu vào | Phiên bản môn/khối/nhánh/YCCĐ/dạng bài và nguồn tham chiếu. |
| Dữ liệu/khái niệm liên quan | PhienBanDanhMuc, NutKienThuc, NhatKy |
| Quy tắc | BR-02, BR-03, BR-16 |
| Quan hệ | Không có quan hệ include/extend bắt buộc; xem tiền điều kiện và luồng. |

### Luồng thành công chính

1. **Quản trị viên kỹ thuật:** Soạn bản sửa danh mục chung và khai báo nguồn.
2. **Quesy:** Kiểm tra cây, mã trùng, nguồn và tác động tham chiếu.
3. **Quản trị viên kỹ thuật:** Xem khác biệt và xác nhận công bố.
4. **Quesy:** Phát hành phiên bản danh mục mới; giữ phiên bản cũ.

### Luồng thay thế và ngoại lệ

- **UC-26-E1:** Nhánh đang được tham chiếu: ngừng dùng ở bản mới thay cho xóa bản cũ.
- **UC-26-E2:** Chuyển nhãn câu cá nhân: chỉ đề xuất ánh xạ, chờ giáo viên chấp thuận qua UC-05/UC-07.

### Hậu điều kiện và nghiệm thu

Khi hoàn tất: Danh mục chung có phiên bản được công bố; dữ liệu cá nhân cũ không bị đổi nhãn ngầm. Khi thất bại, giữ bảo đảm tối thiểu chung và trạng thái trung gian đã mô tả trong nhánh ngoại lệ. Hủy ở bước chưa xác nhận không tạo thay đổi nghiệp vụ mới.

Nghiệm thu dự kiến: luồng chính phải cho đúng đầu ra; chạy riêng các ca UC-26-E1 đến UC-26-E2; đối chiếu quyền và phiên bản tại điểm ghi. Các yêu cầu này chưa phải bằng chứng đã chạy kiểm thử sản phẩm.

Truy vết: [FR-26](02_YEU_CAU_CHUC_NANG.md#fr-26) · [UCD-26](07_SO_DO_USE_CASE.md#ucd-26) · [ACT-26](09_SO_DO_HOAT_DONG.md#act-26) · [SEQ-26](11_SO_DO_TUAN_TU.md#seq-26).


<a id="uc-27"></a>
## UC-27 — Quản lý hồ sơ đề và quy tắc chấm

| Thuộc tính | Mô tả |
|---|---|
| Mục tiêu/đáp ứng | Hồ sơ mới được công bố có phiên bản; đề và điểm cũ giữ quy tắc đã ghim. |
| Tác nhân chính | Quản trị viên kỹ thuật |
| Tác nhân hỗ trợ | Không bắt buộc |
| Căn cứ | SL; Đề xuất suy luận nghiệp vụ; cần duyệt khi lập kế hoạch triển khai |
| Tiền điều kiện | Có quyền cấu hình mẫu; thay đổi dựa trên quyết định nghiệp vụ được ghi nhận. |
| Kích hoạt | Soạn hồ sơ cấu trúc và quy tắc chấm. |
| Đầu vào | Các phần thi, dạng câu, mức nhận thức, điểm MCQ/trả lời ngắn, thang Đúng/Sai và rubric tự luận. |
| Dữ liệu/khái niệm liên quan | HoSoDe, HoSoCham, NhatKy |
| Quy tắc | BR-02, BR-13, BR-16 |
| Quan hệ | Không có quan hệ include/extend bắt buộc; xem tiền điều kiện và luồng. |

### Luồng thành công chính

1. **Quản trị viên kỹ thuật:** Soạn hồ sơ cấu trúc và quy tắc chấm.
2. **Quesy:** Kiểm tra tổng điểm và các ca mẫu, gồm 0..4 ý Đúng/Sai.
3. **Quản trị viên kỹ thuật:** Đối chiếu nguồn nghiệp vụ và xác nhận công bố.
4. **Quesy:** Lưu phiên bản hồ sơ và nhật ký; không áp dụng ngược vào đề cũ.

### Luồng thay thế và ngoại lệ

- **UC-27-E1:** Thang điểm không đầy đủ hoặc điểm âm: chặn công bố.
- **UC-27-E2:** Muốn chấm lại kỳ cũ: tạo phiên bản kết quả qua UC-23 và ghi rõ hồ sơ mới.

### Hậu điều kiện và nghiệm thu

Khi hoàn tất: Hồ sơ mới được công bố có phiên bản; đề và điểm cũ giữ quy tắc đã ghim. Khi thất bại, giữ bảo đảm tối thiểu chung và trạng thái trung gian đã mô tả trong nhánh ngoại lệ. Hủy ở bước chưa xác nhận không tạo thay đổi nghiệp vụ mới.

Nghiệm thu dự kiến: luồng chính phải cho đúng đầu ra; chạy riêng các ca UC-27-E1 đến UC-27-E2; đối chiếu quyền và phiên bản tại điểm ghi. Các yêu cầu này chưa phải bằng chứng đã chạy kiểm thử sản phẩm.

Truy vết: [FR-27](02_YEU_CAU_CHUC_NANG.md#fr-27) · [UCD-27](07_SO_DO_USE_CASE.md#ucd-27) · [ACT-27](09_SO_DO_HOAT_DONG.md#act-27) · [SEQ-27](11_SO_DO_TUAN_TU.md#seq-27).


<a id="uc-28"></a>
## UC-28 — Cấu hình dịch vụ AI và biên dịch

| Thuộc tính | Mô tả |
|---|---|
| Mục tiêu/đáp ứng | Cấu hình được kiểm tra bằng dữ liệu mẫu, kích hoạt có phiên bản; bí mật được che. |
| Tác nhân chính | Quản trị viên kỹ thuật |
| Tác nhân hỗ trợ | Dịch vụ AI hoặc biên dịch được thử |
| Căn cứ | XN; Phạm vi được người dùng xác nhận ngày 17/11/2026 |
| Tiền điều kiện | Có quyền vận hành cấu hình và quyền dùng dịch vụ ngoài. |
| Kích hoạt | Nhập cấu hình và chính sách dữ liệu. |
| Đầu vào | Nhà cung cấp, bí mật kết nối, giới hạn thời gian/dung lượng/hạn mức và phạm vi dữ liệu gửi. |
| Dữ liệu/khái niệm liên quan | CauHinhDichVu, TacVu, NhatKy |
| Quy tắc | BR-08, BR-14, BR-16 |
| Quan hệ | Không có quan hệ include/extend bắt buộc; xem tiền điều kiện và luồng. |

### Luồng thành công chính

1. **Quản trị viên kỹ thuật:** Nhập cấu hình và chính sách dữ liệu.
2. **Quesy:** Kiểm tra trường, địa chỉ dịch vụ và lưu bí mật được bảo vệ.
3. **Quesy:** Thử kết nối bằng tài liệu mẫu không chứa dữ liệu riêng.
4. **Quản trị viên kỹ thuật:** Xem kết quả thử và xác nhận kích hoạt.
5. **Quesy:** Kích hoạt phiên bản mới; giữ khả năng quay về bản trước.

### Luồng thay thế và ngoại lệ

- **UC-28-E1:** Thử kết nối thất bại: giữ bản đang hoạt động, không báo AI sẵn sàng.
- **UC-28-E2:** Tác vụ đang chạy: tiếp tục dùng cấu hình đã ghim; không đổi cấu hình giữa chừng.

### Hậu điều kiện và nghiệm thu

Khi hoàn tất: Cấu hình được kiểm tra bằng dữ liệu mẫu, kích hoạt có phiên bản; bí mật được che. Khi thất bại, giữ bảo đảm tối thiểu chung và trạng thái trung gian đã mô tả trong nhánh ngoại lệ. Hủy ở bước chưa xác nhận không tạo thay đổi nghiệp vụ mới.

Nghiệm thu dự kiến: luồng chính phải cho đúng đầu ra; chạy riêng các ca UC-28-E1 đến UC-28-E2; đối chiếu quyền và phiên bản tại điểm ghi. Các yêu cầu này chưa phải bằng chứng đã chạy kiểm thử sản phẩm.

Truy vết: [FR-28](02_YEU_CAU_CHUC_NANG.md#fr-28) · [UCD-28](07_SO_DO_USE_CASE.md#ucd-28) · [ACT-28](09_SO_DO_HOAT_DONG.md#act-28) · [SEQ-28](11_SO_DO_TUAN_TU.md#seq-28).


<a id="uc-29"></a>
## UC-29 — Giám sát tác vụ, nhật ký và xử lý lỗi

| Thuộc tính | Mô tả |
|---|---|
| Mục tiêu/đáp ứng | Báo cáo vận hành và quyết định xử lý có nhật ký; không tạo kết quả trùng. |
| Tác nhân chính | Quản trị viên kỹ thuật |
| Tác nhân hỗ trợ | Không bắt buộc |
| Căn cứ | XN; Phạm vi được người dùng xác nhận ngày 17/11/2026 |
| Tiền điều kiện | Có quyền xem thông tin vận hành đã giảm dữ liệu nhạy cảm. |
| Kích hoạt | Tra cứu lỗi và tiến độ theo mã tác vụ. |
| Đầu vào | Bộ lọc trạng thái, mã tác vụ, khoảng thời gian và lệnh hủy/thử lại. |
| Dữ liệu/khái niệm liên quan | TacVu, LanChay, NhatKy |
| Quy tắc | BR-07, BR-14, BR-16 |
| Quan hệ | Không có quan hệ include/extend bắt buộc; xem tiền điều kiện và luồng. |

### Luồng thành công chính

1. **Quản trị viên kỹ thuật:** Tra cứu lỗi và tiến độ theo mã tác vụ.
2. **Quesy:** Trả trạng thái và thông tin chẩn đoán đã che dữ liệu riêng.
3. **Quản trị viên kỹ thuật:** Chọn hủy hoặc thử lại phần lỗi khi được phép.
4. **Quesy:** Kiểm tra trạng thái và khóa chống lặp; ghi lệnh điều khiển.
5. **Quesy:** Trả trạng thái sau xử lý, giữ lịch sử lần chạy.

### Luồng thay thế và ngoại lệ

- **UC-29-E1:** Tác vụ đã hoàn tất hoặc không thể hủy: từ chối chuyển trạng thái sai.
- **UC-29-E2:** Thử lại: chỉ chạy phần lỗi với khóa chống lặp, không lặp nhập câu hoặc công bố gói.

### Hậu điều kiện và nghiệm thu

Khi hoàn tất: Báo cáo vận hành và quyết định xử lý có nhật ký; không tạo kết quả trùng. Khi thất bại, giữ bảo đảm tối thiểu chung và trạng thái trung gian đã mô tả trong nhánh ngoại lệ. Hủy ở bước chưa xác nhận không tạo thay đổi nghiệp vụ mới.

Nghiệm thu dự kiến: luồng chính phải cho đúng đầu ra; chạy riêng các ca UC-29-E1 đến UC-29-E2; đối chiếu quyền và phiên bản tại điểm ghi. Các yêu cầu này chưa phải bằng chứng đã chạy kiểm thử sản phẩm.

Truy vết: [FR-29](02_YEU_CAU_CHUC_NANG.md#fr-29) · [UCD-29](07_SO_DO_USE_CASE.md#ucd-29) · [ACT-29](09_SO_DO_HOAT_DONG.md#act-29) · [SEQ-29](11_SO_DO_TUAN_TU.md#seq-29).


<a id="uc-30"></a>
## UC-30 — Sao lưu và khôi phục hệ thống

| Thuộc tính | Mô tả |
|---|---|
| Mục tiêu/đáp ứng | Bản sao nhất quán được kiểm tra; phục hồi chỉ có hiệu lực sau đối soát, có điểm quay lui. |
| Tác nhân chính | Quản trị viên kỹ thuật |
| Tác nhân hỗ trợ | Kho sao lưu ngoài Quesy |
| Căn cứ | SL; Đề xuất suy luận nghiệp vụ; cần duyệt khi lập kế hoạch triển khai |
| Tiền điều kiện | Có quyền vận hành; phục hồi cần cửa sổ bảo trì và xác minh tăng cường. |
| Kích hoạt | Chọn sao lưu hoặc bản sao cần khôi phục. |
| Đầu vào | Lựa chọn sao lưu hoặc bản sao cần phục hồi, phạm vi dữ liệu và lý do. |
| Dữ liệu/khái niệm liên quan | BanSaoLuu, NhatKy, TacVu |
| Quy tắc | BR-02, BR-14, BR-16 |
| Quan hệ | Không có quan hệ include/extend bắt buộc; xem tiền điều kiện và luồng. |

### Luồng thành công chính

1. **Quản trị viên kỹ thuật:** Chọn sao lưu hoặc bản sao cần khôi phục.
2. **Quesy:** Kiểm tra quyền, phạm vi, tính tương thích và kế hoạch bảo trì.
3. **Quesy:** Tạo ảnh chụp nhất quán hoặc phục hồi vào vùng kiểm tra; giữ điểm quay lui.
4. **Quesy:** Đối chiếu cơ sở dữ liệu, tài sản, số lượng và mã kiểm tra.
5. **Quản trị viên kỹ thuật:** Xem kết quả và xác nhận chuyển bản phục hồi vào hoạt động nếu có.
6. **Quesy:** Công bố bản sao hợp lệ hoặc chuyển phục hồi; ghi nhật ký và trạng thái.

### Luồng thay thế và ngoại lệ

- **UC-30-E1:** Bản sao thiếu tài sản hoặc sai mã kiểm tra: đánh dấu không hợp lệ, không đưa vào hoạt động.
- **UC-30-E2:** Chuyển phục hồi thất bại: quay lại điểm trước phục hồi; giữ nhật ký sự cố.
- **UC-30-E3:** Sao lưu chứa kho riêng: chỉ xử lý theo quyền vận hành, không cung cấp giao diện đọc nội dung cho quản trị.

### Hậu điều kiện và nghiệm thu

Khi hoàn tất: Bản sao nhất quán được kiểm tra; phục hồi chỉ có hiệu lực sau đối soát, có điểm quay lui. Khi thất bại, giữ bảo đảm tối thiểu chung và trạng thái trung gian đã mô tả trong nhánh ngoại lệ. Hủy ở bước chưa xác nhận không tạo thay đổi nghiệp vụ mới.

Nghiệm thu dự kiến: luồng chính phải cho đúng đầu ra; chạy riêng các ca UC-30-E1 đến UC-30-E3; đối chiếu quyền và phiên bản tại điểm ghi. Các yêu cầu này chưa phải bằng chứng đã chạy kiểm thử sản phẩm.

Truy vết: [FR-30](02_YEU_CAU_CHUC_NANG.md#fr-30) · [UCD-30](07_SO_DO_USE_CASE.md#ucd-30) · [ACT-30](09_SO_DO_HOAT_DONG.md#act-30) · [SEQ-30](11_SO_DO_TUAN_TU.md#seq-30).
