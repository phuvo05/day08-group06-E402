# Báo Cáo Cá Nhân — Lab Day 08: RAG Pipeline

| | |
|---|---|
| **Họ và tên** | Võ Thiên Phú |
| **Vai trò trong nhóm** | Retrieval Owner (Indexing) |
| **Ngày nộp** | 13/04/2026 |
| **Độ dài yêu cầu** | 500–800 từ |

---

## 1. Tôi đã làm gì trong lab này?

Trong lab lần này, tôi đảm nhận toàn bộ phần indexing pipeline ở Sprint 1 và xây dựng retrieval cơ bản ở Sprint 2. Nhiệm vụ chính của tôi là hoàn thiện phần TODO trong hàm `build_index()`: đọc lần lượt các file trong thư mục `data/docs/`, chia nhỏ nội dung theo ranh giới đoạn văn với overlap 50 token, đính kèm metadata gồm `source`, `section` và `effective_date` vào từng chunk, sau đó thực hiện embed và upsert vào ChromaDB.

Để kiểm tra chất lượng, tôi dùng `list_chunks()` nhằm xác nhận rằng không có điều khoản nào bị cắt vụn. Sang Sprint 2, tôi tiếp tục xây dựng hàm `retrieve_dense()` — nhận vào một chuỗi query, embed thông qua hàm của Quân, rồi truy vấn ChromaDB để lấy top-k chunk có điểm cao nhất. Kết quả đầu ra của bước này được dùng trực tiếp trong `call_llm()` của Quân và các variant do Định phụ trách.

---

## 2. Điều tôi hiểu rõ hơn sau lab này

Lab này giúp tôi nhận ra tầm quan trọng thực sự của **chiến lược chunking**. Lúc đầu tôi chia chunk cứng theo 200 token — cách làm đơn giản nhưng dẫn đến hậu quả là nhiều điều khoản bị tách đôi ra hai collection khác nhau. Điển hình là điều khoản hoàn tiền chỉ được retrieve một nửa, khiến thông tin trả về không đầy đủ. Khi chuyển sang chia theo ranh giới đoạn văn, `list_chunks()` phản ánh rõ sự cải thiện — các chunk trọn vẹn hơn và điểm context recall tăng lên đáng kể.

Bên cạnh đó, tôi hiểu thêm rằng **metadata filtering** không chỉ mang tính hình thức. Khi Khang chạy scorecard, trường `effective_date` trong metadata đóng vai trò then chốt trong việc phân biệt chính sách cũ và mới, ngăn hệ thống retrieve nhầm sang các phiên bản đã lỗi thời.

---

## 3. Điều tôi ngạc nhiên hoặc gặp khó khăn

Thách thức lớn nhất đến từ file `it_helpdesk_faq.txt` với định dạng Q&A không có cấu trúc rõ ràng. Khi áp dụng chunking theo đoạn văn, kết quả cho ra các chunk chỉ vỏn vẹn 1–2 dòng — quá ngắn để mang đủ ngữ cảnh. Để xử lý, tôi phải bổ sung logic nhận diện pattern `"Q:"` và `"A:"` nhằm ghép cặp câu hỏi và câu trả lời vào chung một chunk.

Điều khiến tôi bất ngờ là ChromaDB xử lý upsert nhanh hơn kỳ vọng rất nhiều — toàn bộ 5 file với khoảng 150 chunk, tính cả thời gian embed, chỉ mất khoảng 4 giây. Tôi đã chuẩn bị tinh thần chờ lâu hơn nhiều.

---

## 4. Phân tích một câu hỏi trong scorecard

**Câu hỏi:** *"Khách hàng có thể yêu cầu hoàn tiền trong bao nhiêu ngày?"*

Ở bản baseline, hệ thống trả lời "30 ngày" — hoàn toàn khớp với nội dung trong `policy_refund_v4.txt`. Tuy nhiên điểm chỉ dừng ở 0.8/1.0 vì câu trả lời bỏ sót hai điều kiện quan trọng: "kể từ ngày nhận hàng" và "không áp dụng cho sản phẩm đã kích hoạt".

Nguyên nhân nằm ở cách chia chunk: hai điều kiện trên thuộc đoạn văn tiếp theo, bị tách thành chunk riêng với điểm retrieve thấp hơn nên không được đưa vào ngữ cảnh. Sau khi tăng overlap từ 50 lên 100 token, hai đoạn này được gộp vào chung một chunk và câu trả lời trở nên đầy đủ hơn.

> Kết quả: **0.8 / 1.0 → 1.0 / 1.0**

---

## 5. Nếu có thêm thời gian, tôi sẽ làm gì?

Tôi muốn thử nghiệm **hierarchical chunking** — duy trì đồng thời cả chunk nhỏ ở cấp câu lẫn chunk lớn ở cấp đoạn trong cùng một index. Kết quả eval cho thấy một số câu hỏi cần ngữ cảnh rộng để trả lời chính xác, trong khi một số khác chỉ cần đúng một câu cụ thể. Retrieve theo hai cấp như vậy có tiềm năng cải thiện đồng thời cả precision lẫn recall, thay vì phải đánh đổi giữa hai chỉ số này.
