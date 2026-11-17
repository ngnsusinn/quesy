# Yêu cầu chức năng

> Quesy · Bản phân tích nghiệp vụ 1.0 · Ngày 17/11/2026
> Trạng thái: bản đặc tả đề xuất, không phải báo cáo chức năng đã triển khai.

## Cấu trúc yêu cầu

Mỗi FR tương ứng một mục tiêu Use Case. `BC`, `XN`, `SL` có nghĩa tại tài liệu 00. Tiêu chí chấp nhận là điều kiện dự kiến để kiểm thử triển khai, không là kết quả đã chạy. Quy tắc BR tham chiếu [Yêu cầu hệ thống và bài toán nghiệp vụ](01_YEU_CAU_HE_THONG.md); các chi tiết bổ sung vẫn chịu các giả định AS-01–AS-08.

<a id="fr-01"></a>
## FR-01 — Đăng ký tài khoản giáo viên

| Thuộc tính | Yêu cầu |
|---|---|
| Tác nhân | Khách chưa đăng nhập |
| Căn cứ | SL — Đề xuất suy luận nghiệp vụ; cần duyệt khi lập kế hoạch triển khai |
| Điều kiện | Chưa đăng nhập; chính sách đăng ký đang mở. |
| Đầu vào | Tên hiển thị, định danh đăng nhập, mật khẩu và chấp nhận chính sách dữ liệu. |
| Đầu ra/đáp ứng phải có | Tài khoản giáo viên và không gian cá nhân được tạo; chưa tự cấp quyền quản trị. |
| Quy tắc | BR-01 |
| Truy vết | [UC-01](08_MO_TA_USE_CASE.md#uc-01); ACT-01; SEQ-01 |

**Tiêu chí chấp nhận**

1. Với đầu vào hợp lệ và đủ quyền, hoàn tất luồng chính, cho kết quả: Tài khoản giáo viên và không gian cá nhân được tạo; chưa tự cấp quyền quản trị.
2. Định danh đã dùng hoặc đăng ký bị đóng: từ chối tạo, giữ dữ liệu nhập trừ mật khẩu.
3. Ghi dữ liệu thất bại: hoàn tác tài khoản và không gian; cho gửi lại an toàn.


<a id="fr-02"></a>
## FR-02 — Đăng nhập

| Thuộc tính | Yêu cầu |
|---|---|
| Tác nhân | Khách chưa đăng nhập |
| Căn cứ | SL — Đề xuất suy luận nghiệp vụ; cần duyệt khi lập kế hoạch triển khai |
| Điều kiện | Có tài khoản đang hoạt động; chưa có phiên hợp lệ. |
| Đầu vào | Định danh và mật khẩu. |
| Đầu ra/đáp ứng phải có | Phiên xác thực mang đúng vai trò được tạo. |
| Quy tắc | BR-01 |
| Truy vết | [UC-02](08_MO_TA_USE_CASE.md#uc-02); ACT-02; SEQ-02 |

**Tiêu chí chấp nhận**

1. Với đầu vào hợp lệ và đủ quyền, hoàn tất luồng chính, cho kết quả: Phiên xác thực mang đúng vai trò được tạo.
2. Sai thông tin, bị khóa hoặc vượt giới hạn: báo đăng nhập không thành công, không tiết lộ tài khoản tồn tại.
3. Phiên hết hạn ở chức năng khác: yêu cầu đăng nhập lại và giữ bản nháp có thể khôi phục.


<a id="fr-03"></a>
## FR-03 — Đăng xuất

| Thuộc tính | Yêu cầu |
|---|---|
| Tác nhân | Người dùng đã xác thực |
| Căn cứ | SL — Đề xuất suy luận nghiệp vụ; cần duyệt khi lập kế hoạch triển khai |
| Điều kiện | Có phiên đăng nhập hoặc phiên vừa hết hạn. |
| Đầu vào | Lệnh đăng xuất và lựa chọn xử lý bản nháp chưa lưu. |
| Đầu ra/đáp ứng phải có | Phiên hiện tại bị thu hồi; dữ liệu ngân hàng đã lưu vẫn còn. |
| Quy tắc | BR-01 |
| Truy vết | [UC-03](08_MO_TA_USE_CASE.md#uc-03); ACT-03; SEQ-03 |

**Tiêu chí chấp nhận**

1. Với đầu vào hợp lệ và đủ quyền, hoàn tất luồng chính, cho kết quả: Phiên hiện tại bị thu hồi; dữ liệu ngân hàng đã lưu vẫn còn.
2. Hủy tại cảnh báo bản nháp: tiếp tục làm việc, không thu hồi phiên.
3. Không kết nối được máy chủ: xóa phiên phía giao diện và báo chưa xác nhận thu hồi phía máy chủ; phiên vẫn phải hết hạn theo chính sách.


<a id="fr-04"></a>
## FR-04 — Cập nhật hồ sơ và đổi mật khẩu

| Thuộc tính | Yêu cầu |
|---|---|
| Tác nhân | Người dùng đã xác thực |
| Căn cứ | SL — Đề xuất suy luận nghiệp vụ; cần duyệt khi lập kế hoạch triển khai |
| Điều kiện | Đã đăng nhập; đổi mật khẩu cần xác minh mật khẩu hiện tại. |
| Đầu vào | Tên hiển thị hoặc mật khẩu hiện tại và mật khẩu mới. |
| Đầu ra/đáp ứng phải có | Hồ sơ được cập nhật; đổi mật khẩu thu hồi các phiên cũ theo chính sách. |
| Quy tắc | BR-01, BR-02 |
| Truy vết | [UC-04](08_MO_TA_USE_CASE.md#uc-04); ACT-04; SEQ-04 |

**Tiêu chí chấp nhận**

1. Với đầu vào hợp lệ và đủ quyền, hoàn tất luồng chính, cho kết quả: Hồ sơ được cập nhật; đổi mật khẩu thu hồi các phiên cũ theo chính sách.
2. Mật khẩu hiện tại sai hoặc mật khẩu mới không hợp lệ: không thay thông tin xác thực.
3. Hồ sơ bị cập nhật đồng thời: yêu cầu tải lại để tránh ghi đè.


<a id="fr-05"></a>
## FR-05 — Tổ chức cây kiến thức cá nhân

| Thuộc tính | Yêu cầu |
|---|---|
| Tác nhân | Giáo viên |
| Căn cứ | BC — Bối cảnh Quesy do người dùng cung cấp |
| Điều kiện | Đã đăng nhập với không gian riêng; có môn và khối cần quản lý. |
| Đầu vào | Môn, khối, chương/chủ đề, bài, yêu cầu cần đạt và dạng bài; thao tác thêm, sửa hoặc ngừng dùng. |
| Đầu ra/đáp ứng phải có | Danh mục cá nhân hợp lệ; tham chiếu của câu hỏi cũ được giữ. |
| Quy tắc | BR-01, BR-03 |
| Truy vết | [UC-05](08_MO_TA_USE_CASE.md#uc-05); ACT-05; SEQ-05 |

**Tiêu chí chấp nhận**

1. Với đầu vào hợp lệ và đủ quyền, hoàn tất luồng chính, cho kết quả: Danh mục cá nhân hợp lệ; tham chiếu của câu hỏi cũ được giữ.
2. Nhánh có con hoặc đang được tham chiếu: ngừng dùng thay cho xóa phá hủy.
3. Giáo viên sửa danh mục chuẩn dùng chung: từ chối; cho sao chép thành nhánh cá nhân.


<a id="fr-06"></a>
## FR-06 — Tra cứu và xem câu hỏi

| Thuộc tính | Yêu cầu |
|---|---|
| Tác nhân | Giáo viên |
| Căn cứ | BC — Bối cảnh Quesy do người dùng cung cấp |
| Điều kiện | Đã đăng nhập. |
| Đầu vào | Từ khóa, môn, khối, nhánh kiến thức, dạng câu hỏi, mức nhận thức và trang kết quả. |
| Đầu ra/đáp ứng phải có | Danh sách và chi tiết câu hỏi trong phạm vi được phép, gồm công thức, hình và lời giải. |
| Quy tắc | BR-01, BR-02 |
| Truy vết | [UC-06](08_MO_TA_USE_CASE.md#uc-06); ACT-06; SEQ-06 |

**Tiêu chí chấp nhận**

1. Với đầu vào hợp lệ và đủ quyền, hoàn tất luồng chính, cho kết quả: Danh sách và chi tiết câu hỏi trong phạm vi được phép, gồm công thức, hình và lời giải.
2. Không có kết quả: hiển thị danh sách rỗng và gợi ý giảm điều kiện.
3. Truy cập mã câu hỏi ngoài quyền hoặc đã ngừng dùng: không tiết lộ nội dung trái phép.


<a id="fr-07"></a>
## FR-07 — Tạo và chỉnh sửa câu hỏi

| Thuộc tính | Yêu cầu |
|---|---|
| Tác nhân | Giáo viên |
| Căn cứ | BC — Bối cảnh Quesy do người dùng cung cấp |
| Điều kiện | Đã đăng nhập; sửa câu hỏi cần quyền sở hữu và phiên bản hiện hành. |
| Đầu vào | Đề bài, dạng MCQ/Đúng-Sai/trả lời ngắn/tự luận, lựa chọn/ý, đáp án, lời giải, nhãn và hình. |
| Đầu ra/đáp ứng phải có | Bản nháp hoặc phiên bản sẵn sàng được lưu; đề đã chốt không bị đổi nội dung. |
| Quy tắc | BR-02, BR-04, BR-05 |
| Truy vết | [UC-07](08_MO_TA_USE_CASE.md#uc-07); ACT-07; SEQ-07 |

**Tiêu chí chấp nhận**

1. Với đầu vào hợp lệ và đủ quyền, hoàn tất luồng chính, cho kết quả: Bản nháp hoặc phiên bản sẵn sàng được lưu; đề đã chốt không bị đổi nội dung.
2. Thiếu đáp án hoặc lời giải: cho lưu nháp có cờ lỗi; không chuyển sẵn sàng.
3. Nghi trùng: hiển thị cặp câu để giáo viên quyết định; không tự xóa. Phiên bản cũ: báo xung đột, giữ nội dung đang soạn để đối chiếu.


<a id="fr-08"></a>
## FR-08 — Ngừng dùng và khôi phục câu hỏi

| Thuộc tính | Yêu cầu |
|---|---|
| Tác nhân | Giáo viên |
| Căn cứ | SL — Đề xuất suy luận nghiệp vụ; cần duyệt khi lập kế hoạch triển khai |
| Điều kiện | Câu hỏi thuộc không gian cá nhân và vẫn tồn tại. |
| Đầu vào | Mã câu hỏi, phiên bản, thao tác ngừng dùng hoặc khôi phục và lý do. |
| Đầu ra/đáp ứng phải có | Trạng thái sử dụng thay đổi; bản chụp trong các đề cũ còn nguyên. |
| Quy tắc | BR-02, BR-06 |
| Truy vết | [UC-08](08_MO_TA_USE_CASE.md#uc-08); ACT-08; SEQ-08 |

**Tiêu chí chấp nhận**

1. Với đầu vào hợp lệ và đủ quyền, hoàn tất luồng chính, cho kết quả: Trạng thái sử dụng thay đổi; bản chụp trong các đề cũ còn nguyên.
2. Hủy xác nhận: không đổi trạng thái.
3. Khôi phục câu có lỗi: trả về nháp; cần hậu kiểm trước khi sẵn sàng.


<a id="fr-09"></a>
## FR-09 — Nhập ngân hàng từ dữ liệu có cấu trúc

| Thuộc tính | Yêu cầu |
|---|---|
| Tác nhân | Giáo viên |
| Căn cứ | SL — Đề xuất suy luận nghiệp vụ; cần duyệt khi lập kế hoạch triển khai |
| Điều kiện | Đã đăng nhập; có tệp theo mẫu công bố. |
| Đầu vào | Tệp bảng dữ liệu câu hỏi và ánh xạ cột/nhãn. |
| Đầu ra/đáp ứng phải có | Các dòng được chọn được nhập; mỗi dòng có kết quả và khóa chống nhập lặp. |
| Quy tắc | BR-04, BR-05, BR-07 |
| Truy vết | [UC-09](08_MO_TA_USE_CASE.md#uc-09); ACT-09; SEQ-09 |

**Tiêu chí chấp nhận**

1. Với đầu vào hợp lệ và đủ quyền, hoàn tất luồng chính, cho kết quả: Các dòng được chọn được nhập; mỗi dòng có kết quả và khóa chống nhập lặp.
2. Dòng lỗi: loại khỏi tập được nhập, nêu trường lỗi và giữ số dòng nguồn.
3. Gửi lại cùng lô: trả kết quả cũ cho dòng đã nhập, không tạo bản sao.


<a id="fr-10"></a>
## FR-10 — Xuất tập câu hỏi ngân hàng

| Thuộc tính | Yêu cầu |
|---|---|
| Tác nhân | Giáo viên |
| Căn cứ | SL — Đề xuất suy luận nghiệp vụ; cần duyệt khi lập kế hoạch triển khai |
| Điều kiện | Có quyền đọc các câu được chọn. |
| Đầu vào | Bộ lọc hoặc danh sách câu, định dạng PDF/LaTeX/bảng dữ liệu và lựa chọn kèm đáp án. |
| Đầu ra/đáp ứng phải có | Tệp xuất tái hiện đúng tập phiên bản đã chọn, tải được trong phạm vi quyền. |
| Quy tắc | BR-01, BR-02, BR-12 |
| Truy vết | [UC-10](08_MO_TA_USE_CASE.md#uc-10); ACT-10; SEQ-10 |

**Tiêu chí chấp nhận**

1. Với đầu vào hợp lệ và đủ quyền, hoàn tất luồng chính, cho kết quả: Tệp xuất tái hiện đúng tập phiên bản đã chọn, tải được trong phạm vi quyền.
2. Tập câu rỗng: yêu cầu chọn lại.
3. Biên dịch hoặc tài sản thiếu: báo câu gây lỗi, giữ lựa chọn và không công bố tệp lỗi.


<a id="fr-11"></a>
## FR-11 — Số hóa tài liệu nguồn bằng AI

| Thuộc tính | Yêu cầu |
|---|---|
| Tác nhân | Giáo viên |
| Căn cứ | BC — Bối cảnh Quesy do người dùng cung cấp |
| Điều kiện | Đã đăng nhập; dịch vụ AI được cấu hình; còn hạn mức. |
| Đầu vào | PDF/ảnh/Word/LaTeX và phạm vi trang cần xử lý. |
| Đầu ra/đáp ứng phải có | Bản trích xuất nháp gắn trang, vùng nguồn và tài sản; chưa vào kho sẵn sàng. |
| Quy tắc | BR-04, BR-05, BR-07, BR-08 |
| Truy vết | [UC-11](08_MO_TA_USE_CASE.md#uc-11); ACT-11; SEQ-11 |

**Tiêu chí chấp nhận**

1. Với đầu vào hợp lệ và đủ quyền, hoàn tất luồng chính, cho kết quả: Bản trích xuất nháp gắn trang, vùng nguồn và tài sản; chưa vào kho sẵn sàng.
2. Tệp sai định dạng, không đọc được hoặc vượt hạn mức: từ chối trước xử lý.
3. AI lỗi hoặc hết thời gian: đánh dấu lỗi theo trang, giữ phần thành công; cho thử lại phần lỗi với cùng khóa tác vụ. Nguồn không có đáp án/lời giải: đánh dấu thiếu, không tự khẳng định nội dung suy đoán là dữ liệu gốc.


<a id="fr-12"></a>
## FR-12 — Hậu kiểm và đưa câu số hóa vào kho

| Thuộc tính | Yêu cầu |
|---|---|
| Tác nhân | Giáo viên |
| Căn cứ | BC — Bối cảnh Quesy do người dùng cung cấp |
| Điều kiện | Có bản trích xuất thuộc không gian; bản nguồn còn truy cập được. |
| Đầu vào | Bản trích xuất, sửa nội dung/hình/công thức, đáp án, lời giải, nhãn và lựa chọn nhập. |
| Đầu ra/đáp ứng phải có | Chỉ các câu được giáo viên xác nhận mới vào kho; giữ truy nguyên tới nguồn. |
| Quy tắc | BR-04, BR-05, BR-07, BR-08 |
| Truy vết | [UC-12](08_MO_TA_USE_CASE.md#uc-12); ACT-12; SEQ-12 |

**Tiêu chí chấp nhận**

1. Với đầu vào hợp lệ và đủ quyền, hoàn tất luồng chính, cho kết quả: Chỉ các câu được giáo viên xác nhận mới vào kho; giữ truy nguyên tới nguồn.
2. Thiếu dữ liệu bắt buộc hoặc còn lỗi: chỉ được lưu nháp; chỉ rõ câu và trường cần sửa.
3. Nghi trùng: đối chiếu câu cũ, bỏ nhập hoặc xác nhận lưu phiên bản/câu độc lập kèm lý do. Bấm xác nhận lại: trả mã câu đã nhập, không nhập đôi.


<a id="fr-13"></a>
## FR-13 — Thiết lập ma trận đặc tả

| Thuộc tính | Yêu cầu |
|---|---|
| Tác nhân | Giáo viên |
| Căn cứ | BC — Bối cảnh Quesy do người dùng cung cấp |
| Điều kiện | Có cây kiến thức và hồ sơ cấu trúc đề được chọn. |
| Đầu vào | Môn, khối, thời lượng, phần thi; ô kiến thức × dạng câu × mức nhận thức, số câu và điểm. |
| Đầu ra/đáp ứng phải có | Phiên bản ma trận được lưu; tổng câu, điểm và phân bổ được tính nhất quán. |
| Quy tắc | BR-03, BR-09, BR-13 |
| Truy vết | [UC-13](08_MO_TA_USE_CASE.md#uc-13); ACT-13; SEQ-13 |

**Tiêu chí chấp nhận**

1. Với đầu vào hợp lệ và đủ quyền, hoàn tất luồng chính, cho kết quả: Phiên bản ma trận được lưu; tổng câu, điểm và phân bổ được tính nhất quán.
2. Tổng điểm hoặc số lượng trái hồ sơ đã chọn: chỉ rõ ô gây sai; cho sửa hoặc lưu nháp.
3. Hai ô chồng miền câu hỏi: cảnh báo khả năng thiếu phân bổ; kiểm tra toàn cục ở UC-14.


<a id="fr-14"></a>
## FR-14 — Kiểm tra khả năng đáp ứng ma trận

| Thuộc tính | Yêu cầu |
|---|---|
| Tác nhân | Giáo viên |
| Căn cứ | BC — Bối cảnh Quesy do người dùng cung cấp |
| Điều kiện | Có phiên bản ma trận; câu hỏi chỉ lấy từ không gian được phép. |
| Đầu vào | Ma trận, quy tắc loại trừ câu đã dùng và tập câu sẵn sàng. |
| Đầu ra/đáp ứng phải có | Báo cáo tồn kho từng ô và tính khả thi phân bổ toàn cục, không nhân đôi một câu. |
| Quy tắc | BR-06, BR-09 |
| Truy vết | [UC-14](08_MO_TA_USE_CASE.md#uc-14); ACT-14; SEQ-14 |

**Tiêu chí chấp nhận**

1. Với đầu vào hợp lệ và đủ quyền, hoàn tất luồng chính, cho kết quả: Báo cáo tồn kho từng ô và tính khả thi phân bổ toàn cục, không nhân đôi một câu.
2. Thiếu câu: trả đầy đủ môn/khối/nhánh/dạng/mức/phần và số thiếu; không báo đạt.
3. Từng ô đủ nhưng cùng tranh chấp một tập câu: báo thiếu toàn cục và các ô liên quan. Kho thay đổi sau kiểm tra: kết quả chỉ có giá trị tại thời điểm kiểm tra, UC-15 phải kiểm tra lại.


<a id="fr-15"></a>
## FR-15 — Sinh đề gốc theo ma trận

| Thuộc tính | Yêu cầu |
|---|---|
| Tác nhân | Giáo viên |
| Căn cứ | BC — Bối cảnh Quesy do người dùng cung cấp |
| Điều kiện | Ma trận hợp lệ và được chốt; có quyền sử dụng các câu nguồn. |
| Đầu vào | Phiên bản ma trận, điều kiện loại trừ và tiêu chí chọn câu. |
| Đầu ra/đáp ứng phải có | Bản nháp đề gốc đúng ma trận được lưu bằng các bản chụp câu hỏi. |
| Quy tắc | BR-02, BR-06, BR-09, BR-10 |
| Truy vết | [UC-15](08_MO_TA_USE_CASE.md#uc-15); ACT-15; SEQ-15 |

**Tiêu chí chấp nhận**

1. Với đầu vào hợp lệ và đủ quyền, hoàn tất luồng chính, cho kết quả: Bản nháp đề gốc đúng ma trận được lưu bằng các bản chụp câu hỏi.
2. Không còn đủ câu: báo tọa độ và số thiếu; không tạo đề một phần.
3. Có câu đã đổi trạng thái lúc chốt: hủy lưu, kiểm tra lại tập ứng viên.


<a id="fr-16"></a>
## FR-16 — Biên soạn và xem trước đề

| Thuộc tính | Yêu cầu |
|---|---|
| Tác nhân | Giáo viên |
| Căn cứ | BC — Bối cảnh Quesy do người dùng cung cấp |
| Điều kiện | Có đề thuộc không gian hoặc khởi tạo đề mới. |
| Đầu vào | Thông tin đầu đề, nội dung câu, phần thi, thứ tự, đáp án, lời giải và hình. |
| Đầu ra/đáp ứng phải có | Bản nháp có phiên bản; bản xem trước ghi đúng phiên bản vừa biên dịch. |
| Quy tắc | BR-02, BR-04, BR-12 |
| Truy vết | [UC-16](08_MO_TA_USE_CASE.md#uc-16); ACT-16; SEQ-16 |

**Tiêu chí chấp nhận**

1. Với đầu vào hợp lệ và đủ quyền, hoàn tất luồng chính, cho kết quả: Bản nháp có phiên bản; bản xem trước ghi đúng phiên bản vừa biên dịch.
2. Lỗi công thức, hình hoặc lệnh không được hỗ trợ: giữ nháp và trả vị trí lỗi; không dùng bản xem trước cũ làm bản mới.
3. Có thay đổi đồng thời: giữ bản đang soạn, yêu cầu so sánh phiên bản.


<a id="fr-17"></a>
## FR-17 — Nhận và duyệt đề xuất của Copilot

| Thuộc tính | Yêu cầu |
|---|---|
| Tác nhân | Giáo viên |
| Căn cứ | BC — Bối cảnh Quesy do người dùng cung cấp |
| Điều kiện | Có bản nháp và cấu hình AI sử dụng được. |
| Đầu vào | Yêu cầu tự nhiên, phạm vi câu/đoạn, phiên bản đề và lỗi biên dịch nếu liên quan. |
| Đầu ra/đáp ứng phải có | Đề xuất được xem xét; chỉ phần giáo viên chấp nhận mới thành phiên bản nháp mới. |
| Quy tắc | BR-02, BR-08, BR-11 |
| Truy vết | [UC-17](08_MO_TA_USE_CASE.md#uc-17); ACT-17; SEQ-17 |

**Tiêu chí chấp nhận**

1. Với đầu vào hợp lệ và đủ quyền, hoàn tất luồng chính, cho kết quả: Đề xuất được xem xét; chỉ phần giáo viên chấp nhận mới thành phiên bản nháp mới.
2. AI lỗi hoặc quá hạn: báo lỗi; giữ nguyên nháp.
3. Nội dung đề đã đổi sau khi gửi: không áp dụng tự động, yêu cầu so sánh lại. Yêu cầu hỏi đáp: trả lời trong khung trợ lý, không thay nội dung đề.


<a id="fr-18"></a>
## FR-18 — Thay câu bằng đối chiếu song song

| Thuộc tính | Yêu cầu |
|---|---|
| Tác nhân | Giáo viên |
| Căn cứ | BC — Bối cảnh Quesy do người dùng cung cấp |
| Điều kiện | Có câu trong đề nháp và ô ma trận tương ứng; đề chưa chốt xuất bản. |
| Đầu vào | Câu cần thay, tiêu chí cùng ô và lựa chọn tìm kho hoặc đề xuất AI. |
| Đầu ra/đáp ứng phải có | Câu được thay sau xác nhận; đề vẫn đúng ma trận và có phiên bản mới. |
| Quy tắc | BR-02, BR-09, BR-10, BR-11 |
| Truy vết | [UC-18](08_MO_TA_USE_CASE.md#uc-18); ACT-18; SEQ-18 |

**Tiêu chí chấp nhận**

1. Với đầu vào hợp lệ và đủ quyền, hoàn tất luồng chính, cho kết quả: Câu được thay sau xác nhận; đề vẫn đúng ma trận và có phiên bản mới.
2. Không có ứng viên kho: cho hủy hoặc gọi UC-17 sinh đề xuất AI; ứng viên AI vẫn cần hậu kiểm.
3. Ứng viên đã có trong đề, làm vỡ nhóm ngữ liệu hoặc sai ô: từ chối thay. Đề thay đổi khi đang đối chiếu: yêu cầu chọn lại trên phiên bản mới.


<a id="fr-19"></a>
## FR-19 — Kiểm định đề và chốt phiên bản

| Thuộc tính | Yêu cầu |
|---|---|
| Tác nhân | Giáo viên |
| Căn cứ | BC — Bối cảnh Quesy do người dùng cung cấp |
| Điều kiện | Có phiên bản đề nháp đọc được. |
| Đầu vào | Phiên bản đề, hồ sơ cấu trúc/chấm và lựa chọn chế độ kiểm định ẩn đáp án trước. |
| Đầu ra/đáp ứng phải có | Báo cáo QA gắn phiên bản; chỉ đề không có lỗi chặn mới được chốt. |
| Quy tắc | BR-04, BR-09, BR-11, BR-12 |
| Truy vết | [UC-19](08_MO_TA_USE_CASE.md#uc-19); ACT-19; SEQ-19 |

**Tiêu chí chấp nhận**

1. Với đầu vào hợp lệ và đủ quyền, hoàn tất luồng chính, cho kết quả: Báo cáo QA gắn phiên bản; chỉ đề không có lỗi chặn mới được chốt.
2. Có lỗi chặn: không chốt; quay lại sửa rồi chạy QA mới.
3. Phiên bản thay đổi sau QA: báo cáo cũ hết hiệu lực đối với phiên bản mới. QA cấu trúc không chứng minh đáp án đúng về chuyên môn; giáo viên phải rà soát nội dung.


<a id="fr-20"></a>
## FR-20 — Sinh các mã đề hoán vị an toàn

| Thuộc tính | Yêu cầu |
|---|---|
| Tác nhân | Giáo viên |
| Căn cứ | BC — Bối cảnh Quesy do người dùng cung cấp |
| Điều kiện | Đề gốc đã chốt và QA còn hiệu lực. |
| Đầu vào | Phiên bản đề gốc, số mã đề, mã định danh và cấu hình trộn. |
| Đầu ra/đáp ứng phải có | Bộ mã đề và ánh xạ đáp án được lưu sau kiểm chứng đầy đủ bất biến. |
| Quy tắc | BR-02, BR-10, BR-13 |
| Truy vết | [UC-20](08_MO_TA_USE_CASE.md#uc-20); ACT-20; SEQ-20 |

**Tiêu chí chấp nhận**

1. Với đầu vào hợp lệ và đủ quyền, hoàn tất luồng chính, cho kết quả: Bộ mã đề và ánh xạ đáp án được lưu sau kiểm chứng đầy đủ bất biến.
2. Có phương án phụ thuộc vị trí không thể xử lý an toàn: giữ vị trí phù hợp hoặc từ chối trộn câu đó, nêu lý do.
3. Bất kỳ mã nào vi phạm bất biến: không công bố cả bộ; giữ đề gốc và báo lỗi.


<a id="fr-21"></a>
## FR-21 — Xuất bản bộ ấn phẩm khảo thí

| Thuộc tính | Yêu cầu |
|---|---|
| Tác nhân | Giáo viên |
| Căn cứ | BC — Bối cảnh Quesy do người dùng cung cấp |
| Điều kiện | Đề gốc đã chốt; các mã đề nếu có đã đạt kiểm chứng; có đủ tài sản. |
| Đầu vào | Phiên bản đề/bộ mã, mẫu dàn trang, chế độ đề/đáp án/lời giải và định dạng PDF/LaTeX/ZIP. |
| Đầu ra/đáp ứng phải có | Ấn phẩm đúng phiên bản và mã đề; đề phát cho học sinh không lộ đáp án. |
| Quy tắc | BR-01, BR-02, BR-10, BR-12 |
| Truy vết | [UC-21](08_MO_TA_USE_CASE.md#uc-21); ACT-21; SEQ-21 |

**Tiêu chí chấp nhận**

1. Với đầu vào hợp lệ và đủ quyền, hoàn tất luồng chính, cho kết quả: Ấn phẩm đúng phiên bản và mã đề; đề phát cho học sinh không lộ đáp án.
2. Biên dịch lỗi: chỉ rõ mã đề/câu, giữ kết quả nháp; không gắn nhãn gói hoàn tất.
3. Tệp đáp án không khớp phiên bản hoặc mã đề: chặn xuất bản. Thay đề sau xuất bản: tạo phiên bản và gói mới, giữ gói cũ để đối chiếu.


<a id="fr-22"></a>
## FR-22 — Quản lý danh sách lớp và kỳ chấm

| Thuộc tính | Yêu cầu |
|---|---|
| Tác nhân | Giáo viên |
| Căn cứ | SL — Đề xuất suy luận nghiệp vụ; cần duyệt khi lập kế hoạch triển khai |
| Điều kiện | Đã đăng nhập; có mục đích quản lý kết quả học tập. |
| Đầu vào | Danh sách học sinh tối thiểu, mã học sinh, lớp và kỳ chấm gắn đề/bộ mã. |
| Đầu ra/đáp ứng phải có | Danh sách lớp và kỳ chấm hợp lệ, không trùng mã trong cùng danh sách. |
| Quy tắc | BR-01, BR-07, BR-14 |
| Truy vết | [UC-22](08_MO_TA_USE_CASE.md#uc-22); ACT-22; SEQ-22 |

**Tiêu chí chấp nhận**

1. Với đầu vào hợp lệ và đủ quyền, hoàn tất luồng chính, cho kết quả: Danh sách lớp và kỳ chấm hợp lệ, không trùng mã trong cùng danh sách.
2. Mã học sinh trùng hoặc thiếu: báo dòng, không tự gộp người.
3. Kỳ đã có điểm: sửa danh sách phải giữ lịch sử và tham chiếu kết quả; không xóa âm thầm.


<a id="fr-23"></a>
## FR-23 — Nhập bài và chấm theo đúng mã đề

| Thuộc tính | Yêu cầu |
|---|---|
| Tác nhân | Giáo viên |
| Căn cứ | BC — Bối cảnh Quesy do người dùng cung cấp |
| Điều kiện | Có kỳ chấm, bộ mã và hồ sơ chấm đã chốt; học sinh là dữ liệu, không đăng nhập hệ thống. |
| Đầu vào | Câu trả lời nhập tay/bảng dữ liệu/ảnh phiếu; mã học sinh, mã đề; điểm tự luận do giáo viên chấm. |
| Đầu ra/đáp ứng phải có | Kết quả và chi tiết điểm gắn bài, mã đề và phiên bản hồ sơ chấm; có lịch sử sửa. |
| Quy tắc | BR-10, BR-13, BR-14 |
| Truy vết | [UC-23](08_MO_TA_USE_CASE.md#uc-23); ACT-23; SEQ-23 |

**Tiêu chí chấp nhận**

1. Với đầu vào hợp lệ và đủ quyền, hoàn tất luồng chính, cho kết quả: Kết quả và chi tiết điểm gắn bài, mã đề và phiên bản hồ sơ chấm; có lịch sử sửa.
2. Không xác định được mã đề hoặc còn ô mờ: giữ bài chờ xác minh; không chấm theo mã mặc định.
3. Đúng/Sai bỏ trống tính là ý không khớp; 0 ý đúng được 0 điểm. Tự luận: chỉ lưu điểm giáo viên nhập theo rubric, không suy ra điểm tự động. Sửa đáp án sau chốt: tạo phiên bản chấm lại, không ghi đè lịch sử.


<a id="fr-24"></a>
## FR-24 — Phân tích kết quả và chất lượng câu hỏi

| Thuộc tính | Yêu cầu |
|---|---|
| Tác nhân | Giáo viên |
| Căn cứ | SL — Đề xuất suy luận nghiệp vụ; cần duyệt khi lập kế hoạch triển khai |
| Điều kiện | Có kết quả đã chốt và ánh xạ về câu gốc. |
| Đầu vào | Kỳ chấm, lớp, bộ lọc kết quả và quy tắc chọn mẫu. |
| Đầu ra/đáp ứng phải có | Phổ điểm và chỉ số câu hỏi có mẫu số, nhóm mẫu, phiên bản và cảnh báo giới hạn. |
| Quy tắc | BR-01, BR-10, BR-15 |
| Truy vết | [UC-24](08_MO_TA_USE_CASE.md#uc-24); ACT-24; SEQ-24 |

**Tiêu chí chấp nhận**

1. Với đầu vào hợp lệ và đủ quyền, hoàn tất luồng chính, cho kết quả: Phổ điểm và chỉ số câu hỏi có mẫu số, nhóm mẫu, phiên bản và cảnh báo giới hạn.
2. Không có mẫu hợp lệ hoặc không lập được hai nhóm phân biệt: hiển thị không đủ dữ liệu, không chia cho 0.
3. MCQ tính p và D; Đúng/Sai báo từng ý hoặc chỉ số điểm đã chuẩn hóa có nhãn riêng; tự luận không gán p nhị phân tùy tiện.


<a id="fr-25"></a>
## FR-25 — Quản lý tài khoản và quyền truy cập

| Thuộc tính | Yêu cầu |
|---|---|
| Tác nhân | Quản trị viên kỹ thuật |
| Căn cứ | XN — Phạm vi được người dùng xác nhận ngày 17/11/2026 |
| Điều kiện | Quản trị viên đã đăng nhập; thay quyền cần xác minh tăng cường theo chính sách. |
| Đầu vào | Tài khoản, trạng thái mở/khóa, vai trò, hạn mức và lý do thay đổi. |
| Đầu ra/đáp ứng phải có | Tài khoản và quyền được cập nhật có nhật ký; không tạo quyền xem kho riêng mặc định. |
| Quy tắc | BR-01, BR-14, BR-16 |
| Truy vết | [UC-25](08_MO_TA_USE_CASE.md#uc-25); ACT-25; SEQ-25 |

**Tiêu chí chấp nhận**

1. Với đầu vào hợp lệ và đủ quyền, hoàn tất luồng chính, cho kết quả: Tài khoản và quyền được cập nhật có nhật ký; không tạo quyền xem kho riêng mặc định.
2. Định khóa/hạ quyền quản trị viên hoạt động cuối cùng: chặn.
3. Quản trị viên yêu cầu mở nội dung kho cá nhân bằng quyền vận hành: từ chối, trừ quy trình hỗ trợ riêng được chủ sở hữu cho phép.


<a id="fr-26"></a>
## FR-26 — Quản lý danh mục kiến thức dùng chung

| Thuộc tính | Yêu cầu |
|---|---|
| Tác nhân | Quản trị viên kỹ thuật |
| Căn cứ | SL — Đề xuất suy luận nghiệp vụ; cần duyệt khi lập kế hoạch triển khai |
| Điều kiện | Có quyền quản trị danh mục; có nguồn tham chiếu giáo dục được phê duyệt. |
| Đầu vào | Phiên bản môn/khối/nhánh/YCCĐ/dạng bài và nguồn tham chiếu. |
| Đầu ra/đáp ứng phải có | Danh mục chung có phiên bản được công bố; dữ liệu cá nhân cũ không bị đổi nhãn ngầm. |
| Quy tắc | BR-02, BR-03, BR-16 |
| Truy vết | [UC-26](08_MO_TA_USE_CASE.md#uc-26); ACT-26; SEQ-26 |

**Tiêu chí chấp nhận**

1. Với đầu vào hợp lệ và đủ quyền, hoàn tất luồng chính, cho kết quả: Danh mục chung có phiên bản được công bố; dữ liệu cá nhân cũ không bị đổi nhãn ngầm.
2. Nhánh đang được tham chiếu: ngừng dùng ở bản mới thay cho xóa bản cũ.
3. Chuyển nhãn câu cá nhân: chỉ đề xuất ánh xạ, chờ giáo viên chấp thuận qua UC-05/UC-07.


<a id="fr-27"></a>
## FR-27 — Quản lý hồ sơ đề và quy tắc chấm

| Thuộc tính | Yêu cầu |
|---|---|
| Tác nhân | Quản trị viên kỹ thuật |
| Căn cứ | SL — Đề xuất suy luận nghiệp vụ; cần duyệt khi lập kế hoạch triển khai |
| Điều kiện | Có quyền cấu hình mẫu; thay đổi dựa trên quyết định nghiệp vụ được ghi nhận. |
| Đầu vào | Các phần thi, dạng câu, mức nhận thức, điểm MCQ/trả lời ngắn, thang Đúng/Sai và rubric tự luận. |
| Đầu ra/đáp ứng phải có | Hồ sơ mới được công bố có phiên bản; đề và điểm cũ giữ quy tắc đã ghim. |
| Quy tắc | BR-02, BR-13, BR-16 |
| Truy vết | [UC-27](08_MO_TA_USE_CASE.md#uc-27); ACT-27; SEQ-27 |

**Tiêu chí chấp nhận**

1. Với đầu vào hợp lệ và đủ quyền, hoàn tất luồng chính, cho kết quả: Hồ sơ mới được công bố có phiên bản; đề và điểm cũ giữ quy tắc đã ghim.
2. Thang điểm không đầy đủ hoặc điểm âm: chặn công bố.
3. Muốn chấm lại kỳ cũ: tạo phiên bản kết quả qua UC-23 và ghi rõ hồ sơ mới.


<a id="fr-28"></a>
## FR-28 — Cấu hình dịch vụ AI và biên dịch

| Thuộc tính | Yêu cầu |
|---|---|
| Tác nhân | Quản trị viên kỹ thuật |
| Căn cứ | XN — Phạm vi được người dùng xác nhận ngày 17/11/2026 |
| Điều kiện | Có quyền vận hành cấu hình và quyền dùng dịch vụ ngoài. |
| Đầu vào | Nhà cung cấp, bí mật kết nối, giới hạn thời gian/dung lượng/hạn mức và phạm vi dữ liệu gửi. |
| Đầu ra/đáp ứng phải có | Cấu hình được kiểm tra bằng dữ liệu mẫu, kích hoạt có phiên bản; bí mật được che. |
| Quy tắc | BR-08, BR-14, BR-16 |
| Truy vết | [UC-28](08_MO_TA_USE_CASE.md#uc-28); ACT-28; SEQ-28 |

**Tiêu chí chấp nhận**

1. Với đầu vào hợp lệ và đủ quyền, hoàn tất luồng chính, cho kết quả: Cấu hình được kiểm tra bằng dữ liệu mẫu, kích hoạt có phiên bản; bí mật được che.
2. Thử kết nối thất bại: giữ bản đang hoạt động, không báo AI sẵn sàng.
3. Tác vụ đang chạy: tiếp tục dùng cấu hình đã ghim; không đổi cấu hình giữa chừng.


<a id="fr-29"></a>
## FR-29 — Giám sát tác vụ, nhật ký và xử lý lỗi

| Thuộc tính | Yêu cầu |
|---|---|
| Tác nhân | Quản trị viên kỹ thuật |
| Căn cứ | XN — Phạm vi được người dùng xác nhận ngày 17/11/2026 |
| Điều kiện | Có quyền xem thông tin vận hành đã giảm dữ liệu nhạy cảm. |
| Đầu vào | Bộ lọc trạng thái, mã tác vụ, khoảng thời gian và lệnh hủy/thử lại. |
| Đầu ra/đáp ứng phải có | Báo cáo vận hành và quyết định xử lý có nhật ký; không tạo kết quả trùng. |
| Quy tắc | BR-07, BR-14, BR-16 |
| Truy vết | [UC-29](08_MO_TA_USE_CASE.md#uc-29); ACT-29; SEQ-29 |

**Tiêu chí chấp nhận**

1. Với đầu vào hợp lệ và đủ quyền, hoàn tất luồng chính, cho kết quả: Báo cáo vận hành và quyết định xử lý có nhật ký; không tạo kết quả trùng.
2. Tác vụ đã hoàn tất hoặc không thể hủy: từ chối chuyển trạng thái sai.
3. Thử lại: chỉ chạy phần lỗi với khóa chống lặp, không lặp nhập câu hoặc công bố gói.


<a id="fr-30"></a>
## FR-30 — Sao lưu và khôi phục hệ thống

| Thuộc tính | Yêu cầu |
|---|---|
| Tác nhân | Quản trị viên kỹ thuật |
| Căn cứ | SL — Đề xuất suy luận nghiệp vụ; cần duyệt khi lập kế hoạch triển khai |
| Điều kiện | Có quyền vận hành; phục hồi cần cửa sổ bảo trì và xác minh tăng cường. |
| Đầu vào | Lựa chọn sao lưu hoặc bản sao cần phục hồi, phạm vi dữ liệu và lý do. |
| Đầu ra/đáp ứng phải có | Bản sao nhất quán được kiểm tra; phục hồi chỉ có hiệu lực sau đối soát, có điểm quay lui. |
| Quy tắc | BR-02, BR-14, BR-16 |
| Truy vết | [UC-30](08_MO_TA_USE_CASE.md#uc-30); ACT-30; SEQ-30 |

**Tiêu chí chấp nhận**

1. Với đầu vào hợp lệ và đủ quyền, hoàn tất luồng chính, cho kết quả: Bản sao nhất quán được kiểm tra; phục hồi chỉ có hiệu lực sau đối soát, có điểm quay lui.
2. Bản sao thiếu tài sản hoặc sai mã kiểm tra: đánh dấu không hợp lệ, không đưa vào hoạt động.
3. Chuyển phục hồi thất bại: quay lại điểm trước phục hồi; giữ nhật ký sự cố. Sao lưu chứa kho riêng: chỉ xử lý theo quyền vận hành, không cung cấp giao diện đọc nội dung cho quản trị.
