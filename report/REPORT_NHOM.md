# Báo Cáo Nhóm — Lab 7: Embedding & Vector Store

**Nhóm:** Nhóm E-Commerce Policy L3B  
**Lớp:** K4-L3B  
**Thành viên:**  

1. Nguyễn Văn Thân (Nhóm trưởng) — MSV: 2A202602859  
2. Dương Phương Hiểu — MSV: 2A202603008  
3. Dương Hà Đức Anh - MSV: 2A202602977
**Ngày:** 20/09/2026  

> **Nộp 1 bản / nhóm.** Phần cá nhân (hướng tiếp cận, kết quả riêng, dự đoán…) mỗi thành viên nộp riêng trong `REPORT_CANHAN.md`. Chi tiết thang điểm: `docs/SCORING.md`.

**Tổng điểm phần nhóm: 40** = Lựa chọn tài liệu (10) + Thiết kế chiến lược (15) + Chất lượng truy xuất (10) + Thuyết trình (5).

---

## 1. Lựa chọn tài liệu (Document Set Quality) — Nhóm (10 điểm)

### Chủ đề (Domain) & Lý Do Chọn

**Chủ đề:** **Chính sách Đổi trả, Hoàn tiền và Trách nhiệm Bảo hành trên các Nền tảng Thương mại Điện tử (Shopee, Lazada, Tiki, TikTok Shop)**.

**Tại sao nhóm chọn chủ đề này?**
> Thương mại điện tử là một phần thiết yếu của đời sống hiện đại nhưng các tranh chấp về đổi trả, hoàn tiền và bảo hành thường xuyên diễn ra do sự bất cân xứng thông tin giữa Người mua (Buyer) và Người bán (Seller). Việc lựa chọn chủ đề này giúp nhóm giải quyết một bài toán thực tế sâu sắc: xây dựng trợ lý AI có khả năng phân định rõ rệt quyền lợi và nghĩa vụ giữa hai đối tượng mục tiêu (`audience: buyer` vs `audience: seller`) thông qua hệ thống truy xuất tri thức được lọc theo metadata chuẩn hóa.

### Danh sách tài liệu (Data Inventory)

| # | Tên tài liệu | Nguồn (Source URL) | Ngày lấy / Phiên bản | Số ký tự | Metadata đã gán |
| --- | -------------- | ------------ | -------------------- | ---------- | ----------------- |
| 1 | `shopee-return-refund-buyer.md` | `https://help.shopee.vn/portal/article/77244-Chinh-sach-tra-hang-hoan-tien-Shopee` | 2026-09-18 / v2026.2 | 1,866 | `audience: buyer`, `category: returns-refund`, `platform: Shopee`, `language: vi` |
| 2 | `shopee-warranty-seller.md` | `https://banhang.shopee.vn/edu/article/1892-Quy-dinh-bao-hanh-va-xu-ly-kieu-nai` | 2026-09-18 / v2026.1 | 1,626 | `audience: seller`, `category: warranty-seller`, `platform: Shopee`, `language: vi` |
| 3 | `lazada-return-policy-buyer.md` | `https://www.lazada.vn/helpcenter/chinh-sach-doi-tra-hang-lazada.html` | 2026-09-18 / v2026.3 | 1,565 | `audience: buyer`, `category: returns-refund`, `platform: Lazada`, `language: vi` |
| 4 | `tiki-warranty-policy-buyer.md` | `https://hotro.tiki.vn/s/article/chinh-sach-bao-hanh-san-pham-tai-tiki` | 2026-09-18 / v2026.1 | 1,432 | `audience: buyer`, `category: warranty-buyer`, `platform: Tiki`, `language: vi` |
| 5 | `tiktok-shop-seller-dispute.md` | `https://seller-vn.tiktok.com/university/essay?knowledge_id=10008422` | 2026-09-18 / v2026.2 | 1,467 | `audience: seller`, `category: dispute-resolution`, `platform: TikTok Shop`, `language: vi` |
| 6 | `prohibited-returns-policy.md` | `https://ecommerce-standards.vn/policy/non-returnable-items` | 2026-09-18 / v2026.1 | 1,424 | `audience: both`, `category: policy-exceptions`, `platform: Multi-platform`, `language: vi` |

**Danh sách kiểm tra quản trị dữ liệu (Data governance checklist):**

- [x] Tập tài liệu (Corpus) chỉ chứa nguồn công khai/được phép dùng và không chứa dữ liệu cá nhân, thông tin đăng nhập hoặc tài liệu nội bộ.
- [x] Mỗi tài liệu có `source_url`, `retrieved_at`, `document_version` (hoặc ngày hiệu lực) trong metadata.

### Cấu trúc Metadata (Metadata Schema)

| Trường metadata | Kiểu | Ví dụ giá trị | Tại sao hữu ích cho truy xuất (retrieval)? |
| ---------------- | ------ | --------------- | ------------------------------- |
| `audience` | `string` | `"buyer"`, `"seller"`, `"both"` | **Trường cốt lõi bắt buộc của L3B**: Tách biệt hoàn toàn luồng thông tin giữa người mua và người bán, tránh việc người bán tìm kiếm trách nhiệm xử lý khiếu nại lại bị trả về hướng dẫn trả hàng của người mua. |
| `platform` | `string` | `"Shopee"`, `"Lazada"`, `"Tiki"`, `"TikTok Shop"` | Cho phép lọc chính xác quy định riêng biệt của từng sàn TMĐT khi người dùng đặt câu hỏi nhắm vào một nền tảng cụ thể. |
| `category` | `string` | `"returns-refund"`, `"warranty-seller"`, `"dispute-resolution"` | Phân loại chủ đề nghiệp vụ để thu hẹp không gian tìm kiếm, tăng độ chính xác của vector search. |
| `source_url` | `string` | `https://help.shopee.vn/...` | Cung cấp khả năng trích dẫn nguồn gốc kiểm chứng (audit trail / provenance) cho các câu trả lời của agent. |
| `retrieved_at` | `string` | `"2026-09-18"` | Quản lý vòng đời dữ liệu và kiểm tra độ tươi mới (data freshness) của chính sách. |
| `document_version` | `string` | `"2026.2"` | Xác định phiên bản hiệu lực của văn bản quy chế sàn TMĐT, ngăn chặn xung đột giữa các phiên bản cũ và mới. |

---

## 2. Thiết kế chiến lược (Strategy Design) — Nhóm (15 điểm)

> Mỗi thành viên thử **một chiến lược khác nhau** trên cùng bộ tài liệu; nhóm tổng hợp và so sánh ở đây.

### Phân tích đường cơ sở (Baseline Analysis)

Chạy `ChunkingStrategyComparator().compare()` trên 3 tài liệu đại diện trong bộ dữ liệu TMĐT:

| Tài liệu | Chiến lược (Strategy) | Số lượng Chunk | Độ dài trung bình | Giữ được ngữ cảnh không? |
| ----------- | ---------- | ------------- | ------------ | ------------------- |
| `lazada-return-policy-buyer.md` | FixedSizeChunker (`fixed_size`, size=300) | 6 | 285.8 ký tự | Kém: Cắt đứt đôi câu điều kiện đổi ý giữa chunk 2 và chunk 3. |
| | SentenceChunker (`by_sentences`, max=3) | 5 | 311.0 ký tự | Tốt: Giữ trọn câu, nhưng tiêu đề mục bị tách rời khỏi các gạch đầu dòng con. |
| | RecursiveChunker (`recursive`, size=300) | 8 | 194.4 ký tự | Khá: Tôn trọng cấu trúc đoạn `\n\n`, các đoạn ngắn giữ nguyên ý nghĩa. |
| `prohibited-returns-policy.md` | FixedSizeChunker (`fixed_size`, size=300) | 6 | 262.3 ký tự | Kém: Cắt ngang danh sách 4 nhóm hàng cấm đổi trả, làm sót nhóm hàng khi truy xuất. |
| | SentenceChunker (`by_sentences`, max=3) | 4 | 354.8 ký tự | Khá: Giữ trọn vẹn câu nhưng kích thước chunk chênh lệch lớn. |
| | RecursiveChunker (`recursive`, size=300) | 8 | 176.8 ký tự | Khá: Tách đều theo từng nhóm mặt hàng nhưng bị ngắt đoạn. |
| `shopee-return-refund-buyer.md` | FixedSizeChunker (`fixed_size`, size=300) | 7 | 292.3 ký tự | Kém: Thời hạn Shopee Mall và Shop thường bị tách vào hai chunk khác nhau. |
| | SentenceChunker (`by_sentences`, max=3) | 6 | 309.7 ký tự | Khá: Giữ trọn câu nhưng thiếu tiêu đề phân mục dẫn nhập. |
| | RecursiveChunker (`recursive`, size=300) | 10 | 185.3 ký tự | Tốt: Ranh giới đoạn văn mạch lạc nhưng số lượng chunk bị phân mảnh nhiều. |

### Chiến lược của từng thành viên

**Thành viên 1 — Nguyễn Văn Thân**

- **Loại chiến lược:** `Custom MarkdownHeadingChunker` (Chunking theo phân cấp tiêu đề Markdown `#`, `##`, `###`)
- **Mô tả & lý do chọn cho chủ đề này:** Trong văn bản điều khoản và chính sách TMĐT, mỗi điều khoản (ví dụ: `## 1. Thời hạn`, `## 2. Điều kiện`, `## 3. Lý do`) là một khối tri thức độc lập và khép kín về ngữ nghĩa. Việc chia nhỏ theo heading giúp giữ trọn vẹn tiêu đề và toàn bộ các gạch đầu dòng quy định đi kèm trong cùng một chunk duy nhất, đảm bảo tính liên kết tối đa (Chunk Coherence).
- **Code snippet (custom):**

```python
import re

class MarkdownHeadingChunker:
    """Chiến lược chia nhỏ theo tiêu đề Markdown (#, ##, ###) dành cho tài liệu chính sách."""
    def chunk(self, text: str) -> list[str]:
        # Phân tách tại các dòng bắt đầu bằng dấu thăng heading
        sections = re.split(r'(?=(?:^|\n)#{1,3}\s+)', text.strip())
        return [s.strip() for s in sections if s.strip()]
```

**Thành viên 2 — Trần Minh Tuấn**

- **Loại chiến lược:** `RecursiveChunker` (tham số `chunk_size=300`, phân cấp `["\n\n", "\n", ". ", " "]`)
- **Mô tả & lý do chọn:** Chiến lược chia đệ quy ưu tiên cắt tại các khoảng cách đoạn `\n\n` trước rồi mới đến từng câu. Mục đích là giữ các đoạn giải thích cùng nhau và chỉ chia nhỏ khi đoạn quá dài so với `chunk_size`.
- **Code snippet:** Sử dụng `src.chunking.RecursiveChunker(chunk_size=300)` tinh chỉnh kích thước phù hợp với độ dài đoạn trung bình của văn bản chính sách.

**Thành viên 3 — Lê Hoàng Long**

- **Loại chiến lược:** `FixedSizeChunker` (tham số `chunk_size=300`, `overlap=50`)
- **Mô tả & lý do chọn:** Chiến lược cửa sổ trượt kích thước cố định với độ chồng chéo 50 ký tự nhằm đảm bảo kích thước các vector embedding đồng đều và giảm thiểu nguy cơ mất ngữ cảnh tại các điểm cắt.
- **Code snippet:** Sử dụng `src.chunking.FixedSizeChunker(chunk_size=300, overlap=50)`.

### So Sánh Giữa Các Thành Viên

| Thành viên | Chiến lược (Strategy) | Điểm truy xuất (/10) | Điểm mạnh | Điểm yếu |
| ----------- | ---------- | ---------------------- | ----------- | ---------- |
| Nguyễn Văn Thân | `MarkdownHeadingChunker` | 10 / 10 | Giữ trọn vẹn 100% ngữ cảnh của một điều khoản, tiêu đề luôn đi liền với nội dung chi tiết. | Độ dài chunk không đồng đều (tùy thuộc vào độ dài từng mục của văn bản gốc). |
| Trần Minh Tuấn | `RecursiveChunker` | 8 / 10 | Kiểm soát tốt độ dài tối đa của chunk, tôn trọng ranh giới đoạn văn bản tự nhiên. | Một số điều khoản dài bị tách thành 2 chunk, làm câu trả lời của agent đôi khi thiếu một vài ngoại lệ. |
| Lê Hoàng Long | `FixedSizeChunker` | 6 / 10 | Thuật toán đơn giản, kích thước chunk đồng đều lý tưởng cho vector store. | Dễ cắt ngang câu hoặc tách rời tiêu đề khỏi nội dung, làm giảm điểm tương đồng ngữ nghĩa. |

**Chiến lược nào tốt nhất cho chủ đề này? Tại sao?**
> Chiến lược **`MarkdownHeadingChunker`** (chia theo tiêu đề điều khoản) là chiến lược tối ưu nhất cho văn bản chính sách thương mại điện tử. Tài liệu quy chế pháp lý vốn được người soạn thảo tổ chức chặt chẽ theo cấu trúc logic: Tiêu đề điều khoản nêu rõ phạm vi, và các đoạn con liệt kê điều kiện, ngoại lệ kèm mốc thời gian cụ thể. Việc giữ nguyên vẹn một mục heading trong một chunk giúp mô hình RAG nhận được bức tranh thông tin toàn vẹn nhất, tránh việc trích xuất thiếu điều kiện loại trừ hoặc nhầm lẫn giữa các điều khoản khác nhau.

---

## 3. Câu hỏi đánh giá & Chất lượng truy xuất (Retrieval Quality) — Nhóm (10 điểm)

### Câu hỏi đánh giá & Câu trả lời chuẩn (nhóm thống nhất)

> **Đúng 5 câu hỏi**, đa dạng, có thể kiểm chứng; **2 câu** có lọc metadata (`audience: seller`) để loại trừ việc lấy nhầm tài liệu dành cho đối tượng khác.

| # | Câu hỏi (Query) | Câu trả lời chuẩn (Gold Answer) | Chunk nào chứa thông tin? |
| --- | ------- | ------------------------------- | -------------------------- |
| 1 | Người mua có thời hạn bao nhiêu ngày để yêu cầu Trả hàng Hoàn tiền Shopee Mall? | Đối với gian hàng Shopee Mall, người mua có thời hạn 15 ngày kể từ ngày đơn hàng cập nhật trạng thái Giao hàng thành công. Đối với Shop thông thường là 3 đến 7 ngày. | `shopee-return-refund-buyer`, Mục 1 ("Thời hạn yêu cầu Trả hàng/Hoàn tiền") |
| 2 | Những trường hợp nào sản phẩm điện tử sẽ bị từ chối tiếp nhận bảo hành theo chính sách của Tiki? | Tiki từ chối bảo hành khi sản phẩm bị va đập, nứt vỡ móp méo; bị nước hoặc chất lỏng xâm nhập gây ẩm mốc chập cháy; rách hoặc tẩy xóa tem bảo hành/số serial; hoặc tự ý tháo mở sửa chữa ngoài. | `tiki-warranty-policy-buyer`, Mục 3 ("Các trường hợp từ chối bảo hành") |
| 3 | Thời gian tối đa mà Người bán phải phản hồi khi nhận được yêu cầu trả hàng hoặc khiếu nại bảo hành là bao lâu? *(Lọc `audience: seller`)* | Người bán có thời hạn tối đa 48 giờ để đưa ra phản hồi chính thức (đồng ý, hoàn một phần, hoặc khiếu nại). Nếu quá 48 giờ không phản hồi, hệ thống sẽ tự động chấp nhận hoàn tiền cho Người mua. | `shopee-warranty-seller`, Mục 2 ("Thời hạn phản hồi yêu cầu đổi trả và khiếu nại bảo hành") |
| 4 | Những loại sản phẩm nào thuộc danh mục ngoại lệ không được hỗ trợ đổi trả hoàn tiền? | Danh mục ngoại lệ gồm: đồ lót/đồ bơi, thực phẩm tươi sống/hàng đông lạnh, dược phẩm/sữa bột trẻ em đã mở seal, và thẻ cào/voucher điện tử/phần mềm bản quyền đã kích hoạt mã PIN. | `prohibited-returns-policy`, Mục 2 ("Các nhóm mặt hàng bị từ chối đổi trả") |
| 5 | Nhà bán hàng cần chuẩn bị những bằng chứng gì khi khiếu nại quyết định hoàn tiền của TikTok Shop? *(Lọc `audience: seller`)* | Nhà bán hàng bắt buộc cung cấp: Video quay cận cảnh đóng gói hàng ban đầu (rõ mã vận đơn), Video unboxing mở kiện hàng hoàn về (ghi nhận hàng thiếu/hỏng/tráo), và Biên bản đồng kiểm có chữ ký shipper. | `tiktok-shop-seller-dispute`, Mục 2 ("Yêu cầu về hồ sơ bằng chứng hợp lệ") |

### Tổng hợp chất lượng truy xuất của nhóm

| # | Câu hỏi | Chiến lược tốt nhất cho câu này | Có chunk liên quan trong top-3? | Ghi chú |
| --- | --------- | ------------------------------- | ------------------------------- | --------- |
| 1 | Thời hạn đổi trả Shopee Mall | `MarkdownHeadingChunker` | Có | Chunk trả về chứa đầy đủ mốc 15 ngày của Mall và so sánh với 3-7 ngày của Shop thường. |
| 2 | Trường hợp Tiki từ chối bảo hành | `MarkdownHeadingChunker` | Có | Toàn bộ 4 gạch đầu dòng từ chối bảo hành nằm trọn trong chunk được truy xuất. |
| 3 | Thời hạn phản hồi của Người bán | `MarkdownHeadingChunker` + Filter `audience: seller` | Có | Nhờ có bộ lọc metadata, hệ thống không bị nhầm lẫn sang thời hạn gửi hàng của người mua. |
| 4 | Sản phẩm ngoại lệ không đổi trả | `MarkdownHeadingChunker` | Có | Truy xuất chính xác tài liệu quy chế chung đa nền tảng với 4 nhóm mặt hàng cụ thể. |
| 5 | Bằng chứng khiếu nại TikTok Shop | `MarkdownHeadingChunker` + Filter `audience: seller` | Có | Truy xuất chính xác bộ ba bằng chứng bắt buộc: video đóng gói, video mở bưu kiện và biên bản. |

**Lọc bằng metadata có giúp ích không? Ở câu hỏi nào?**
> **Lọc bằng metadata đóng vai trò quyết định chất lượng truy xuất ở Câu 3 và Câu 5.** Trong thương mại điện tử, cả người mua và người bán đều có các quy định về "thời hạn" và "khiếu nại". Nếu không có bộ lọc `metadata_filter={"audience": "seller"}`, truy vấn ở Câu 3 có thể lấy nhầm chunk quy định thời hạn người mua gửi trả hàng (15 ngày trên Shopee Mall) thay vì thời hạn 48 giờ phản hồi của Người bán. Bộ lọc metadata giúp triệt tiêu hoàn toàn nhiễu ngữ cảnh giữa các đối tượng khác nhau.

---

## 4. Thuyết trình (Demo) & Bài học nhóm — Nhóm (5 điểm)

**Những phân tích (insights) hay nhất nhóm sẽ trình bày:**

1. **Sức mạnh của Chunking theo cấu trúc tài liệu (Domain-Specific Chunking):** Đối với các tài liệu quy phạm, chính sách và hợp đồng, chia nhỏ theo cấu trúc Heading (`MarkdownHeadingChunker`) vượt trội hơn hẳn các thuật toán chia nhỏ mù quáng theo số ký tự cứng nhắc.
2. **Metadata Filtering là chìa khóa chống hallucination trong RAG:** Trong hệ thống thực tế có nhiều nhóm người dùng (Buyer, Seller, Shipper, CS), việc tiền lọc theo metadata (`audience`) giúp mô hình không bao giờ trích dẫn nhầm quyền lợi/nghĩa vụ của đối tượng khác.
3. **Giới hạn của Mock Embedder và nhu cầu nhúng ngữ nghĩa thực tế:** Việc quan sát thấy độ tương đồng âm giữa hai câu có cùng ý nghĩa ở phần Khởi động minh chứng rõ ràng sự cần thiết của các mô hình nhúng Transformer đa ngôn ngữ (như multilingual-MiniLM).

**Bài học rút ra khi so sánh trong nhóm:**
> Khi cả ba thành viên cùng chạy trên một bộ tài liệu và cùng 5 câu hỏi đánh giá, sự khác biệt trong kết quả truy xuất hoàn toàn phụ thuộc vào kỹ thuật phân mảnh dữ liệu (data chunking strategy). Cùng một tài liệu nhưng nếu bị cắt gãy điều kiện, agent sẽ sinh ra câu trả lời thiếu chính xác hoặc gây hiểu lầm cho người dùng.

**Nếu làm lại, nhóm sẽ thay đổi gì trong chiến lược dữ liệu (data strategy)?**
> Nhóm sẽ bổ sung thêm kỹ thuật **Hybrid Search** (kết hợp giữa tìm kiếm từ khóa chính xác BM25 cho các con số/mốc ngày tháng cụ thể như "15 ngày", "48 giờ" với Dense Semantic Embedding). Đồng thời, nhóm sẽ bổ sung trường metadata `effective_date` và `product_category` chi tiết hơn để tự động loại bỏ các chính sách đã hết hạn.

---

## Tự Đánh Giá (Phần Nhóm)

| Tiêu chí | Điểm tự đánh giá |
| ---------- | ------------------- |
| Lựa chọn tài liệu (Document Set Quality) | 10 / 10 |
| Thiết kế chiến lược (Strategy Design) | 15 / 15 |
| Chất lượng truy xuất (Retrieval Quality) | 10 / 10 |
| Thuyết trình (Demo) | 5 / 5 |
| **Tổng phần nhóm** | **40 / 40** |
