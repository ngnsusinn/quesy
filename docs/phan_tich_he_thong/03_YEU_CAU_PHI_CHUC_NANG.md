# Yêu cầu phi chức năng

> Quesy · Bản phân tích nghiệp vụ 1.0 · Ngày 17/11/2026
> Trạng thái: bản đặc tả đề xuất, không phải báo cáo chức năng đã triển khai.

## Cơ sở và điều kiện đo

Áp dụng phân biệt thuộc tính chất lượng và ràng buộc từ **M02, tr. 3–6**. Các ngưỡng số dưới đây là **mục tiêu đề xuất**, chưa là SLA đã thống nhất hay số liệu đã đạt. Tính đúng quyền, không sai đáp án và giữ dữ liệu là bất biến nghiệm thu; các mục tiêu hiệu năng/dung lượng cần xác nhận bằng khảo sát và cấu hình máy cụ thể.

Điều kiện đo phải ghi phần cứng, mạng, số câu, số người đang thao tác, kích thước tài sản, nhà cung cấp, tập mẫu và phiên bản hồ sơ. Tách thời gian phản hồi giao diện, thời gian nhận việc và thời gian hoàn tất xử lý. Kiểm tra chất lượng AI trên tập có đáp án chuyên gia; báo tỷ lệ đúng theo văn bản, công thức, hình và nhãn; **chưa có ngưỡng chính xác AI được duyệt**. Độ chính xác gợi ý không thay điều kiện hậu kiểm bắt buộc.

<a id="nfr-01"></a>
## NFR-01 — Phân quyền đối tượng

**Yêu cầu:** Mọi yêu cầu đọc, sửa, xuất và tải phải kiểm tra vai trò và chủ sở hữu; tỷ lệ truy cập chéo không được cấp là 0 trong bộ kiểm thử quyền.

**Cách nghiệm thu:** Lập hai giáo viên và một quản trị vận hành; thử mã đối tượng và liên kết tệp của nhau. Không có nội dung trái quyền trong kết quả/lỗi.

**Phạm vi truy vết:** UC-05–UC-24, UC-25.


<a id="nfr-02"></a>
## NFR-02 — Bảo vệ xác thực và bí mật

**Yêu cầu:** Mật khẩu không lưu dạng đọc lại; bí mật dịch vụ không hiển thị toàn bộ, không xuất ra nhật ký. Phiên hết hạn/thu hồi phải bị từ chối ở lần kiểm tra quyền tiếp theo.

**Cách nghiệm thu:** Đối chiếu thiết kế lưu trữ, quan sát log và thử phiên đã hết hạn/thu hồi. Giới hạn thử sai đề xuất: tối đa 5 lần/15 phút trên cùng định danh và nguồn, có chống khóa tài khoản ác ý.

**Phạm vi truy vết:** UC-01–UC-04, UC-25, UC-28.


<a id="nfr-03"></a>
## NFR-03 — Đúng dữ liệu và phiên bản

**Yêu cầu:** 100% mã đề kiểm tra phải bảo toàn câu, phần, nhóm, phương án neo và ánh xạ đáp án. Cập nhật đề đã QA tạo phiên bản mới.

**Cách nghiệm thu:** Dùng ca biên MCQ, Đúng/Sai, câu chùm và phương án phụ thuộc vị trí; đối chiếu đáp án từng mã.

**Phạm vi truy vết:** UC-07, UC-15–UC-23.


<a id="nfr-04"></a>
## NFR-04 — Giao dịch và phục hồi lỗi

**Yêu cầu:** Không có đề/gói mang trạng thái hoàn tất khi thiếu thành phần bắt buộc; gửi lại cùng định danh yêu cầu không tạo bản sao.

**Cách nghiệm thu:** Ngắt tại từng bước lưu của nhập/sinh/trộn/xuất/chấm; gửi lại và so số kết quả, nhật ký.

**Phạm vi truy vết:** UC-09, UC-11–UC-12, UC-15, UC-20–UC-23, UC-29.


<a id="nfr-05"></a>
## NFR-05 — Hiệu năng tra cứu

**Yêu cầu:** Mục tiêu đề xuất: P95 từ gửi truy vấn đến nhận danh sách <=2 giây với 50.000 câu/không gian, 20 phiên đang thao tác, trang 25 câu, không tính tải ảnh gốc.

**Cách nghiệm thu:** Đo tối thiểu 1.000 yêu cầu sau làm nóng; công bố phần cứng, mạng, dữ liệu và tỷ lệ lỗi. Ngân sách áp dụng truy vấn thông thường, không gồm AI/biên dịch.

**Phạm vi truy vết:** UC-06, UC-14.


<a id="nfr-06"></a>
## NFR-06 — Phản hồi tác vụ dài

**Yêu cầu:** Mục tiêu đề xuất: tiếp nhận tác vụ <=2 giây P95; cập nhật tiến độ ít nhất mỗi 5 giây khi có thay đổi. Quá giới hạn phải báo lỗi có thể xử lý.

**Cách nghiệm thu:** Đo số hóa tài liệu mẫu 20 trang và xuất 4 mã × 40 câu. Thời gian hoàn tất AI/biên dịch được báo riêng; chưa đặt cam kết khi chưa có nhà cung cấp.

**Phạm vi truy vết:** UC-10–UC-11, UC-16–UC-17, UC-21, UC-29.


<a id="nfr-07"></a>
## NFR-07 — Giới hạn tài nguyên

**Yêu cầu:** Giới hạn dung lượng, số trang, số mã đề và thời gian phải có cấu hình công bố trước thao tác. Đề xuất ban đầu: 50 MB/tệp, 100 trang/lần số hóa; giới hạn được duyệt lại qua mẫu thực tế.

**Cách nghiệm thu:** Thử tại giới hạn và vượt giới hạn; lỗi trước xử lý tốn tài nguyên, không để tác vụ treo vô hạn.

**Phạm vi truy vết:** UC-09–UC-11, UC-20–UC-21, UC-28.


<a id="nfr-08"></a>
## NFR-08 — Khả dụng

**Yêu cầu:** Mục tiêu đề xuất cho triển khai dùng chung: 99,5%/tháng, loại bảo trì đã thông báo; mất dịch vụ AI không làm mất chức năng soạn/lưu tay.

**Cách nghiệm thu:** Theo dõi từ điểm đo định trước; công bố thời gian bảo trì và số phút gián đoạn. Bản cài cá nhân cần thỏa thuận riêng.

**Phạm vi truy vết:** UC-07, UC-16, UC-28–UC-29.


<a id="nfr-09"></a>
## NFR-09 — Sao lưu và khôi phục

**Yêu cầu:** Mục tiêu đề xuất: RPO <=24 giờ, RTO <=4 giờ trên bộ dữ liệu nghiệm thu. Bản sao gồm dữ liệu và tài sản nhất quán, có mã kiểm tra và kiểm soát truy cập.

**Cách nghiệm thu:** Diễn tập phục hồi một bộ kho, đề, mã, kết quả và tài sản; so số lượng, mã kiểm tra và liên kết. Đo đến lúc dịch vụ dùng được sau phục hồi.

**Phạm vi truy vết:** UC-30.


<a id="nfr-10"></a>
## NFR-10 — Dễ sử dụng và tiếp cận

**Yêu cầu:** Nhãn, lỗi và thuật ngữ tiếng Việt nhất quán; thao tác chính dùng bàn phím; trạng thái không chỉ phân biệt bằng màu. Mục tiêu đề xuất: >=4/5 giáo viên hoàn thành luồng nhập–tạo–xuất sau hướng dẫn 15 phút.

**Cách nghiệm thu:** Thử người dùng với nhiệm vụ cố định; ghi thời gian và lỗi. Kiểm tra tiêu điểm, tương phản, tên điều khiển, đọc lỗi theo trường.

**Phạm vi truy vết:** UC-06–UC-23.


<a id="nfr-11"></a>
## NFR-11 — Đúng hiển thị toán và ấn phẩm

**Yêu cầu:** 100% mẫu toán/hình được duyệt phải hiển thị không mất ký tự, hình hay đáp án; không cắt nội dung ngoài trang. Tệp Unicode giữ dấu tiếng Việt.

**Cách nghiệm thu:** Bộ mẫu gồm phân số, căn, hệ, bảng, hình TikZ, ảnh nguồn và 4 dạng câu. Đối chiếu nguồn, xem trước, PDF và bản in A4; kiểm tra tách đề/đáp án.

**Phạm vi truy vết:** UC-10–UC-12, UC-16, UC-21.


<a id="nfr-12"></a>
## NFR-12 — Truy nguyên và quan sát

**Yêu cầu:** Tác vụ có mã tương quan, trạng thái, thời gian, người khởi tạo và lỗi có thể hành động. Câu số hóa truy tới tệp/trang/vùng; điểm truy tới bài/mã/hồ sơ chấm.

**Cách nghiệm thu:** Chọn mẫu từ ấn phẩm/kết quả quay về phiên bản câu và nguồn; thử log đã che thông tin nhạy cảm.

**Phạm vi truy vết:** UC-11–UC-12, UC-20–UC-24, UC-29.


<a id="nfr-13"></a>
## NFR-13 — Dữ liệu cá nhân và dịch vụ ngoài

**Yêu cầu:** Chỉ gửi vùng/nội dung tối thiểu cần thiết cho AI; thông tin học sinh không đi kèm khi không cần. Thời hạn giữ/xóa và phạm vi sao lưu phải được công bố trước vận hành.

**Cách nghiệm thu:** Kiểm tra nội dung yêu cầu gửi ngoài và chu kỳ xóa theo chính sách được duyệt. Chưa ấn định số ngày khi chưa có quyết định chủ dữ liệu.

**Phạm vi truy vết:** UC-11, UC-17, UC-22–UC-24, UC-28–UC-30.


<a id="nfr-14"></a>
## NFR-14 — Tương thích và xuất dữ liệu

**Yêu cầu:** Hỗ trợ rõ phiên bản mẫu nhập/xuất; từ chối định dạng chưa hỗ trợ với hướng dẫn chuyển đổi. Xuất bảng dữ liệu không biến nội dung câu thành công thức thực thi trong ứng dụng bảng tính.

**Cách nghiệm thu:** Thử PDF có chữ/scan, ảnh, Word và LaTeX theo danh mục công bố; thử tiếng Việt và chuỗi bắt đầu bằng ký hiệu công thức bảng tính. .doc cũ cần bộ chuyển đổi được kiểm chứng, không mặc định mọi tệp mở được.

**Phạm vi truy vết:** UC-09–UC-12, UC-21–UC-24.


<a id="nfr-15"></a>
## NFR-15 — Bảo trì và kiểm chứng

**Yêu cầu:** Yêu cầu có mã, quy tắc có phiên bản và ca nghiệm thu truy vết; thay hồ sơ không sửa ngầm đề/điểm cũ. Không ràng buộc framework hoặc máy chủ khi chưa có thiết kế triển khai.

**Cách nghiệm thu:** Rà soát ma trận truy vết, thay cấu hình và kiểm tra đề cũ; kiểm tra đủ sơ đồ theo mục tiêu nghiệp vụ.

**Phạm vi truy vết:** Toàn bộ bộ tài liệu.


<a id="nfr-16"></a>
## NFR-16 — An toàn xử lý nội dung nhập

**Yêu cầu:** Văn bản nguồn không được thực thi thành mã trong trình duyệt. LaTeX và tệp nhập phải xử lý trong môi trường bị giới hạn quyền, thời gian và tài nguyên; không được đọc tệp tùy ý ngoài phạm vi công việc.

**Cách nghiệm thu:** Thử nguồn chứa thẻ script, đường dẫn tài sản ngoài quyền, lệnh LaTeX yêu cầu thực thi và tệp vượt tài nguyên; từ chối hoặc vô hiệu hành vi, giữ nội dung hợp lệ.

**Phạm vi truy vết:** UC-07, UC-09–UC-12, UC-16–UC-17, UC-21.


## Ràng buộc cần chốt trước nghiệm thu sản phẩm

Chủ dự án và giáo viên duyệt tập mẫu chuyên môn, hồ sơ cấu trúc/chấm, dữ liệu thử tải, giới hạn tài nguyên, chính sách lưu trữ và tiêu chí thống kê. Người vận hành duyệt nhà cung cấp, năng lực phục hồi và ngưỡng quan sát. Không dùng báo cáo test cũ hoặc đặc tả này làm bằng chứng các NFR đã đạt.
