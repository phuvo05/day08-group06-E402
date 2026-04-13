# Tuning Log — RAG Pipeline (Day 08 Lab)

> A/B Rule: Chỉ đổi MỘT biến mỗi lần.

---

## Baseline (Sprint 2)

**Ngày:** 13/04/2026  
**Config:**
```
retrieval_mode = "dense"
chunk_size = 400 tokens
overlap = 80 tokens
top_k_search = 10
top_k_select = 3
use_rerank = False
llm_model = gpt-4o-mini
```

**Scorecard Baseline:**
| Metric | Average Score |
|--------|--------------|
| Faithfulness | 4.90/5 |
| Answer Relevance | 4.60/5 |
| Context Recall | 5.00/5 |
| Completeness | 3.70/5 |

**Câu hỏi yếu nhất:**
- **q07** (Approval Matrix) — completeness 2/5: dense retrieve đúng document nhưng LLM không trả lời được tên mới của tài liệu vì chunk không chứa alias mapping.
- **q09** (ERR-403-AUTH) — completeness 2/5: câu hỏi out-of-scope, pipeline không abstain rõ ràng mà trả lời chung chung từ model knowledge.
- **q10** (VIP refund) — relevance 1/5, completeness 2/5: pipeline abstain nhưng không nêu được quy trình tiêu chuẩn 3-5 ngày.

**Giả thuyết nguyên nhân:**
- [x] Retrieval: Dense bỏ lỡ exact keyword / alias (q07: "Approval Matrix" ≠ "Access Control SOP")
- [x] Generation: Prompt không đủ grounding khi context thiếu thông tin (q09, q10)
- [ ] Indexing: Chunking cắt giữa điều khoản
- [ ] Retrieval: Top-k quá ít

---

## Variant 1 (Sprint 3)

**Ngày:** 13/04/2026  
**Biến thay đổi:** Thêm cross-encoder rerank sau dense retrieval  
**Lý do chọn biến này:**  
Baseline cho thấy dense search trả về nhiều chunk có score gần nhau (0.72–0.78), đặc biệt ở q01 (SLA P1) — chunk từ `it_helpdesk_faq.txt` nói về SLA chung chung được rank cao hơn chunk từ `sla_p1_2026.txt` chứa con số cụ thể. Cross-encoder nhìn cả cặp (query, chunk) nên phân biệt được chunk nào thực sự trả lời câu hỏi, không chỉ liên quan về chủ đề. Chọn rerank thay vì hybrid vì context recall baseline đã đạt 5.00/5 — retrieval đã lấy đúng document, vấn đề là ranking trong top-10.

**Config thay đổi:**
```
retrieval_mode = "dense"   # giữ nguyên
use_rerank = True          # thay đổi duy nhất
# cross-encoder: cross-encoder/ms-marco-MiniLM-L-6-v2
# Các tham số còn lại giữ nguyên như baseline
```

**Scorecard Variant 1:**
| Metric | Baseline | Variant 1 | Delta |
|--------|----------|-----------|-------|
| Faithfulness | 4.90/5 | 5.00/5 | +0.10 |
| Answer Relevance | 4.60/5 | 4.60/5 | 0.00 |
| Context Recall | 5.00/5 | 5.00/5 | 0.00 |
| Completeness | 3.70/5 | 3.80/5 | +0.10 |

**Nhận xét:**  
Variant cải thiện rõ nhất ở q01 (SLA P1): baseline trả lời sai "24 giờ" vì chunk FAQ được rank cao hơn, rerank đẩy chunk `sla_p1_2026.txt` lên rank 1 → trả lời đúng "4 giờ". Faithfulness tăng từ 4.90 lên 5.00 vì không còn trường hợp nào dùng chunk sai. Completeness tăng nhẹ (+0.10) ở q04 và q09. Answer Relevance và Context Recall không thay đổi vì retrieval pool (top-10) giữ nguyên.  
Không có câu nào variant kém hơn baseline.

**Kết luận:**  
Variant 1 (rerank) tốt hơn baseline ở Faithfulness (+0.10) và Completeness (+0.10). Bằng chứng: q01 từ sai → đúng sau rerank. Trade-off: latency tăng ~1.2s/câu do cross-encoder chạy trên CPU. Với corpus nhỏ (150 chunks), trade-off này chấp nhận được cho production nội bộ.

---

## Tóm tắt học được

1. **Lỗi phổ biến nhất:** Semantic similarity của bi-encoder không phân biệt được "liên quan về chủ đề" vs "trả lời đúng câu hỏi" — rerank giải quyết được vấn đề này.

2. **Biến có tác động lớn nhất:** Rerank — cải thiện Faithfulness từ 4.90 lên 5.00 chỉ bằng cách sắp xếp lại top-10 đã có sẵn, không cần thay đổi indexing hay prompt.

3. **Nếu có thêm 1 giờ:** Thử hybrid (BM25 + dense) + rerank vì q07 (alias query "Approval Matrix") và q09 (mã lỗi ERR-403-AUTH) vẫn chưa được cải thiện — đây là loại query cần exact keyword match mà BM25 xử lý tốt hơn dense.
