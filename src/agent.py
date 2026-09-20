from typing import Callable

from .store import EmbeddingStore


class KnowledgeBaseAgent:
    """
    An agent that answers questions using a vector knowledge base.

    Retrieval-augmented generation (RAG) pattern:
        1. Retrieve top-k relevant chunks from the store.
        2. Build a prompt with the chunks as context.
        3. Call the LLM to generate an answer.
    """

    def __init__(self, store: EmbeddingStore, llm_fn: Callable[[str], str]) -> None:
        self.store = store
        self.llm_fn = llm_fn

    def answer(self, question: str, top_k: int = 3) -> str:
        # Handle empty store
        if self.store.get_collection_size() == 0:
            return "Không tìm thấy tài liệu nào trong cơ sở tri thức để trả lời câu hỏi này."

        # Step 1: Retrieve top-k relevant chunks
        results = self.store.search(question, top_k=top_k)

        if not results:
            return "Không tìm thấy thông tin liên quan trong cơ sở tri thức."

        # Step 2: Build prompt with numbered context chunks
        context_parts = []
        for i, result in enumerate(results, start=1):
            source = result["metadata"].get("source", result["metadata"].get("doc_id", "unknown"))
            context_parts.append(f"[{i}] (Nguồn: {source})\n{result['content']}")

        context = "\n\n".join(context_parts)

        prompt = (
            f"Dựa trên các ngữ cảnh sau đây, hãy trả lời câu hỏi. "
            f"Chỉ sử dụng thông tin từ ngữ cảnh được cung cấp. "
            f"Trích dẫn số nguồn [1], [2], [3] khi trả lời. "
            f"Nếu ngữ cảnh không chứa đủ thông tin, hãy nói rõ là không tìm thấy.\n\n"
            f"Ngữ cảnh:\n{context}\n\n"
            f"Câu hỏi: {question}\n\n"
            f"Trả lời:"
        )

        # Step 3: Call the LLM
        return self.llm_fn(prompt)
