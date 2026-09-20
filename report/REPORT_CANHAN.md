# Báo Cáo Cá Nhân — Lab 7: Embedding & Vector Store

**Họ tên:** Dương Phương Hiểu  
**Mã sinh viên:** 2A202603008  
**Lớp / Nhóm:** Nhóm E-Commerce Policy L3B  
**Ngày:** 20/09/2026  

> **Nộp 1 bản / sinh viên.** Phần nhóm (lựa chọn tài liệu, thiết kế chiến lược, bộ câu hỏi đánh giá, demo) nộp chung 1 bản trong `REPORT_NHOM.md`. Chi tiết thang điểm: `docs/SCORING.md`.

**Tổng điểm phần cá nhân: 60** = Khởi động (5) + Hướng tiếp cận (10) + Hoàn thiện code (30) + Dự đoán độ tương tự (5) + Kết quả truy xuất của tôi (10).

---

## 1. Khởi động (Warm-up) — Cá nhân (5 điểm)

### Độ tương tự Cosine (Cosine Similarity) (Bài tập 1.1)

**Độ tương tự cosine cao (High cosine similarity) nghĩa là gì?**
> Độ tương tự cosine cao (tiệm cận 1.0) thể hiện hai vector biểu diễn văn bản cùng trỏ về một hướng trong không gian embedding đa chiều (góc giữa chúng tiệm cận 0 độ). Điều này có nghĩa là hai đoạn văn bản có mức độ tương đồng ngữ nghĩa rất cao, cùng chia sẻ ngữ cảnh hoặc cùng nói về một chủ đề/khái niệm, bất kể sự khác biệt về độ dài câu hay từ ngữ bề mặt.

**Ví dụ có độ tương tự CAO:**
- Câu A: "Shopee hỗ trợ người mua trả hàng và hoàn tiền trong vòng 15 ngày đối với các đơn hàng thuộc gian hàng Shopee Mall."
- Câu B: "Khách hàng mua sắm tại Shopee Mall có quyền gửi yêu cầu đổi trả, nhận lại tiền trong thời hạn tối đa 15 ngày."
- Tại sao tương đồng: Cả hai câu đều truyền tải cùng một chính sách cụ thể (quyền đổi trả/hoàn tiền 15 ngày tại Shopee Mall). Các cụm từ đồng nghĩa ("người mua" ↔ "khách hàng", "hỗ trợ" ↔ "có quyền", "trả hàng và hoàn tiền" ↔ "đổi trả, nhận lại tiền") được ánh xạ về cùng một vùng không gian ngữ nghĩa.

**Ví dụ có độ tương tự THẤP:**
- Câu A: "Nhà bán hàng trên sàn thương mại điện tử có tối đa 48 giờ để phản hồi yêu cầu khiếu nại trả hàng."
- Câu B: "Tiki tiếp nhận bảo hành thiết bị điện gia dụng và hỗ trợ lấy hàng sửa chữa tận nơi cho người tiêu dùng."
- Tại sao khác: Hai câu hướng đến hai đối tượng hoàn toàn khác nhau (nghĩa vụ của người bán vs quyền lợi dịch vụ của người mua) và hai quy trình nghiệp vụ độc lập (xử lý tranh chấp khiếu nại đơn hàng vs dịch vụ bảo hành sửa chữa thiết bị điện gia dụng), không chia sẻ ngữ cảnh hoạt động.

**Tại sao độ tương tự cosine (cosine similarity) được ưu tiên hơn khoảng cách Euclid (Euclidean distance) cho text embeddings?**
> Độ tương tự cosine chỉ đo góc định hướng giữa hai vector mà không bị phụ thuộc vào độ lớn (magnitude/norm) do độ dài văn bản tạo ra. Khi so sánh một câu ngắn gọn với một đoạn văn dài có cùng nội dung, khoảng cách Euclid sẽ rất lớn do độ dài vector khác nhau (dễ dẫn tới đánh giá sai là không giống nhau), trong khi cosine similarity chuẩn hóa độ dài và chỉ đo hướng ngữ nghĩa, giúp phản ánh trung thực mức độ tương đồng nội dung.

### Bài toán tính toán Chunking (Bài tập 1.2)

**Tài liệu 10,000 ký tự, chunk_size=500, overlap=50. Bao nhiêu chunks?**
> *Trình bày phép tính:*
> - Kích thước mỗi chunk ($L$) = 500 ký tự.
> - Độ chồng chéo ($overlap$) = 50 ký tự.
> - Bước nhảy (stride/step size) giữa các chunk liên tiếp: $S = L - overlap = 500 - 50 = 450$ ký tự.
> - Chunk 1 bao phủ đoạn ký tự $[0, 500)$.
> - Phần văn bản còn lại sau chunk đầu tiên: $10,000 - 500 = 9,500$ ký tự.
> - Số chunk bổ sung cần thiết: $\lceil 9,500 / 450 \rceil = \lceil 21.111... \rceil = 22$ chunk.
> - Tổng số chunk: $1 + 22 = 23$ chunk.  
> *(Hoặc theo công thức tổng quát: $N = \lceil \frac{Total - overlap}{chunk\_size - overlap} \rceil = \lceil \frac{10,000 - 50}{500 - 50} \rceil = \lceil \frac{9,950}{450} \rceil = \lceil 22.111... \rceil = 23$ chunks).*
> *Đáp án:* **23 chunks**.

**Nếu độ chồng chéo (overlap) tăng lên 100, số lượng chunk thay đổi thế nào? Tại sao muốn độ chồng chéo nhiều hơn?**
> - Khi overlap tăng lên 100 ký tự, bước nhảy giảm xuống $S = 500 - 100 = 400$ ký tự. Số lượng chunk sẽ tăng lên: $1 + \lceil (10,000 - 500) / 400 \rceil = 1 + \lceil 23.75 \rceil = 1 + 24 = 25$ chunks (tăng thêm 2 chunks).
> - Chúng ta muốn độ chồng chéo nhiều hơn để bảo toàn tính liên tục của ngữ cảnh (context preservation). Khi văn bản bị cắt giữa câu hoặc giữa một điều khoản và điều kiện ràng buộc của nó, phần overlap gối đầu đảm bảo thông tin quan trọng (như mốc thời gian 48 giờ, danh mục ngoại lệ) không bị xé rách giữa 2 chunk rời rạc, giúp mô hình embedding và retrieval không bị mất thông tin ngữ cảnh.

---

## 2. Hướng tiếp cận của tôi (My Approach) — Cá nhân (10 điểm)

Giải thích cách tiếp cận của bạn khi lập trình (implement) các phần chính trong gói `src`.

### Các hàm chia nhỏ (Chunking Functions)

**`SentenceChunker.chunk`** — hướng tiếp cận:
> Sử dụng biểu thức chính quy Lookbehind `r'(?<=[.!?])\s+'` kết hợp nhận diện ký tự xuống dòng `\n+` để tách câu tự nhiên dựa trên dấu chấm, dấu chấm than, chấm hỏi mà không làm vỡ các trường hợp số thực hay từ viết tắt. Sau đó, gom các câu liên tiếp theo cửa sổ trượt (sliding window) với dung lượng tối đa `max_sentences`; nếu chỉ định `overlap_sentences > 0`, thuật toán bước lùi lại để giữ lại các câu cuối làm gối đầu cho chunk kế tiếp. Xử lý các edge case như chuỗi văn bản rỗng, khoảng trắng thừa (strip sạch) và trường hợp toàn bộ văn bản chỉ có 1 câu duy nhất.

**`RecursiveChunker.chunk` / `_split`** — hướng tiếp cận:
> Áp dụng thuật toán đệ quy chia để trị (divide-and-conquer) với danh sách ký tự phân cách phân tầng theo thứ tự ưu tiên giảm dần: đoạn văn (`"\n\n"`), xuống dòng (`"\n"`), hết câu (`". "`), từ (`" "`), và ký tự rỗng fallback (`""`). Base case là khi độ dài đoạn văn bản hiện tại $\le chunk\_size$ hoặc danh sách separators đã cạn kiệt thì trả về chính đoạn đó. Ở mỗi bước, văn bản được tách bằng separator hiện tại, sau đó duyệt qua từng phần tử để gom nhóm (merge) lại thành các chunk lớn nhất có thể không vượt quá `chunk_size`; nếu một phần tử đơn lẻ vẫn lớn hơn `chunk_size`, thuật toán đệ quy gọi `_split` với separator mức sâu hơn.

### Lớp EmbeddingStore

**`add_documents` + `search`** — hướng tiếp cận:
> Lưu trữ hoàn toàn in-memory dưới dạng danh sách các bản ghi (list of dicts) trong `self._store`. Mỗi khi `add_documents` được gọi, phương thức sao chép trường metadata (tránh side-effect), đồng bộ `metadata["doc_id"] = doc.id`, sinh vector embedding qua `self._embedding_fn` và append vào store. Khi `search`, hàm mã hóa query thành vector `query_embedding`, sau đó tính tích vô hướng (dot product) với từng vector tài liệu đã lưu (vì vector đã được L2-normalized nên tích vô hướng tương đương chính xác với Cosine Similarity), cuối cùng sắp xếp giảm dần theo điểm số để trích xuất `top_k` kết quả.

**`search_with_filter` + `delete_document`** — hướng tiếp cận:
> Triển khai kỹ thuật lọc trước (Pre-filtering) để tối ưu hiệu năng và độ chính xác: duyệt qua toàn bộ kho bản ghi và đối chiếu từng cặp khóa-giá trị trong `metadata_filter`; chỉ những bản ghi thỏa mãn chính xác toàn bộ điều kiện lọc mới được đưa vào bước tính điểm similarity và xếp hạng top-k. Đối với `delete_document`, sử dụng list comprehension để lọc giữ lại những bản ghi có `metadata["doc_id"] != doc_id`, so sánh độ dài danh sách trước và sau khi lọc để trả về `True` nếu có ít nhất một chunk bị xóa, hoặc `False` nếu không tìm thấy `doc_id`.

### Tác tử KnowledgeBaseAgent

**`answer`** — hướng tiếp cận:
> Thiết kế system prompt nghiêm ngặt đóng vai trò trợ lý hỏi đáp thông minh chỉ dựa trên ngữ cảnh thực tế: yêu cầu trích dẫn rõ nguồn `[1]`, `[2]`, `[3]` cho từng luận điểm và bắt buộc thừa nhận không tìm thấy thông tin nếu ngữ cảnh không đủ (chống hallucination). Cách inject context: gọi `EmbeddingStore.search()` (hoặc `search_with_filter()` nếu có filter) để lấy top-k kết quả, ghép các đoạn nội dung kèm số thứ tự và đường dẫn nguồn file thành khối "Ngữ cảnh:" thống nhất, sau đó chèn vào prompt template gửi tới `llm_fn`.

---

## 3. Hoàn thiện code (Core Implementation) — Cá nhân (30 điểm)

Vượt qua bộ kiểm thử là điều kiện tính điểm phần này.

### Kết Quả Kiểm Thử (Test Results)

```
============================= test session starts =============================
platform win32 -- Python 3.11.5, pytest-9.1.1, pluggy-1.6.0
rootdir: D:\ASUS\Courses\VinAI\K4-DAY07-DuongPhuongHieu-2A202603008
plugins: anyio-4.9.0, langsmith-0.3.45, asyncio-1.1.0, repeat-0.9.4, rerunfailures-12.0, xdist-3.8.0
asyncio: mode=Mode.STRICT, asyncio_default_fixture_loop_scope=None, asyncio_default_test_loop_scope=function
collected 42 items

tests/test_solution.py::TestProjectStructure::test_root_main_entrypoint_exists PASSED [  2%]
tests/test_solution.py::TestProjectStructure::test_src_package_exists PASSED [  4%]
tests/test_solution.py::TestClassBasedInterfaces::test_chunker_classes_exist PASSED [  7%]
tests/test_solution.py::TestClassBasedInterfaces::test_mock_embedder_exists PASSED [  9%]
tests/test_solution.py::TestFixedSizeChunker::test_chunks_respect_size PASSED [ 11%]
tests/test_solution.py::TestFixedSizeChunker::test_correct_number_of_chunks_no_overlap PASSED [ 14%]
tests/test_solution.py::TestFixedSizeChunker::test_empty_text_returns_empty_list PASSED [ 16%]
tests/test_solution.py::TestFixedSizeChunker::test_no_overlap_no_shared_content PASSED [ 19%]
tests/test_solution.py::TestFixedSizeChunker::test_overlap_creates_shared_content PASSED [ 21%]
tests/test_solution.py::TestFixedSizeChunker::test_returns_list PASSED   [ 23%]
tests/test_solution.py::TestFixedSizeChunker::test_single_chunk_if_text_shorter PASSED [ 26%]
tests/test_solution.py::TestSentenceChunker::test_chunks_are_strings PASSED [ 28%]
tests/test_solution.py::TestSentenceChunker::test_respects_max_sentences PASSED [ 30%]
tests/test_solution.py::TestSentenceChunker::test_returns_list PASSED    [ 33%]
tests/test_solution.py::TestSentenceChunker::test_single_sentence_max_gives_many_chunks PASSED [ 35%]
tests/test_solution.py::TestRecursiveChunker::test_chunks_within_size_when_possible PASSED [ 38%]
tests/test_solution.py::TestRecursiveChunker::test_empty_separators_falls_back_gracefully PASSED [ 40%]
tests/test_solution.py::TestRecursiveChunker::test_handles_double_newline_separator PASSED [ 42%]
tests/test_solution.py::TestRecursiveChunker::test_returns_list PASSED   [ 45%]
tests/test_solution.py::TestEmbeddingStore::test_add_documents_increases_size PASSED [ 47%]
tests/test_solution.py::TestEmbeddingStore::test_add_more_increases_further PASSED [ 50%]
tests/test_solution.py::TestEmbeddingStore::test_initial_size_is_zero PASSED [ 52%]
tests/test_solution.py::TestEmbeddingStore::test_search_results_have_content_key PASSED [ 54%]
tests/test_solution.py::TestEmbeddingStore::test_search_results_have_score_key PASSED [ 57%]
tests/test_solution.py::TestEmbeddingStore::test_search_results_sorted_by_score_descending PASSED [ 59%]
tests/test_solution.py::TestEmbeddingStore::test_search_returns_at_most_top_k PASSED [ 61%]
tests/test_solution.py::TestEmbeddingStore::test_search_returns_list PASSED [ 64%]
tests/test_solution.py::TestKnowledgeBaseAgent::test_answer_non_empty PASSED [ 66%]
tests/test_solution.py::TestKnowledgeBaseAgent::test_answer_returns_string PASSED [ 69%]
tests/test_solution.py::TestComputeSimilarity::test_identical_vectors_return_1 PASSED [ 71%]
tests/test_solution.py::TestComputeSimilarity::test_opposite_vectors_return_minus_1 PASSED [ 73%]
tests/test_solution.py::TestComputeSimilarity::test_orthogonal_vectors_return_0 PASSED [ 76%]
tests/test_solution.py::TestComputeSimilarity::test_zero_vector_returns_0 PASSED [ 78%]
tests/test_solution.py::TestCompareChunkingStrategies::test_counts_are_positive PASSED [ 80%]
tests/test_solution.py::TestCompareChunkingStrategies::test_each_strategy_has_count_and_avg_length PASSED [ 83%]
tests/test_solution.py::TestCompareChunkingStrategies::test_returns_three_strategies PASSED [ 85%]
tests/test_solution.py::TestEmbeddingStoreSearchWithFilter::test_filter_by_department PASSED [ 88%]
tests/test_solution.py::TestEmbeddingStoreSearchWithFilter::test_no_filter_returns_all_candidates PASSED [ 90%]
tests/test_solution.py::TestEmbeddingStoreSearchWithFilter::test_returns_at_most_top_k PASSED [ 92%]
tests/test_solution.py::TestEmbeddingStoreDeleteDocument::test_delete_reduces_collection_size PASSED [ 95%]
tests/test_solution.py::TestEmbeddingStoreDeleteDocument::test_delete_returns_false_for_nonexistent_doc PASSED [ 97%]
tests/test_solution.py::TestEmbeddingStoreDeleteDocument::test_delete_returns_true_for_existing_doc PASSED [100%]

============================= 42 passed in 0.06s ==============================
```

**Số lượng bài test vượt qua (pass):** **42 / 42**

---

## 4. Dự đoán độ tương tự (Similarity Predictions) — Cá nhân (5 điểm)

| Cặp | Câu A | Câu B | Dự đoán | Điểm thực tế | Đúng? |
|:---:|:------|:------|:-------:|:------------:|:-----:|
| 1 | Người mua Shopee Mall có quyền trả hàng trong 15 ngày kể từ khi nhận. | Thời hạn gửi yêu cầu hoàn tiền cho đơn hàng Shopee Mall là 15 ngày. | cao | -0.0222 | Sai (bất ngờ) |
| 2 | Sản phẩm đồ lót và đồ bơi bị bóc seal không được đổi trả. | Các mặt hàng vệ sinh cá nhân và đồ lót mở bao bì thuộc danh mục cấm trả hàng. | cao | -0.1417 | Sai (bất ngờ) |
| 3 | Người bán trên Shopee có 48 giờ để phản hồi yêu cầu trả hàng của khách. | Tiki hỗ trợ lấy hàng bảo hành tận nhà với thời gian xử lý 7 đến 14 ngày. | thấp | -0.0430 | Đúng |
| 4 | TikTok Shop yêu cầu video unboxing 6 mặt hộp khi người bán khiếu nại. | Nhà bán hàng TikTok Shop cần video mở kiện hàng thấy rõ 6 mặt để tranh chấp. | cao | +0.1238 | Đúng |
| 5 | Bảo hành sản phẩm điện tử Tiki từ 12 đến 36 tháng. | Trang phục dạ hội và thời trang dự tiệc cao cấp tại Hà Nội. | thấp | +0.0098 | Đúng |

**Kết quả nào bất ngờ nhất? Điều này nói gì về cách embeddings biểu diễn ý nghĩa?**
> Kết quả bất ngờ nhất là ở **Cặp 1** và **Cặp 2**: đây là hai cặp câu hoàn toàn đồng nghĩa về mặt ngữ nghĩa tiếng Việt (thời hạn 15 ngày đổi trả Shopee Mall và quy định cấm đổi trả đồ lót bóc seal), nhưng điểm tương tự thực tế lại mang giá trị **âm** (-0.0222 và -0.1417). Ngược lại, Cặp 5 nói về hai chủ đề hoàn toàn không liên quan lại có điểm dương (+0.0098).
> Điều này phơi bày rõ hạn chế cốt tử của `MockEmbedder`: thuật toán chỉ băm chuỗi ký tự theo mã băm MD5 giả lập để tạo vector phân tán ngẫu nhiên trên mặt cầu đơn vị, hoàn toàn không học được tri thức ngữ nghĩa hay mối quan hệ đồng nghĩa giữa các từ ngữ. Để biểu diễn ý nghĩa văn bản thực sự, hệ thống RAG bắt buộc phải sử dụng các mô hình Neural Embedding được huấn luyện trước trên kho ngữ liệu lớn (như OpenAI text-embedding-3-small, Gemini Embedding, hay multilingual-e5).

---

## 5. Kết quả truy xuất của tôi (Competition Results) — Cá nhân (10 điểm)

Chạy **5 câu hỏi đánh giá của nhóm** trên mã nguồn cá nhân của bạn trong gói `src`. **5 câu hỏi này phải trùng với các thành viên cùng nhóm** (xem `REPORT_NHOM.md`).

| # | Câu hỏi (Query) | Top-1 Chunk truy xuất được (tóm tắt) | Điểm Score | Có liên quan không? (Relevant) | Câu trả lời của Agent (tóm tắt) |
|---|-----------------|--------------------------------------|:----------:|:-----------------------------:|---------------------------------|
| 1 | Người mua có bao nhiêu ngày để gửi yêu cầu trả hàng trên Shopee? | `tiki-warranty-policy-buyer#3` (Từ chối bảo hành do rơi vỡ, nứt móp Tiki) | 0.2639 | Không | Trả lời trích dẫn chính sách từ chối bảo hành của Tiki thay vì Shopee |
| 2 | Những nhóm sản phẩm nào thuộc danh mục ngoại lệ không áp dụng đổi trả và hoàn tiền? | `lazada-return-policy-buyer#0` (Chính sách Đổi trả và Hoàn tiền Lazada) | 0.2285 | Không | Trả lời trích dẫn thời hạn đổi trả Lazada thay vì danh mục cấm đổi trả |
| 3 | Người bán trên Shopee phải phản hồi yêu cầu trả hàng trong bao lâu và nếu quá hạn thì sao? *(filter: audience=seller)* | `tiktok-shop-seller-dispute#2` (Video unboxing mở bưu kiện hoàn trả TikTok) | 0.1449 | Có (đúng miền seller, có context mốc thời gian) | Trả lời trích dẫn quy trình người bán xử lý tranh chấp và thời hạn xử lý |
| 4 | Tiki hỗ trợ những phương thức bảo hành thiết bị điện tử nào và thời gian xử lý là bao lâu? | `lazada-return-policy-buyer#1` (Thời hạn đổi trả theo kênh bán lẻ Lazada) | 0.1959 | Không | Trả lời trích dẫn chính sách LazMall 30 ngày |
| 5 | Nhà bán hàng TikTok Shop cần cung cấp những bằng chứng gì khi khiếu nại quyết định hoàn tiền? *(filter: audience=seller)* | `shopee-warranty-seller#0` (Quy định Bảo hành Shopee); Top-2: `tiktok-shop-seller-dispute#2` (0.1329 ✓ RELEVANT) | 0.2151 (Top-1) | Có (Top-2 chứa đúng bộ ba bằng chứng: video đóng gói, unboxing 6 mặt, biên bản đồng kiểm) | Trả lời trích dẫn đầy đủ video unboxing 6 mặt hộp và biên bản đồng kiểm giao nhận |

**Bao nhiêu câu hỏi trả về chunk có liên quan trong top-3?** **2 / 5** *(Câu 3 và Câu 5 đạt kết quả nhờ có bộ lọc `metadata_filter={'audience': 'seller'}` loại bỏ toàn bộ dữ liệu người mua).*

**Điều hay nhất tôi học được từ thành viên khác / nhóm khác (qua demo):**
> 1. **Sức mạnh then chốt của Metadata Filtering**: Trong các bài toán nghiệp vụ TMĐT có cấu trúc phức tạp và nhiều bên tham gia (người mua vs người bán), metadata filter hoạt động dựa trên logic lọc chính xác (deterministic exact match), giúp loại bỏ triệt để tài liệu sai đối tượng trước khi xếp hạng similarity. Nhờ đó, ngay cả khi backend embedding là Mock, các câu hỏi có metadata filter vẫn đưa ra kết quả sát thực tế.
> 2. **Ý nghĩa của chiến lược RecursiveChunker**: So với Fixed-size cắt cứng cơ học dễ làm cụt câu hay SentenceChunker gom câu cứng nhắc, RecursiveChunker tôn trọng cấu trúc phân đoạn tự nhiên của văn bản pháp lý/chính sách (tách theo đề mục `##`, danh sách gạch đầu dòng `-`, ngắt câu `. `), giúp chunk giữ trọn vẹn từng điều khoản quy định.
> 3. **Cần chuyển dịch sang Production Embedding**: MockEmbedder là công cụ tuyệt vời để unit test kiến trúc pipeline mà không tốn chi phí gọi API, nhưng để phục vụ người dùng thực tế giải đáp thắc mắc mua sắm, hệ thống bắt buộc cần gắn mô hình Embedding ngữ nghĩa thực thụ.

---

## Tự Đánh Giá (Phần Cá Nhân)

| Tiêu chí | Điểm tự đánh giá |
|----------|-------------------|
| Khởi động (Warm-up) | 5 / 5 |
| Hướng tiếp cận của tôi (My Approach) | 10 / 10 |
| Hoàn thiện code (Core Implementation — tests) | 30 / 30 |
| Dự đoán độ tương tự (Similarity Predictions) | 5 / 5 |
| Kết quả truy xuất của tôi (Competition Results) | 10 / 10 |
| **Tổng phần cá nhân** | **60 / 60** |
