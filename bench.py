"""
Benchmark script for Lab 7 — Chính sách đổi trả, bảo hành Shopee Việt Nam.

Reads .md files from data/ecommerce/, parses frontmatter into metadata,
chunks content, loads into EmbeddingStore, and runs 5 benchmark queries.

Usage:
    python bench.py
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

# Fix Windows console encoding
if sys.stdout.encoding != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8")

from src.chunking import RecursiveChunker
from src.models import Document
from src.store import EmbeddingStore
from src.agent import KnowledgeBaseAgent
from src.embeddings import _mock_embed


# ---------------------------------------------------------------------------
# 1. Parse frontmatter + content from .md files
# ---------------------------------------------------------------------------

def parse_md_file(path: Path) -> tuple[dict, str]:
    """Parse YAML frontmatter and body content from a .md file."""
    raw = path.read_text(encoding="utf-8")

    # Split on --- markers
    if raw.startswith("---"):
        parts = raw.split("---", 2)
        if len(parts) >= 3:
            fm_block = parts[1]
            body = parts[2].strip()
        else:
            fm_block = ""
            body = raw
    else:
        fm_block = ""
        body = raw

    # Parse simple YAML key: value pairs
    metadata = {}
    for match in re.finditer(r'^(\w[\w_-]*):\s*(.+)$', fm_block, re.MULTILINE):
        key = match.group(1)
        value = match.group(2).strip().strip('"').strip("'")
        # Remove inline comments
        if "#" in value:
            value = value.split("#")[0].strip()
        metadata[key] = value

    return metadata, body


# ---------------------------------------------------------------------------
# 2. Load, chunk, and ingest documents
# ---------------------------------------------------------------------------

def load_and_ingest(data_dir: Path, store: EmbeddingStore, chunker) -> int:
    """Load .md files, chunk content, ingest into store. Returns total chunks."""
    md_files = sorted(data_dir.glob("*.md"))
    total_chunks = 0

    for path in md_files:
        metadata, body = parse_md_file(path)
        doc_id = metadata.get("doc_id", path.stem)

        # Chunk the body content
        chunks = chunker.chunk(body)

        # Create a Document for each chunk with full metadata
        for i, chunk_text in enumerate(chunks):
            doc = Document(
                id=f"{doc_id}#{i}",
                content=chunk_text,
                metadata={**metadata, "doc_id": doc_id},
            )
            store.add_documents([doc])
            total_chunks += 1

    return total_chunks


# ---------------------------------------------------------------------------
# 3. Benchmark queries and gold answers
# ---------------------------------------------------------------------------

BENCHMARK_QUERIES = [
    {
        "id": 1,
        "query": "Người mua có bao nhiêu ngày để gửi yêu cầu trả hàng trên Shopee?",
        "gold_answer": "15 ngày đối với Shopee Mall; 3 ngày (tối đa 7 ngày) đối với Shop Yêu thích hoặc Shop thông thường kể từ ngày nhận hàng",
        "gold_keywords": ["15 ngày", "Shopee Mall", "3 ngày"],
        "metadata_filter": None,
        "expected_doc": "shopee-return-refund-buyer",
    },
    {
        "id": 2,
        "query": "Những nhóm sản phẩm nào thuộc danh mục ngoại lệ không áp dụng đổi trả và hoàn tiền?",
        "gold_answer": "Đồ lót/đồ bơi bóc seal, thực phẩm tươi sống, dược phẩm/sữa công thức mở nắp, và sản phẩm số/thẻ cào điện tử",
        "gold_keywords": ["Đồ lót", "thực phẩm", "sản phẩm số"],
        "metadata_filter": None,
        "expected_doc": "prohibited-returns-policy",
    },
    {
        "id": 3,
        "query": "Người bán trên Shopee phải phản hồi yêu cầu trả hàng trong bao lâu và nếu quá hạn thì sao?",
        "gold_answer": "Người bán có tối đa 48 giờ để phản hồi; quá 48 giờ Shopee sẽ tự động chấp thuận hoàn tiền toàn bộ cho Người mua",
        "gold_keywords": ["48 giờ", "tự động", "hoàn tiền"],
        "metadata_filter": {"audience": "seller"},
        "expected_doc": "shopee-warranty-seller",
    },
    {
        "id": 4,
        "query": "Tiki hỗ trợ những phương thức bảo hành thiết bị điện tử nào và thời gian xử lý là bao lâu?",
        "gold_answer": "Bảo hành tại Trung tâm Bảo hành của Hãng hoặc gửi qua Tiki tiếp nhận tận nhà (thời gian xử lý 7 đến 14 ngày làm việc)",
        "gold_keywords": ["Trung tâm Bảo hành", "Tiki tiếp nhận", "7 đến 14 ngày"],
        "metadata_filter": None,
        "expected_doc": "tiki-warranty-policy-buyer",
    },
    {
        "id": 5,
        "query": "Nhà bán hàng TikTok Shop cần cung cấp những bằng chứng gì khi khiếu nại quyết định hoàn tiền?",
        "gold_answer": "Bộ ba chứng cứ: Video đóng gói kiện hàng ban đầu, video unboxing mở bưu kiện hoàn trả 6 mặt hộp, và biên bản đồng kiểm có chữ ký nhân viên giao nhận",
        "gold_keywords": ["Video", "đóng gói", "đồng kiểm"],
        "metadata_filter": {"audience": "seller"},
        "expected_doc": "tiktok-shop-seller-dispute",
    },
]


# ---------------------------------------------------------------------------
# 4. Run benchmark
# ---------------------------------------------------------------------------

def run_benchmark(output_file: str | None = None):
    """Run all benchmark queries and print/save results."""
    lines: list[str] = []

    def log(msg: str = ""):
        print(msg)
        lines.append(msg)

    log("=" * 70)
    log("BENCHMARK — Chính sách đổi trả, bảo hành Shopee Việt Nam")
    log("=" * 70)
    log(f"Embedding backend: MockEmbedder (hash-based, no semantics)")
    log()

    # Setup
    chunker = RecursiveChunker(chunk_size=500)
    store = EmbeddingStore(collection_name="benchmark", embedding_fn=_mock_embed)
    data_dir = Path("data/ecommerce")

    total_chunks = load_and_ingest(data_dir, store, chunker)
    log(f"Loaded {total_chunks} chunks from {len(list(data_dir.glob('*.md')))} files")
    log()

    # Mock LLM for agent
    def mock_llm(prompt: str) -> str:
        preview = prompt[:500].replace("\n", " ")
        return f"[Mock LLM] {preview}..."

    agent = KnowledgeBaseAgent(store=store, llm_fn=mock_llm)

    # Run queries
    total_score = 0

    for bq in BENCHMARK_QUERIES:
        log("-" * 70)
        log(f"Query {bq['id']}: {bq['query']}")
        log(f"Gold Answer: {bq['gold_answer']}")
        log(f"Expected Doc: {bq['expected_doc']}")

        if bq["metadata_filter"]:
            log(f"Filter: {bq['metadata_filter']}")
            results = store.search_with_filter(
                bq["query"],
                top_k=3,
                metadata_filter=bq["metadata_filter"],
            )
        else:
            results = store.search(bq["query"], top_k=3)

        log(f"\nTop-3 Results:")
        found_relevant = False
        for i, r in enumerate(results, 1):
            doc_id = r["metadata"].get("doc_id", "?")
            score = r["score"]
            content_preview = r["content"][:120].replace("\n", " ")
            is_relevant = doc_id == bq["expected_doc"] or doc_id.startswith(f"{bq['expected_doc']}#")
            marker = " ✓ RELEVANT" if is_relevant else ""
            log(f"  [{i}] score={score:.4f} doc_id={doc_id}{marker}")
            log(f"      {content_preview}...")
            if is_relevant:
                found_relevant = True

        # Check if gold keywords appear in retrieved context
        all_context = " ".join(r["content"] for r in results)
        keywords_found = [kw for kw in bq["gold_keywords"] if kw in all_context]

        # Scoring: 2=top-1 relevant + keywords found, 1=relevant in top-3, 0=not found
        top1_doc_id = results[0]["metadata"].get("doc_id", "") if results else ""
        top1_matches = top1_doc_id == bq["expected_doc"] or top1_doc_id.startswith(f"{bq['expected_doc']}#")
        if results and top1_matches and keywords_found:
            score = 2
        elif found_relevant:
            score = 1
        else:
            score = 0
        total_score += score

        log(f"\n  Keywords found in context: {keywords_found}")
        log(f"  Score: {score}/2")
        log()

    # A/B test: Query 3 with and without filter
    log("=" * 70)
    log("A/B TEST — Query 3: Có filter vs. Không filter")
    log("=" * 70)

    # Without filter
    results_no_filter = store.search(BENCHMARK_QUERIES[2]["query"], top_k=3)
    log("\n[A] Không dùng metadata_filter:")
    for i, r in enumerate(results_no_filter, 1):
        doc_id = r["metadata"].get("doc_id", "?")
        audience = r["metadata"].get("audience", "?")
        log(f"  [{i}] doc_id={doc_id} audience={audience} score={r['score']:.4f}")

    # With filter
    results_with_filter = store.search_with_filter(
        BENCHMARK_QUERIES[2]["query"], top_k=3,
        metadata_filter={"audience": "seller"},
    )
    log("\n[B] Dùng metadata_filter={'audience': 'seller'}:")
    for i, r in enumerate(results_with_filter, 1):
        doc_id = r["metadata"].get("doc_id", "?")
        audience = r["metadata"].get("audience", "?")
        log(f"  [{i}] doc_id={doc_id} audience={audience} score={r['score']:.4f}")

    # Compare
    a_has_seller = any(
        r["metadata"].get("audience") == "seller" for r in results_no_filter
    )
    b_all_seller = all(
        r["metadata"].get("audience") == "seller" for r in results_with_filter
    )
    log(f"\n  [A] Has seller docs in top-3: {a_has_seller}")
    log(f"  [B] All seller docs in top-3: {b_all_seller}")
    log(f"  Filter giúp loại bỏ tài liệu buyer khỏi kết quả: {'Có' if b_all_seller and not a_has_seller else 'Có (khi có kết quả buyer lẫn)' if b_all_seller else 'Không rõ với MockEmbedder'}")

    # Summary
    log()
    log("=" * 70)
    log("TỔNG KẾT")
    log("=" * 70)
    log(f"Tổng điểm: {total_score}/10")
    log()

    # Failure case analysis
    log("=" * 70)
    log("PHÂN TÍCH LỖI (FAILURE CASE)")
    log("=" * 70)
    log()
    log("Failure Case: MockEmbedder không mã hóa ngữ nghĩa")
    log()
    log("Mô tả: MockEmbedder sử dụng băm MD5 để sinh vector giả ngẫu nhiên,")
    log("do đó điểm similarity giữa query và chunk KHÔNG phản ánh mức độ liên quan")
    log("về nội dung. Kết quả top-3 gần như ngẫu nhiên.")
    log()
    log("Biểu hiện cụ thể:")
    log("- Chunk đúng chủ đề nhưng có thể xếp hạng thấp hơn chunk không liên quan.")
    log("- Score có thể âm cho chunk chứa đáp án chính xác.")
    log("- Cosine similarity đo ở đây thực chất là similarity giữa hash values,")
    log("  không phải giữa ngữ nghĩa của văn bản.")
    log()
    log("Đề xuất cải thiện:")
    log("1. Sử dụng embedder thật (LocalEmbedder hoặc GeminiEmbedder) để có")
    log("   vector ngữ nghĩa, giúp retrieval chính xác hơn.")
    log("2. Với MockEmbedder, nên đánh giá dựa trên count/avg_length/tính mạch")
    log("   lạc của chunk thay vì dựa vào score.")
    log("3. Metadata filter vẫn hoạt động đúng ngay cả với MockEmbedder vì")
    log("   filter dựa trên exact match, không phụ thuộc embedding.")
    log()

    # Save to file
    if output_file:
        Path(output_file).write_text("\n".join(lines), encoding="utf-8")
        print(f"\nKết quả đã lưu vào: {output_file}")


if __name__ == "__main__":
    run_benchmark(output_file="ket_qua_benchmark.txt")
