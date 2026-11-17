# Sơ đồ lớp phân tích

> Quesy · Bản phân tích nghiệp vụ 1.0 · Ngày 17/11/2026
> Trạng thái: bản đặc tả đề xuất, không phải báo cáo chức năng đã triển khai.

## Mục đích và mức trừu tượng

Đây là **Class Diagram phân tích miền nghiệp vụ**, suy ra từ dữ liệu và quy tắc trong các Use Case. Không phải sơ đồ bảng dữ liệu hay bản sao lớp trong mã. Thuộc tính kiểu `Chuoi`, `NoiDung`, `CauTruc` là kiểu khái niệm; chỉ thể hiện thông tin cần tồn tại, chưa quy định công nghệ lưu trữ. Các phương thức biểu diễn trách nhiệm nghiệp vụ tiêu biểu.

Đường có bội số chỉ quan hệ có thể kiểm tra; hình thoi đặc là vòng đời thành phần thuộc toàn thể, không là lệnh xóa vật lý. Chính sách lưu phiên bản và tham chiếu lịch sử vẫn áp dụng. Mỗi sơ đồ tự chứa các lớp tham chiếu để đọc độc lập; lớp lặp tên là cùng khái niệm, không là thực thể thứ hai.

## Bất biến mô hình

| Mã | Ràng buộc |
|---|---|
| CL-01 | Một không gian có một tài khoản sở hữu; quyền quản trị không tạo quan hệ sở hữu kho khác. Tài khoản có thể có cả hai vai trò nhưng quyền được xét theo phạm vi. |
| CL-02 | Cây không có chu trình; mã con duy nhất theo phạm vi/phiên bản đã quy định. Khối và môn là hai chiều gốc liên quan, nhánh kiến thức nằm dưới tổ hợp môn–khối; không bắt buộc bảy cấp vật lý cố định. |
| CL-03 | Phiên bản câu sẵn sàng thỏa BR-04; 0..4 phương án/ý trong sơ đồ chỉ là biên tổng quát, ràng buộc đúng 4 áp dụng theo dạng. Mức nhận thức và dạng câu không là hai cấp con bắt buộc trong cây. |
| CL-04 | Câu số hóa có trang/vùng và tài liệu nguồn; câu nhập tay có thể không có vùng nguồn. Một câu kéo qua nhiều trang được gắn nhiều vùng. |
| CL-05 | Một phiên bản đề ghim hồ sơ và giữ bản chụp từng mục. Thay nhãn, hình hoặc đáp án ở kho không sửa bản chụp cũ. Đề soạn tay có thể chưa liên kết ma trận. |
| CL-06 | Mỗi mã đề chứa song ánh tới toàn bộ mục đề gốc; ràng buộc duy nhất vị trí trong phần và thứ tự nhóm được kiểm chứng trước lưu. Hồ sơ chấm và khóa tương ứng đúng phiên bản. |
| CL-07 | Chấm đề gốc không trộn dùng mã tham chiếu gốc và ánh xạ đồng nhất, tránh hai cách diễn giải khóa khác nhau. Mỗi điểm thành phần tham chiếu đúng câu theo mã. |
| CL-08 | Nghiệp vụ chấm lại thêm phiên bản kết quả; báo cáo phân tích chọn rõ phiên bản, không đếm hai lần cùng một bài. |
| CL-09 | Tác vụ, cấu hình và bản sao có nguồn/phạm vi, trạng thái và nhật ký. Thử lại cùng khóa không tạo bản ghi nghiệp vụ lặp. |

## Tổng quan các miền nghiệp vụ

```plantuml
@startuml CLASS_OVERVIEW
skinparam defaultFontName Segoe UI
skinparam shadowing false
skinparam defaultFontSize 13
title Tổng quan các miền nghiệp vụ
left to right direction
package "Danh tính và quyền" {
  class TaiKhoan
  class KhongGian
}
package "Nội dung và nguồn" {
  class PhienBanCauHoi
  class VungNguon
}
package "Đặc tả và đề" {
  class PhienBanMaTran
  class PhienBanDe
  class MaDe
  class AnPham
}
package "Chấm và phân tích" {
  class KyCham
  class KetQuaCham
}
package "Vận hành" {
  class TacVu
  class NhatKy
}
TaiKhoan "1" -- "0..*" KhongGian : sở hữu
KhongGian "1" -- "0..*" PhienBanCauHoi : phạm vi
PhienBanCauHoi "0..*" -- "0..*" VungNguon : truy nguyên
PhienBanMaTran "0..1" -- "0..*" PhienBanDe : căn cứ sinh
PhienBanDe "1" -- "0..*" MaDe : bảo toàn nội dung
PhienBanDe "1" -- "0..*" AnPham : nguồn
PhienBanDe "1" -- "0..*" KyCham : đề dùng chấm
KyCham "1" -- "0..*" KetQuaCham : kết quả
TaiKhoan "1" -- "0..*" TacVu : khởi tạo
TaiKhoan "0..1" -- "0..*" NhatKy : chủ thể
PhienBanDe ..> PhienBanCauHoi : tạo bản chụp
KetQuaCham ..> MaDe : dùng đúng ánh xạ
@enduml
```


## Danh tính, cấu hình và vận hành

```plantuml
@startuml CLASS_IDENTITY_OPS
skinparam defaultFontName Segoe UI
skinparam shadowing false
skinparam defaultFontSize 13
title Danh tính, cấu hình và vận hành
left to right direction
class TaiKhoan {
  ma: DinhDanh
  dinhDanhDangNhap: Chuoi
  tenHienThi: Chuoi
  thongTinXacThucDuocBaoVe: Chuoi
  trangThai: TrangThaiTaiKhoan
  phienBan: SoNguyen
  +doiHoSo()
  +khoaTaiKhoan()
}
class VaiTro {
  ma: Chuoi
  ten: Chuoi
  phamViQuyen: TapQuyen
}
class PhienDangNhap {
  ma: DinhDanh
  hetHanLuc: ThoiDiem
  thuHoiLuc: ThoiDiem [0..1]
  +thuHoi()
}
class KhongGian {
  ma: DinhDanh
  ten: Chuoi
  trangThai: Chuoi
}
class CauHinhDichVu {
  ma: DinhDanh
  phienBan: SoNguyen
  loai: AI_HOAC_BIEN_DICH
  thamChieuBiMat: Chuoi
  gioiHan: CauHinhGioiHan
  chinhSachDuLieu: Chuoi
  trangThai: NHAP_HOAC_HOAT_DONG
  +thuKetNoi()
  +kichHoat()
}
class TacVu {
  ma: DinhDanh
  loai: Chuoi
  khoaChongLap: Chuoi
  trangThai: TrangThaiTacVu
  tienDo: SoThuc
  +huyNeuDuocPhep()
  +thuLaiPhanLoi()
}
class LanChay {
  soLan: SoNguyen
  batDauLuc: ThoiDiem
  ketThucLuc: ThoiDiem [0..1]
  phamViXuLy: Chuoi
  loiDaChe: Chuoi [0..1]
}
class NhatKy {
  ma: DinhDanh
  luc: ThoiDiem
  hanhDong: Chuoi
  doiTuong: ThamChieu
  lyDo: Chuoi
  ketQua: Chuoi
}
class BanSaoLuu {
  ma: DinhDanh
  lucChup: ThoiDiem
  danhMucDuLieuTaiSan: DanhMuc
  maKiemTra: Chuoi
  trangThaiKiemTra: Chuoi
  thamChieuBanSao: Chuoi
  diemQuayLui: ThamChieu [0..1]
  +doiSoat()
}
TaiKhoan "0..*" -- "1..*" VaiTro : được cấp
TaiKhoan "1" -- "0..*" PhienDangNhap : có
TaiKhoan "1" -- "0..*" KhongGian : sở hữu
TaiKhoan "1" -- "0..*" TacVu : khởi tạo
KhongGian "0..1" -- "0..*" TacVu : phạm vi riêng hoặc toàn hệ thống
TacVu "0..*" -- "0..1" CauHinhDichVu : ghim cấu hình ngoài nếu dùng
TacVu "1" *-- "0..*" LanChay : lịch sử chạy
TaiKhoan "0..1" -- "0..*" NhatKy : chủ thể; có thể là hệ thống
TacVu "0..1" -- "0..*" NhatKy : phát sinh
TaiKhoan "1" -- "0..*" BanSaoLuu : yêu cầu theo quyền
note bottom of VaiTro
  Giáo viên và quản trị là vai trò được cấp,
  không là hai lớp tài khoản kế thừa nhau.
end note
note bottom of BanSaoLuu
  Chứa cả dữ liệu và tài sản đã bảo vệ.
  Mã kiểm tra đúng chưa thay kiểm tra khả năng dùng.
end note
@enduml
```


## Kiến thức, câu hỏi và nguồn số hóa

```plantuml
@startuml CLASS_CONTENT
skinparam defaultFontName Segoe UI
skinparam shadowing false
skinparam defaultFontSize 13
title Kiến thức, câu hỏi và nguồn số hóa
left to right direction
class PhienBanDanhMuc {
  ma: DinhDanh
  soPhienBan: SoNguyen
  phamVi: CHUNG_HOAC_CA_NHAN
  nguonThamChieu: Chuoi
  trangThai: Chuoi
}
class NutKienThuc {
  ma: DinhDanh
  loaiCap: MON_KHOI_NHANH_BAI_YCCD_DANG
  maNghiepVu: Chuoi
  ten: Chuoi
  dangDung: Boolean
}
class CauHoi {
  ma: DinhDanh
  trangThaiSuDung: DANG_DUNG_HOAC_NGUNG
}
class PhienBanCauHoi {
  ma: DinhDanh
  soPhienBan: SoNguyen
  dang: MCQ_DS_NGAN_TULUAN
  mucNhanThuc: Chuoi
  deBai: NoiDungToan
  dapAnNgan: Chuoi [0..1]
  huongDanCham: NoiDung [0..1]
  loiGiai: NoiDung
  trangThai: NHAP_HOAC_SAN_SANG
  +kiemTraCauTruc()
}
class PhuongAn {
  maOnDinh: DinhDanh
  noiDung: NoiDungToan
  laDapAn: Boolean
  rangBuocViTri: Chuoi [0..1]
}
class MenhDe {
  maOnDinh: DinhDanh
  noiDung: NoiDungToan
  giaTriDung: Boolean
  rangBuocViTri: Chuoi [0..1]
}
class NhomNguLieu {
  ma: DinhDanh
  noiDungChung: NoiDung
  rangBuocThuTu: Chuoi
}
class TaiLieuNguon {
  ma: DinhDanh
  ten: Chuoi
  dinhDang: Chuoi
  maKiemTra: Chuoi
  thamChieuTep: Chuoi
}
class VungNguon {
  ma: DinhDanh
  soTrang: SoNguyen
  toaDoVung: HopBao
  heToaDo: Chuoi
}
class TaiSan {
  ma: DinhDanh
  loai: ANH_HOAC_TIKZ
  thamChieu: Chuoi
  maKiemTra: Chuoi
}
class BanTrichXuat {
  ma: DinhDanh
  noiDungGoiY: NoiDung
  canhBao: TapCanhBao
  trangThai: NHAP_XAC_NHAN_BO_QUA
  khoaNhap: Chuoi
}
class KetQuaTuongDong {
  ma: DinhDanh
  diemGoiY: SoThuc
  quyetDinh: Chuoi [0..1]
  lyDo: Chuoi [0..1]
}
class LoNhap {
  ma: DinhDanh
  mauDuLieu: Chuoi
  khoaChongLap: Chuoi
}
class DongNhap {
  soDong: SoNguyen
  trangThai: Chuoi
  loiTheoTruong: Chuoi [0..1]
}
class KhongGian
class TacVu
KhongGian "0..1" -- "0..*" PhienBanDanhMuc : rỗng khi danh mục chung
PhienBanDanhMuc "1" *-- "1..*" NutKienThuc
NutKienThuc "0..1 cha" -- "0..* con" NutKienThuc : cây không chu trình
KhongGian "1" -- "0..*" CauHoi
CauHoi "1" *-- "1..*" PhienBanCauHoi
PhienBanCauHoi "0..*" -- "0..*" NutKienThuc : nhãn kiến thức đã ghim; bắt buộc khi sẵn sàng
PhienBanCauHoi "1" *-- "0..4" PhuongAn
PhienBanCauHoi "1" *-- "0..4" MenhDe
NhomNguLieu "0..1" -- "1..*" PhienBanCauHoi : thuộc nhóm
PhienBanCauHoi "0..*" -- "0..*" TaiSan : dùng
KhongGian "1" -- "0..*" TaiLieuNguon
TaiLieuNguon "1" *-- "0..*" VungNguon
VungNguon "0..1" -- "0..*" TaiSan : cắt từ nguồn nếu có
TaiLieuNguon "1" -- "0..*" BanTrichXuat
BanTrichXuat "0..*" -- "1..*" VungNguon : gồm vùng nối trang nếu cần
TacVu "1" -- "0..*" BanTrichXuat : tạo
BanTrichXuat "0..1" -- "0..1" PhienBanCauHoi : kết quả nhập xác nhận
PhienBanCauHoi "0..*" -- "0..*" VungNguon : truy nguyên
KetQuaTuongDong "0..*" --> "1" PhienBanCauHoi : câu ứng viên trong kho
BanTrichXuat "0..1" -- "0..*" KetQuaTuongDong : cảnh báo số hóa
PhienBanCauHoi "0..1" -- "0..*" KetQuaTuongDong : câu đang đối chiếu khi lưu tay
LoNhap "1" *-- "1..*" DongNhap
DongNhap "0..1" -- "0..1" PhienBanCauHoi : kết quả nhập theo dòng
note bottom of PhienBanCauHoi
  MCQ: đúng 4 PhuongAn, đúng 1 khóa.
  Đúng/Sai: đúng 4 MenhDe, mỗi ý có khóa.
  Hai dạng còn lại không có lựa chọn/ý.
  Câu thiếu nhãn/lời giải chỉ là nháp.
end note
note bottom of KetQuaTuongDong
  Nguồn đối chiếu là bản trích xuất HOẶC
  phiên bản câu đang lưu; đúng một nguồn.
end note
@enduml
```


## Ma trận, phiên bản đề và ánh xạ mã đề

```plantuml
@startuml CLASS_EXAMS
skinparam defaultFontName Segoe UI
skinparam shadowing false
skinparam defaultFontSize 13
title Ma trận, phiên bản đề và ánh xạ mã đề
left to right direction
class KhongGian
class NutKienThuc
class MaTran {
  ma: DinhDanh
  ten: Chuoi
}
class PhienBanMaTran {
  ma: DinhDanh
  soPhienBan: SoNguyen
  trangThai: NHAP_HOAC_CHOT
  +tinhTong()
}
class OMaTran {
  ma: DinhDanh
  phanThi: Chuoi
  dangCau: Chuoi
  mucNhanThuc: Chuoi
  soCau: SoNguyen
  diemTheoHoSo: ThapPhan
}
class BaoCaoThieu {
  lucKiemTra: ThoiDiem
  toaDoO: TapToaDo
  canCoThieu: TapSoLuong
  xungDotToanCuc: Chuoi [0..1]
}
class HoSoDe {
  maPhienBan: DinhDanh
  cacPhanVaDang: CauTruc
  mucNhanThucChoPhep: TapMuc
  thoiLuong: SoNguyen
  tongDiem: ThapPhan
}
class HoSoCham {
  maPhienBan: DinhDanh
  diemMCQ: ThapPhan
  thangDungSai: BangDiem
  diemTraLoiNgan: ThapPhan
  quyTacChuanHoa: Chuoi
  rubricTuLuan: NoiDung
  quyTacLamTron: Chuoi
}
class DeGoc {
  ma: DinhDanh
  ten: Chuoi
}
class PhienBanDe {
  ma: DinhDanh
  soPhienBan: SoNguyen
  trangThai: NHAP_HOAC_CHOT
  dauDe: NoiDung
  +kiemDinh()
  +chot()
}
class MucDe {
  ma: DinhDanh
  phan: Chuoi
  thuTu: SoNguyen
  diem: ThapPhan
  nhomNguLieuDaChup: DinhDanh [0..1]
}
class BanChupCauHoi {
  ma: DinhDanh
  noiDungVaKhoa: NoiDung
  nhanVaRangBuoc: CauTruc
  nguonPhienBan: DinhDanh [0..1]
  maKiemTra: Chuoi
}
class PhienBanCauHoi
class BaoCaoQA {
  ma: DinhDanh
  loiTheoCau: TapLoi
  canhBao: TapCanhBao
  xacNhanChuyenMon: Chuoi [0..1]
  +coLoiChan(): Boolean
}
class DeXuatAI {
  ma: DinhDanh
  phamVi: Chuoi
  noiDungTruocSau: NoiDung
  quyetDinh: CHO_DUYET_DUYET_TU_CHOI
}
class MaDe {
  ma: DinhDanh
  kyHieu: Chuoi
  cauHinhTron: CauTruc
  trangThaiKiemChung: Chuoi
}
class AnhXaCau {
  viTriMoi: SoNguyen
  phan: Chuoi
  khoaDapAnMoi: CauTruc
}
class AnhXaLuaChon {
  loai: PHUONG_AN_HOAC_MENH_DE
  maNoiDungGoc: DinhDanh
  nhanHienThiMoi: Chuoi
  giaTriKhoa: Chuoi
}
class AnPham {
  ma: DinhDanh
  loai: DE_DAPAN_LOIGIAI_PHIEU_GOI
  dinhDang: PDF_LATEX_BANG_ZIP
  danhMucThanhPhan: DanhMuc
  trangThai: NHAP_HOAC_HOAN_TAT
  thamChieuTep: Chuoi
  maKiemTra: Chuoi
}
KhongGian "1" -- "0..*" MaTran
MaTran "1" *-- "1..*" PhienBanMaTran
PhienBanMaTran "1" *-- "1..*" OMaTran
OMaTran "0..*" -- "1..*" NutKienThuc : tọa độ kiến thức
PhienBanMaTran "0..*" --> "1" HoSoDe : ghim
HoSoDe "0..*" --> "1" HoSoCham : ghim quy tắc
PhienBanMaTran "1" -- "0..*" BaoCaoThieu
KhongGian "1" -- "0..*" DeGoc
DeGoc "1" *-- "1..*" PhienBanDe
PhienBanDe "0..*" --> "0..1" PhienBanMaTran : nguồn nếu sinh từ ma trận
PhienBanDe "0..*" --> "1" HoSoDe : ghim
PhienBanDe "1" *-- "0..*" MucDe
MucDe "0..*" --> "0..1" OMaTran : ô đích nếu có
MucDe "1" *-- "1" BanChupCauHoi
BanChupCauHoi "0..*" --> "0..1" PhienBanCauHoi : nguồn kho nếu có
PhienBanDe "1" -- "0..*" BaoCaoQA : đúng phiên bản
PhienBanDe "1" -- "0..*" DeXuatAI : phiên bản nền
PhienBanDe "1" -- "0..*" MaDe
MaDe "1" *-- "1..*" AnhXaCau
AnhXaCau "0..*" --> "1" MucDe : câu gốc duy nhất
AnhXaCau "1" *-- "0..4" AnhXaLuaChon
PhienBanDe "0..1" -- "0..*" AnPham : đề hoặc bộ mã
AnPham "0..*" -- "0..*" MaDe : mã thuộc gói
AnPham "0..*" -- "0..*" PhienBanCauHoi : tập câu nếu xuất kho
note bottom of AnPham
  Nguồn ấn phẩm là tập phiên bản câu HOẶC
  đúng một phiên bản đề (có thể kèm mã đề).
  Chỉ bản hoàn tất mới được công bố.
end note
note bottom of AnhXaCau
  Trong mỗi MaDe, mỗi MucDe xuất hiện đúng 1 lần.
  ViTriMoi duy nhất trong phần; giữ nhóm/ngữ liệu.
  MCQ/Đúng-Sai: 4 ánh xạ con; dạng khác: 0.
end note
note bottom of MucDe
  Đề nháp có thể rỗng; đề chốt phải có đủ mục.
  Bản chụp chứa cả ngữ liệu, hình và khóa;
  không phụ thuộc việc sửa hoặc ngừng dùng câu kho.
end note
@enduml
```


## Lớp, bài làm, điểm và báo cáo phân tích

```plantuml
@startuml CLASS_GRADING
skinparam defaultFontName Segoe UI
skinparam shadowing false
skinparam defaultFontSize 13
title Lớp, bài làm, điểm và báo cáo phân tích
left to right direction
class KhongGian
class LopHoc {
  ma: DinhDanh
  ten: Chuoi
  namHoc: Chuoi
}
class HocSinh {
  ma: DinhDanh
  maTrongKhongGian: Chuoi
  tenHienThi: Chuoi
}
class DangKyLop {
  ma: DinhDanh
  trangThai: Chuoi
}
class KyCham {
  ma: DinhDanh
  ten: Chuoi
  trangThai: Chuoi
  +chotKetQua()
}
class PhienBanDe
class HoSoCham
class MaDe
class BaiLam {
  ma: DinhDanh
  trangThaiXacMinh: CHO_HOAC_DA_XAC_MINH
  nguonNhap: TAY_BANG_ANH
  maBaiTheoKy: Chuoi
  khoaChongLap: Chuoi
}
class TraLoi {
  viTriTrenMa: SoNguyen
  giaTri: Chuoi
  canXacMinh: Boolean
}
class KetQuaCham {
  ma: DinhDanh
  soPhienBan: SoNguyen
  tongDiem: ThapPhan
  trangThai: NHAP_HOAC_CHOT
  lyDoSua: Chuoi [0..1]
  +tinhDiem()
}
class DiemThanhPhan {
  diem: ThapPhan
  soYKhop: SoNguyen [0..1]
  cachCham: TU_DONG_HOAC_GIAO_VIEN
}
class AnhXaCau
class BaoCaoPhanTich {
  ma: DinhDanh
  phienBanMau: Chuoi
  tapKetQuaThamChieu: TapDinhDanh
  quyTacChonMau: Chuoi
  soMau: SoNguyen
  phoDiem: BangThongKe
  pMCQ: BangThongKe
  DMCQ: BangThongKe
  canhBaoDuLieu: TapCanhBao
}
KhongGian "1" -- "0..*" LopHoc
KhongGian "1" -- "0..*" HocSinh
LopHoc "1" -- "0..*" DangKyLop
HocSinh "1" -- "0..*" DangKyLop
LopHoc "1" -- "0..*" KyCham
KyCham "0..*" --> "1" PhienBanDe : ghim đề dùng chấm
KyCham "0..*" --> "1" HoSoCham : ghim
KyCham "1" -- "0..*" BaiLam
DangKyLop "1" -- "0..*" BaiLam : người làm trong kỳ
BaiLam "0..*" --> "0..1" MaDe : bắt buộc khi đã xác minh
BaiLam "1" *-- "0..*" TraLoi
BaiLam "1" -- "0..*" KetQuaCham : lịch sử chấm lại
KetQuaCham "0..*" --> "1" HoSoCham : phiên bản dùng lần chấm
KetQuaCham "1" *-- "1..*" DiemThanhPhan
DiemThanhPhan "0..*" --> "1" AnhXaCau : đúng câu trên mã
KyCham "1" -- "0..*" BaoCaoPhanTich
BaoCaoPhanTich "0..*" -- "1..*" KetQuaCham : mẫu đã chốt
note bottom of BaiLam
  Khi chưa rõ mã, giữ chờ xác minh.
  Đề gốc không trộn dùng mã tham chiếu gốc
  với ánh xạ đồng nhất để chấm nhất quán.
end note
note bottom of BaoCaoPhanTich
  Chỉ lấy một phiên bản điểm đang được chọn mỗi bài.
  Quy về câu gốc trước khi tính p, D.
  Thiếu mẫu thì không tính chỉ số, không chia cho 0.
end note
@enduml
```


## Từ vựng dữ liệu xuyên suốt

`DinhDanh` là mã ổn định; `PhienBan` cho phép xác định nội dung tại một thời điểm; `BanChupCauHoi` giữ nội dung thật sự dùng trong đề; `AnhXaCau`/`AnhXaLuaChon` giữ liên hệ từ mã đề về nội dung gốc. Các tên trong Sequence như “Quản lý ngân hàng câu hỏi” là dịch vụ trách nhiệm logic, không phải actor ngoài hoặc bảng dữ liệu. M01/M03 cung cấp phương pháp tìm công việc và dữ liệu; các lớp, bội số và bất biến trên là kết quả phân tích đề xuất cho Quesy.
