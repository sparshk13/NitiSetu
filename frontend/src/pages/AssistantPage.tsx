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
  ArrowRight
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
  timestamp: string;
}

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

  // Initialize or update welcome message and dynamic prompts based on selected context
  useEffect(() => {
    const isSpecific = selectedSchemeSlug !== 'all' && activeScheme;
    const contextName = isSpecific ? activeScheme.name : "All Government Schemes & Welfare Policies";

    const welcomeMsg: ChatMessage = {
      id: 'welcome',
      sender: 'assistant',
      text: isSpecific
        ? `Namaste! I am your CivicPilot Policy Assistant for **${activeScheme.name}** (${activeScheme.level}).\n\nI answer queries strictly grounded in this scheme's published guidelines, eligibility criteria, income thresholds, and application procedures. How can I help you today?`
        : `Namaste! I am your CivicPilot Policy Assistant. I answer citizen welfare and scheme questions grounded in official Gazette notifications and operational guidelines from **myScheme.gov.in** and respective central and state ministries.\n\nYou can query across all government policies, or select a specific scheme from the dropdown above to focus the context.`,
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
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    };

    setMessages([welcomeMsg]);
  }, [selectedSchemeSlug, activeScheme]);

  // Dynamic sample prompts based on selected context
  const getSamplePrompts = () => {
    if (selectedSchemeSlug !== 'all' && activeScheme) {
      return [
        `What is the income ceiling for ${activeScheme.name.split(' ')[0]}?`,
        `Who is eligible for this scheme?`,
        `What documents are required to apply?`,
        `What benefits and allowances are provided?`
      ];
    }
    return [
      "What are the common family income limits for scholarships?",
      "Can I receive two government scholarships at the same time?",
      "What documents are needed for One Time Registration (OTR)?",
      "How does Direct Benefit Transfer (DBT) disbursal work?"
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
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      };

      setMessages(prev => [...prev, assistantMsg]);
    } catch (err) {
      setMessages(prev => [
        ...prev,
        {
          id: (Date.now() + 1).toString(),
          sender: 'assistant',
          text: 'An error occurred while connecting to the assistant. Please try again or check your query.',
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
              Scheme & Policy Guidelines Explainer
            </h1>
            <p className="text-xs text-slate-500 mt-0.5">
              Ask questions about any Indian government scheme, eligibility rule, or welfare notification.
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
            className="text-xs px-3 py-1.5 rounded-full bg-white hover:bg-slate-50 border border-slate-200 text-slate-600 font-medium transition-all shadow-2xs hover:border-blue-300"
          >
            "{prompt}"
          </button>
        ))}
      </div>

      {/* Chat Messages Log */}
      <div className="bg-white rounded-2xl border border-slate-200 p-5 shadow-xs min-h-[420px] max-h-[580px] overflow-y-auto space-y-5">
        {messages.map((msg) => (
          <div
            key={msg.id}
            className={`flex items-start gap-3 ${msg.sender === 'user' ? 'flex-row-reverse' : ''}`}
          >
            <div className={`w-8 h-8 rounded-full flex items-center justify-center shrink-0 text-xs font-bold ${
              msg.sender === 'user' 
                ? 'bg-blue-600 text-white' 
                : 'bg-slate-900 text-white'
            }`}>
              {msg.sender === 'user' ? <User className="w-4 h-4" /> : <Bot className="w-4 h-4" />}
            </div>

            <div className={`max-w-[85%] rounded-2xl p-4 text-xs sm:text-sm leading-relaxed ${
              msg.sender === 'user'
                ? 'bg-blue-600 text-white rounded-tr-xs'
                : 'bg-slate-50 border border-slate-200 text-slate-800 rounded-tl-xs'
            }`}>
              <div className="whitespace-pre-line">{msg.text}</div>

              {/* Insufficient Evidence Notice */}
              {msg.insufficientEvidence && (
                <div className="mt-3 p-3 rounded-lg bg-amber-50 border border-amber-200 text-xs text-amber-900 flex items-start gap-2">
                  <AlertCircle className="w-4 h-4 text-amber-600 shrink-0 mt-0.5" />
                  <div>
                    <strong>Unverified Fact Boundary:</strong> To prevent hallucinations, CivicPilot only answers questions verified by official government notifications.
                  </div>
                </div>
              )}

              {/* Citations Panel */}
              {msg.citations && msg.citations.length > 0 && (
                <div className="mt-4 pt-3 border-t border-slate-200/60 space-y-2">
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
                        className="bg-white rounded-lg border border-slate-200 p-2.5 text-xs text-slate-700 space-y-1.5"
                      >
                        <div className="flex items-center justify-between gap-2">
                          <span className="font-semibold text-slate-900 truncate">
                            {cite.source_title}
                          </span>
                          <button
                            onClick={() => setExpandedCitationId(isExpanded ? null : citeKey)}
                            className="text-[11px] font-medium text-blue-600 hover:text-blue-800 shrink-0 flex items-center gap-0.5"
                          >
                            {isExpanded ? 'Hide Excerpt' : 'View Excerpt'}
                            {isExpanded ? <ChevronUp className="w-3 h-3" /> : <ChevronDown className="w-3 h-3" />}
                          </button>
                        </div>

                        <div className="text-[11px] text-slate-500 font-mono">
                          Section: {cite.section_title || 'General Guidelines'}
                        </div>

                        {isExpanded && (
                          <div className="mt-2 p-2 bg-slate-50 rounded border border-slate-100 text-[11px] text-slate-600 italic leading-relaxed">
                            "{cite.excerpt}"
                          </div>
                        )}

                        {cite.source_url && (
                          <div className="pt-1">
                            <a
                              href={cite.source_url}
                              target="_blank"
                              rel="noreferrer"
                              className="text-[10px] text-blue-600 underline inline-flex items-center gap-1"
                            >
                              Open Source Document <ExternalLink className="w-2.5 h-2.5" />
                            </a>
                          </div>
                        )}
                      </div>
                    );
                  })}
                </div>
              )}

              <div className={`text-[10px] mt-2 font-mono ${msg.sender === 'user' ? 'text-blue-200' : 'text-slate-400'}`}>
                {msg.timestamp}
              </div>
            </div>
          </div>
        ))}

        {loading && (
          <div className="flex items-center gap-2 text-xs text-slate-500 italic p-3 bg-slate-50 rounded-lg w-max border border-slate-200">
            <Bot className="w-4 h-4 animate-bounce text-blue-600" />
            Retrieving official guidelines and synthesizing grounded answer...
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
          className="px-5 py-3 rounded-xl bg-blue-600 hover:bg-blue-500 disabled:opacity-50 text-white text-xs sm:text-sm font-semibold flex items-center gap-2 transition-all shadow-xs"
        >
          <Send className="w-4 h-4" />
          <span>Send</span>
        </button>
      </form>

      <div className="text-center text-[11px] text-slate-400 font-mono">
        All responses are checked against authenticated Government of India policy documents. CivicPilot does not generate legal advice.
      </div>
    </div>
  );
};
