# Báo Cáo Cá Nhân — Lab Day 08: RAG Pipeline

**Họ và tên:** Đào Hồng Sơn

**Vai trò trong nhóm:** Documentation Owner

**Ngày nộp:** 13/04/2026

**Độ dài yêu cầu:** 500–800 từ

---

## 1. Đóng góp cụ thể của tôi

Tôi nhận vai Documentation Owner nên không trực tiếp viết hàm retrieve hay rerank, mà bám theo bạn Tech Lead và Retrieval Owner để chuyển log chạy thật thành tài liệu. Sprint 1, sau khi `index.py` chạy xong, tôi soi output để ghi lại con số chunk thật của từng file vào `docs/architecture.md`: `policy_refund_v4.txt` 6, `sla_p1_2026.txt` 5, `access_control_sop.txt` 7, `it_helpdesk_faq.txt` 6, `hr_leave_policy.txt` 5, tổng 29. Tôi cũng liệt kê đầy đủ 5 metadata field (`source`, `section`, `effective_date`, `department`, `access`) — vượt yêu cầu 3 field tối thiểu của README.

Sprint 2–3, tôi đối chiếu `BASELINE_CONFIG` và `VARIANT_CONFIG` trong `eval.py` để chốt lại trong `tuning-log.md`: baseline = `dense, top_k_search=10, top_k_select=3, rerank=False`, variant = `hybrid + rerank=True`. Đây là chỗ đầu tiên tôi suýt viết sai vì có lúc tài liệu chỉ thấy phần rerank, dễ tưởng nhóm chỉ đổi một biến.

Sprint 4, tôi viết script `run_grading.py` theo mẫu trong SCORING.md để chạy `docs/grading_questions.json` qua pipeline variant, ghi ra `logs/grading_run.json` đúng schema bắt buộc (id, question, answer, sources, chunks_retrieved, retrieval_mode, timestamp), thêm `use_rerank` theo gợi ý FAQ. Sau đó tôi tự chấm 10 câu theo `grading_criteria` và đối chiếu với expected_answer để nộp.

---

## 2. Phân tích một câu grading: gq05 (Contractor + Admin Access)

Tôi chọn gq05 vì đây là câu pipeline **fail nặng nhất** (0/10 theo rubric). Câu hỏi: *“Contractor có được cấp quyền Admin Access không? Cần bao nhiêu ngày và yêu cầu đặc biệt gì?”*

**Pipeline trả lời:** “Có, contractor có thể được cấp Admin Access tạm thời, tối đa 24 giờ sau khi Tech Lead phê duyệt… ghi log Security Audit”.

**Expected (theo `grading_criteria`):** Level 4 cần phê duyệt **IT Manager + CISO**, thời gian **5 ngày làm việc**, có **training bắt buộc về security policy** (Section 2 của `access_control_sop.txt`).

**Failure mode — fail ở RETRIEVAL/RERANK, không phải generation:** Doc gốc chứa cả 2 thông tin liên quan: Section 2 mô tả Level 4 (IT Manager + CISO, 5 ngày, training), và Section 4 mô tả emergency escalation (24h, Tech Lead). Truy vấn lấy đúng `access_control_sop.md` (recall đúng), nhưng cross-encoder rerank đẩy chunk Section 4 lên đầu vì cụm từ “cấp quyền tạm thời” trong câu hỏi khớp lexical với “quyền tạm thời 24 giờ” trong Section 4. Chunk Section 2 chứa Level 4 detail bị rớt khỏi top-3.

Hệ quả: model thấy context chỉ nói về quy trình emergency 24h nên trả lời theo đúng context — faithfulness vẫn đúng (model không bịa), nhưng câu trả lời lệch hoàn toàn câu hỏi gốc. Đây đúng kiểu failure mà criteria liệt kê: *“Chỉ describe quy trình thông thường (không phải emergency escalation)”* — chỉ là theo chiều ngược lại.

**Fix cụ thể:** thay vì rerank thuần, có thể (a) tăng `top_k_select` lên 5 để giữ cả 2 chunk, hoặc (b) thêm filter metadata `section` để bắt buộc lấy ít nhất 1 chunk từ Section 2 khi query có chữ “Admin Access”/”Level 4”.

---

## 3. Rút kinh nghiệm thực tế

Bất ngờ nhất với tôi là **rerank không phải bao giờ cũng tốt**. Trước lab tôi đọc tài liệu thấy “cross-encoder cải thiện ranking” là mặc nhiên đúng. Nhưng khi đối chiếu `scorecard_baseline.md` và `scorecard_variant.md`: faithfulness tăng (4.90 → 5.00) và recall không đổi, nhưng **relevance giảm 4.40 → 4.20** và **completeness giảm 3.90 → 3.80**. q07 trong test_questions thậm chí từ 5/5/5/2 (baseline) tụt xuống 5/1/5/1 (variant). Trade-off này không hiện ra nếu chỉ nhìn faithfulness.

Khó khăn lớn thứ hai là **timestamp bonus**. SCORING.md cho +1 nếu `grading_run.json` có timestamp trong khoảng 17:00–18:00. Tôi chạy lúc 16:23–16:24 nên không đạt — đây là lỗi do tôi không đọc kỹ phần Bonus của SCORING trước khi bấm chạy. Nếu lùi lại, tôi sẽ chốt thời gian chạy thật cùng cả nhóm.

Việc rà chéo grading_run.json với grading_criteria cũng dạy tôi rằng **answer “nghe đúng” chưa chắc khớp criteria**. gq04 pipeline trả 110% và có citation — nghe rất đúng — nhưng thiếu chữ “tùy chọn (không bắt buộc)” nên rớt từ Full 8/8 xuống Partial 4/8. Documentation không thể chỉ skim qua, phải tick từng gạch đầu dòng.

---

## 4. Đề xuất cải tiến (có evidence từ scorecard)

**Cải tiến 1 — Tăng `top_k_select` từ 3 lên 5 cho câu multi-section.** Bằng chứng: gq05 fail vì rerank giữ Section 4 (emergency) và rớt Section 2 (Level 4 standard). Nếu select 5 chunk thay vì 3, xác suất giữ lại chunk chứa “IT Manager + CISO + 5 ngày + training” cao hơn rõ rệt. Estimate: gq05 từ 0 → ~8/10, kéo điểm grading từ ~21.4đ lên ~23.9đ.

**Cải tiến 2 — Thêm filter metadata `effective_date` cho query có yếu tố thời gian.** Bằng chứng: gq10 (refund v4 vs đơn trước 01/02/2026) hiện tại pass nhờ may mắn — chunk Điều 1 lọt top-3. Nhưng nếu chunk khác có score cao hơn, pipeline có thể trả lời sai phạm vi áp dụng. Filter `effective_date <= order_date` ở retrieval layer sẽ chặn được failure mode “stale document” mà SCORING.md ghi rõ là rủi ro chính của câu này.
