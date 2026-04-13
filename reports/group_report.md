# Group Report — Lab Day 08: RAG Pipeline

**Nhóm:** Nguyễn Anh Quân, Võ Thiên Phú, Phan Dương Định, Phạm Minh Khang, Đào Hồng Sơn  
**Ngày nộp:** 13/04/2026

---

## 1. Tổng quan hệ thống

Nhóm xây dựng RAG pipeline cho internal helpdesk, cho phép nhân viên hỏi về chính sách công ty (HR, IT, Refund, SLA) và nhận câu trả lời có trích dẫn nguồn. Pipeline gồm 5 tài liệu nội bộ, ChromaDB làm vector store, sentence-transformers làm embedding model, và GPT-4o-mini làm LLM.

---

## 2. Quyết định kỹ thuật cấp nhóm

### Chunking
Chọn **heading-based chunking** (cắt tại `=== Section ===` trước, sau đó cắt theo paragraph nếu section quá dài) thay vì fixed-size chunking. Lý do: corpus là policy documents có cấu trúc section rõ ràng — cắt theo heading đảm bảo mỗi chunk chứa một điều khoản hoàn chỉnh, không bị cắt giữa điều kiện. Chunk size 400 tokens, overlap 80 tokens.

### Embedding
Chọn **paraphrase-multilingual-MiniLM-L12-v2** (local, sentence-transformers) thay vì OpenAI Embeddings vì corpus tiếng Anh ngắn và nhóm không đủ API credit. Kết quả retrieval tương đương trên corpus này.

### Grounded Prompt
Prompt ép model "Answer only from context, if not found say you do not know" — kiểm soát hallucination. Test q09 (ERR-403-AUTH, out-of-scope) và q10 (VIP refund, không có trong docs) đều abstain đúng.

### A/B Experiment
Biến thay đổi duy nhất: **thêm cross-encoder rerank** (cross-encoder/ms-marco-MiniLM-L-6-v2) sau dense retrieval. Không thay đổi chunking, embedding, hay prompt để đảm bảo A/B rule.

---

## 3. Kết quả A/B

| Metric | Baseline (dense) | Variant (dense + rerank) | Delta |
|--------|-----------------|--------------------------|-------|
| Faithfulness | 4.90/5 | 5.00/5 | +0.10 |
| Answer Relevance | 4.60/5 | 4.60/5 | 0.00 |
| Context Recall | 5.00/5 | 5.00/5 | 0.00 |
| Completeness | 3.70/5 | 3.80/5 | +0.10 |

Rerank cải thiện Faithfulness và Completeness. Case study rõ nhất: q01 (SLA P1) — baseline trả lời sai "24 giờ" vì chunk FAQ được rank cao hơn chunk `sla_p1_2026.txt`; sau rerank trả lời đúng "4 giờ làm việc". Trade-off: latency tăng ~1.2s/câu.

---

## 4. Điểm yếu còn lại

- **q07** (Approval Matrix alias): cả baseline lẫn variant đều completeness 2/5 — dense không match được "Approval Matrix" với "Access Control SOP". Cần hybrid (BM25) để xử lý alias query.
- **q10** (VIP refund): relevance 1/5 — pipeline abstain nhưng không nêu được quy trình tiêu chuẩn 3-5 ngày. Cần cải thiện prompt để hướng dẫn model trả lời "không có quy trình đặc biệt, áp dụng quy trình tiêu chuẩn X".

---

## 5. Phân công

| Thành viên | Vai trò | Sprint chính |
|-----------|---------|-------------|
| Nguyễn Anh Quân | Tech Lead | Sprint 2: `call_llm()`, `rag_answer()`, end-to-end test |
| Võ Thiên Phú | Retrieval Owner (Indexing) | Sprint 1: `build_index()`, `retrieve_dense()` |
| Phan Dương Định | Retrieval Owner (Tuning) | Sprint 3: `rerank()`, A/B experiment |
| Phạm Minh Khang | Eval Owner | Sprint 4: `run_scorecard()`, `compare_ab()`, test questions |
| Đào Hồng Sơn | Documentation Owner | Sprint 1–4: `architecture.md`, `tuning-log.md` |
