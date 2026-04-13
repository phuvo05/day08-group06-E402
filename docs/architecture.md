# Architecture — RAG Pipeline (Day 08 Lab)

> Template: Điền vào các mục này khi hoàn thành từng sprint.
> Deliverable của Documentation Owner.

## 1. Tổng quan kiến trúc

```
[Raw Docs]
    ↓
[index.py: Preprocess → Chunk → Embed → Store]
    ↓
[ChromaDB Vector Store + BM25 Inverted Index]
    ↓
[rag_answer.py: Query → Hybrid Retrieve → Fuse → Generate]
    ↓
[Grounded Answer + Citation]
```

**Mô tả ngắn gọn:**
Nhóm xây dựng RAG pipeline cho internal helpdesk — cho phép nhân viên hỏi về chính sách công ty (HR, IT, Refund, SLA) và nhận câu trả lời có trích dẫn nguồn. Pipeline giải quyết vấn đề LLM hallucinate khi trả lời câu hỏi về policy nội bộ bằng cách ép model chỉ trả lời từ retrieved context.

---

## 2. Indexing Pipeline (Sprint 1)

### Tài liệu được index
| File | Nguồn | Department | Số chunk |
|------|-------|-----------|---------|
| `policy_refund_v4.txt` | policy/refund-v4.pdf | CS | 6 |
| `sla_p1_2026.txt` | support/sla-p1-2026.pdf | IT | 7 |
| `access_control_sop.txt` | it/access-control-sop.md | IT Security | 8 |
| `it_helpdesk_faq.txt` | support/helpdesk-faq.md | IT | 5 |
| `hr_leave_policy.txt` | hr/leave-policy-2026.pdf | HR | 5 |

### Quyết định chunking
| Tham số | Giá trị | Lý do |
|---------|---------|-------|
| Chunk size | 400 tokens (~1600 ký tự) | Đủ để chứa 1 điều khoản hoàn chỉnh, không quá dài gây lost-in-the-middle |
| Overlap | 80 tokens (~320 ký tự) | Tránh cắt đứt điều kiện nằm ở ranh giới 2 chunk |
| Chunking strategy | Heading-based → paragraph-based | Ưu tiên cắt tại `=== Section ===`, nếu section quá dài thì cắt theo paragraph `\n\n` |
| Metadata fields | source, section, effective_date, department, access | Phục vụ filter, freshness, citation |

### Embedding model
- **Model**: paraphrase-multilingual-MiniLM-L12-v2 (sentence-transformers, local)
- **Vector store**: ChromaDB (PersistentClient)
- **Sparse index**: BM25 inverted index (token-based)
- **Similarity metric**: Cosine (dense) + BM25 score (sparse)

---

## 3. Retrieval Pipeline (Sprint 2 + 3)

### Baseline (Sprint 2)
| Tham số | Giá trị |
|---------|---------|
| Strategy | Dense (embedding similarity) |
| Top-k search | 10 |
| Top-k select | 3 |
| Rerank | Không |

### Variant (Sprint 3)
| Tham số | Giá trị | Thay đổi so với baseline |
|---------|---------|------------------------|
| Strategy | Hybrid (Dense + BM25) | Đổi từ Dense-only |
| Dense top-k | 10 | Giữ như baseline |
| Sparse top-k | 10 | Thêm mới |
| Fusion | Weighted score fusion (0.7 dense + 0.3 sparse) | Thêm mới |
| Top-k select | 3 | Không đổi |
| Rerank | Không | Không đổi |
| Query transform | Không | Không đổi |

**Lý do chọn variant này:**
Dense search mạnh ở semantic match nhưng đôi khi bỏ sót chunk có keyword quan trọng (ví dụ mã SLA, mốc thời gian, điều khoản có số liệu cụ thể). BM25 bổ sung tín hiệu lexical để kéo lên các chunk chứa từ khóa trọng yếu. Hybrid giúp tăng độ ổn định retrieval trên cả câu hỏi diễn đạt tự nhiên và câu hỏi có từ khóa exact-match, trong khi vẫn giữ pipeline đủ đơn giản để debug.

---

## 4. Generation (Sprint 2)

### Grounded Prompt Template
```
Answer only from the retrieved context below.
If the context is insufficient, say you do not know.
Cite the source field when possible.
Keep your answer short, clear, and factual.

Question: {query}

Context:
[1] {source} | {section} | score={score}
{chunk_text}

[2] ...

Answer:
```

### LLM Configuration
| Tham số | Giá trị |
|---------|---------|
| Model | gpt-4o-mini |
| Temperature | 0 (để output ổn định cho eval) |
| Max tokens | 512 |

---

## 5. Failure Mode Checklist

> Dùng khi debug — kiểm tra lần lượt: index → retrieval → generation

| Failure Mode | Triệu chứng | Cách kiểm tra |
|-------------|-------------|---------------|
| Index lỗi | Retrieve về docs cũ / sai version | `inspect_metadata_coverage()` trong index.py |
| Chunking tệ | Chunk cắt giữa điều khoản | `list_chunks()` và đọc text preview |
| Retrieval lỗi | Không tìm được expected source | `score_context_recall()` trong eval.py |
| Hybrid fuse lệch | BM25 lấn át semantic hoặc ngược lại | So sánh distribution score dense vs sparse theo query |
| Generation lỗi | Answer không grounded / bịa | `score_faithfulness()` trong eval.py |
| Token overload | Context quá dài → lost in the middle | Kiểm tra độ dài context_block |

---

## 6. Diagram (tùy chọn)

> TODO: Vẽ sơ đồ pipeline nếu có thời gian. Có thể dùng Mermaid hoặc drawio.

```mermaid
graph LR
    A[User Query] --> B[Query Embedding]
    A --> C[Keyword Query]
    B --> D[ChromaDB Dense Search]
    C --> E[BM25 Sparse Search]
    D --> F[Top Dense Candidates]
    E --> G[Top Sparse Candidates]
    F --> H[Score Fusion]
    G --> H
    H --> I[Top-3 Select]
    I --> J[Build Context Block]
    J --> K[Grounded Prompt]
    K --> L[LLM]
    L --> M[Answer + Citation]
```
