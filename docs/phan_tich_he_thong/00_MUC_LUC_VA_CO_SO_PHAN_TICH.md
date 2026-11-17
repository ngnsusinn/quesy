# Mục lục và cơ sở phân tích

> Quesy · Bản phân tích nghiệp vụ 1.0 · Ngày 17/11/2026
> Trạng thái: bản đặc tả đề xuất, không phải báo cáo chức năng đã triển khai.

## Cách đọc

Đây là bộ tài liệu phân tích **Quesy**, áp dụng phương pháp của 5 PDF trong `docs/pdf`. Các ví dụ bán hàng, ATM và thương mại điện tử trong PDF chỉ minh họa phương pháp. PDF không cung cấp đặc tả nghiệp vụ Quesy và không có hướng dẫn riêng đủ để coi mô hình lớp, Activity hoặc Sequence dưới đây là nội dung trích nguyên bản.

Phạm vi đã được người dùng xác nhận ngày 17/11/2026: giáo viên tự quản lý kho cá nhân; quản trị viên quản lý tài khoản, cấu hình và vận hành kỹ thuật. Bộ tài liệu được suy ra từ nhu cầu khảo thí, **không đọc mã nguồn, không lấy API, bảng dữ liệu hay trạng thái triển khai trong mã làm yêu cầu**. Việc xem cây thư mục và bản đồ nguồn chỉ để tuân thủ quy trình kho tài liệu.

| Tài liệu | Nội dung |
|---|---|
| [Mục lục và cơ sở phân tích](00_MUC_LUC_VA_CO_SO_PHAN_TICH.md) | Nguồn PDF, phương pháp, phạm vi và hướng dẫn PlantUML. |
| [Yêu cầu hệ thống và bài toán nghiệp vụ](01_YEU_CAU_HE_THONG.md) | Bài toán thực tế, quy trình đích, ranh giới, quy tắc và điểm cần chốt. |
| [Yêu cầu chức năng](02_YEU_CAU_CHUC_NANG.md) | 30 yêu cầu chức năng, đầu vào/đầu ra và tiêu chí chấp nhận. |
| [Yêu cầu phi chức năng](03_YEU_CAU_PHI_CHUC_NANG.md) | Yêu cầu chất lượng, ngưỡng đề xuất và phương pháp nghiệm thu. |
| [Các tác nhân của hệ thống](04_CAC_TAC_NHAN.md) | Vai trò, giới hạn quyền và hệ thống bên ngoài. |
| [Use Case người dùng](05_USE_CASE_NGUOI_DUNG.md) | 24 mục tiêu người dùng, gồm tài khoản chung và nghiệp vụ giáo viên. |
| [Use Case quản trị viên](06_USE_CASE_QUAN_TRI_VIEN.md) | 6 mục tiêu quản trị và các chức năng tài khoản dùng chung. |
| [Sơ đồ Use Case chi tiết](07_SO_DO_USE_CASE.md) | Tổng quan theo actor và một sơ đồ chi tiết cho mỗi Use Case. |
| [Mô tả Use Case từng chức năng](08_MO_TA_USE_CASE.md) | Tiền điều kiện, kích hoạt, luồng chính, thay thế, lỗi, hậu điều kiện. |
| [Sơ đồ hoạt động từng chức năng](09_SO_DO_HOAT_DONG.md) | 30 Activity Diagram tương ứng 30 Use Case. |
| [Sơ đồ lớp phân tích](10_SO_DO_LOP.md) | Mô hình miền khái niệm; thuộc tính, quan hệ, bội số và bất biến. |
| [Sơ đồ tuần tự từng chức năng](11_SO_DO_TUAN_TU.md) | 30 Sequence Diagram, các nhánh lỗi và trách nhiệm cộng tác. |
| [Truy vết và tiêu chí nghiệm thu tài liệu](12_TRUY_VET_VA_NGHIEM_THU.md) | Ma trận FR–UC–Activity–Sequence–lớp; tiêu chí kiểm tra tài liệu. |

## Nguồn và mức độ tin cậy

| Mã | PDF nguồn | Số trang vật lý | Phần áp dụng |
|---|---|---:|---|
| M01 | [E-Learning 1_Quy trinh nghiep vu.pdf](../pdf/E-Learning%201_Quy%20trinh%20nghiep%20vu.pdf) | 7 | tr. 1–3, 6–7: Xác định công việc, người chịu trách nhiệm, điều kiện và điểm nghẽn; không sao chép quy trình bán hàng sang khảo thí. |
| M02 | [E-Learning 2_Đánh giá hiện trạng_Yêu cầu phi chức năng.pdf](../pdf/E-Learning%202_Đánh%20giá%20hiện%20trạng_Yêu%20cầu%20phi%20chức%20năng.pdf) | 6 | tr. 1–2, 3–6: Tách hiện trạng đã khảo sát khỏi giả định; phân loại yêu cầu chức năng và thuộc tính chất lượng có cách đo. |
| M03 | [E-Learning 3_Sơ đồ luồng dữ liệu.pdf](../pdf/E-Learning%203_Sơ%20đồ%20luồng%20dữ%20liệu.pdf) | 13 | tr. 3–5, 10–13: Xác định ranh giới, tác nhân ngoài, dữ liệu vào/ra và phân rã; không dùng DFD thay cho Activity hoặc Sequence. |
| M04 | [E-Learning 4_Xây dựng sơ đồ Use Case.pdf](../pdf/E-Learning%204_Xây%20dựng%20sơ%20đồ%20Use%20Case.pdf) | 5 | tr. 1–5: Actor, ranh giới hệ thống, association, generalization, include, extend và cách tìm Use Case theo mục tiêu. |
| M05 | [E-Learning 5_Component Diagram Deployment Diagram.pdf](../pdf/E-Learning%205_Component%20Diagram%20Deployment%20Diagram.pdf) | 7 | tr. 1–5, 6–7: Phân chia trách nhiệm logic và phân biệt thành phần với nút triển khai; không suy ra số máy chủ Quesy từ ví dụ eCommerce. |

Phân biệt ba loại căn cứ trong yêu cầu: **BC** = bối cảnh Quesy do người dùng cung cấp trong hướng dẫn dự án; **XN** = phạm vi quản trị/người dùng đã được xác nhận trong trao đổi; **SL** = đề xuất suy luận để làm rõ nghiệp vụ, cần duyệt khi chuyển thành phạm vi triển khai. Một yêu cầu BC hoặc XN vẫn có chi tiết thiết kế đề xuất, được ràng buộc bởi các giả định tại tài liệu 01. M01–M05 là nguồn **phương pháp**, không được dùng để chứng thực rằng Quesy đã có các chức năng này.

Các tài liệu cũ đã được xem để nhận diện mâu thuẫn: tài liệu BRD/UC cũ có tổ trưởng, ban giám hiệu và học sinh thi trực tuyến, trong khi kế hoạch tập trung giáo viên cá nhân; các tài liệu có cả 3 và 4 mức nhận thức. Bộ mới sử dụng phạm vi người dùng đã chốt và hồ sơ cấu hình thay vì mặc định các mô tả cũ đều đúng. Chưa phỏng vấn giáo viên, chưa đo thời gian tác nghiệp và chưa khảo sát chất lượng OCR thực tế; những mô tả điểm nghẽn là giả thuyết cần kiểm chứng.

## Quy ước PlantUML

Mọi sơ đồ nằm trong khối `plantuml`, có `@startuml <tên_duy_nhất>` và `@enduml`. Có thể sao chép riêng khối vào tệp `.puml` và kết xuất cục bộ bằng PlantUML, hoặc dùng tiện ích Markdown hỗ trợ PlantUML. Trình xem Markdown thông thường có thể chỉ hiện mã; không mặc định GitHub sẽ hiển thị hình. Không cần gửi dữ liệu đề thi lên dịch vụ kết xuất công khai.

Use Case mô tả mục tiêu, Activity mô tả luồng nghiệp vụ và quyết định, Sequence mô tả thông điệp giữa các trách nhiệm logic. Lớp là khái niệm miền, không phải thiết kế ORM. Các vai trò cộng tác trong Sequence không là cam kết framework, giao thức, API hoặc sơ đồ triển khai vật lý. Quan hệ `include` luôn từ Use Case gọi đến Use Case bắt buộc được dùng; `extend` từ hành vi bổ sung đến Use Case nền, có điều kiện và điểm mở rộng.

## Quan hệ với tài liệu cũ

Bộ này là bản phân tích mới được đề xuất để rà soát phạm vi. Các đặc tả cũ vẫn giữ để đối chiếu lịch sử, không dùng để phủ định quyết định phạm vi đã xác nhận ở đây. Tài liệu hướng dẫn `ex_test` và báo cáo kiểm thử cũ vẫn là tài liệu chuyên biệt/lịch sử; không có tuyên bố rằng các thay đổi trong bộ này đã được lập trình hay kiểm thử hệ thống.
