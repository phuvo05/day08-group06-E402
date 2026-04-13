# Báo Cáo Nhóm — Lab Day 08: Full RAG Pipeline

**Tên nhóm:** Group 06
**Thành viên:**
| Tên | Vai trò | Email |
|-----|---------|-------|
| Nguyễn Anh Quân | Tech Lead | N/A |
| Võ Thiên Phú | Retrieval Owner (Indexing) | N/A |
| Phan Dương Định | Retrieval Owner (Tuning) | N/A |
| Phạm Minh Khang | Eval Owner | N/A |
| Đào Hồng Sơn | Documentation Owner | N/A |

**Ngày nộp:** 13/04/2026
**Repo:** phuvo05/day08-group06-E402
**Độ dài khuyến nghị:** 600–900 từ

---

## 1. Pipeline nhóm đã xây dựng (150–200 từ)

**Chunking decision:**
Nhóm chọn **heading-based chunking** (cắt tại `=== Section ===` trước, sau đó cắt theo paragraph nếu section quá dài) thay vì fixed-size chunking. Lý do: corpus là các policy documents của công ty có cấu trúc section vô cùng rõ ràng — cắt theo heading đảm bảo mỗi chunk được chia chứa một điều khoản duy nhất, hoàn chỉnh, không bị cắt giữa nội dung điều kiện. Chunk size là 400 tokens, overlap là 80 tokens.

**Embedding model:**
Nhóm sử dụng model **paraphrase-multilingual-MiniLM-L12-v2** (của thư viện sentence-transformers chạy cục bộ) thay vì sử dụng OpenAI Embeddings để tiết kiệm API credit. Corpus tiếng Anh dành cho task tương đối ngắn gọn và thực tế đáp ứng kết quả retrieval của mô hình local đã là vô cùng ấn tượng.

**Retrieval variant (Sprint 3):**
Nhóm bổ sung thêm bước **cross-encoder rerank** (sử dụng model `cross-encoder/ms-marco-MiniLM-L-6-v2`) chạy ngay sau bước dense retrieval. Rerank giúp mô hình nhìn vào toàn phần cả cụm (query, chunk) để phân biệt những nội dung chứa thực sự đáp án thay vì chỉ là sự liên quan về mặt chủ điểm chung chung của mô hình bi-encoder truyền thống. Qua đó tăng độ chính xác (Faithfulness).

---

## 2. Quyết định kỹ thuật quan trọng nhất (200–250 từ)

**Quyết định:** Sử dụng cross-encoder rerank đối với các chunk kết quả lấy trên truy vấn dense retrieval.

**Bối cảnh vấn đề:**
Kết quả ở bước baseline cho thấy dense search trả về rất nhiều chunk có score (khoảng 0.72–0.78) là ngang ngưỡng với nhau. Khuyết điểm lộ rõ nhất ở câu hỏi SLA q01 — chunk chứa thông tin chung chung từ file FAQ bị xếp ở hàng top 1, vượt qua cả rank context của chunk chứa đáp án chi tiết nằm ở file SLA chính. Việc này dẫn đến kết cục bot sử dụng FAQ context để trả lời sai thời gian giải quyết sự cố thực tế.

**Các phương án đã cân nhắc:**

| Phương án | Ưu điểm | Nhược điểm |
|-----------|---------|-----------|
| Tăng số lượng `top_k` | Phương pháp cực dễ cấu hình, giúp tăng khả năng bao phủ context. | Tăng nhiễu từ các ngữ cảnh vô giá trị, nguy cơ bot sinh trả lời sai, thêm chi phí input token tại bước LLM. |
| Hybrid Search (BM25 + Dense) | BM25 bao phủ rất tốt keyword/alias chính xác để vá lỗi keyword mismatch. | Bi-encoder model vẫn bị loãng về mặt chủ đề nếu top danh sách xếp hạng không được kiểm soát. |
| Cross-encoder Rerank | Scoring song song chi tiết cặp truy xuất (query+chunk), lọc bỏ nhiễu và đôn chính xác chunk giá trị lên hạng top. | Bù đắp cho độ trễ hệ thống tính toán gia tăng (tăng chi phí latency ~1.2s bằng chạy trên CPU). |

**Phương án đã chọn và lý do:**
Nhóm chọn thêm cross-encoder rerank bởi context recall tại đường cơ sở (baseline) đã hoàn toàn chạm nóc (5.00/5) — tức danh sách tài liệu từ ChromaDB (top-10) tìm được qua dense đều bao gồm đầy đủ dữ kiện. Vấn đề chỉ hoàn toàn nằm tại thứ hạng xếp bậc nội tại pool cung cấp. Reranker là module đặc thù giải quyết khuyết điểm đó một cách triệt để. Đánh đổi thời gia tăng độ phản hồi (cộng ~1.2s mỗi lượt) được thông qua bởi kích thước CSDL (khoảng 150 chunks) chưa đủ mức độ tạo thắt nút cổ chai ở quy mô ứng dụng trợ lý nhỏ.

**Bằng chứng từ scorecard/tuning-log:**
File `tuning-log.md` chỉ ra minh chứng ở q01 trả lời từ mức sai ("24 giờ") đã cải chính sau đó là đúng ("4 giờ") khi variant can thiệp. Mức thống kê điểm trung bình ở mục tiêu Faithfulness nhờ vậy đôn từ 4.90 điểm lên khung tuyệt đối 5.00 điểm duy trì giữ nguyên prompt gốc.

---

## 3. Kết quả grading questions (100–150 từ)

**Ước tính điểm raw:** 98 / 98 

**Câu tốt nhất:** ID: q01 — Lý do: Pipeline đã được minh chứng là giải quyết xử lý rất tốt việc gỡ rối ranking thứ tự cho các context dễ gây xao nhãng liên quan mặt chủ đề thông thường. Rerank đẩy thông tin chứa yếu tố thực tiễn "4 giờ" lên thẳng top rank ưu tiên giúp LLM vận hành vô cùng lý tưởng, sinh câu trả lời tính chính xác vô đối.

**Câu fail:** ID: q07 — Root cause: Hạn chế trầm trọng đến từ giới hạn cơ chế Dense Embeddings trong Retrieval. Hệ thống đã không map được cụm ý nghĩa alias ("Approval Matrix") từ phía truy vấn người dùng khớp liền với cụm từ "Access Control SOP" trên văn bản kiến thức. Nguyên do lack thông tin từ đồng nghĩa trong kho metadata.

**Câu gq07 (abstain):** Pipeline phản hồi thông tin abstain cho câu hỏi vắng chủ đề xuất hiện khá chỉn chu. Grounded prompt mang cấu trúc bắt bí model "Answer only from context, if not found say you do not know". Trợ lý dứt khoát xác nhận là không có thông tin từ ngữ cảnh tài liệu tương ứng một cách ổn thỏa thay vì trả lời bịa đặt.

---

## 4. A/B Comparison — Baseline vs Variant (150–200 từ)

**Biến đã thay đổi (chỉ 1 biến):** Thêm bước tính toán cross-encoder rerank lọc lại top-10 hạng đầu.

| Metric | Baseline | Variant | Delta |
|--------|---------|---------|-------|
| Faithfulness | 4.90/5 | 5.00/5 | +0.10 |
| Answer Relevance | 4.60/5 | 4.60/5 | 0.00 |
| Context Recall | 5.00/5 | 5.00/5 | 0.00 |
| Completeness | 3.70/5 | 3.80/5 | +0.10 |

**Kết luận:**
Variant (dense + rerank) vận động xuất sắc lấn át baseline phương diện bám sát yếu tố dữ kiện có thực (Faithfulness) và đẩy mạnh tính chu toàn (Completeness). Rerank can chỉnh đúng trọng tâm tài liệu thay vì hoán vị các context chỉ liên quan bề mặt ngữ nghĩa, minh họa chân dung chunk nội dung đáp án trọn vẹn lên rank đầu. Điểm Context Recall & Answer Relevance được duy trì không có sai số do pool context từ dense return ra chưa hề bị xáo động.

---

## 5. Phân công và đánh giá nhóm (100–150 từ)

**Phân công thực tế:**

| Thành viên | Phần đã làm | Sprint |
|------------|-------------|--------|
| Nguyễn Anh Quân | Lập trình module sinh `call_llm()`, `rag_answer()`, thiết lập pipeline E2E cơ bản. | Sprint 2 |
| Võ Thiên Phú | Nghiển cứu phương pháp Indexing, làm hàm `build_index()`, xử lý chức năng `retrieve_dense()`. | Sprint 1 |
| Phan Dương Định | Xây dựng chiến thuật tinh chỉnh Ranking, tạo script hàm `rerank()`, thực nghiệm A/B. | Sprint 3 |
| Phạm Minh Khang | Xác định benchmark list câu hỏi tập dữ liệu, xử lý evaluate log `run_scorecard()`, `compare_ab()`. | Sprint 4 |
| Đào Hồng Sơn | Đóng góp chuẩn hóa tài liệu architecture của RAG pipeline, cấu trúc `tuning-log.md`. | Sprint 1-4 |

**Điều nhóm làm tốt:**
Làm theo sát chỉ dẫn phòng nghiên cứu Lab. Đội tuân thủ khắc nghiệt quy chuẩn test kiểm thử A/B: Không tinh chỉnh chéo chồng lên nhau thay đổi, chỉ đo đạc metric trên đúng 1 hệ số tương ứng được đánh dấu.

**Điều nhóm làm chưa tốt:**
Thiết kế Indexing (Chunking strategy) vẫn chưa mở rộng các keyword dictionary/alias mapping để tạo metadata làm phong phú thêm khả năng đối sánh truy vấn bí danh rút gọn của tổ chức.

---

## 6. Nếu có thêm 1 ngày, nhóm sẽ làm gì? (50–100 từ)

Nhóm chắc chắn sẽ cài đặt thêm phương thức **Hybrid Search (BM25 kết hợp với Dense base hiện tại)**. Thông tin tracking trên tuning-log và đánh giá scorecard phản ánh việc Retrieval bỏ lỡ các keyword/alias mang tính đặc biệt ("Approval Matrix"). Hệ thống BM25 làm rất xuất sắc mảng phủ tìm kiếm keyword thô theo exact-match. Nếu kết nối chung vào pipeline rồi sau đó dùng cross-encoder kiểm chứng chắt mẻ hạng mục top down, nhược điểm yếu nhất hiện thời sẽ được san lấp triệt để.
