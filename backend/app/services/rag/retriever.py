import re
import math
import logging
from typing import List, Dict, Tuple, Optional, Any
import numpy as np
from backend.app.services.rag.chunking import UnifiedChunk, ChunkMetadata
from backend.app.services.rag.embeddings import embedding_service
from backend.app.services.scheme_service import scheme_service

logger = logging.getLogger("nitisetu.rag.retriever")

STOP_WORDS = {
    "what", "when", "where", "which", "who", "whom", "this", "that", "there",
    "have", "from", "with", "does", "about", "tell", "the", "for", "and", "are",
    "can", "how", "any", "you", "your", "per", "all", "not", "but", "why", "their",
    "will", "would", "should", "could", "been", "being", "into", "onto", "under",
    "over", "after", "before", "between", "while", "during", "much", "many", "more"
}


class HybridRetriever:
    """
    Production-grade Hybrid Retriever combining:
    1. Dense Vector Similarity (cosine over 768-dim embeddings)
    2. BM25 / Sparse Full-Text Search
    3. Reciprocal Rank Fusion (RRF)
    4. Parent-Child Context Expansion
    5. Strict Scheme Boundary Metadata Filtering
    """

    def __init__(self, rrf_k: int = 60):
        self.rrf_k = rrf_k
        self._chunks: List[UnifiedChunk] = []
        self._parent_map: Dict[str, UnifiedChunk] = {}
        self._embeddings_cache: Dict[str, np.ndarray] = {}
        self._avg_doc_len: float = 120.0

    def index_chunks(self, parent_chunks: List[UnifiedChunk], child_chunks: List[UnifiedChunk]):
        """Index chunks, precompute dense embeddings, and populate parent context mapping."""
        self._chunks.clear()
        self._parent_map.clear()
        self._embeddings_cache.clear()

        for p in parent_chunks:
            self._parent_map[p.metadata.chunk_id] = p
            self._chunks.append(p)

        for c in child_chunks:
            self._chunks.append(c)

        for chunk in self._chunks:
            self._embeddings_cache[chunk.metadata.chunk_id] = np.array(
                embedding_service.get_embedding(chunk.content), dtype=np.float32
            )

        if self._chunks:
            self._avg_doc_len = sum(c.word_count for c in self._chunks) / len(self._chunks)

        logger.info(f"HybridRetriever indexed {len(self._chunks)} total chunks ({len(parent_chunks)} parents, {len(child_chunks)} children) with precomputed dense embeddings.")

    def _compute_dense_rankings(
        self,
        query: str,
        candidate_chunks: List[UnifiedChunk]
    ) -> List[Tuple[UnifiedChunk, float]]:
        """Calculate cosine similarity against 768-dim embeddings."""
        q_vec = np.array(embedding_service.get_embedding(query), dtype=np.float32)
        q_norm = np.linalg.norm(q_vec)
        if q_norm < 1e-6:
            return [(c, 0.0) for c in candidate_chunks]

        scored = []
        for c in candidate_chunks:
            cid = c.metadata.chunk_id
            if cid not in self._embeddings_cache:
                self._embeddings_cache[cid] = np.array(embedding_service.get_embedding(c.content), dtype=np.float32)

            c_vec = self._embeddings_cache[cid]
            c_norm = np.linalg.norm(c_vec)
            if c_norm > 1e-6:
                sim = float(np.dot(q_vec, c_vec) / (q_norm * c_norm))
            else:
                sim = 0.0
            scored.append((c, sim))

        scored.sort(key=lambda x: x[1], reverse=True)
        return scored

    def _compute_sparse_bm25_rankings(
        self,
        query: str,
        candidate_chunks: List[UnifiedChunk],
        intent: str
    ) -> List[Tuple[UnifiedChunk, float]]:
        """Calculate length-normalized BM25 sparse scores with intent affinity."""
        q_tokens = [w for w in re.findall(r'\b[a-zA-Z0-9]{3,}\b', query.lower()) if w not in STOP_WORDS]
        if not q_tokens:
            return [(c, 0.0) for c in candidate_chunks]

        k1 = 1.5
        b = 0.75
        avg_len = self._avg_doc_len or 120.0

        scored = []
        for chunk in candidate_chunks:
            score = 0.0
            for t in q_tokens:
                tf = chunk.words.count(t)
                if tf > 0:
                    bm25_term = (tf * (k1 + 1.0)) / (tf + k1 * (1.0 - b + b * (chunk.word_count / avg_len)))
                    score += bm25_term
                if t in chunk.title_words:
                    score += 3.5

            # Intent alignment bonus
            if intent == chunk.metadata.category:
                score += 5.0
            elif intent == "exclusions" and chunk.metadata.category in ("eligibility", "general"):
                score += 3.0

            scored.append((chunk, score))

        scored.sort(key=lambda x: x[1], reverse=True)
        return scored

    def _reciprocal_rank_fusion(
        self,
        dense_results: List[Tuple[UnifiedChunk, float]],
        sparse_results: List[Tuple[UnifiedChunk, float]]
    ) -> List[Tuple[UnifiedChunk, float]]:
        """Combine dense and sparse rankings using standard RRF."""
        rrf_scores: Dict[str, float] = {}
        chunk_lookup: Dict[str, UnifiedChunk] = {}

        for rank, (chunk, _) in enumerate(dense_results):
            cid = chunk.metadata.chunk_id
            chunk_lookup[cid] = chunk
            rrf_scores[cid] = rrf_scores.get(cid, 0.0) + (1.0 / (self.rrf_k + rank + 1))

        for rank, (chunk, _) in enumerate(sparse_results):
            cid = chunk.metadata.chunk_id
            chunk_lookup[cid] = chunk
            rrf_scores[cid] = rrf_scores.get(cid, 0.0) + (1.0 / (self.rrf_k + rank + 1))

        fused = [(chunk_lookup[cid], score) for cid, score in rrf_scores.items()]
        fused.sort(key=lambda x: x[1], reverse=True)
        return fused

    def _build_virtual_chunks_for_scheme(self, scheme, target_scheme_slug: str) -> List[UnifiedChunk]:
        """Generate structured virtual chunks from authentic 2066-scheme catalog."""
        return [
            UnifiedChunk(
                content=f"### Eligibility Criteria for {scheme.name}\n{scheme.eligibility_criteria_text}\n\nExclusions:\n{scheme.exclusions_text or 'Standard statutory welfare exclusions apply.'}",
                metadata=ChunkMetadata(
                    chunk_id=f"cat_elig_{target_scheme_slug}",
                    scheme_id=target_scheme_slug,
                    scheme_name=scheme.name,
                    document_id=f"doc_{target_scheme_slug}",
                    document_title=f"{scheme.name} Official Gazette",
                    source_url=scheme.official_url,
                    page_number=1,
                    section_heading="Eligibility Criteria & Exclusions",
                    category="eligibility",
                    is_parent=True
                )
            ),
            UnifiedChunk(
                content=f"### Benefits of {scheme.name}\n{scheme.benefit_summary or scheme.summary}",
                metadata=ChunkMetadata(
                    chunk_id=f"cat_ben_{target_scheme_slug}",
                    scheme_id=target_scheme_slug,
                    scheme_name=scheme.name,
                    document_id=f"doc_{target_scheme_slug}",
                    document_title=f"{scheme.name} Official Gazette",
                    source_url=scheme.official_url,
                    page_number=1,
                    section_heading="Financial Benefits & Subsidies",
                    category="benefits",
                    is_parent=True
                )
            ),
            UnifiedChunk(
                content=f"### Required Documents for {scheme.name}\n{scheme.documents_required_text}\n\nApplication Process:\n{scheme.application_process_text or 'Apply online via official portal.'}",
                metadata=ChunkMetadata(
                    chunk_id=f"cat_doc_{target_scheme_slug}",
                    scheme_id=target_scheme_slug,
                    scheme_name=scheme.name,
                    document_id=f"doc_{target_scheme_slug}",
                    document_title=f"{scheme.name} Official Gazette",
                    source_url=scheme.official_url,
                    page_number=1,
                    section_heading="Required Documents & Application",
                    category="documents",
                    is_parent=True
                )
            )
        ]

    def retrieve(
        self,
        query: str,
        target_scheme_slug: Optional[str] = None,
        intent: str = "general",
        top_k: int = 4
    ) -> List[Tuple[UnifiedChunk, float]]:
        """
        Execute Hybrid Search with Strict Metadata Scheme Isolation and Parent-Context Resolution.
        """
        # 1. Apply Metadata Filtering (Scheme boundary isolation)
        candidate_pool = self._chunks
        if target_scheme_slug:
            filtered = [c for c in self._chunks if c.metadata.scheme_id == target_scheme_slug]
            if not filtered:
                # Scheme is in the master 2066-scheme catalog (e.g. KCC, MUDRA, SSY, APY)
                scheme = scheme_service.get_scheme_by_slug(target_scheme_slug)
                if scheme:
                    virtual_chunks = self._build_virtual_chunks_for_scheme(scheme, target_scheme_slug)
                    candidate_pool = virtual_chunks
                    for vc in virtual_chunks:
                        self._parent_map[vc.metadata.chunk_id] = vc
            else:
                candidate_pool = filtered

        # 2. Compute Dense Vector Rankings
        dense_ranked = self._compute_dense_rankings(query, candidate_pool)

        # 3. Compute Sparse BM25 Rankings
        sparse_ranked = self._compute_sparse_bm25_rankings(query, candidate_pool, intent)

        # 4. Reciprocal Rank Fusion
        fused = self._reciprocal_rank_fusion(dense_ranked, sparse_ranked)

        # 5. Parent-Child Context Expansion
        expanded: List[Tuple[UnifiedChunk, float]] = []
        seen_parent_ids = set()

        for chunk, score in fused:
            if not chunk.metadata.is_parent and chunk.metadata.parent_chunk_id:
                parent = self._parent_map.get(chunk.metadata.parent_chunk_id)
                if parent and parent.metadata.chunk_id not in seen_parent_ids:
                    seen_parent_ids.add(parent.metadata.chunk_id)
                    expanded.append((parent, score + 0.005))
                    continue

            if chunk.metadata.chunk_id not in seen_parent_ids:
                seen_parent_ids.add(chunk.metadata.chunk_id)
                expanded.append((chunk, score))

            if len(expanded) >= top_k:
                break

        return expanded[:top_k]


retriever = HybridRetriever()
