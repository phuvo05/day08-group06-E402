# Báo Cáo Cá Nhân — Lab Day 08: RAG Pipeline

**Họ và tên:** Phạm Minh Khang  
**Vai trò trong nhóm:** Eval Owner  
**Ngày nộp:** 13/04/2026  
**Độ dài yêu cầu:** 500–800 từ

---

## 1. Tôi đã làm gì trong lab này?

Tôi phụ trách toàn bộ phần evaluation. Ở Sprint 1, tôi rà soát `test_questions.json` có sẵn và bổ sung thêm 4 câu hỏi để đủ 10, mỗi câu có `expected_answer` và `expected_source` để làm ground truth. Ở Sprint 3, tôi chạy `run_scorecard()` cho cả baseline config (dense only) và variant config (dense + rerank), chấm điểm theo 3 tiêu chí: faithfulness, context recall, và answer correctness — kết hợp chấm thủ công và LLM-as-Judge. Sprint 4 tôi chạy `compare_ab()` để tính delta giữa hai config và lưu kết quả vào `results/`. Công việc của tôi là bước cuối cùng, phụ thuộc vào output của cả Quân, Phú và Định.

---

## 2. Điều tôi hiểu rõ hơn sau lab này

Tôi hiểu rõ hơn về **LLM-as-Judge** — dùng LLM để chấm điểm output của LLM khác. Ban đầu tôi nghĩ đây là vòng tròn logic, nhưng thực tế nó hoạt động tốt vì judge model được cho context gốc và rubric rõ ràng, trong khi answer model không có rubric. Kết quả chấm của GPT-4 judge khớp với chấm thủ công của tôi ở 8/10 câu — đủ tin cậy cho mục đích so sánh A/B.

Ngoài ra tôi hiểu **faithfulness ≠ correctness**: một câu trả lời có thể faithful (bám sát context) nhưng vẫn sai nếu context được retrieve là sai. Đây là lý do cần đo cả hai metric riêng biệt.

---

## 3. Điều tôi ngạc nhiên hoặc gặp khó khăn

Khó khăn là thiết kế `expected_answer` cho các câu hỏi có nhiều đáp án đúng một phần. Ví dụ câu "Ai phê duyệt Level 3?" — policy nói "IT Manager hoặc CISO tùy trường hợp", nhưng nếu model chỉ trả lời "IT Manager" thì đúng hay sai? Tôi phải định nghĩa rubric rõ: đúng hoàn toàn (1.0), đúng một phần (0.5), sai (0.0) thay vì chỉ binary.

Điều ngạc nhiên là baseline đã đạt faithfulness trung bình 0.82/1.0 — cao hơn tôi kỳ vọng. Prompt "Answer only from context" của Quân hoạt động hiệu quả hơn tôi nghĩ.

---

## 4. Phân tích một câu hỏi trong scorecard

**Câu hỏi:** "Nhân viên được nghỉ phép tối đa bao nhiêu ngày/năm?"

Đây là câu hỏi tôi thêm vào để test cross-document retrieval. Baseline trả lời "12 ngày" — đúng với `hr_leave_policy.txt`. Tuy nhiên policy còn có điều khoản "cộng thêm 1 ngày cho mỗi 5 năm thâm niên" mà model bỏ qua. Điểm answer correctness: 0.6/1.0.

Lỗi nằm ở **retrieval**: chunk chứa điều khoản thâm niên có score thấp hơn vì không có từ "tối đa" hay "ngày phép". Sau rerank, chunk này vẫn không lên top-3 vì cross-encoder cũng không nhận ra liên quan. Đây là giới hạn của cả hai approach — cần query transformation để expand "tối đa" thành "số ngày + điều kiện cộng thêm".

---

## 5. Nếu có thêm thời gian, tôi sẽ làm gì?

Tôi sẽ mở rộng test set lên 20 câu và thêm **adversarial questions** — câu hỏi mà câu trả lời không có trong corpus — để đo tỷ lệ abstain chính xác. Kết quả eval hiện tại cho thấy model abstain đúng 2/2 câu out-of-scope, nhưng sample quá nhỏ để kết luận.
