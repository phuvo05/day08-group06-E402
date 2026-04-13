# Báo Cáo Cá Nhân — Lab Day 08: RAG Pipeline

**Họ và tên:** Võ Thiên Phú  
**Vai trò trong nhóm:** Retrieval Owner (Indexing)  
**Ngày nộp:** 13/04/2026  
**Độ dài yêu cầu:** 500–800 từ

---

## 1. Tôi đã làm gì trong lab này?

Tôi phụ trách toàn bộ phần indexing pipeline ở Sprint 1 và retrieval cơ bản ở Sprint 2. Cụ thể, tôi implement phần TODO trong `build_index()`: load từng file trong `data/docs/`, chunk theo paragraph với overlap 50 token, gắn metadata `source`, `section`, `effective_date` cho mỗi chunk, rồi embed và upsert vào ChromaDB. Sau đó tôi dùng `list_chunks()` để kiểm tra xem chunk có bị cắt giữa điều khoản không. Ở Sprint 2, tôi implement `retrieve_dense()` — nhận query string, embed bằng hàm của Quân, rồi query ChromaDB lấy top-k chunk kèm score. Phần này là đầu vào trực tiếp cho `call_llm()` của Quân và variant của Định.

---

## 2. Điều tôi hiểu rõ hơn sau lab này

Tôi hiểu rõ hơn về tầm quan trọng của **chunking strategy**. Ban đầu tôi chunk cứng theo 200 token, kết quả là nhiều điều khoản bị cắt đôi — ví dụ điều khoản hoàn tiền bị tách thành 2 chunk khác collection, khiến retrieval chỉ lấy được một nửa thông tin. Sau khi chuyển sang chunk theo paragraph boundary, `list_chunks()` cho thấy các chunk hoàn chỉnh hơn và điểm context recall tăng rõ rệt.

Ngoài ra tôi hiểu **metadata filtering** không chỉ để đẹp — khi Khang chạy scorecard, việc có `effective_date` trong metadata giúp phân biệt được policy cũ và mới, tránh trường hợp retrieve nhầm phiên bản lỗi thời.

---

## 3. Điều tôi ngạc nhiên hoặc gặp khó khăn

Khó khăn lớn nhất là xử lý file `it_helpdesk_faq.txt` — file này có format Q&A lẫn lộn, không có paragraph rõ ràng. Chunk theo paragraph boundary cho ra các chunk chỉ 1-2 dòng, quá ngắn để có context đủ. Phải viết thêm logic nhận diện pattern "Q:" và "A:" để ghép cặp Q&A thành một chunk.

Điều ngạc nhiên là ChromaDB xử lý upsert rất nhanh — 5 file với ~150 chunk tổng cộng chỉ mất khoảng 4 giây kể cả thời gian embed. Tôi tưởng sẽ mất lâu hơn nhiều.

---

## 4. Phân tích một câu hỏi trong scorecard

**Câu hỏi:** "Khách hàng có thể yêu cầu hoàn tiền trong bao nhiêu ngày?"

Baseline trả lời "30 ngày" — đúng với `policy_refund_v4.txt`. Tuy nhiên điểm chỉ đạt 0.8/1.0 vì câu trả lời thiếu điều kiện "kể từ ngày nhận hàng" và "không áp dụng cho sản phẩm đã kích hoạt".

Lỗi nằm ở **chunking**: điều kiện này nằm ở paragraph tiếp theo, bị tách thành chunk riêng và không được retrieve vì score thấp hơn. Sau khi tôi tăng chunk overlap từ 50 lên 100 token, hai paragraph này nằm trong cùng một chunk, câu trả lời đầy đủ hơn và điểm tăng lên 1.0/1.0.

---

## 5. Nếu có thêm thời gian, tôi sẽ làm gì?

Tôi sẽ thử **hierarchical chunking** — giữ cả chunk nhỏ (câu) lẫn chunk lớn (đoạn) trong index, vì kết quả eval cho thấy một số câu hỏi cần context rộng (đoạn) trong khi một số khác chỉ cần một câu cụ thể. Retrieve theo 2 cấp có thể cải thiện cả precision lẫn recall cùng lúc.
