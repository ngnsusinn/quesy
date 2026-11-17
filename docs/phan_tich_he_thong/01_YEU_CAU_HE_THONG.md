# Yêu cầu hệ thống và bài toán nghiệp vụ

> Quesy · Bản phân tích nghiệp vụ 1.0 · Ngày 17/11/2026
> Trạng thái: bản đặc tả đề xuất, không phải báo cáo chức năng đã triển khai.

## 1. Bài toán cần giải quyết

Đầu vào nghiệp vụ là đề thi và câu hỏi rời rạc từ PDF, ảnh, Word hoặc LaTeX. Giáo viên cần một kho có thể tìm lại theo kiến thức, lập đề đúng mục tiêu đánh giá, có nhiều mã đề nhưng vẫn cùng nội dung và chấm đúng mã. Đầu ra là kho đã hậu kiểm, ma trận, đề gốc, bộ mã, ấn phẩm và kết quả chấm có thể truy nguyên.

| Giả thuyết hiện trạng cần khảo sát | Hệ quả nghiệp vụ | Yêu cầu giải quyết | Dữ liệu cần thu khi khảo sát |
|---|---|---|---|
| Câu hỏi nằm trong nhiều tệp và thiếu nhãn thống nhất | Khó tìm lại, soạn lại nhiều lần | Cây kiến thức, kho có phiên bản, tìm và chống trùng | Số tệp, số câu trùng, thời gian tìm một câu |
| Công thức/hình phải chép và sửa thủ công | Dễ mất ký hiệu, thiếu hình hoặc đáp án | Số hóa hai lượt, lưu nguồn và hậu kiểm song song | Mẫu tài liệu theo định dạng, tỷ lệ câu cần sửa |
| Lập đề bằng lựa chọn thủ công khó cân đối | Sai phân bổ, thiếu câu ở một ô ma trận | Ma trận và kiểm tra khả thi trước sinh đề | Hồ sơ đề thực tế, số câu từng ô và lượng kho |
| Trộn không xét câu chùm và phương án neo | Đổi nghĩa câu, sai khóa đáp án | Hoán vị có kiểm chứng và bảng ánh xạ | Các ví dụ câu phụ thuộc vị trí/ngữ liệu |
| Chấm và thống kê qua nhiều bảng rời | Nhầm mã đề, sai thang điểm, khó truy vết | Kỳ chấm gắn đúng phiên bản và lịch sử sửa | Phiếu trả lời, rubric và ca điểm mẫu |

Không đưa số giờ tiết kiệm, độ chính xác tuyệt đối của AI hoặc số người dùng đồng thời vào kết luận hiện trạng khi chưa có số đo.

## 2. Mục tiêu và phạm vi

Mục tiêu G01: câu được tái sử dụng và truy về nguồn. G02: đề đúng đặc tả và bảo toàn khi hoán vị. G03: xuất bản, chấm và đối chiếu dùng cùng phiên bản. G04: mỗi giáo viên giữ quyền kiểm soát nội dung và dữ liệu riêng; quản trị vận hành có thể giám sát mà không cần mở kho riêng.

Trong phạm vi: tài khoản, danh mục riêng/chung, bốn dạng câu, nhập/xuất kho, số hóa AI và hậu kiểm, ma trận, sinh/soạn/thay/QA đề, trộn, xuất bản, danh sách lớp, chấm và phân tích, quản trị tài khoản/cấu hình/nhật ký/sao lưu. Nghiệp vụ OMR là cách nhập câu trả lời có hậu kiểm; chưa chốt thiết bị camera hay nhà cung cấp nhận dạng.

Ngoài phạm vi: học sinh đăng nhập làm bài trực tuyến, chống gian lận trình duyệt, LMS, thu học phí, quản trị trường nhiều cấp, hội đồng duyệt bắt buộc, chia sẻ công khai ngân hàng hoặc mua bán câu hỏi. Quyết định chuyên môn thuộc giáo viên; quản trị viên không thay vai tổ trưởng thẩm định.

## 3. Quy trình nghiệp vụ đích

1. Chuẩn bị tài khoản, cây kiến thức và hồ sơ đề/chấm.
2. Nhập câu thủ công, nhập dữ liệu có cấu trúc hoặc số hóa tài liệu; lưu nguồn.
3. Giáo viên hậu kiểm, xử lý tương đồng và xác nhận câu sẵn sàng.
4. Lập ma trận; kiểm tra lượng kho và phân bổ không dùng lặp câu.
5. Sinh hoặc biên soạn đề nháp; thay câu tương đương và duyệt đề xuất AI khi cần.
6. QA, giáo viên kiểm tra chuyên môn và chốt phiên bản; sinh bộ mã đã kiểm chứng.
7. Xuất riêng đề/đáp án/lời giải, gắn đúng phiên bản và mã đề.
8. Thu bài ngoài hệ thống; nhập, xác minh, chấm và phân tích trên đúng ánh xạ.

Khi thiếu kho, quay về bổ sung câu hoặc chỉnh ma trận. Khi QA lỗi, quay về bản nháp. Khi AI/biên dịch lỗi, giữ dữ liệu đã lưu và thử lại phần lỗi. Quản trị vận hành hỗ trợ xuyên suốt, không là bước duyệt nội dung.

## 4. Quy tắc nghiệp vụ dùng chung

### BR-01 — Tách quyền và không gian

Giáo viên chỉ thao tác dữ liệu trong không gian được cấp. Quản trị viên có quyền vận hành, không mặc nhiên có quyền đọc kho riêng. Đăng ký không cấp vai trò quản trị. Quyền được kiểm tra cho từng đối tượng và liên kết tải.

### BR-02 — Ghim phiên bản và chống ghi đè

Câu hỏi, danh mục, ma trận, đề, hồ sơ chấm và ấn phẩm có phiên bản. Đề giữ bản chụp câu; sửa ngân hàng không đổi đề cũ. Cập nhật cần đối chiếu phiên bản kỳ vọng. Sửa đề sau QA tạo phiên bản mới và cần QA lại.

### BR-03 — Cây kiến thức và mức nhận thức

Phân loại bằng môn, khối, nhánh kiến thức (chương/chủ đề, bài), yêu cầu cần đạt, dạng bài; dạng câu hỏi và mức nhận thức là chiều độc lập. Cây cá nhân tách danh mục chung. Không buộc tổ chức theo bộ sách. Hồ sơ mặc định dùng NB/TH/VD; VDC chỉ khi hồ sơ nghiệp vụ được duyệt quy định, không tự coi là yêu cầu pháp lý.

### BR-04 — Điều kiện câu sẵn sàng

MCQ có đúng 4 phương án và đúng 1 khóa; Đúng/Sai có đúng 4 ý với giá trị đúng/sai cho từng ý; trả lời ngắn có đáp án và quy tắc chuẩn hóa; tự luận có hướng dẫn chấm. Công thức, hình và lời giải cần đủ để hậu kiểm. Câu chưa đạt chỉ lưu nháp, không dùng sinh đề.

### BR-05 — Tương đồng không đồng nghĩa trùng tuyệt đối

Phát hiện tương đồng phục vụ cảnh báo và đối chiếu. Không tự xóa hoặc gộp câu theo tỷ lệ chưa được hiệu chuẩn. Giáo viên xác nhận quyết định; lưu lý do khi giữ các câu tương đồng.

### BR-06 — Ngừng dùng và tồn kho

Câu ngừng dùng không là ứng viên sinh đề mới. Đề cũ vẫn giữ bản chụp. Tồn kho chỉ tính câu sẵn sàng, đúng quyền, đúng cấu hình loại trừ và không dùng lặp một câu trong đề.

### BR-07 — Gửi lại an toàn và tác vụ

Lô nhập, xác nhận hậu kiểm, sinh đề, trộn và xuất bản dùng định danh yêu cầu để tránh tạo kết quả lặp. Thử lại chỉ xử lý phần chưa thành công. Trạng thái tác vụ: chờ, đang chạy, hoàn tất, hoàn tất một phần, lỗi, đã hủy; chuyển trạng thái được kiểm soát.

### BR-08 — AI và hai lượt số hóa

Pass 1 xử lý bố cục, vùng câu/hình, cắt và cải thiện ảnh. Pass 2 trích ngữ nghĩa, chuẩn hóa toán về LaTeX nội dòng `$...$` hoặc khối `$$...$$`, gợi ý nhãn và đối chiếu tương đồng. Lưu trang/vùng nguồn. Kết quả AI là nháp; giáo viên chịu trách nhiệm xác nhận. Không có số liệu độ chính xác AI được chứng minh trong bộ PDF.

### BR-09 — Ma trận phải khả thi toàn cục

Ô xác định bằng kiến thức × dạng × mức nhận thức × phần, có số câu và điểm. Ngoài đếm theo ô phải kiểm tra phân bổ toàn cục vì các ô có thể chung ứng viên. Khi thiếu, trả tọa độ đầy đủ và cần/có/thiếu; không tạo đề một phần được ghi nhận như đề đạt.

### BR-10 — Bất biến đề và ánh xạ

Mọi mã đề là song ánh với tập câu/bản chụp đề gốc; không vượt ranh giới phần; giữ nhóm dùng ngữ liệu; xử lý an toàn phương án phụ thuộc vị trí; ánh xạ chính xác khóa MCQ và từng ý Đúng/Sai. Không buộc mọi phương án neo ở D nếu việc chuyển vị trí làm đổi nghĩa. Không xử lý an toàn được thì giữ thứ tự hoặc chặn thao tác. Đáp án và chấm điểm luôn tra đúng mã đề.

### BR-11 — Con người quyết định nội dung

Copilot chỉ đề xuất; áp dụng sau chấp thuận và đối chiếu phiên bản. Thay câu phải giữ ô ma trận, điểm, nhóm và không trùng. QA kiểm tra cấu trúc và cảnh báo; QA tự động không chứng minh tính đúng đắn chuyên môn.

### BR-12 — Xuất bản và công thức

PDF/LaTeX dùng cấu trúc ex_test: ex, choice có True, choiceTF, shortans, loigiai; hỗ trợ hình TikZ hoặc tài sản hợp lệ. Tách đề học sinh khỏi đáp án/lời giải. Chỉ công bố gói đầy đủ sau kiểm tra. Không cam kết hình cắt từ nguồn sẽ trở thành vector. 4 dạng câu được hỗ trợ; số phần cụ thể theo hồ sơ đề, không ép mọi kỳ thi có đúng 3 phần.

### BR-13 — Điểm theo hồ sơ được ghim

MCQ: đúng nhận điểm cấu hình (mặc định đề xuất 0,25), sai/bỏ trống nhận 0. Đúng/Sai: số ý khớp 0/1/2/3/4 tương ứng 0/0,1/0,25/0,5/1,0 điểm. Trả lời ngắn chuẩn hóa dấu phẩy/chấm trong số thập phân theo định dạng được chọn; điểm đúng theo hồ sơ, không tự dùng dung sai. Tự luận do giáo viên chấm theo rubric. Dùng tính toán thập phân và làm tròn ở điểm tổng theo hồ sơ.

### BR-14 — Giảm dữ liệu nhạy cảm

Chỉ thu dữ liệu học sinh cần cho chấm; học sinh không là actor đăng nhập. Nhật ký che nội dung đề, khóa dịch vụ, mật khẩu và dữ liệu cá nhân không cần thiết. Chỉ gửi dữ liệu tối thiểu tới dịch vụ ngoài theo chính sách đã chọn. Sao lưu cũng phải bảo vệ như dữ liệu hoạt động.

### BR-15 — Diễn giải thống kê có điều kiện

MCQ: p=R/N, N là số bài hợp lệ trong tập đã công bố, bài bỏ trống tính sai. D=p_nhóm_cao-p_nhóm_thấp; đề xuất chọn mỗi nhóm ceil(0,27N), xếp theo tổng điểm giảm dần, hòa điểm theo mã học sinh, không chồng nhóm; nếu không lập được hai nhóm thì không tính. Công bố N, cách loại mẫu và số người mỗi nhóm. Không áp dụng p nhị phân cho mọi dạng câu; chỉ số không tự kết luận câu sai.

### BR-16 — Thay đổi vận hành có kiểm soát

Thay quyền, cấu hình, danh mục, hồ sơ chấm và phục hồi phải ghi ai/lúc nào/đối tượng/lý do/kết quả. Chặn vô hiệu quản trị viên hoạt động cuối cùng. Cấu hình mới phải qua dữ liệu mẫu, giữ bản trước. Phục hồi kiểm tra ở vùng riêng, có điểm quay lui trước khi chuyển hoạt động.

## 5. Yêu cầu tổng hợp và ưu tiên

| Nhóm | Phạm vi | Ưu tiên đề xuất |
|---|---|---|
| Kho và số hóa | UC-05–UC-12 | Cốt lõi, nhập bảng/xuất kho là bổ sung |
| Ma trận và đề | UC-13–UC-21 | Cốt lõi; AI hỗ trợ có thể triển khai sau luồng thủ công |
| Chấm và phân tích | UC-22–UC-24 | Sau khi chốt quy tắc đề và điểm; OMR cần đánh giá mẫu |
| Tài khoản và vận hành | UC-01–UC-04, UC-25–UC-30 | Quyền dữ liệu và sao lưu là điều kiện vận hành |

Chi tiết chức năng ở [Yêu cầu chức năng](02_YEU_CAU_CHUC_NANG.md); ràng buộc chất lượng ở [Yêu cầu phi chức năng](03_YEU_CAU_PHI_CHUC_NANG.md). Mã ưu tiên này phục vụ thảo luận kế hoạch, chưa là cam kết tiến độ.

## 6. Giả định và quyết định còn cần duyệt

| Mã | Nội dung | Cách xử lý trong bản này |
|---|---|---|
| AS-01 | Hai vai trò giáo viên và quản trị kỹ thuật đã được xác nhận; chưa có quản trị trường | Hai miền quyền tách biệt; tài khoản cá nhân có thể được cấp cả hai vai trò bằng quyết định rõ ràng |
| AS-02 | Cơ chế tự đăng ký hay cấp tài khoản chưa chốt | UC-01 theo chính sách mở/đóng; không đưa email xác minh hay OAuth vào yêu cầu bắt buộc |
| AS-03 | Cấu trúc đề, mức nhận thức, cách làm tròn và giới hạn tệp chưa có hồ sơ đã duyệt | Dùng hồ sơ có phiên bản; ví dụ thang điểm là quy tắc được cung cấp, không phải xác nhận văn bản pháp lý hiện hành |
| AS-04 | Chưa chốt nhà cung cấp AI, nơi lưu dữ liệu, thời hạn giữ nguồn/nhật ký/sao lưu | Chỉ đặc tả năng lực và giới hạn; quản trị công bố chính sách trước vận hành |
| AS-05 | OMR, lớp học và CTT được suy ra từ bối cảnh kế hoạch, chưa được khảo sát thực địa | UC-22–UC-24 là phạm vi phân tích đề xuất; có luồng nhập tay, không phụ thuộc OMR để chấm |
| AS-06 | Ngưỡng hiệu năng và dung lượng chưa đo | Mọi ngưỡng số trong NFR là mục tiêu đề xuất với điều kiện đo công bố, cần duyệt trước nghiệm thu sản phẩm |
| AS-07 | Định dạng trả lời ngắn, số hợp lệ và dung sai cần chốt theo môn | Mặc định so số sau chuẩn hóa dấu thập phân, không suy đoán chuỗi mơ hồ hoặc thêm dung sai |
| AS-08 | Chưa có khảo sát người dùng chứng minh các giả thuyết hiện trạng | Thực hiện phỏng vấn và dùng bộ tài liệu này làm đầu vào thẩm định, không nhận là kết quả khảo sát |

## 7. Kết quả phân tích cần bàn giao

30 chức năng có cùng mã truy vết sang 30 Use Case, 30 Activity và 30 Sequence; một mô hình lớp khái niệm theo các miền tài khoản, nội dung, đề, chấm và vận hành. Phần mô tả nêu cả thành công, lỗi và dữ liệu không được thay đổi khi thất bại. Đây là đầu vào cho thiết kế/triển khai sau khi duyệt, không suy ra từ cấu trúc phần mềm hiện tại.
