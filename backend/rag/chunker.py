"""Token-aware, sentence-boundary chunker for DementIA knowledge ingestion.

Uses the embedding model's own tokenizer so chunk sizes are exact token counts,
not character estimates. Sentences are kept intact wherever possible; only
sentences that exceed max_tokens are split at word boundaries as a last resort.
"""

from __future__ import annotations

import re

from backend.config import settings

# Sentence boundary: punctuation followed by whitespace + sentence-start character,
# OR a newline (PDF/structured text paragraph break).
# Works for both English (PubMed) and German (AWMF).
_SENT_SPLIT = re.compile(
    r"(?<=[.!?])\s+(?=[A-ZÜÄÖА-Я\d\(\[\"])"  # punctuation → capital/digit/bracket
    r"|(?<=\n)\s*(?=[A-ZÜÄÖА-Я\d\(\[\"])"  # newline → sentence-start
)


def _split_sentences(text: str) -> list[str]:
    parts = _SENT_SPLIT.split(text)
    return [p.strip() for p in parts if p.strip()]


class TokenChunker:
    """Sentence-packed token chunker with sliding overlap.

    Packs sentences greedily up to max_tokens. When a chunk is full, rolls
    back by overlap_tokens worth of sentences to seed the next chunk.
    A sentence longer than max_tokens is word-split as a fallback.
    """

    def __init__(
        self,
        model_name: str | None = None,
        max_tokens: int = 512,
        overlap_tokens: int = 64,
    ) -> None:
        from transformers import AutoTokenizer

        self._tok = AutoTokenizer.from_pretrained(model_name or settings.embed_model)
        self.max_tokens = max_tokens
        self.overlap_tokens = overlap_tokens

    def count(self, text: str) -> int:
        return len(self._tok.encode(text, add_special_tokens=False))

    def chunk(self, text: str) -> list[str]:
        sentences = _split_sentences(text)
        if not sentences:
            return []

        chunks: list[str] = []
        window: list[str] = []  # sentences in the current chunk
        window_toks = 0

        for sent in sentences:
            sent_toks = self.count(sent)

            # Sentence itself exceeds budget — word-split it.
            if sent_toks > self.max_tokens:
                if window:
                    chunks.append(" ".join(window))
                    window, window_toks = [], 0
                chunks.extend(self._word_split(sent))
                continue

            # Adding this sentence would overflow — flush current window first.
            if window_toks + sent_toks > self.max_tokens:
                chunks.append(" ".join(window))
                # Seed next chunk with trailing sentences up to overlap_tokens.
                overlap: list[str] = []
                overlap_toks = 0
                for s in reversed(window):
                    t = self.count(s)
                    if overlap_toks + t > self.overlap_tokens:
                        break
                    overlap.insert(0, s)
                    overlap_toks += t
                window, window_toks = overlap, overlap_toks

            window.append(sent)
            window_toks += sent_toks

        if window:
            chunks.append(" ".join(window))

        return chunks

    def _word_split(self, text: str) -> list[str]:
        """Token-accurate split for overlong sentences."""
        words = text.split()
        chunks: list[str] = []
        buf: list[str] = []
        buf_toks = 0
        for word in words:
            w_toks = self.count(word)
            if buf_toks + w_toks > self.max_tokens and buf:
                chunks.append(" ".join(buf))
                buf, buf_toks = [], 0
            buf.append(word)
            buf_toks += w_toks
        if buf:
            chunks.append(" ".join(buf))
        return chunks


class _LazyChunker:
    _inner: TokenChunker | None = None

    def _get(self) -> TokenChunker:
        if self._inner is None:
            self._inner = TokenChunker()
        return self._inner

    def chunk(self, text: str) -> list[str]:
        return self._get().chunk(text)

    def count(self, text: str) -> int:
        return self._get().count(text)


chunker = _LazyChunker()
