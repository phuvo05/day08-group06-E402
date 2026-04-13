# Báo Cáo Cá Nhân — Lab Day 08: RAG Pipeline

**Họ và tên:** Phan Dương Định  
**Vai trò trong nhóm:** Retrieval Owner (Tuning)  
**Ngày nộp:** 13/04/2026  
**Độ dài yêu cầu:** 500–800 từ

---

## 1. Tôi đã làm gì trong lab này?

Tôi phụ trách Sprint 3 — tuning retrieval strategy. Sau khi phân tích corpus, tôi chọn variant **Rerank** vì dense search trả về nhiều chunk có score gần nhau (~0.72–0.78), khó phân biệt chunk nào thực sự liên quan nhất. Tôi implement `rerank()` dùng cross-encoder `cross-encoder/ms-marco-MiniLM-L-6-v2` từ Sentence Transformers: lấy top-10 từ dense search, cho cross-encoder score lại từng cặp (query, chunk), rồi chỉ giữ top-3 để đưa vào LLM. Tôi cũng chạy `compare_retrieval_strategies()` để so sánh baseline dense vs rerank trên toàn bộ test questions, và ghi kết quả vào `docs/tuning-log.md`. Công việc của tôi phụ thuộc vào `retrieve_dense()` của Phú và kết quả được Khang dùng để chạy scorecard.

---

## 2. Điều tôi hiểu rõ hơn sau lab này

Tôi hiểu rõ hơn sự khác biệt giữa **bi-encoder** (dùng trong dense retrieval) và **cross-encoder** (dùng trong rerank). Bi-encoder encode query và document độc lập nên nhanh nhưng kém chính xác hơn. Cross-encoder nhìn cả cặp (query, document) cùng lúc nên chính xác hơn nhiều nhưng không thể dùng để search toàn bộ corpus vì quá chậm. Việc kết hợp hai loại — dùng bi-encoder để lọc nhanh, cross-encoder để rerank — là pattern thực tế được dùng trong production search system.

---

## 3. Điều tôi ngạc nhiên hoặc gặp khó khăn

Khó khăn là cross-encoder mất ~1.2 giây để rerank 10 chunk trên CPU — chậm hơn tôi kỳ vọng. Với 10 test questions, tổng thời gian tăng thêm ~12 giây so với baseline. Đây là trade-off thực tế giữa accuracy và latency.

Điều ngạc nhiên là rerank cải thiện rõ nhất ở các câu hỏi có từ khóa kỹ thuật như "SLA P1", "Level 3 access" — những câu mà dense search trả về nhiều chunk "gần đúng" nhưng không phải chunk chứa con số cụ thể. Cross-encoder phân biệt được chunk nào thực sự trả lời câu hỏi, không chỉ liên quan về chủ đề.

---

## 4. Phân tích một câu hỏi trong scorecard

**Câu hỏi:** "SLA xử lý ticket P1 là bao lâu?"

Baseline dense search trả về chunk từ `sla_p1_2026.txt` ở rank 3 (score 0.74), trong khi rank 1-2 là các chunk từ `it_helpdesk_faq.txt` nói về SLA chung chung. LLM dùng context rank 1-2 và trả lời "trong vòng 24 giờ" — sai, vì SLA P1 thực tế là 4 giờ.

Sau rerank, chunk từ `sla_p1_2026.txt` được đẩy lên rank 1 với cross-encoder score 0.91. LLM trả lời đúng "4 giờ làm việc" kèm citation. Đây là case study rõ nhất cho thấy rerank giải quyết được vấn đề dense search bị nhiễu bởi semantic similarity chung chung.

---

## 5. Nếu có thêm thời gian, tôi sẽ làm gì?

Tôi sẽ thử **hybrid retrieval** kết hợp BM25 + dense + rerank vì eval cho thấy còn 2 câu hỏi có mã lỗi (`ERR-403-AUTH`, `ERR-500-DB`) mà cả dense lẫn rerank đều không retrieve được đúng — những câu này cần exact keyword match mà BM25 xử lý tốt hơn.
