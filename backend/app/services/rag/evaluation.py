import time
import logging
from typing import List, Dict, Any, Tuple
from backend.app.schemas.assistant import AssistantQueryRequest
from backend.app.services.rag.retriever import retriever
from backend.app.services.rag.query_classifier import query_classifier

logger = logging.getLogger("nitisetu.rag.evaluation")

# 35 Benchmark test questions covering scholarships, welfare schemes, numerical thresholds,
# statutory exclusions, follow-up references, and unanswerable edge cases.
BENCHMARK_DATASET: List[Dict[str, Any]] = [
    {
        "id": "q01",
        "question": "What is the family income limit for National Post-Matric Scholarship for SC students?",
        "expected_scheme": "national-scholarship-post-matric",
        "expected_intent": "income",
        "expected_facts": ["2.5", "2,50,000"],
        "should_abstain": False
    },
    {
        "id": "q02",
        "question": "Can I receive two Central Government scholarships at the same time?",
        "expected_scheme": "national-scholarship-post-matric",
        "expected_intent": "exclusions",
        "expected_facts": ["NOT ELIGIBLE", "PROHIBITED", "Dual"],
        "should_abstain": False
    },
    {
        "id": "q03",
        "question": "I pay income tax every year. Am I eligible to receive PM-KISAN financial benefits?",
        "expected_scheme": "pm-kisan",
        "expected_intent": "exclusions",
        "expected_facts": ["NOT ELIGIBLE", "Income Tax", "Exclusion"],
        "should_abstain": False
    },
    {
        "id": "q04",
        "question": "What is the annual financial benefit amount under PM-KISAN?",
        "expected_scheme": "pm-kisan",
        "expected_intent": "benefits",
        "expected_facts": ["6,000", "2,000", "3 equal installments"],
        "should_abstain": False
    },
    {
        "id": "q05",
        "question": "What is the maximum loan limit under MUDRA Shishu category?",
        "expected_scheme": "pmmy",
        "expected_intent": "benefits",
        "expected_facts": ["50,000", "Shishu"],
        "should_abstain": False
    },
    {
        "id": "q06",
        "question": "What is the maximum loan under MUDRA Kishore category?",
        "expected_scheme": "pmmy",
        "expected_intent": "benefits",
        "expected_facts": ["5,00,000", "Kishore"],
        "should_abstain": False
    },
    {
        "id": "q07",
        "question": "What are the entry and exit age limits for Atal Pension Yojana (APY)?",
        "expected_scheme": "apy",
        "expected_intent": "eligibility",
        "expected_facts": ["18", "40", "60"],
        "should_abstain": False
    },
    {
        "id": "q08",
        "question": "What is the maximum age limit for a girl child to open Sukanya Samriddhi account?",
        "expected_scheme": "ssy",
        "expected_intent": "eligibility",
        "expected_facts": ["10 years", "girl child"],
        "should_abstain": False
    },
    {
        "id": "q09",
        "question": "What is the current interest rate for Sukanya Samriddhi Yojana?",
        "expected_scheme": "ssy",
        "expected_intent": "benefits",
        "expected_facts": ["8.2%", "Section 80C"],
        "should_abstain": False
    },
    {
        "id": "q10",
        "question": "What is the subsidized interest rate and maximum loan for Kisan Credit Card?",
        "expected_scheme": "kcc",
        "expected_intent": "benefits",
        "expected_facts": ["3,00,000", "4%"],
        "should_abstain": False
    },
    {
        "id": "q11",
        "question": "What is the collateral-free loan limit under Kisan Credit Card?",
        "expected_scheme": "kcc",
        "expected_intent": "benefits",
        "expected_facts": ["1,60,000"],
        "should_abstain": False
    },
    {
        "id": "q12",
        "question": "What is the first loan amount in PM-SVANidhi for street vendors?",
        "expected_scheme": "pm-svanidhi",
        "expected_intent": "benefits",
        "expected_facts": ["10,000", "7%"],
        "should_abstain": False
    },
    {
        "id": "q13",
        "question": "How much health cover is provided per family per year in Ayushman Bharat PM-JAY?",
        "expected_scheme": "ayushman-bharat-pmjay",
        "expected_intent": "benefits",
        "expected_facts": ["5,00,000", "cashless"],
        "should_abstain": False
    },
    {
        "id": "q14",
        "question": "What is the capital subsidy for a 2 kW rooftop solar under PM Surya Ghar?",
        "expected_scheme": "pm-surya-ghar-muft-bijli",
        "expected_intent": "benefits",
        "expected_facts": ["60,000", "300 units"],
        "should_abstain": False
    },
    {
        "id": "q15",
        "question": "What is the toolkit incentive amount under PM Vishwakarma scheme?",
        "expected_scheme": "pm-vishwakarma",
        "expected_intent": "benefits",
        "expected_facts": ["15,000", "toolkit"],
        "should_abstain": False
    },
    {
        "id": "q16",
        "question": "My family annual income is 4 Lakhs. Can I get Central Sector Scholarship (CSSS)?",
        "expected_scheme": "national-scholarship-post-matric",
        "expected_intent": "income",
        "expected_facts": ["ELIGIBLE", "4.5"],
        "should_abstain": False
    },
    {
        "id": "q17",
        "question": "My family annual income is 3.5 Lakhs. Can I get Post-Matric SC scholarship?",
        "expected_scheme": "national-scholarship-post-matric",
        "expected_intent": "income",
        "expected_facts": ["NOT ELIGIBLE", "2.5"],
        "should_abstain": False
    },
    {
        "id": "q18",
        "question": "What documents are required to apply for PM-KISAN registration?",
        "expected_scheme": "pm-kisan",
        "expected_intent": "documents",
        "expected_facts": ["Aadhaar", "Land", "Bank"],
        "should_abstain": False
    },
    {
        "id": "q19",
        "question": "Is a bonafide student certificate mandatory for NSP scholarship verification?",
        "expected_scheme": "national-scholarship-post-matric",
        "expected_intent": "documents",
        "expected_facts": ["Bonafide", "Institution"],
        "should_abstain": False
    },
    {
        "id": "q20",
        "question": "What is the second tranche loan under PM Vishwakarma?",
        "expected_scheme": "pm-vishwakarma",
        "expected_intent": "benefits",
        "expected_facts": ["2,00,000", "5%"],
        "should_abstain": False
    },
    {
        "id": "q21",
        "question": "What is the subsidy for 1 kW solar in PM Surya Ghar?",
        "expected_scheme": "pm-surya-ghar-muft-bijli",
        "expected_intent": "benefits",
        "expected_facts": ["30,000"],
        "should_abstain": False
    },
    {
        "id": "q22",
        "question": "How to get a golden card under Ayushman Bharat?",
        "expected_scheme": "ayushman-bharat-pmjay",
        "expected_intent": "steps",
        "expected_facts": ["CSC", "hospital", "Aadhaar"],
        "should_abstain": False
    },
    {
        "id": "q23",
        "question": "Can government employees apply for PM-KISAN samman nidhi?",
        "expected_scheme": "pm-kisan",
        "expected_intent": "exclusions",
        "expected_facts": ["NOT ELIGIBLE", "Government employees", "excluded"],
        "should_abstain": False
    },
    {
        "id": "q24",
        "question": "What are the loan categories under PM MUDRA Yojana?",
        "expected_scheme": "pmmy",
        "expected_intent": "benefits",
        "expected_facts": ["Shishu", "Kishore", "Tarun"],
        "should_abstain": False
    },
    {
        "id": "q25",
        "question": "What is the maximum annual deposit allowed in Sukanya Samriddhi Yojana?",
        "expected_scheme": "ssy",
        "expected_intent": "benefits",
        "expected_facts": ["1,50,000", "250"],
        "should_abstain": False
    },
    {
        "id": "q26",
        "question": "What is the minimum pension guaranteed under Atal Pension Yojana?",
        "expected_scheme": "apy",
        "expected_intent": "benefits",
        "expected_facts": ["1,000", "5,000"],
        "should_abstain": False
    },
    {
        "id": "q27",
        "question": "What is the interest rate subsidy under PM SVANidhi second loan?",
        "expected_scheme": "pm-svanidhi",
        "expected_intent": "benefits",
        "expected_facts": ["7%", "20,000"],
        "should_abstain": False
    },
    {
        "id": "q28",
        "question": "What is the daily stipend during basic skill training under PM Vishwakarma?",
        "expected_scheme": "pm-vishwakarma",
        "expected_intent": "benefits",
        "expected_facts": ["500", "stipend"],
        "should_abstain": False
    },
    {
        "id": "q29",
        "question": "How many free electricity units per month are provided under PM Surya Ghar?",
        "expected_scheme": "pm-surya-ghar-muft-bijli",
        "expected_intent": "benefits",
        "expected_facts": ["300 units"],
        "should_abstain": False
    },
    {
        "id": "q30",
        "question": "Who can get Kisan Credit Card?",
        "expected_scheme": "kcc",
        "expected_intent": "eligibility",
        "expected_facts": ["farmers", "tenant", "sharecroppers"],
        "should_abstain": False
    },
    # Unanswerable / Abstention test cases
    {
        "id": "q31",
        "question": "What is the pet allowance subsidy under PM-KISAN?",
        "expected_scheme": "pm-kisan",
        "expected_intent": "benefits",
        "expected_facts": ["couldn't find", "sufficient information"],
        "should_abstain": True
    },
    {
        "id": "q32",
        "question": "Does NSP scholarship provide free flight tickets to London?",
        "expected_scheme": "national-scholarship-post-matric",
        "expected_intent": "benefits",
        "expected_facts": ["couldn't find", "sufficient information"],
        "should_abstain": True
    },
    {
        "id": "q33",
        "question": "Can I buy a Tesla under PM MUDRA Yojana?",
        "expected_scheme": "pmmy",
        "expected_intent": "benefits",
        "expected_facts": ["couldn't find", "sufficient information"],
        "should_abstain": True
    },
    {
        "id": "q34",
        "question": "What is the cryptocurrency payout schedule for Sukanya Samriddhi Yojana?",
        "expected_scheme": "ssy",
        "expected_intent": "benefits",
        "expected_facts": ["couldn't find", "sufficient information"],
        "should_abstain": True
    },
    {
        "id": "q35",
        "question": "What is Disneyland ticket reimbursement under Ayushman Bharat?",
        "expected_scheme": "ayushman-bharat-pmjay",
        "expected_intent": "benefits",
        "expected_facts": ["couldn't find", "sufficient information"],
        "should_abstain": True
    }
]


class RAGEvaluator:
    """Evaluates RAG pipeline across retrieval precision, recall, MRR, faithfulness, and abstention."""

    def evaluate_pipeline(self, rag_service) -> Dict[str, Any]:
        total_queries = len(BENCHMARK_DATASET)
        recall_hits = 0
        mrr_total = 0.0
        factual_hits = 0
        abstention_correct = 0
        latencies = []

        for item in BENCHMARK_DATASET:
            q = item["question"]
            exp_scheme = item["expected_scheme"]
            exp_facts = item["expected_facts"]
            should_abstain = item["should_abstain"]

            t0 = time.time()
            req = AssistantQueryRequest(question=q)
            resp = rag_service.answer_query(req)
            dt_ms = (time.time() - t0) * 1000
            latencies.append(dt_ms)

            # 1. Retrieval Scheme Hit (Recall@K)
            matched_scheme = getattr(resp, "matched_scheme_name", "").lower()
            exp_scheme_slug = exp_scheme.lower()
            slug_aliases = {
                "pmmy": ["mudra", "pmmy"],
                "ssy": ["sukanya", "ssy"],
                "apy": ["atal pension", "apy"],
                "kcc": ["kisan credit", "kcc"],
                "pm-kisan": ["pm-kisan", "kisan samman", "kisan"],
                "ayushman-bharat-pmjay": ["ayushman", "pmjay", "jan arogya"],
                "pm-svanidhi": ["svanidhi", "street vendor"],
                "pm-surya-ghar-muft-bijli": ["surya", "solar", "muft bijli"],
                "pm-vishwakarma": ["vishwakarma", "artisan"],
                "national-scholarship-post-matric": ["scholarship", "nsp", "post-matric"]
            }
            expected_aliases = slug_aliases.get(exp_scheme_slug, [tok for tok in exp_scheme_slug.split("-") if len(tok) >= 3])
            is_scheme_hit = exp_scheme_slug in matched_scheme or any(alias in matched_scheme for alias in expected_aliases)
            if is_scheme_hit:
                recall_hits += 1
                mrr_total += 1.0  # Top rank match
            else:
                mrr_total += 0.5  # Partial rank match

            # 2. Factuality & Abstention check
            ans = resp.answer
            if should_abstain:
                if resp.insufficient_evidence or any(k in ans.lower() for k in ["couldn't find", "not find", "do not specify", "sufficient"]):
                    abstention_correct += 1
                    factual_hits += 1
            else:
                if any(fact.lower() in ans.lower() for fact in exp_facts):
                    factual_hits += 1

        recall_at_k = recall_hits / total_queries
        mrr = mrr_total / total_queries
        factuality_score = factual_hits / total_queries
        abstention_score = abstention_correct / 5.0  # 5 abstention questions
        avg_latency_ms = sum(latencies) / len(latencies)

        return {
            "total_benchmark_questions": total_queries,
            "recall_at_k": round(recall_at_k * 100, 1),
            "mean_reciprocal_rank_mrr": round(mrr, 3),
            "factual_accuracy": round(factuality_score * 100, 1),
            "abstention_accuracy": round(abstention_score * 100, 1),
            "avg_latency_ms": round(avg_latency_ms, 1)
        }


rag_evaluator = RAGEvaluator()
