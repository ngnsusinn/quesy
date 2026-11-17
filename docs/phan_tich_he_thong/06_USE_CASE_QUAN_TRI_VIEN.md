# Use Case quản trị viên

> Quesy · Bản phân tích nghiệp vụ 1.0 · Ngày 17/11/2026
> Trạng thái: bản đặc tả đề xuất, không phải báo cáo chức năng đã triển khai.

## Phạm vi quản trị đã xác nhận

Quản trị viên là vai trò kỹ thuật hỗ trợ giáo viên. Quản trị không bao gồm duyệt chuyên môn bắt buộc, sửa kho riêng, đại diện ban giám hiệu hoặc điều phối thi trực tuyến. Các chi tiết danh mục chung, hồ sơ và sao lưu là đề xuất phân tích để làm rõ vận hành, cần duyệt trước triển khai.

| Mã | Mục tiêu | Tác nhân chính | Nhóm | Căn cứ |
|---|---|---|---|---|
| [UC-25](08_MO_TA_USE_CASE.md#uc-25) | Quản lý tài khoản và quyền truy cập | Quản trị viên kỹ thuật | Quản trị | XN |
| [UC-26](08_MO_TA_USE_CASE.md#uc-26) | Quản lý danh mục kiến thức dùng chung | Quản trị viên kỹ thuật | Quản trị | SL |
| [UC-27](08_MO_TA_USE_CASE.md#uc-27) | Quản lý hồ sơ đề và quy tắc chấm | Quản trị viên kỹ thuật | Quản trị | SL |
| [UC-28](08_MO_TA_USE_CASE.md#uc-28) | Cấu hình dịch vụ AI và biên dịch | Quản trị viên kỹ thuật | Quản trị | XN |
| [UC-29](08_MO_TA_USE_CASE.md#uc-29) | Giám sát tác vụ, nhật ký và xử lý lỗi | Quản trị viên kỹ thuật | Quản trị | XN |
| [UC-30](08_MO_TA_USE_CASE.md#uc-30) | Sao lưu và khôi phục hệ thống | Quản trị viên kỹ thuật | Quản trị | SL |

## Tài khoản dùng chung

Quản trị viên đăng nhập qua UC-02 khi đang là khách, sau đó dùng UC-03 đăng xuất và UC-04 cập nhật hồ sơ chính chủ. Quyền quản trị phải được cấp rõ ràng trong UC-25; đăng ký UC-01 chỉ tạo tài khoản giáo viên.

## Kịch bản vận hành

1. Cấp quyền và trạng thái tài khoản bằng UC-25; kiểm tra quản trị viên hoạt động cuối cùng.
2. Chuẩn bị danh mục/hồ sơ chung bằng UC-26–UC-27, kiểm tra tác động rồi công bố phiên bản.
3. Thử dịch vụ bằng dữ liệu mẫu qua UC-28, kích hoạt sau khi thử thành công; giữ cấu hình trước để quay lui.
4. Theo dõi UC-29, thử lại phần lỗi có kiểm soát; không mở dữ liệu đề riêng để xem nhật ký.
5. Tạo bản sao và diễn tập khôi phục bằng UC-30; chỉ chuyển sau kiểm tra và xác nhận trong cửa sổ bảo trì.

Các bước xác minh và xác nhận trong UC-25/UC-28/UC-30 là yêu cầu của **sản phẩm được đặc tả** cho thao tác vận hành nhạy cảm; không phải yêu cầu người dùng phê duyệt việc viết tài liệu này.
