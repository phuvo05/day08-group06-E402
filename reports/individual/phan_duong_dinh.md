# Báo Cáo Cá Nhân — Lab Day 08: RAG Pipeline

**Họ và tên:** Phan Dương Định  
**Vai trò trong nhóm:** Retrieval Owner (Tuning)  
**Ngày nộp:** 13/04/2026  
**Độ dài yêu cầu:** 500–800 từ

---

## 1. Tôi đã làm gì trong lab này?

Trong Sprint 3, tôi nhận trách nhiệm tối ưu hóa chiến lược truy xuất thông tin. Sau khi kiểm tra dữ liệu kho, tôi nhận thấy phương pháp tìm kiếm vector mật độ cao cho điểm số rất gần nhau (khoảng 0.72–0.78) giữa các đoạn văn bản, làm khó xác định đoạn nào phù hợp nhất. Để giải quyết vấn đề này, tôi xây dựng mô-đun `rerank()` sử dụng mô hình cross-encoder `cross-encoder/ms-marco-MiniLM-L-6-v2` từ thư viện Sentence Transformers. Quy trình hoạt động gồm: lấy 10 kết quả hàng đầu từ tìm kiếm vector, ghi điểm lại từng cặp (truy vấn, đoạn text) qua cross-encoder, và chỉ giữ 3 kết quả tốt nhất để cung cấp cho mô hình ngôn ngữ. Tôi cũng thực hiện so sánh toàn diện giữa baseline và phương pháp rerank trên tất cả câu hỏi kiểm thử thông qua `compare_retrieval_strategies()`, với kết quả được lưu trong `docs/tuning-log.md`. Công việc này dựa trên hàm `retrieve_dense()` mà Phú phát triển, và Khang sử dụng kết quả của tôi để đánh giá hiệu năng tổng thể.

---

## 2. Điều tôi hiểu rõ hơn sau lab này

Trải qua lab này, tôi nắm rõ hơn về sự khác biệt cơ bản giữa hai kiến trúc mô hình. Mô hình bi-encoder (dùng trong tìm kiếm vector) xử lý query và tài liệu riêng biệt, cho phép tìm kiếm nhanh nhưng với độ chính xác hạn chế. Ngược lại, cross-encoder phân tích cả cặp query-tài liệu đồng thời, cung cấp độ chính xác cao hơn đáng kể nhưng không khả thi cho tìm kiếm toàn bộ kho dữ liệu do độ trễ cao. Kết hợp hai phương pháp — dùng bi-encoder lọc nhanh, sau đó dùng cross-encoder để xếp hạng lại — là một mẫu thực tiễn được áp dụng rộng rãi trong các hệ thống tìm kiếm sản xuất.

---

## 3. Điều tôi ngạc nhiên hoặc gặp khó khăn

Thách thức chính là hiệu năng xử lý: cross-encoder mất khoảng 1.2 giây để xếp hạng 10 đoạn văn trên bộ xử lý thông thường — chậm hơn dự kiến ban đầu. Cộng dồn lên 10 câu hỏi kiểm thử, thời gian xử lý tăng thêm khoảng 12 giây so với phương pháp cơ bản. Đây là sự cân bằng thiết thực giữa tính chính xác và tốc độ phản hồi.

Điểm thú vị là cải tiến hiệu suất xuất hiện rõ rệt nhất ở những truy vấn chứa thuật ngữ kỹ thuật chuyên biệt như "SLA P1" hay "Level 3 access". Với những truy vấn này, tìm kiếm vector trả về nhiều đoạn "gần đúng" nhưng không phải đoạn chứa thông tin chính xác. Cross-encoder chứng minh khả năng phân biệt được đoạn nào thực sự trả lời câu hỏi, thay vì chỉ liên quan về chủ đề nói chung.

---

## 4. Phân tích một câu hỏi trong bảng đánh giá

**Câu hỏi:** "SLA xử lý ticket P1 là bao lâu?"

Khi dùng phương pháp cơ bản, kết quả từ `sla_p1_2026.txt` chỉ đứng ở vị trí 3 (điểm số 0.74), trong khi 2 vị trí hàng đầu là các đoạn từ `it_helpdesk_faq.txt` chỉ nói chung chung về SLA. Mô hình ngôn ngữ sử dụng context từ 2 kết quả đầu và đưa ra câu trả lời "trong vòng 24 giờ" — sai, vì SLA P1 thực tế là 4 giờ.

Sau khi áp dụng xếp hạng lại, đoạn từ `sla_p1_2026.txt` được nâng lên vị trí 1 với điểm cross-encoder là 0.91. Mô hình ngôn ngữ giờ đưa ra câu trả lời chính xác: "4 giờ làm việc" có kèm trích dẫn nguồn. Trường hợp này minh họa rõ ràng cách xếp hạng lại khắc phục được hạn chế của tìm kiếm vector khi bị ảnh hưởng bởi các đoạn văn liên quan về mặt ngữ nghĩa nhưng không phải câu trả lời chính xác.

---

## 5. Hướng phát triển nếu có thêm thời gian

Nếu có nhiều thời gian hơn, tôi muốn thử nghiệm **kết hợp nhiều phương pháp** bao gồm BM25 + tìm kiếm vector + xếp hạng lại. Đánh giá hiện tại cho thấy 2 câu hỏi chứa mã lỗi (`ERR-403-AUTH`, `ERR-500-DB`) mà cả tìm kiếm vector lẫn xếp hạng lại đều không tìm được đúng kết quả. Những truy vấn này cần khớp từ khóa chính xác, là điểm mạnh của phương pháp BM25.
