# Báo Cáo Cá Nhân — Lab Day 08: RAG Pipeline

**Họ và tên:** Nguyễn Anh Quân  
**Vai trò trong nhóm:** Tech Lead  
**Ngày nộp:** 13/04/2026  
**Độ dài yêu cầu:** 500–800 từ

---

## 1. Tôi đã làm gì trong lab này?

Với vai trò Tech Lead, tôi chịu trách nhiệm giữ nhịp cho cả 4 sprint và đảm bảo các phần code của từng thành viên kết nối được với nhau. Cụ thể, ở Sprint 1 tôi implement hàm `get_embedding()` sử dụng Sentence Transformers (`all-MiniLM-L6-v2`) để tạo vector embedding cho các chunk văn bản. Ở Sprint 2, tôi implement `call_llm()` gọi OpenAI GPT với prompt có ràng buộc "Answer only from context", đồng thời test toàn bộ `rag_answer()` với 5 câu hỏi mẫu. Sprint 4 tôi chạy demo end-to-end và fix các lỗi import, path còn sót lại. Công việc của tôi là nền tảng để Phú kết nối `build_index()` và Định tích hợp variant retrieval.

---

## 2. Điều tôi hiểu rõ hơn sau lab này

Trước lab, tôi nghĩ embedding chỉ đơn giản là "chuyển text thành số". Sau khi implement `get_embedding()` và thấy kết quả retrieve thay đổi rõ rệt khi đổi model, tôi hiểu rằng chất lượng embedding ảnh hưởng trực tiếp đến toàn bộ pipeline — một model embedding kém sẽ khiến retrieval sai dù prompt có tốt đến đâu.

Ngoài ra, tôi hiểu rõ hơn về **grounded generation**: việc thêm "Answer only from context, if not found say Không đủ dữ liệu" vào prompt không chỉ là kỹ thuật — nó là cơ chế kiểm soát hallucination. Khi test câu `ERR-403-AUTH`, model thực sự abstain thay vì bịa đặt, điều này cho thấy prompt engineering có tác động thực sự đo được.

---

## 3. Điều tôi ngạc nhiên hoặc gặp khó khăn

Khó khăn lớn nhất là việc kết nối embedding model với ChromaDB. Ban đầu tôi dùng `text-embedding-ada-002` của OpenAI nhưng nhóm không đủ credit, phải chuyển sang Sentence Transformers giữa chừng. Việc đổi model khiến dimension vector thay đổi (1536 → 384), dẫn đến lỗi khi query collection cũ. Phải xóa collection và build lại index từ đầu — mất khoảng 15 phút.

Điều ngạc nhiên là Sentence Transformers cho kết quả retrieval gần tương đương OpenAI Embeddings trên corpus tiếng Anh ngắn này, trong khi hoàn toàn miễn phí. Đây là insight thực tế quan trọng hơn nhiều so với lý thuyết trên slide.

---

## 4. Phân tích một câu hỏi trong scorecard

**Câu hỏi:** "Ai phải phê duyệt để cấp quyền Level 3?"

Baseline trả lời đúng tên người phê duyệt nhưng thiếu điều kiện đi kèm (phải có ticket mở trước). Điểm faithfulness đạt 0.7/1.0 vì câu trả lời không sai nhưng không đầy đủ so với context được retrieve.

Lỗi nằm ở **generation**: context retrieve được đoạn đúng từ `access_control_sop.txt`, nhưng prompt không yêu cầu model trích dẫn đầy đủ điều kiện. Sau khi Định thêm rerank, chunk liên quan được đẩy lên top-1 và câu trả lời đầy đủ hơn, điểm tăng lên 0.9/1.0. Điều này cho thấy rerank giúp ích ngay cả khi retrieval đã lấy đúng document.

---

## 5. Nếu có thêm thời gian, tôi sẽ làm gì?

Tôi sẽ thử **streaming response** cho `call_llm()` vì kết quả eval cho thấy latency trung bình ~3.2s/câu — quá chậm cho production. Ngoài ra sẽ thử cache embedding của các câu hỏi lặp lại để giảm số lần gọi model, vì test_questions.json có 3 câu hỏi có cùng entity "Level 3".
