# Lab Day 08 — Phân Công Nhiệm Vụ

**Dự án:** RAG Pipeline — CS + IT Helpdesk Assistant  
**Thời gian:** 4 sprints x 60 phút  
**Thành viên:** 5 người

---

## Phân Công Theo Thành Viên

### Nguyễn Anh Quân (2A202600132) — Tech Lead
**Vai trò:** Giữ nhịp sprint, nối code end-to-end

| Sprint | Nhiệm vụ | File | Done khi |
|--------|----------|------|----------|
| Sprint 1 | Implement `get_embedding()` (chọn OpenAI hoặc Sentence Transformers) | `index.py` | Hàm trả về vector hợp lệ |
| Sprint 2 | Implement `call_llm()` — gọi OpenAI hoặc Gemini | `rag_answer.py` | LLM trả về câu trả lời có citation `[1]` |
| Sprint 2 | Test `rag_answer()` với 3+ câu hỏi mẫu | `rag_answer.py` | Output có `sources` field không rỗng |
| Sprint 4 | Chạy demo end-to-end: `python index.py && python rag_answer.py && python eval.py` | — | Pipeline chạy không lỗi |
| Sprint 4 | Viết báo cáo cá nhân (500-800 từ) | `reports/individual/nguyen_anh_quan.md` | File hoàn chỉnh |

---

### Võ Thiên Phú (2A202600336) — Retrieval Owner (Indexing)
**Vai trò:** Chunking, metadata, xây dựng index

| Sprint | Nhiệm vụ | File | Done khi |
|--------|----------|------|----------|
| Sprint 1 | Implement phần TODO trong `build_index()` — embed và upsert vào ChromaDB | `index.py` | Index đủ 5 tài liệu |
| Sprint 1 | Kiểm tra với `list_chunks()` — đảm bảo mỗi chunk có `source`, `section`, `effective_date` | `index.py` | Chunk không bị cắt giữa điều khoản |
| Sprint 2 | Implement `retrieve_dense()` — query ChromaDB với embedding | `rag_answer.py` | Retrieve đúng context cho câu hỏi mẫu |
| Sprint 4 | Viết báo cáo cá nhân (500-800 từ) | `reports/individual/vo_thien_phu.md` | File hoàn chỉnh |

---

### Phan Dương Định (2A202600277) — Retrieval Owner (Tuning)
**Vai trò:** Retrieval strategy, rerank, so sánh variant

| Sprint | Nhiệm vụ | File | Done khi |
|--------|----------|------|----------|
| Sprint 3 | Chọn và implement 1 variant: Hybrid / Rerank / Query Transform | `rag_answer.py` | Variant chạy end-to-end |
| Sprint 3 | Chạy `compare_retrieval_strategies()` — bảng so sánh baseline vs variant | `rag_answer.py` | Có bảng so sánh rõ ràng |
| Sprint 3 | Giải thích lý do chọn variant | `docs/tuning-log.md` | Ghi vào tuning-log |
| Sprint 4 | Viết báo cáo cá nhân (500-800 từ) | `reports/individual/phan_duong_dinh.md` | File hoàn chỉnh |

---

### Phạm Minh Khang (2A202600417) — Eval Owner
**Vai trò:** Test questions, expected evidence, scorecard, A/B

| Sprint | Nhiệm vụ | File | Done khi |
|--------|----------|------|----------|
| Sprint 1 | Rà soát và bổ sung `test_questions.json` — đảm bảo 10 câu hỏi có expected answers | `data/test_questions.json` | Đủ 10 câu, có expected evidence |
| Sprint 3 | Chạy `run_scorecard(BASELINE_CONFIG)` và `run_scorecard(VARIANT_CONFIG)` | `eval.py` | Scorecard baseline và variant đã điền |
| Sprint 4 | Chạy `compare_ab()` — ghi nhận delta | `eval.py` | Có kết quả A/B rõ ràng |
| Sprint 4 | Lưu kết quả vào `results/scorecard_baseline.md` và `scorecard_variant.md` | `results/` | 2 file scorecard hoàn chỉnh |
| Sprint 4 | Viết báo cáo cá nhân (500-800 từ) | `reports/individual/pham_minh_khang.md` | File hoàn chỉnh |

---

### Đào Hồng Sơn (2A202600462) — Documentation Owner
**Vai trò:** Architecture docs, tuning log, báo cáo nhóm

| Sprint | Nhiệm vụ | File | Done khi |
|--------|----------|------|----------|
| Sprint 1 | Phác thảo sơ đồ pipeline vào `architecture.md` (Indexing flow) | `docs/architecture.md` | Có mô tả Indexing → Chunk → Embed → Store |
| Sprint 2 | Cập nhật `architecture.md` (Retrieval + Generation flow) | `docs/architecture.md` | Có mô tả Retrieve → Generate → Citation |
| Sprint 3 | Ghi lại A/B experiments vào `tuning-log.md` (phối hợp Định) | `docs/tuning-log.md` | Có ít nhất 1 experiment với kết quả |
| Sprint 4 | Hoàn thiện `architecture.md` và `tuning-log.md` | `docs/` | Cả 2 file đầy đủ, rõ ràng |
| Sprint 4 | Viết báo cáo cá nhân (500-800 từ) | `reports/individual/dao_hong_son.md` | File hoàn chỉnh |

---

## Tổng Quan Timeline

| Sprint | Quân | Phú | Định | Khang | Sơn |
|--------|------|-----|------|-------|-----|
| Sprint 1 | `get_embedding()` | `build_index()` + `list_chunks()` | Hỗ trợ Phú | Chuẩn bị test questions | Phác thảo architecture |
| Sprint 2 | `call_llm()` + test | `retrieve_dense()` | Nghiên cứu variant | Rà soát test questions | Cập nhật architecture |
| Sprint 3 | Review + fix bug | Hỗ trợ Định | Implement variant + so sánh | Chạy scorecard | Ghi tuning-log |
| Sprint 4 | Demo end-to-end | Báo cáo cá nhân | Báo cáo cá nhân | A/B + scorecard | Hoàn thiện docs |

---

## Deliverables Checklist

- [x] `index.py` — Quân + Phú
- [x] `rag_answer.py` — Quân + Phú + Định
- [x] `eval.py` — Khang
- [x] `data/test_questions.json` — Khang
- [x] `results/scorecard_baseline.md` — Khang
- [x] `results/scorecard_variant.md` — Khang
- [x] `docs/architecture.md` — Sơn
- [x] `docs/tuning-log.md` — Định + Sơn
- [x] `reports/individual/nguyen_anh_quan.md` — Quân
- [x] `reports/individual/vo_thien_phu.md` — Phú
- [x] `reports/individual/phan_duong_dinh.md` — Định
- [x] `reports/individual/pham_minh_khang.md` — Khang
- [x] `reports/individual/dao_hong_son.md` — Sơn
