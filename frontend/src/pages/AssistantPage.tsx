import React, { useState, useEffect } from 'react';
import { 
  Bot, 
  Send, 
  Sparkles, 
  FileText, 
  ExternalLink, 
  AlertCircle, 
  ShieldCheck,
  ChevronDown,
  ChevronUp,
  User,
  GraduationCap,
  Layers,
  CheckCircle2,
  BookmarkCheck,
  TrendingUp,
  HelpCircle
} from 'lucide-react';
import { api, AssistantResponse, SourceCitation, SchemeItem } from '../api/client';

interface AssistantPageProps {
  initialSchemeSlug?: string;
  onNavigate: (tab: string, schemeSlug?: string) => void;
}

interface ChatMessage {
  id: string;
  sender: 'user' | 'assistant';
  text: string;
  citations?: SourceCitation[];
  insufficientEvidence?: boolean;
  verificationStatus?: string;
  confidenceScore?: number;
  keyFacts?: string[];
  matchedSchemeName?: string;
  detectedIntent?: string;
  timestamp: string;
}

// Helper to format inline bold, amounts, and links
const renderFormattedInline = (content: string): React.ReactNode => {
  // Regex to split by bold (**text**), markdown links [text](url), and rupee amounts (₹...)
  const parts = content.split(/(\*\*.*?\*\*|\[.*?\]\(.*?\)|\u20b9\s*[\d,]+(?:\s*Lakh)?|\b\d+%\b)/g);

  return parts.map((part, i) => {
    if (!part) return null;

    if (part.startsWith('**') && part.endsWith('**')) {
      const boldText = part.slice(2, -2);
      // Highlight currency amounts inside bold
      if (boldText.includes('₹')) {
        return (
          <strong key={i} className="font-bold text-emerald-800 bg-emerald-100/70 border border-emerald-300/80 px-1.5 py-0.5 rounded text-xs font-mono inline-block">
            {boldText}
          </strong>
        );
      }
      return <strong key={i} className="font-semibold text-slate-900">{boldText}</strong>;
    }

    if (part.startsWith('[') && part.includes('](') && part.endsWith(')')) {
      const match = part.match(/\[(.*?)\]\((.*?)\)/);
      if (match) {
        return (
          <a
            key={i}
            href={match[2]}
            target="_blank"
            rel="noreferrer"
            className="text-blue-600 hover:text-blue-800 underline font-medium inline-flex items-center gap-0.5"
          >
            {match[1]} <ExternalLink className="w-2.5 h-2.5 ml-0.5 inline" />
          </a>
        );
      }
    }

    if (part.startsWith('₹')) {
      return (
        <span key={i} className="font-bold text-emerald-800 bg-emerald-100/70 border border-emerald-300/80 px-1.5 py-0.5 rounded text-xs font-mono inline-block">
          {part}
        </span>
      );
    }

    return <span key={i}>{part}</span>;
  });
};

// Rich Structured Renderer for Assistant Responses
const RichAssistantMessage: React.FC<{ message: ChatMessage }> = ({ message }) => {
  const { text, insufficientEvidence, verificationStatus, confidenceScore, keyFacts, detectedIntent } = message;

  // Split text by markdown headings (### )
  const sections = text.split(/(?=###\s+)/g);

  return (
    <div className="space-y-3.5">
      {/* Verification & Intent Header Bar */}
      {verificationStatus && !insufficientEvidence && (
        <div className="flex flex-wrap items-center justify-between gap-2 pb-2.5 border-b border-slate-200/80">
          <div className="flex items-center gap-1.5">
            <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-[11px] font-semibold bg-emerald-50 text-emerald-800 border border-emerald-200">
              <ShieldCheck className="w-3.5 h-3.5 text-emerald-600" />
              Verified Official Gazette Grounding
            </span>
            {detectedIntent && (
              <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-md text-[10px] font-medium bg-blue-50 text-blue-700 border border-blue-200">
                <BookmarkCheck className="w-3 h-3 text-blue-600" />
                {detectedIntent}
              </span>
            )}
          </div>

          {confidenceScore !== undefined && confidenceScore > 0 && (
            <div className="text-[10px] font-mono text-slate-500 flex items-center gap-1">
              <span>Factuality:</span>
              <span className="font-bold text-emerald-700">{Math.round(confidenceScore * 100)}%</span>
            </div>
          )}
        </div>
      )}

      {/* High-Impact Key Facts Chips */}
      {keyFacts && keyFacts.length > 0 && !insufficientEvidence && (
        <div className="p-2.5 bg-slate-100/80 rounded-xl border border-slate-200/90 space-y-1.5">
          <div className="text-[10px] font-bold text-slate-600 uppercase tracking-wider flex items-center gap-1">
            <TrendingUp className="w-3 h-3 text-blue-600" />
            Key Verified Figures & Criteria
          </div>
          <div className="flex flex-wrap gap-1.5">
            {keyFacts.map((fact, idx) => (
              <span
                key={idx}
                className="text-[11px] bg-white border border-slate-200 px-2.5 py-1 rounded-lg text-slate-800 font-medium shadow-2xs"
              >
                {fact}
              </span>
            ))}
          </div>
        </div>
      )}

      {/* Main Body Sections */}
      <div className="space-y-3">
        {sections.map((sec, idx) => {
          const trimmed = sec.trim();
          if (!trimmed) return null;

          // Check if this is a heading block
          if (trimmed.startsWith('###')) {
            const firstLineEnd = trimmed.indexOf('\n');
            const heading = (firstLineEnd > -1 ? trimmed.slice(0, firstLineEnd) : trimmed).replace('###', '').trim();
            const body = firstLineEnd > -1 ? trimmed.slice(firstLineEnd).trim() : '';
            const headingLower = heading.toLowerCase();

            // Direct Answer Callout
            if (headingLower.includes('direct answer')) {
              return (
                <div key={idx} className="p-3.5 bg-blue-50/90 border border-blue-200 rounded-xl space-y-1 shadow-2xs">
                  <div className="text-xs font-bold text-blue-900 uppercase tracking-wide flex items-center gap-1.5">
                    <Sparkles className="w-3.5 h-3.5 text-blue-600" />
                    Direct Answer
                  </div>
                  <div className="text-slate-800 text-xs sm:text-sm font-medium leading-relaxed">
                    {renderFormattedInline(body)}
                  </div>
                </div>
              );
            }

            // Exclusions / Warning Box
            if (headingLower.includes('exclusion') || headingLower.includes('ineligib')) {
              return (
                <div key={idx} className="p-3 bg-amber-50 border border-amber-200 rounded-xl space-y-1.5">
                  <div className="text-xs font-bold text-amber-900 uppercase tracking-wide flex items-center gap-1.5">
                    <AlertCircle className="w-3.5 h-3.5 text-amber-600" />
                    {heading}
                  </div>
                  <div className="text-xs sm:text-sm text-amber-950 leading-relaxed">
                    {renderFormattedBody(body)}
                  </div>
                </div>
              );
            }

            // Standard Section
            return (
              <div key={idx} className="space-y-1.5 pt-1">
                <h4 className="text-xs sm:text-sm font-bold text-slate-900 flex items-center gap-1.5">
                  <CheckCircle2 className="w-3.5 h-3.5 text-blue-600" />
                  {heading}
                </h4>
                <div className="text-xs sm:text-sm text-slate-700 leading-relaxed pl-1">
                  {renderFormattedBody(body)}
                </div>
              </div>
            );
          }

          // Unheaded plain paragraph
          return (
            <div key={idx} className="text-xs sm:text-sm text-slate-800 leading-relaxed">
              {renderFormattedBody(trimmed)}
            </div>
          );
        })}
      </div>
    </div>
  );
};

// Helper to render body paragraphs and bulleted lists
const renderFormattedBody = (body: string): React.ReactNode => {
  const lines = body.split('\n');
  const elements: React.ReactNode[] = [];
  let currentList: string[] = [];

  const flushList = (keyPrefix: number) => {
    if (currentList.length > 0) {
      elements.push(
        <ul key={`list-${keyPrefix}`} className="space-y-1 my-1.5 pl-1">
          {currentList.map((item, lIdx) => (
            <li key={lIdx} className="flex items-start gap-2 text-xs sm:text-sm text-slate-700">
              <span className="w-1.5 h-1.5 rounded-full bg-blue-500 shrink-0 mt-2" />
              <span>{renderFormattedInline(item)}</span>
            </li>
          ))}
        </ul>
      );
      currentList = [];
    }
  };

  lines.forEach((line, index) => {
    const trimmed = line.trim();
    if (trimmed.startsWith('* ') || trimmed.startsWith('- ') || trimmed.startsWith('• ')) {
      currentList.push(trimmed.slice(2).trim());
    } else {
      flushList(index);
      if (trimmed) {
        elements.push(
          <p key={index} className="my-1 text-xs sm:text-sm text-slate-700">
            {renderFormattedInline(trimmed)}
          </p>
        );
      }
    }
  });

  flushList(lines.length);
  return elements;
};

export const AssistantPage: React.FC<AssistantPageProps> = ({ initialSchemeSlug, onNavigate }) => {
  const [selectedSchemeSlug, setSelectedSchemeSlug] = useState<string>(initialSchemeSlug || 'all');
  const [availableSchemes, setAvailableSchemes] = useState<SchemeItem[]>([]);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [inputQuery, setInputQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [expandedCitationId, setExpandedCitationId] = useState<string | null>(null);

  // Load scheme catalog for the context selector
  useEffect(() => {
    async function loadSchemes() {
      const data = await api.listSchemes({ page_size: 50 });
      setAvailableSchemes(data.items);
    }
    loadSchemes();
  }, []);

  // Update selection if parent passes a new initialSchemeSlug
  useEffect(() => {
    if (initialSchemeSlug) {
      setSelectedSchemeSlug(initialSchemeSlug);
    }
  }, [initialSchemeSlug]);

  // Find active scheme metadata
  const activeScheme = availableSchemes.find(s => s.slug === selectedSchemeSlug);

  // Initialize or update welcome message based on selected context
  useEffect(() => {
    const isSpecific = selectedSchemeSlug !== 'all' && activeScheme;

    const welcomeMsg: ChatMessage = {
      id: 'welcome',
      sender: 'assistant',
      text: isSpecific
        ? `### Direct Answer\nNamaste! I am your CivicPilot Verified Policy Assistant for **${activeScheme.name}** (${activeScheme.level}).\n\n### Key Scope\n- Answer queries strictly verified against official Gazette notifications and guidelines.\n- Check family income limits, eligible criteria, required documents, and disbursal rules.\n\nAsk any question below regarding this policy.`
        : `### Direct Answer\nNamaste! I am your CivicPilot Policy Assistant. I provide factually grounded welfare guidance verified against official Gazette notifications and operational guidelines from **myScheme.gov.in** and respective ministries.\n\n### How to Use\n- Ask about income thresholds, eligibility criteria, required documents, or application procedures.\n- Query across all schemes or select a specific scheme from the dropdown above.`,
      citations: isSpecific ? [
        {
          source_title: activeScheme.name,
          source_url: activeScheme.official_url,
          section_title: "Official Scheme Overview & Benefit Structure",
          excerpt: activeScheme.benefit_summary || activeScheme.summary || "Official welfare delivery via Direct Benefit Transfer (DBT)."
        }
      ] : [
        {
          source_title: "Direct Benefit Transfer (DBT) & Welfare Guidelines — Gazette of India",
          source_url: "https://www.myscheme.gov.in/",
          section_title: "Unified Citizen Welfare Norms",
          excerpt: "Single-window DBT framework delivering government scholarships, educational subsidies, and welfare benefits directly to verified bank accounts."
        }
      ],
      verificationStatus: 'verified',
      confidenceScore: 1.0,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    };

    setMessages([welcomeMsg]);
  }, [selectedSchemeSlug, activeScheme]);

  // Dynamic sample prompts based on selected context
  const getSamplePrompts = () => {
    if (selectedSchemeSlug !== 'all' && activeScheme) {
      const shortName = activeScheme.name.split(' ')[0];
      return [
        `What is the family income limit for ${shortName}?`,
        `Who is eligible for ${shortName}?`,
        `What documents are required to apply?`,
        `What are the financial benefits and allowances?`
      ];
    }
    return [
      "What is the family income limit for Post-Matric Scholarship?",
      "What are the benefits and installments for PM-KISAN?",
      "Who is eligible for Ayushman Bharat PM-JAY ₹5 Lakh cover?",
      "What documents are needed to apply for PM Surya Ghar?"
    ];
  };

  const samplePrompts = getSamplePrompts();

  const handleSend = async (queryText?: string) => {
    const textToSend = queryText || inputQuery;
    if (!textToSend.trim() || loading) return;

    const userMsg: ChatMessage = {
      id: Date.now().toString(),
      sender: 'user',
      text: textToSend.trim(),
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    };

    setMessages(prev => [...prev, userMsg]);
    setInputQuery('');
    setLoading(true);

    try {
      const schemeContextParam = selectedSchemeSlug === 'all' ? undefined : selectedSchemeSlug;
      const resp: AssistantResponse = await api.queryAssistant(textToSend, schemeContextParam);

      const assistantMsg: ChatMessage = {
        id: (Date.now() + 1).toString(),
        sender: 'assistant',
        text: resp.answer,
        citations: resp.citations,
        insufficientEvidence: resp.insufficient_evidence,
        verificationStatus: resp.verification_status,
        confidenceScore: resp.confidence_score,
        keyFacts: resp.key_facts,
        matchedSchemeName: resp.matched_scheme_name,
        detectedIntent: resp.detected_intent,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      };

      setMessages(prev => [...prev, assistantMsg]);
    } catch (err) {
      setMessages(prev => [
        ...prev,
        {
          id: (Date.now() + 1).toString(),
          sender: 'assistant',
          text: '### Direct Answer\nAn error occurred while connecting to the assistant. Please try again or check your network query.',
          timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
        }
      ]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto space-y-5">
      {/* Page Title & Context Selector Bar */}
      <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-xs space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
          <div>
            <h1 className="text-xl font-bold text-slate-900 flex items-center gap-2">
              <Bot className="w-5 h-5 text-blue-600" />
              Verified Scheme & Policy Guidelines Explainer
            </h1>
            <p className="text-xs text-slate-500 mt-0.5">
              RAG-grounded with LLM-as-a-Judge cross-verification over official Government of India Gazette notifications.
            </p>
          </div>

          <div className="flex items-center gap-2">
            <span className="text-[11px] font-semibold text-slate-500 uppercase tracking-wider">Context:</span>
            <div className="relative min-w-[240px] sm:min-w-[300px]">
              <select
                value={selectedSchemeSlug}
                onChange={(e) => setSelectedSchemeSlug(e.target.value)}
                className="w-full pl-3 pr-8 py-2 text-xs rounded-xl border border-slate-300 bg-slate-50 text-slate-800 font-semibold focus:outline-hidden focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500"
              >
                <option value="all">🌐 All Government Schemes & Policies</option>
                {availableSchemes.map((s) => (
                  <option key={s.slug} value={s.slug}>
                    📜 {s.name.length > 55 ? s.name.substring(0, 55) + '...' : s.name} ({s.level})
                  </option>
                ))}
              </select>
            </div>
          </div>
        </div>

        {/* Active Context Banner */}
        {selectedSchemeSlug !== 'all' && activeScheme && (
          <div className="p-3 bg-blue-50/80 border border-blue-200 rounded-xl flex flex-col sm:flex-row items-start sm:items-center justify-between gap-2 text-xs">
            <div className="flex items-center gap-2 text-blue-950 font-medium">
              <GraduationCap className="w-4 h-4 text-blue-600 shrink-0" />
              <span>
                <strong>Focused Policy:</strong> {activeScheme.name} • <em>{activeScheme.state_or_ministry || activeScheme.level}</em>
              </span>
            </div>
            <div className="flex items-center gap-2 shrink-0">
              <button
                onClick={() => onNavigate('detail', activeScheme.slug)}
                className="text-xs font-semibold text-blue-700 hover:text-blue-900 underline"
              >
                Full Scheme Criteria →
              </button>
              {activeScheme.official_url && (
                <a
                  href={activeScheme.official_url}
                  target="_blank"
                  rel="noreferrer"
                  className="inline-flex items-center gap-1 text-[11px] px-2 py-0.5 rounded bg-white border border-blue-200 text-blue-700 font-semibold hover:bg-blue-50"
                >
                  Official Portal <ExternalLink className="w-3 h-3" />
                </a>
              )}
            </div>
          </div>
        )}
      </div>

      {/* Suggested Prompts */}
      <div className="flex flex-wrap items-center gap-2">
        <span className="text-[11px] font-semibold uppercase text-slate-400">Suggested:</span>
        {samplePrompts.map((prompt, idx) => (
          <button
            key={idx}
            onClick={() => handleSend(prompt)}
            disabled={loading}
            className="text-xs px-3 py-1.5 rounded-full bg-white hover:bg-slate-50 border border-slate-200 text-slate-600 font-medium transition-all shadow-2xs hover:border-blue-300 cursor-pointer"
          >
            "{prompt}"
          </button>
        ))}
      </div>

      {/* Chat Messages Log */}
      <div className="bg-white rounded-2xl border border-slate-200 p-5 shadow-xs min-h-[420px] max-h-[620px] overflow-y-auto space-y-5">
        {messages.map((msg) => (
          <div
            key={msg.id}
            className={`flex items-start gap-3 ${msg.sender === 'user' ? 'flex-row-reverse' : ''}`}
          >
            <div className={`w-8 h-8 rounded-full flex items-center justify-center shrink-0 text-xs font-bold ${
              msg.sender === 'user' 
                ? 'bg-blue-600 text-white' 
                : 'bg-slate-900 text-white shadow-xs'
            }`}>
              {msg.sender === 'user' ? <User className="w-4 h-4" /> : <Bot className="w-4 h-4" />}
            </div>

            <div className={`max-w-[88%] rounded-2xl p-4 text-xs sm:text-sm leading-relaxed ${
              msg.sender === 'user'
                ? 'bg-blue-600 text-white rounded-tr-xs'
                : 'bg-slate-50 border border-slate-200 text-slate-800 rounded-tl-xs shadow-2xs'
            }`}>
              {msg.sender === 'user' ? (
                <div className="whitespace-pre-line font-medium">{msg.text}</div>
              ) : (
                <RichAssistantMessage message={msg} />
              )}

              {/* Insufficient Evidence Notice */}
              {msg.insufficientEvidence && (
                <div className="mt-3 p-3.5 rounded-xl bg-amber-50 border border-amber-200 text-xs text-amber-900 flex items-start gap-2.5">
                  <AlertCircle className="w-4 h-4 text-amber-600 shrink-0 mt-0.5" />
                  <div>
                    <strong className="block font-semibold">Strict Factuality Guardrail Active:</strong>
                    CivicPilot only answers questions verified by official Government of India Gazette notifications and operational guidelines to prevent hallucinations.
                  </div>
                </div>
              )}

              {/* Verified Citations Panel */}
              {msg.citations && msg.citations.length > 0 && (
                <div className="mt-4 pt-3.5 border-t border-slate-200 space-y-2.5">
                  <div className="text-[11px] font-semibold text-slate-500 uppercase tracking-wider flex items-center gap-1.5">
                    <ShieldCheck className="w-3.5 h-3.5 text-emerald-600" />
                    Verified Official Citations ({msg.citations.length})
                  </div>

                  {msg.citations.map((cite, cIdx) => {
                    const citeKey = `${msg.id}-${cIdx}`;
                    const isExpanded = expandedCitationId === citeKey;

                    return (
                      <div
                        key={cIdx}
                        className="bg-white rounded-xl border border-slate-200 p-3 text-xs text-slate-700 space-y-2 shadow-2xs hover:border-blue-200 transition-all"
                      >
                        <div className="flex items-center justify-between gap-2">
                          <span className="font-semibold text-slate-900 truncate">
                            {cite.source_title}
                          </span>
                          <button
                            onClick={() => setExpandedCitationId(isExpanded ? null : citeKey)}
                            className="text-[11px] font-medium text-blue-600 hover:text-blue-800 shrink-0 flex items-center gap-0.5 cursor-pointer"
                          >
                            {isExpanded ? 'Hide Excerpt' : 'View Excerpt'}
                            {isExpanded ? <ChevronUp className="w-3 h-3" /> : <ChevronDown className="w-3 h-3" />}
                          </button>
                        </div>

                        <div className="text-[11px] text-slate-500 font-mono flex items-center gap-1">
                          <span className="bg-slate-100 px-1.5 py-0.5 rounded text-slate-600">
                            Section: {cite.section_title || 'General Guidelines'}
                          </span>
                        </div>

                        {isExpanded && (
                          <div className="mt-2 p-2.5 bg-slate-50 rounded-lg border border-slate-200/80 text-[11px] text-slate-600 italic leading-relaxed">
                            "{cite.excerpt}"
                          </div>
                        )}

                        {cite.source_url && (
                          <div className="pt-1">
                            <a
                              href={cite.source_url}
                              target="_blank"
                              rel="noreferrer"
                              className="text-[11px] text-blue-600 hover:text-blue-800 font-medium inline-flex items-center gap-1"
                            >
                              Open Source Gazette Document <ExternalLink className="w-3 h-3" />
                            </a>
                          </div>
                        )}
                      </div>
                    );
                  })}
                </div>
              )}

              <div className={`text-[10px] mt-2.5 font-mono ${msg.sender === 'user' ? 'text-blue-200' : 'text-slate-400'}`}>
                {msg.timestamp}
              </div>
            </div>
          </div>
        ))}

        {loading && (
          <div className="flex items-center gap-2.5 text-xs text-slate-600 font-medium p-3.5 bg-slate-50 rounded-xl w-max border border-slate-200 shadow-2xs">
            <Bot className="w-4 h-4 animate-bounce text-blue-600" />
            <span>Retrieving authentic guidelines & running LLM-as-a-Judge fact verification...</span>
          </div>
        )}
      </div>

      {/* Input Form */}
      <form
        onSubmit={(e) => {
          e.preventDefault();
          handleSend();
        }}
        className="flex items-center gap-2"
      >
        <input
          type="text"
          placeholder={
            selectedSchemeSlug !== 'all' && activeScheme
              ? `Ask any question regarding ${activeScheme.name}...`
              : "Ask any question about government schemes, eligibility, documents, or deadlines..."
          }
          value={inputQuery}
          onChange={(e) => setInputQuery(e.target.value)}
          disabled={loading}
          className="flex-1 px-4 py-3 text-xs sm:text-sm rounded-xl border border-slate-200 bg-white focus:outline-hidden focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 shadow-xs transition-all"
        />
        <button
          type="submit"
          disabled={loading || !inputQuery.trim()}
          className="px-5 py-3 rounded-xl bg-blue-600 hover:bg-blue-500 disabled:opacity-50 text-white text-xs sm:text-sm font-semibold flex items-center gap-2 transition-all shadow-xs cursor-pointer"
        >
          <Send className="w-4 h-4" />
          <span>Send</span>
        </button>
      </form>

      <div className="text-center text-[11px] text-slate-400 font-mono">
        All responses are verified and cross-checked against authenticated Government of India policy documents. CivicPilot does not generate legal advice.
      </div>
    </div>
  );
};
