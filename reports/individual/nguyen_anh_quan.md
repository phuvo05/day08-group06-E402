# Báo Cáo Cá Nhân — Lab Day 08: RAG Pipeline

**Họ và tên:** Nguyễn Anh Quân  
**Vai trò trong nhóm:** Tech Lead  
**Ngày nộp:** 13/04/2026  
**Độ dài yêu cầu:** 500–800 từ

---

## 1. Tôi đã làm gì trong lab này?

Với vai trò Tech Lead, tôi tập trung vào việc giữ nhịp sprint và nối các phần thành pipeline chạy được từ đầu đến cuối. Ở Sprint 1, tôi phụ trách hoàn thiện `index.py`: parse metadata (`source`, `department`, `effective_date`, `access`), chunk theo section/paragraph có overlap, và build index vào ChromaDB. Tôi cũng thống nhất embedding strategy để tránh mismatch giữa lúc index và lúc query. Ở Sprint 2–3, tôi hỗ trợ hoàn thiện `rag_answer.py` theo hướng có baseline dense retrieval và variant hybrid + rerank để so sánh A/B. Ở Sprint 4, tôi tham gia chạy `eval.py`, rà lỗi import/path, và kiểm tra file output (`scorecard_baseline.md`, `scorecard_variant.md`, `ab_comparison.csv`) để đảm bảo demo end-to-end không vỡ luồng.

---

## 2. Điều tôi hiểu rõ hơn sau lab này

Bài lab giúp tôi hiểu retrieval quyết định chất lượng RAG nhiều hơn tôi từng nghĩ. Trước đây tôi thường tập trung prompt, nhưng khi chạy thực tế tôi thấy: nếu chunking chưa tốt hoặc metadata không sạch, retriever sẽ kéo sai context, và model trả lời sai dù prompt đã “grounded”. Tôi cũng hiểu rõ hơn vai trò của abstain: thay vì cố trả lời mọi câu, hệ thống cần biết nói “không đủ dữ liệu” để giảm hallucination trong các câu không có bằng chứng. Một điểm quan trọng nữa là tính nhất quán embedding giữa indexing và querying. Chỉ cần đổi model embedding mà không re-index thì kết quả search giảm rõ rệt hoặc lỗi dimension, nên vận hành thực tế phải có quy trình quản lý version cho index.

---

## 3. Điều tôi ngạc nhiên hoặc gặp khó khăn

Khó khăn lớn nhất là xử lý tính ổn định môi trường khi chuyển giữa local embedding và API-based embedding. Chúng tôi gặp tình huống dependency thiếu hoặc cấu hình chưa đồng bộ, khiến pipeline chạy nhưng retrieval không đúng kỳ vọng. Ngoài ra, việc tinh chỉnh ngưỡng chọn chunk và top-k tưởng đơn giản nhưng ảnh hưởng lớn đến faithfulness/completeness: top-k thấp dễ thiếu bằng chứng, top-k cao lại tăng nhiễu cho bước generation. Điều làm tôi ngạc nhiên là hybrid retrieval cho hiệu quả tốt hơn trong các câu có alias hoặc từ khóa đặc thù (ví dụ tên tài liệu cũ như “Approval Matrix”), vì dense giữ được ngữ nghĩa còn sparse giữ được exact term. Insight này hữu ích hơn nhiều so với việc chỉ tối ưu prompt.

---

## 4. Phân tích một câu hỏi trong scorecard

Tôi chọn phân tích câu `q07`: “Approval Matrix để cấp quyền hệ thống là tài liệu nào?”. Đây là câu dễ fail với dense baseline vì người dùng dùng tên cũ, trong khi tài liệu hiện tại dùng tên “Access Control SOP”. Ở baseline, retriever có lúc không đưa đúng chunk ghi chú đổi tên, nên answer thiếu chắc chắn hoặc vòng vo. Khi chuyển sang variant hybrid + rerank, hệ thống lấy đúng chunk có câu “trước đây có tên Approval Matrix…”, nên answer bám bằng chứng hơn và citation rõ hơn. Root cause nằm ở retrieval recall (không phải generation): model không “nghĩ sai”, mà do evidence đưa vào chưa đúng. Fix hiệu quả nhất là đổi retrieval strategy, không phải chỉ thêm prompt dài hơn.

---

## 5. Nếu có thêm thời gian, tôi sẽ làm gì?

Nếu có thêm thời gian, tôi sẽ ưu tiên ba việc. Thứ nhất, chuyển một phần scoring từ heuristic sang LLM-as-judge có schema JSON để giảm công chấm tay và dễ so sánh giữa các lần tune. Thứ hai, bổ sung logging chi tiết cho retrieval (query variants, top-k trước/sau rerank, score phân phối) để truy vết failure nhanh hơn khi demo. Thứ ba, chuẩn hóa quy trình build index theo version (embedding model + chunk config + timestamp) để tránh lỗi “query nhầm index cũ”. Mục tiêu của ba việc này là làm pipeline bớt phụ thuộc may mắn khi chạy một lần, và tăng khả năng lặp lại kết quả khi nhóm cần trình bày A/B comparison trước lớp.

