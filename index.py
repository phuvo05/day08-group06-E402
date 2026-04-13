"""
index.py — Sprint 1: Build RAG Index
====================================
Mục tiêu Sprint 1 (60 phút):
  - Đọc và preprocess tài liệu từ data/docs/
  - Chunk tài liệu theo cấu trúc tự nhiên (heading/section)
  - Gắn metadata: source, section, department, effective_date, access
  - Embed và lưu vào vector store (ChromaDB)

Definition of Done Sprint 1:
  ✓ Script chạy được và index đủ docs
  ✓ Có ít nhất 3 metadata fields hữu ích cho retrieval
  ✓ Có thể kiểm tra chunk bằng list_chunks()
"""

import os
import json
import re
from pathlib import Path
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv

load_dotenv()

# =============================================================================
# CẤU HÌNH
# =============================================================================

DOCS_DIR = Path(__file__).parent / "data" / "docs"
CHROMA_DB_DIR = Path(__file__).parent / "chroma_db"

# TODO Sprint 1: Điều chỉnh chunk size và overlap theo quyết định của nhóm
# Gợi ý từ slide: chunk 300-500 tokens, overlap 50-80 tokens
CHUNK_SIZE = 400       # tokens (ước lượng bằng số ký tự / 4)
CHUNK_OVERLAP = 80     # tokens overlap giữa các chunk


# =============================================================================
# STEP 1: PREPROCESS
# Làm sạch text trước khi chunk và embed
# =============================================================================

def preprocess_document(raw_text: str, filepath: str) -> Dict[str, Any]:
    """
    Preprocess một tài liệu: extract metadata từ header và làm sạch nội dung.

    Args:
        raw_text: Toàn bộ nội dung file text
        filepath: Đường dẫn file để làm source mặc định

    Returns:
        Dict chứa:
          - "text": nội dung đã clean
          - "metadata": dict với source, department, effective_date, access

    TODO Sprint 1:
    - Extract metadata từ dòng đầu file (Source, Department, Effective Date, Access)
    - Bỏ các dòng header metadata khỏi nội dung chính
    - Normalize khoảng trắng, xóa ký tự rác

    Gợi ý: dùng regex để parse dòng "Key: Value" ở đầu file.
    """
    lines = raw_text.strip().split("\n")
    metadata = {
        "source": filepath,
        "section": "",
        "department": "unknown",
        "effective_date": "unknown",
        "access": "internal",
    }
    content_lines = []
    header_done = False

    for line in lines:
        if not header_done:
            # TODO: Parse metadata từ các dòng "Key: Value"
            # Ví dụ: "Source: policy/refund-v4.pdf" → metadata["source"] = "policy/refund-v4.pdf"
            if line.startswith("Source:"):
                metadata["source"] = line.replace("Source:", "").strip()
            elif line.startswith("Department:"):
                metadata["department"] = line.replace("Department:", "").strip()
            elif line.startswith("Effective Date:"):
                metadata["effective_date"] = line.replace("Effective Date:", "").strip()
            elif line.startswith("Access:"):
                metadata["access"] = line.replace("Access:", "").strip()
            elif line.startswith("==="):
                # Gặp section heading đầu tiên → kết thúc header
                header_done = True
                content_lines.append(line)
            elif line.strip() == "" or line.isupper():
                # Dòng tên tài liệu (toàn chữ hoa) hoặc dòng trống
                continue
        else:
            content_lines.append(line)

    cleaned_text = "\n".join(content_lines)

    # Normalize text:
    # - thay nhiều khoảng trắng liên tiếp bằng 1 dấu cách
    # - max 2 dòng trống liên tiếp
    # - bỏ whitespace thừa đầu/cuối mỗi dòng
    lines = cleaned_text.split("\n")
    normalized_lines = []
    for line in lines:
        # Bỏ khoảng trắng thừa trong dòng, giữ 1 dấu cách giữa các từ
        line = re.sub(r"[ \t]+", " ", line).strip()
        if line or (normalized_lines and normalized_lines[-1] != ""):
            normalized_lines.append(line)
    cleaned_text = "\n".join(normalized_lines)
    cleaned_text = re.sub(r"\n{3,}", "\n\n", cleaned_text)  # max 2 dòng trống liên tiếp

    return {
        "text": cleaned_text,
        "metadata": metadata,
    }


# =============================================================================
# STEP 2: CHUNK
# Chia tài liệu thành các đoạn nhỏ theo cấu trúc tự nhiên
# =============================================================================

def chunk_document(doc: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Chunk một tài liệu đã preprocess thành danh sách các chunk nhỏ.

    Args:
        doc: Dict với "text" và "metadata" (output của preprocess_document)

    Returns:
        List các Dict, mỗi dict là một chunk với:
          - "text": nội dung chunk
          - "metadata": metadata gốc + "section" của chunk đó

    TODO Sprint 1:
    1. Split theo heading "=== Section ... ===" hoặc "=== Phần ... ===" trước
    2. Nếu section quá dài (> CHUNK_SIZE * 4 ký tự), split tiếp theo paragraph
    3. Thêm overlap: lấy đoạn cuối của chunk trước vào đầu chunk tiếp theo
    4. Mỗi chunk PHẢI giữ metadata đầy đủ từ tài liệu gốc

    Gợi ý: Ưu tiên cắt tại ranh giới tự nhiên (section, paragraph)
    thay vì cắt theo token count cứng.
    """
    text = doc["text"]
    base_metadata = doc["metadata"].copy()
    chunks = []

    # TODO: Implement chunking theo section heading
    # Bước 1: Split theo heading pattern "=== ... ==="
    sections = re.split(r"(===.*?===)", text)

    current_section = "General"
    current_section_text = ""

    for part in sections:
        if re.match(r"===.*?===", part):
            # Lưu section trước (nếu có nội dung)
            if current_section_text.strip():
                section_chunks = _split_by_size(
                    current_section_text.strip(),
                    base_metadata=base_metadata,
                    section=current_section,
                )
                chunks.extend(section_chunks)
            # Bắt đầu section mới
            current_section = part.strip("= ").strip()
            current_section_text = ""
        else:
            current_section_text += part

    # Lưu section cuối cùng
    if current_section_text.strip():
        section_chunks = _split_by_size(
            current_section_text.strip(),
            base_metadata=base_metadata,
            section=current_section,
        )
        chunks.extend(section_chunks)

    return chunks


def _split_by_size(
    text: str,
    base_metadata: Dict,
    section: str,
    chunk_chars: int = CHUNK_SIZE * 4,
    overlap_chars: int = CHUNK_OVERLAP * 4,
) -> List[Dict[str, Any]]:
    """
    Helper: Split text dài thành chunks với overlap.

    Ưu tiên cắt theo ranh giới paragraph (\n\n), chỉ cắt theo dòng
    hoặc câu khi paragraph vẫn vượt chunk_chars.
    """
    if len(text) <= chunk_chars:
        return [{
            "text": text,
            "metadata": {**base_metadata, "section": section},
        }]

    # Bước 1: Tách theo paragraph (double newline)
    raw_paragraphs = text.split("\n\n")
    paragraphs = []
    for p in raw_paragraphs:
        stripped = p.strip()
        if stripped:
            paragraphs.append(stripped)

    if not paragraphs:
        paragraphs = [text]

    chunks = []
    current_chunk_parts = []
    current_len = 0

    def _flush_chunk():
        nonlocal current_chunk_parts, current_len
        if current_chunk_parts:
            combined = "\n\n".join(current_chunk_parts)
            chunks.append({
                "text": combined,
                "metadata": {**base_metadata, "section": section},
            })
            current_chunk_parts = []
            current_len = 0

    for para in paragraphs:
        para_len = len(para)

        # Nếu một paragraph đơn lẻ vượt chunk_chars, phải cắt nhỏ hơn
        if para_len > chunk_chars:
            _flush_chunk()
            sub_chunks = _split_paragraph_into_chunks(
                para, chunk_chars, overlap_chars, base_metadata, section
            )
            chunks.extend(sub_chunks)
            continue

        # Nếu thêm paragraph này sẽ vượt limit
        if current_len + para_len + 2 > chunk_chars:  # +2 cho \n\n
            _flush_chunk()
            # Overlap: ghép lại từ đoạn cuối của chunk trước
            if chunks and overlap_chars > 0:
                prev_text = chunks[-1]["text"]
                overlap_text = prev_text[-overlap_chars:]
                # Reset với overlap text
                current_chunk_parts = [overlap_text]
                current_len = len(overlap_text)
            else:
                current_chunk_parts = []
                current_len = 0

        current_chunk_parts.append(para)
        current_len += para_len + 2  # +2 cho separator \n\n

    _flush_chunk()
    return chunks


def _split_paragraph_into_chunks(
    text: str,
    chunk_chars: int,
    overlap_chars: int,
    base_metadata: Dict,
    section: str,
) -> List[Dict[str, Any]]:
    """
    Helper: Cắt một paragraph quá dài thành nhiều chunk,
    ưu tiên tìm ranh giới tự nhiên (dấu . hoặc \n) gần boundary.
    """
    chunks = []
    start = 0

    while start < len(text):
        end = min(start + chunk_chars, len(text))

        if end < len(text):
            # Tìm ranh giới tự nhiên gần nhất trong vùng [end-100, end]
            search_start = max(start, end - 100)
            segment = text[search_start:end]

            # Ưu tiên: xuống dòng → dấu chấm → dấu phẩy → ký tự trắng
            # Tìm vị trí xuống dòng gần cuối
            last_newline = segment.rfind("\n")
            if last_newline > len(segment) * 0.3:
                boundary = search_start + last_newline + 1
            else:
                # Tìm dấu chấm gần cuối (kết thúc câu)
                last_period = segment.rfind(".")
                if last_period > len(segment) * 0.5:
                    boundary = search_start + last_period + 1
                else:
                    # Tìm dấu phẩy gần cuối
                    last_comma = segment.rfind(",")
                    if last_comma > len(segment) * 0.6:
                        boundary = search_start + last_comma + 1
                    else:
                        # Tìm khoảng trắng gần cuối
                        last_space = segment.rfind(" ")
                        if last_space > len(segment) * 0.7:
                            boundary = search_start + last_space + 1
                        else:
                            boundary = end

            end = boundary

        chunk_text = text[start:end].strip()
        if chunk_text:
            chunks.append({
                "text": chunk_text,
                "metadata": {**base_metadata, "section": section},
            })

        # Overlap: lùi lại overlap_chars từ cuối chunk
        start = end - overlap_chars
        if start <= 0:
            start = end

    return chunks


# =============================================================================
# STEP 3: EMBED + STORE
# Embed các chunk và lưu vào ChromaDB
# =============================================================================

_embedding_model = None  # Singleton model cho sentence-transformers


def _get_st_model():
    """Lazy-load sentence-transformers model (singleton)."""
    global _embedding_model
    if _embedding_model is None:
        from sentence_transformers import SentenceTransformer
        model_name = os.getenv("LOCAL_EMBEDDING_MODEL", "paraphrase-multilingual-MiniLM-L12-v2")
        _embedding_model = SentenceTransformer(model_name)
    return _embedding_model


def get_embedding(text: str) -> List[float]:
    """
    Tạo embedding vector cho một đoạn text.

    Ưu tiên theo thứ tự:
    1. EMBEDDING_PROVIDER=openai → dùng OpenAI API
    2. EMBEDDING_PROVIDER=local  → dùng sentence-transformers local
    """
    provider = os.getenv("EMBEDDING_PROVIDER", "openai").lower().strip()

    if provider == "openai":
        from openai import OpenAI
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError(
                "OPENAI_API_KEY không được tìm thấy trong .env. "
                "Đổi EMBEDDING_PROVIDER=local nếu muốn dùng sentence-transformers."
            )
        client = OpenAI(api_key=api_key)
        response = client.embeddings.create(
            input=text,
            model="text-embedding-3-small",
        )
        return response.data[0].embedding

    elif provider == "local":
        model = _get_st_model()
        return model.encode(text).tolist()

    else:
        raise ValueError(
            f"EMBEDDING_PROVIDER không hợp lệ: '{provider}'. "
            "Chọn 'openai' hoặc 'local'."
        )


def build_index(docs_dir: Path = DOCS_DIR, db_dir: Path = CHROMA_DB_DIR) -> None:
    """
    Thực thi toàn bộ pipeline xây dựng vector index cho hệ thống RAG:
    1. Thu thập dữ liệu: Đọc các tài liệu text (.txt) từ thư mục `docs_dir`.
    2. Tiền xử lý (preprocess): Trích xuất metadata (source, department, effective_date,...) và làm sạch nội dung.
    3. Phân chia (chunking): Chia văn bản thành các đoạn (chunk) nhỏ theo cấu trúc tự nhiên để LLM dễ xử lý, đính kèm metadata liên quan.
    4. Nhúng vector (embedding): Biến đổi từng chunk thành vector embeddings dựa trên OpenAI API hoặc mô hình sentence-transformers local (`EMBEDDING_PROVIDER`).
    5. Lưu trữ (store): Lưu toàn bộ ID, vector, chunk và metadata bằng phương thức batch upsert vào cơ sở dữ liệu vector ChromaDB định tuyến tại `db_dir`.

    Args:
        docs_dir (Path): Thư mục chứa các tài liệu văn bản để index. Mặc định `DOCS_DIR` (data/docs/).
        db_dir (Path): Thư mục lưu dữ liệu cục bộ của ChromaDB. Mặc định `CHROMA_DB_DIR` (chroma_db/).
    """
    import chromadb

    print(f"Đang build index từ: {docs_dir}")
    db_dir.mkdir(parents=True, exist_ok=True)

    # Khởi tạo ChromaDB
    client = chromadb.PersistentClient(path=str(db_dir))
    collection = client.get_or_create_collection(
        name="rag_lab",
        metadata={"hnsw:space": "cosine"},
    )

    # Batch embeddings để giảm số API calls
    BATCH_SIZE = 100

    total_chunks = 0
    total_docs = 0
    doc_files = list(docs_dir.glob("*.txt"))

    if not doc_files:
        print(f"Không tìm thấy file .txt trong {docs_dir}")
        return

    for filepath in doc_files:
        raw_text = filepath.read_text(encoding="utf-8")

        # preprocess + chunk
        doc = preprocess_document(raw_text, str(filepath))
        chunks = chunk_document(doc)

        if not chunks:
            print(f"  [WARN] {filepath.name}: 0 chunks, bỏ qua")
            continue

        # Batch embed và upsert
        ids = []
        embeddings = []
        documents = []
        metadatas = []

        for i, chunk in enumerate(chunks):
            chunk_id = f"{filepath.stem}_{i}"
            ids.append(chunk_id)
            documents.append(chunk["text"])
            metadatas.append(chunk["metadata"])

        # Embed theo batch
        provider = os.getenv("EMBEDDING_PROVIDER", "openai").lower().strip()
        if provider == "openai":
            from openai import OpenAI
            api_key = os.getenv("OPENAI_API_KEY")
            client_emb = OpenAI(api_key=api_key)

            for batch_start in range(0, len(documents), BATCH_SIZE):
                batch_docs = documents[batch_start:batch_start + BATCH_SIZE]
                batch_ids = ids[batch_start:batch_start + BATCH_SIZE]
                batch_metas = metadatas[batch_start:batch_start + BATCH_SIZE]

                response = client_emb.embeddings.create(
                    input=batch_docs,
                    model="text-embedding-3-small",
                )
                batch_embeddings = [r.embedding for r in response.data]

                collection.upsert(
                    ids=batch_ids,
                    embeddings=batch_embeddings,
                    documents=batch_docs,
                    metadatas=batch_metas,
                )
        else:
            # local: sentence-transformers
            model = _get_st_model()
            for batch_start in range(0, len(documents), BATCH_SIZE):
                batch_docs = documents[batch_start:batch_start + BATCH_SIZE]
                batch_ids = ids[batch_start:batch_start + BATCH_SIZE]
                batch_metas = metadatas[batch_start:batch_start + BATCH_SIZE]

                batch_embeddings = model.encode(batch_docs).tolist()

                collection.upsert(
                    ids=batch_ids,
                    embeddings=batch_embeddings,
                    documents=batch_docs,
                    metadatas=batch_metas,
                )

        print(f"  ✓ {filepath.name}: {len(chunks)} chunks indexed")
        total_chunks += len(chunks)
        total_docs += 1

    print(f"\nHoàn thành! Đã index {total_docs} tài liệu → {total_chunks} chunks")


# =============================================================================
# STEP 4: INSPECT / KIỂM TRA
# Dùng để debug và kiểm tra chất lượng index
# =============================================================================

def list_chunks(db_dir: Path = CHROMA_DB_DIR, n: int = 5) -> None:
    """
    In ra n chunk đầu tiên trong ChromaDB để kiểm tra chất lượng index.

    TODO Sprint 1:
    Implement sau khi hoàn thành build_index().
    Kiểm tra:
    - Chunk có giữ đủ metadata không? (source, section, effective_date)
    - Chunk có bị cắt giữa điều khoản không?
    - Metadata effective_date có đúng không?
    """
    try:
        import chromadb
        client = chromadb.PersistentClient(path=str(db_dir))
        collection = client.get_collection("rag_lab")
        results = collection.get(limit=n, include=["documents", "metadatas"])

        print(f"\n=== Top {n} chunks trong index ===\n")
        for i, (doc, meta) in enumerate(zip(results["documents"], results["metadatas"])):
            print(f"[Chunk {i+1}]")
            print(f"  Source: {meta.get('source', 'N/A')}")
            print(f"  Section: {meta.get('section', 'N/A')}")
            print(f"  Effective Date: {meta.get('effective_date', 'N/A')}")
            print(f"  Text preview: {doc[:120]}...")
            print()
    except Exception as e:
        print(f"Lỗi khi đọc index: {e}")
        print("Hãy chạy build_index() trước.")


def inspect_metadata_coverage(db_dir: Path = CHROMA_DB_DIR) -> None:
    """
    Kiểm tra phân phối metadata trong toàn bộ index.

    Checklist Sprint 1:
    - Mọi chunk đều có source?
    - Có bao nhiêu chunk từ mỗi department?
    - Chunk nào thiếu effective_date?

    TODO: Implement sau khi build_index() hoàn thành.
    """
    try:
        import chromadb
        client = chromadb.PersistentClient(path=str(db_dir))
        collection = client.get_collection("rag_lab")
        results = collection.get(include=["metadatas"])

        print(f"\nTổng chunks: {len(results['metadatas'])}")

        # TODO: Phân tích metadata
        # Đếm theo department, kiểm tra effective_date missing, v.v.
        departments = {}
        missing_date = 0
        for meta in results["metadatas"]:
            dept = meta.get("department", "unknown")
            departments[dept] = departments.get(dept, 0) + 1
            if meta.get("effective_date") in ("unknown", "", None):
                missing_date += 1

        print("Phân bố theo department:")
        for dept, count in departments.items():
            print(f"  {dept}: {count} chunks")
        print(f"Chunks thiếu effective_date: {missing_date}")

    except Exception as e:
        print(f"Lỗi: {e}. Hãy chạy build_index() trước.")


# =============================================================================
# MAIN
# =============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("Sprint 1: Build RAG Index")
    print("=" * 60)

    # Bước 1: Kiểm tra docs
    doc_files = list(DOCS_DIR.glob("*.txt"))
    print(f"\nTìm thấy {len(doc_files)} tài liệu:")
    for f in doc_files:
        print(f"  - {f.name}")

    # Bước 2: Test preprocess và chunking
    print("\n--- Test preprocess + chunking ---")
    for filepath in doc_files:
        raw = filepath.read_text(encoding="utf-8")
        doc = preprocess_document(raw, str(filepath))
        chunks = chunk_document(doc)
        print(f"\nFile: {filepath.name}")
        print(f"  Metadata: {doc['metadata']}")
        print(f"  Số chunks: {len(chunks)}")
        for i, chunk in enumerate(chunks[:3]):
            print(f"\n  [Chunk {i+1}] Section: {chunk['metadata']['section']}")
            print(f"  Text: {chunk['text'][:150]}...")
        if len(chunks) > 3:
            print(f"\n  ... và {len(chunks) - 3} chunk(s) nữa")

    # Bước 3: Build full index (embed + store)
    print("\n--- Build Full Index ---")
    build_index()
