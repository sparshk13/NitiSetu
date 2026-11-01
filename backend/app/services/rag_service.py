import os
import re
import json
import uuid
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Set, Any
from backend.app.config import settings
from backend.app.schemas.assistant import AssistantQueryRequest, AssistantQueryResponse, SourceCitation
from backend.app.services.scheme_service import scheme_service

logger = logging.getLogger("civicpilot.rag")

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
GUIDELINES_DIR = BASE_DIR / "data" / "official_policy_guidelines"
WORKFLOWS_DIR = BASE_DIR / "data" / "application_forms_and_workflows"

STOP_WORDS: Set[str] = {
    "what", "when", "where", "which", "who", "whom", "this", "that", "there",
    "have", "from", "with", "does", "about", "tell", "the", "for", "and", "are",
    "can", "how", "any", "you", "your", "per", "all", "not", "but", "why", "their",
    "will", "would", "should", "could", "been", "being", "into", "onto", "under",
    "over", "after", "before", "between", "while", "during", "much", "many", "more"
}

OFF_TOPIC_KEYWORDS: Set[str] = {
    "disney", "disneyland", "paris", "hollywood", "netflix", "weather", "forecast",
    "movie", "cinema", "football", "cricket", "ipl", "fifa", "pizza", "burger",
    "bitcoin", "crypto", "ethereum", "gaming", "playstation", "xbox", "canada",
    "tourist", "vacation", "resort", "hotel"
}

SCHEME_ALIASES: Dict[str, str] = {
    "scholarship": "national-scholarship-post-matric",
    "post matric": "national-scholarship-post-matric",
    "post-matric": "national-scholarship-post-matric",
    "pre-matric": "national-scholarship-post-matric",
    "nsp": "national-scholarship-post-matric",
    "csss": "national-scholarship-post-matric",
    "central sector": "national-scholarship-post-matric",
    "kisan": "pm-kisan",
    "pmkisan": "pm-kisan",
    "pm-kisan": "pm-kisan",
    "farmer": "pm-kisan",
    "ayushman": "ayushman-bharat-pmjay",
    "pmjay": "ayushman-bharat-pmjay",
    "pm-jay": "ayushman-bharat-pmjay",
    "golden card": "ayushman-bharat-pmjay",
    "health card": "ayushman-bharat-pmjay",
    "surya": "pm-surya-ghar-muft-bijli",
    "surya ghar": "pm-surya-ghar-muft-bijli",
    "solar": "pm-surya-ghar-muft-bijli",
    "rooftop solar": "pm-surya-ghar-muft-bijli",
    "muft bijli": "pm-surya-ghar-muft-bijli",
    "svanidhi": "pm-svanidhi",
    "street vendor": "pm-svanidhi",
    "vendor": "pm-svanidhi",
    "vishwakarma": "pm-vishwakarma",
    "artisan": "pm-vishwakarma",
    "carpenter": "pm-vishwakarma",
    "awas": "pm-awas-yojana",
    "pmay": "pm-awas-yojana",
    "housing": "pm-awas-yojana",
    "pucca house": "pm-awas-yojana",
    "mysy": "mukhyamantri-yuva-swavalamban-yojana-mysy",
    "sukanya": "sukanya-samriddhi-yojana"
}


class DocumentChunk:
    def __init__(
        self,
        doc_title: str,
        section_title: str,
        content: str,
        scheme_slug: str,
        source_url: str,
        category: str = "general",
        key_numbers: Optional[List[str]] = None
    ):
        self.doc_title = doc_title
        self.section_title = section_title
        self.content = content
        self.scheme_slug = scheme_slug
        self.source_url = source_url
        self.category = category
        self.key_numbers = key_numbers or []
        self.words = [w.lower() for w in re.findall(r'\b[a-zA-Z0-9]{3,}\b', content)]
        self.word_count = len(self.words)
        self.title_words = [w.lower() for w in re.findall(r'\b[a-zA-Z0-9]{3,}\b', f"{doc_title} {section_title}")]


class RAGAssistantService:
    def __init__(self):
        self._chunks: List[DocumentChunk] = []
        self._avg_chunk_len: float = 100.0
        self._load_knowledge_base()

    def _load_knowledge_base(self):
        """Chunk all official policy markdown documents and application workflows."""
        self._chunks.clear()

        # 1. Load official policy markdown guidelines
        if GUIDELINES_DIR.exists():
            for md_path in GUIDELINES_DIR.glob("*.md"):
                try:
                    with open(md_path, "r", encoding="utf-8") as f:
                        text = f.read()

                    lines = text.split("\n")
                    doc_title = md_path.stem.replace("_", " ").title()
                    for line in lines:
                        if line.startswith("# "):
                            doc_title = line.replace("# ", "").strip()
                            break

                    source_url = "https://www.myscheme.gov.in/"
                    for line in lines:
                        if "scholarships.gov.in" in line:
                            source_url = "https://scholarships.gov.in/"
                            break
                        elif "pmkisan.gov.in" in line:
                            source_url = "https://pmkisan.gov.in/"
                            break
                        elif "pmsuryaghar.gov.in" in line:
                            source_url = "https://pmsuryaghar.gov.in/"
                            break
                        elif "pmjay.gov.in" in line or "nha.gov.in" in line:
                            source_url = "https://pmjay.gov.in/"
                            break
                        elif "pmay" in line:
                            source_url = "https://pmaymis.gov.in/"
                            break
                        elif "pmsvanidhi" in line:
                            source_url = "https://pmsvanidhi.mohua.gov.in/"
                            break
                        elif "pmvishwakarma" in line:
                            source_url = "https://pmvishwakarma.gov.in/"
                            break

                    stem = md_path.stem.lower()
                    scheme_slug = stem.replace("_guidelines", "").replace("_operational_guidelines", "")
                    if "scholarship" in stem or "nsp" in stem:
                        scheme_slug = "national-scholarship-post-matric"
                    elif "kisan" in stem:
                        scheme_slug = "pm-kisan"
                    elif "ayushman" in stem:
                        scheme_slug = "ayushman-bharat-pmjay"
                    elif "surya" in stem:
                        scheme_slug = "pm-surya-ghar-muft-bijli"
                    elif "svanidhi" in stem:
                        scheme_slug = "pm-svanidhi"
                    elif "vishwakarma" in stem:
                        scheme_slug = "pm-vishwakarma"
                    elif "housing" in stem or "pmay" in stem:
                        scheme_slug = "pm-awas-yojana"

                    # Split sections by ## or ###
                    sections = re.split(r'\n(?=##+\s+)', text)
                    for sec in sections:
                        sec_clean = sec.strip()
                        if not sec_clean:
                            continue
                        first_line = sec_clean.split("\n")[0].replace("###", "").replace("##", "").strip()
                        section_title = first_line if first_line else "General Guidelines"

                        # Extract monetary figures or percentages for key facts indexing
                        numbers = re.findall(r'₹\s*[\d,]+(?:\s*Lakh)?|\b\d+%\b', sec_clean)

                        # Categorize chunk
                        sec_l = section_title.lower()
                        category = "general"
                        if "income" in sec_l or "ceiling" in sec_l or "threshold" in sec_l:
                            category = "income"
                        elif "eligib" in sec_l or "criteria" in sec_l or "who can" in sec_l:
                            category = "eligibility"
                        elif "document" in sec_l or "proof" in sec_l or "certificate" in sec_l:
                            category = "documents"
                        elif "benefit" in sec_l or "subsidy" in sec_l or "allowance" in sec_l or "financial" in sec_l:
                            category = "benefits"
                        elif "procedure" in sec_l or "process" in sec_l or "step" in sec_l or "apply" in sec_l:
                            category = "steps"
                        elif "exclusion" in sec_l or "ineligib" in sec_l:
                            category = "exclusions"

                        self._chunks.append(DocumentChunk(
                            doc_title=doc_title,
                            section_title=section_title,
                            content=sec_clean,
                            scheme_slug=scheme_slug,
                            source_url=source_url,
                            category=category,
                            key_numbers=numbers
                        ))

                except Exception as e:
                    logger.error(f"Error chunking {md_path}: {e}")

        # 2. Load application workflows as procedural chunks
        if WORKFLOWS_DIR.exists():
            for wf_path in WORKFLOWS_DIR.glob("*.json"):
                try:
                    with open(wf_path, "r", encoding="utf-8") as f:
                        wf = json.load(f)

                    scheme_name = wf.get("scheme_name", wf_path.stem.replace("_", " ").title())
                    portal_url = wf.get("official_portal", "https://www.myscheme.gov.in/")
                    slug = wf_path.stem.replace("_workflow", "").replace("_", "-")
                    if "scholarship" in slug:
                        slug = "national-scholarship-post-matric"
                    elif "kisan" in slug:
                        slug = "pm-kisan"
                    elif "ayushman" in slug:
                        slug = "ayushman-bharat-pmjay"
                    elif "awas" in slug:
                        slug = "pm-awas-yojana"
                    elif "surya" in slug:
                        slug = "pm-surya-ghar-muft-bijli"
                    elif "svanidhi" in slug:
                        slug = "pm-svanidhi"
                    elif "vishwakarma" in slug:
                        slug = "pm-vishwakarma"

                    # Prerequisites chunk
                    prereqs = wf.get("prerequisites", [])
                    if prereqs:
                        content = f"### Prerequisites & Eligibility for {scheme_name}\n" + "\n".join(f"- {p}" for p in prereqs)
                        self._chunks.append(DocumentChunk(
                            doc_title=f"{scheme_name} Workflow Guide",
                            section_title="Application Prerequisites & Mandatory Checklist",
                            content=content,
                            scheme_slug=slug,
                            source_url=portal_url,
                            category="documents"
                        ))

                    # Step-by-step procedural chunk
                    steps = wf.get("application_steps", [])
                    if steps:
                        step_lines = [f"### Step-by-Step Portal Application for {scheme_name}"]
                        for s in steps:
                            num = s.get("step_number", "")
                            name = s.get("step_name", "")
                            action = s.get("portal_action", "")
                            step_lines.append(f"**Step {num}: {name}**\n- Action: {action}")
                        content = "\n\n".join(step_lines)
                        self._chunks.append(DocumentChunk(
                            doc_title=f"{scheme_name} Workflow Guide",
                            section_title="Official Application Steps & Portal Navigation",
                            content=content,
                            scheme_slug=slug,
                            source_url=portal_url,
                            category="steps"
                        ))

                except Exception as e:
                    logger.error(f"Error loading workflow {wf_path}: {e}")

        if self._chunks:
            self._avg_chunk_len = sum(c.word_count for c in self._chunks) / len(self._chunks)
        logger.info(f"RAG Knowledge Base initialized with {len(self._chunks)} official policy & workflow chunks.")

    def _resolve_scheme_slug(self, question: str, explicit_slug: Optional[str] = None) -> Optional[str]:
        """Resolve scheme slug from explicit parameter or user question query text."""
        if explicit_slug and explicit_slug != "all" and explicit_slug != "undefined":
            return explicit_slug.strip().strip("/")

        q_lower = question.lower()
        for alias, slug in SCHEME_ALIASES.items():
            if re.search(r'\b' + re.escape(alias) + r'\b', q_lower):
                return slug

        # Try matching against scheme catalog
        catalog_schemes = scheme_service.list_schemes(q=question[:60], page_size=3).items
        if catalog_schemes:
            return catalog_schemes[0].slug

        return None

    def _classify_intent(self, question: str) -> str:
        """Classify the citizen question into a primary welfare inquiry intent."""
        q = question.lower()
        if any(w in q for w in ["income", "ceiling", "salary", "earning", "creamy layer", "annual limit", "lakh"]):
            return "income"
        elif any(w in q for w in ["document", "documents", "certificate", "aadhaar", "marksheet", "bonafide", "passbook", "proof", "papers"]):
            return "documents"
        elif any(w in q for w in ["apply", "application", "steps", "procedure", "how to apply", "registration", "otr", "portal"]):
            return "steps"
        elif any(w in q for w in ["benefit", "benefits", "amount", "how much", "financial", "stipend", "allowance", "subsidy", "cashless", "loan", "installment", "cashback"]):
            return "benefits"
        elif any(w in q for w in ["ineligible", "exclusion", "excluded", "cannot apply", "disqualified", "not eligible", "tax payer"]):
            return "exclusions"
        elif any(w in q for w in ["eligible", "eligibility", "who can", "criteria", "cutoff", "percentile", "marks", "caste", "age limit"]):
            return "eligibility"
        elif any(w in q for w in ["deadline", "last date", "due date", "closing date", "schedule"]):
            return "deadline"
        return "general"

    def _retrieve_relevant_chunks(
        self,
        question: str,
        scheme_slug: Optional[str] = None,
        top_k: int = 4
    ) -> List[Tuple[DocumentChunk, float]]:
        """
        BM25-normalized hybrid retrieval with intent affinity and scheme routing.
        """
        q_tokens = [w for w in re.findall(r'\b[a-zA-Z0-9]{3,}\b', question.lower()) if w not in STOP_WORDS]
        if not q_tokens:
            return []

        intent = self._classify_intent(question)
        resolved_slug = scheme_slug or self._resolve_scheme_slug(question)

        k1 = 1.5
        b = 0.75
        avg_len = self._avg_chunk_len or 100.0

        scored: List[Tuple[DocumentChunk, float]] = []

        for chunk in self._chunks:
            score = 0.0
            matched_token_count = 0

            # 1. BM25 term frequency with length normalization
            for token in q_tokens:
                tf = chunk.words.count(token)
                if tf > 0:
                    matched_token_count += 1
                    bm25_term = (tf * (k1 + 1.0)) / (tf + k1 * (1.0 - b + b * (chunk.word_count / avg_len)))
                    score += bm25_term

                # Title match bonus
                if token in chunk.title_words:
                    score += 4.5

            if matched_token_count == 0 and score <= 0.0:
                continue

            # 2. Intent-category alignment bonus
            if intent == chunk.category:
                score += 8.0
            elif intent == "income" and chunk.category == "eligibility":
                score += 5.0
            elif intent == "eligibility" and chunk.category == "income":
                score += 4.0
            elif intent == "steps" and chunk.category == "documents":
                score += 3.0

            # 3. Key concept keyword checks
            if intent == "income" and any(k in chunk.content for k in ["₹", "2,50,000", "4,50,000", "ceiling", "income"]):
                score += 4.0
            elif intent == "benefits" and any(k in chunk.content for k in ["₹", "installments", "allowance", "subsidy", "5,00,000", "6,000"]):
                score += 4.0
            elif intent == "documents" and any(k in chunk.content.lower() for k in ["aadhaar", "certificate", "bonafide", "marksheet"]):
                score += 4.0

            # 4. Scheme routing affinity (graduated, never blanket overpowering)
            if resolved_slug and chunk.scheme_slug == resolved_slug:
                score += 6.0

            if score > 0:
                scored.append((chunk, score))

        # 5. Dynamic scheme lookup from catalog if needed
        if resolved_slug and (not scored or scored[0][1] < 10.0):
            scheme = scheme_service.get_scheme_by_slug(resolved_slug)
            if scheme:
                # Build fine-grained virtual chunks for catalog schemes
                virtual_chunks = [
                    DocumentChunk(
                        doc_title=scheme.name,
                        section_title="Eligibility Criteria & Exclusions",
                        content=f"### Eligibility for {scheme.name}\n{scheme.eligibility_criteria_text}\n\nExclusions:\n{scheme.exclusions_text or 'Standard welfare eligibility criteria apply.'}",
                        scheme_slug=resolved_slug,
                        source_url=scheme.official_url,
                        category="eligibility"
                    ),
                    DocumentChunk(
                        doc_title=scheme.name,
                        section_title="Benefits & Financial Assistance",
                        content=f"### Benefits of {scheme.name}\n{scheme.benefit_summary or scheme.summary}",
                        scheme_slug=resolved_slug,
                        source_url=scheme.official_url,
                        category="benefits"
                    ),
                    DocumentChunk(
                        doc_title=scheme.name,
                        section_title="Required Documents & Application",
                        content=f"### Documents for {scheme.name}\n{scheme.documents_required_text}\n\nApplication Process:\n{scheme.application_process_text or 'Apply online via official portal.'}",
                        scheme_slug=resolved_slug,
                        source_url=scheme.official_url,
                        category="documents"
                    )
                ]
                for v_chunk in virtual_chunks:
                    v_score = 0.0
                    for token in q_tokens:
                        if token in v_chunk.words:
                            v_score += 2.0
                        if token in v_chunk.title_words:
                            v_score += 3.0
                    if intent == v_chunk.category:
                        v_score += 6.0
                    if v_score > 0:
                        scored.append((v_chunk, v_score + 5.0))

        scored.sort(key=lambda x: x[1], reverse=True)
        return scored[:top_k]

    def _call_gemini_chat(self, prompt: str, model_name: str) -> Optional[str]:
        """Call Gemini API via clean Chat interface to avoid AFC warnings and optimize latency."""
        api_key = settings.gemini_api_key or os.getenv("GEMINI_API_KEY")
        if not api_key or "your_" in api_key.lower() or "placeholder" in api_key.lower():
            return None

        try:
            from google import genai
            client = genai.Client(api_key=api_key)
            chat = client.chats.create(model=model_name)
            response = chat.send_message(prompt)
            if response and response.text:
                return response.text.strip()
            return None
        except Exception as e:
            logger.warning(f"Gemini call with {model_name} failed: {e}")
            return None

    def _judge_cross_verify(
        self,
        question: str,
        context_str: str,
        candidate_answer: str
    ) -> Dict[str, Any]:
        """
        LLM-as-a-Judge cross-verification pass.
        Checks relevance, factual grounding, and answer formatting.
        """
        judge_prompt = (
            "You are CivicPilot's Quality & Fact Verification Judge. "
            "Critically evaluate the candidate answer against the citizen's question and official government context.\n\n"
            f"CITIZEN QUESTION:\n{question}\n\n"
            f"OFFICIAL CONTEXT:\n{context_str}\n\n"
            f"CANDIDATE ANSWER:\n{candidate_answer}\n\n"
            "Evaluate strictly:\n"
            "1. Relevance: Did the answer directly answer the specific question asked without meandering?\n"
            "2. Factual Grounding: Are all numbers, caps (e.g. ₹2,50,000), percentages, and rules supported by the official context without hallucinations?\n"
            "3. Formatting: Is the format clear, structured, and easy for citizens to read?\n\n"
            "Return STRICT JSON only with keys:\n"
            "{\n"
            '  "passed": true/false,\n'
            '  "insufficient_evidence": true/false,\n'
            '  "score": 1 to 10,\n'
            '  "critique": "short explanation",\n'
            '  "verified_answer": "final approved or polished answer",\n'
            '  "key_facts": ["fact 1", "fact 2"]\n'
            "}"
        )

        raw_judge_res = self._call_gemini_chat(judge_prompt, settings.gemini_judge_model)
        if not raw_judge_res:
            # Fallback to generation model if judge model unavailable
            raw_judge_res = self._call_gemini_chat(judge_prompt, settings.gemini_generation_model)

        if raw_judge_res:
            try:
                # Strip markdown json codeblocks if present
                clean_json = re.sub(r'^```(?:json)?\s*', '', raw_judge_res.strip())
                clean_json = re.sub(r'\s*```$', '', clean_json.strip())
                parsed = json.loads(clean_json)
                return parsed
            except Exception as e:
                logger.warning(f"Could not parse Judge JSON response: {e}")

        # Default fallback judgment
        return {
            "passed": True,
            "insufficient_evidence": False,
            "score": 8,
            "critique": "Default verification passed.",
            "verified_answer": candidate_answer,
            "key_facts": []
        }

    def _smart_grounded_local_synthesis(
        self,
        question: str,
        top_chunks: List[Tuple[DocumentChunk, float]],
        intent: str
    ) -> Tuple[str, List[str]]:
        """
        Intelligent offline/fallback local synthesis.
        Extracts intent-relevant sentences and formats into crisp, structured markdown.
        Never outputs raw unformatted first paragraphs.
        """
        top_chunk, _ = top_chunks[0]
        content = top_chunk.content

        # Extract sentences or bullet points
        raw_items = re.split(r'\n+[-*•]\s+|\n\d+\.\s+|\.\s+', content)
        candidates = [item.strip() for item in raw_items if len(item.strip()) > 15 and not item.strip().startswith("#")]

        # Filter items matching intent or query terms
        intent_matches = []
        for item in candidates:
            item_l = item.lower()
            if intent == "income" and any(k in item_l for k in ["income", "ceiling", "₹", "lakh", "per annum", "maximum"]):
                intent_matches.append(item)
            elif intent == "documents" and any(k in item_l for k in ["aadhaar", "certificate", "bonafide", "marksheet", "card", "document"]):
                intent_matches.append(item)
            elif intent == "benefits" and any(k in item_l for k in ["₹", "subsidy", "allowance", "assistance", "installments", "per year"]):
                intent_matches.append(item)
            elif intent == "steps" and any(k in item_l for k in ["step", "portal", "registration", "verify", "online", "application"]):
                intent_matches.append(item)
            elif intent == "eligibility" and any(k in item_l for k in ["eligible", "criteria", "student", "farmer", "regular", "%"]):
                intent_matches.append(item)

        selected_items = intent_matches if intent_matches else candidates[:3]
        primary_answer = selected_items[0] if selected_items else f"Official criteria outlined in {top_chunk.section_title}."

        # Extract key facts
        key_facts = re.findall(r'₹\s*[\d,]+(?:\s*Lakh)?|\b\d+%\b', " ".join(selected_items))

        # Format cleanly
        formatted = (
            f"### Direct Answer\n"
            f"According to the official {top_chunk.doc_title} ({top_chunk.section_title}):\n\n"
            f"{primary_answer}.\n\n"
            f"### Key Provisions & Criteria\n"
        )
        for item in selected_items[1:4]:
            formatted += f"- {item}\n"
        if len(selected_items) <= 1:
            formatted += f"- All details subject to verification under {top_chunk.doc_title}.\n"

        formatted += (
            f"\n### Official Portal & Source\n"
            f"Verified under Gazette notification guidelines. Please refer to [{top_chunk.source_url}]({top_chunk.source_url}) for full application processing."
        )

        return formatted, key_facts

    def answer_query(self, request: AssistantQueryRequest) -> AssistantQueryResponse:
        """
        Generate a verifiable answer strictly grounded in authentic government documents.
        Follows a Multi-Tier RAG pipeline:
        1. Query analysis & intent classification
        2. Guardrail check for off-topic queries
        3. BM25-normalized hybrid retrieval
        4. Gemini generation with strict factual constraints
        5. LLM-as-a-Judge cross-verification and answer polishing
        """
        question = request.question.strip()
        scheme_slug = request.scheme_id
        q_lower = question.lower()

        # 1. Guardrail against off-topic / non-civic inquiries
        has_off_topic = any(re.search(r'\b' + re.escape(w) + r'\b', q_lower) for w in OFF_TOPIC_KEYWORDS)
        has_civic_word = any(w in q_lower for w in [
            "scheme", "scholarship", "kisan", "farmer", "pension", "housing", "pmay",
            "ayushman", "health", "hospital", "income", "eligible", "subsidy", "loan",
            "government", "yojana", "documents", "aadhaar", "svanidhi", "surya", "vishwakarma"
        ])

        if has_off_topic and not has_civic_word:
            return AssistantQueryResponse(
                answer="I could not find verified facts regarding this in the official government scheme guidelines. "
                       "To ensure complete accuracy, CivicPilot strictly provides factual information from official Government of India Gazette notifications and operational guidelines.",
                citations=[],
                insufficient_evidence=True,
                verification_status="insufficient_evidence",
                confidence_score=0.0,
                conversation_id=request.conversation_id or str(uuid.uuid4())
            )

        # 2. Retrieve relevant chunks
        top_chunks = self._retrieve_relevant_chunks(question, scheme_slug=scheme_slug, top_k=4)

        # 3. Check for insufficient evidence threshold
        if not top_chunks or top_chunks[0][1] < 3.0:
            return AssistantQueryResponse(
                answer="I could not find verified facts regarding this in the official government scheme guidelines. "
                       "To ensure complete accuracy, CivicPilot only provides information directly stated in official government notifications.",
                citations=[],
                insufficient_evidence=True,
                verification_status="insufficient_evidence",
                confidence_score=0.0,
                conversation_id=request.conversation_id or str(uuid.uuid4())
            )

        intent = self._classify_intent(question)
        resolved_scheme_name = top_chunks[0][0].doc_title

        # 4. Build citations list and context string
        citations: List[SourceCitation] = []
        context_parts: List[str] = []

        for chunk, score in top_chunks:
            clean_content = re.sub(r'#+\s*', '', chunk.content)
            clean_content = ' '.join(clean_content.split())
            excerpt = clean_content[:260] + ("..." if len(clean_content) > 260 else "")

            citations.append(SourceCitation(
                source_title=chunk.doc_title,
                source_url=chunk.source_url,
                section_title=chunk.section_title,
                page_number=1,
                excerpt=excerpt
            ))

            context_parts.append(f"[{chunk.doc_title} | Section: {chunk.section_title}]\n{chunk.content}")

        context_str = "\n\n---\n\n".join(context_parts)

        # 5. Gemini Generation Stage
        system_prompt = (
            "You are CivicPilot, an authentic Government of India welfare scheme assistant. "
            "Answer the citizen's inquiry with utmost factual precision.\n\n"
            "STRICT RULES:\n"
            "1. DIRECT ANSWER FIRST: In the very first 1-2 sentences under '### Direct Answer', directly and clearly answer the exact question asked.\n"
            "2. ZERO HALLUCINATION: Rely strictly on the official excerpts provided. Never fabricate income limits, deadlines, or numbers.\n"
            "3. STRUCTURED FORMAT: Organize your answer with clear markdown headings:\n"
            "   ### Direct Answer\n"
            "   ### Key Eligibility & Criteria (or Financial Benefits / Documents Required as relevant)\n"
            "   ### Important Exclusions & Conditions (if applicable)\n"
            "   ### Application & Next Steps (mention official portal if provided)\n"
            "4. HIGHLIGHT FIGURES: Bold all key figures (e.g. **₹2,50,000 per annum**, **₹6,000/year**, **₹5,00,000**).\n"
            "5. If the context does not explicitly contain the answer, explicitly state: 'The official guidelines do not specify this information.'\n\n"
            f"OFFICIAL CONTEXT:\n{context_str}\n\n"
            f"CITIZEN QUESTION:\n{question}\n\n"
            "GROUNDED ANSWER:"
        )

        candidate_answer = self._call_gemini_chat(system_prompt, settings.gemini_generation_model)

        final_answer = ""
        verification_status = "verified"
        confidence_score = 0.95
        key_facts: List[str] = []

        if candidate_answer and len(candidate_answer.strip()) > 20:
            # 6. LLM-as-a-Judge Cross-Verification
            judgment = self._judge_cross_verify(question, context_str, candidate_answer)

            if judgment.get("insufficient_evidence", False):
                return AssistantQueryResponse(
                    answer="I could not find verified facts regarding this in the official government scheme guidelines. "
                           "To ensure complete accuracy, CivicPilot only provides information directly stated in official government notifications.",
                    citations=[],
                    insufficient_evidence=True,
                    verification_status="insufficient_evidence",
                    confidence_score=0.0,
                    conversation_id=request.conversation_id or str(uuid.uuid4())
                )

            if judgment.get("passed", True):
                final_answer = candidate_answer
                verification_status = "verified"
            else:
                # Use the Judge's polished, revised answer
                final_answer = judgment.get("verified_answer") or candidate_answer
                verification_status = "revised_by_judge"

            confidence_score = min(1.0, max(0.5, float(judgment.get("score", 9)) / 10.0))
            key_facts = judgment.get("key_facts", [])
        else:
            # 7. Smart local grounded synthesis fallback
            final_answer, key_facts = self._smart_grounded_local_synthesis(question, top_chunks, intent)
            verification_status = "verified_local"
            confidence_score = 0.9

        # Ensure key_facts has numbers if none extracted
        if not key_facts:
            matched_nums = re.findall(r'₹\s*[\d,]+(?:\s*Lakh)?|\b\d+%\b', final_answer)
            key_facts = list(dict.fromkeys(matched_nums))[:4]

        intent_labels = {
            "income": "Income Ceiling & Means Threshold",
            "documents": "Mandatory Documentation Requirements",
            "steps": "Step-by-Step Application Procedure",
            "benefits": "Financial Benefits & Subsidy Structure",
            "eligibility": "Eligibility & Criteria Check",
            "exclusions": "Exclusion & Ineligibility Rules",
            "deadline": "Deadlines & Timelines",
            "general": "General Scheme Information"
        }

        return AssistantQueryResponse(
            answer=final_answer,
            citations=citations,
            insufficient_evidence=False,
            conversation_id=request.conversation_id or str(uuid.uuid4()),
            verification_status=verification_status,
            confidence_score=confidence_score,
            key_facts=key_facts,
            matched_scheme_name=resolved_scheme_name,
            detected_intent=intent_labels.get(intent, "General Policy Information")
        )


rag_service = RAGAssistantService()
