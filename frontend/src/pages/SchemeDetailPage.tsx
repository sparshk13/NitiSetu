import React, { useEffect, useState } from 'react';
import { 
  ArrowLeft, 
  ExternalLink, 
  CheckCircle2, 
  XCircle, 
  AlertCircle, 
  FileText, 
  Bot, 
  ShieldCheck, 
  Building2, 
  GraduationCap, 
  HelpCircle,
  Clock,
  Sparkles,
  FileCheck2
} from 'lucide-react';
import { api, SchemeDetail, EligibilityResponse } from '../api/client';

interface SchemeDetailProps {
  slug: string;
  onBack: () => void;
  onNavigate: (tab: string, schemeSlug?: string) => void;
}

export const SchemeDetailPage: React.FC<SchemeDetailProps> = ({ slug, onBack, onNavigate }) => {
  const [scheme, setScheme] = useState<SchemeDetail | null>(null);
  const [eligibility, setEligibility] = useState<EligibilityResponse | null>(null);
  const [checkingEligibility, setCheckingEligibility] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function load() {
      setLoading(true);
      const data = await api.getSchemeDetail(slug);
      setScheme(data);
      setLoading(false);
    }
    load();
  }, [slug]);

  const handleCheckEligibility = async () => {
    setCheckingEligibility(true);
    const result = await api.checkEligibility(slug);
    setEligibility(result);
    setCheckingEligibility(false);
  };

  if (loading || !scheme) {
    return (
      <div className="py-20 text-center text-slate-400 text-sm">
        Loading authentic scheme details from official gazette repository...
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto space-y-8">
      {/* Back button and quick actions */}
      <div className="flex items-center justify-between">
        <button
          onClick={onBack}
          className="inline-flex items-center gap-1.5 text-xs sm:text-sm font-semibold text-slate-600 hover:text-slate-900"
        >
          <ArrowLeft className="w-4 h-4" /> Back to Discovery
        </button>

        <div className="flex flex-wrap items-center gap-2">
          <button
            onClick={() => onNavigate('assistant', scheme.slug)}
            className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg border border-slate-200 bg-white hover:bg-slate-50 text-slate-700 text-xs font-semibold shadow-xs"
          >
            <Bot className="w-3.5 h-3.5 text-blue-600" />
            Ask Policy AI
          </button>
          <button
            onClick={() => onNavigate('documents', scheme.slug)}
            className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg border border-slate-200 bg-white hover:bg-slate-50 text-slate-700 text-xs font-semibold shadow-xs"
          >
            <FileText className="w-3.5 h-3.5 text-blue-600" />
            Check Documents
          </button>
          <button
            onClick={() => onNavigate('application', scheme.slug)}
            className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-slate-900 hover:bg-slate-800 text-white text-xs font-semibold shadow-xs"
          >
            <FileCheck2 className="w-3.5 h-3.5 text-emerald-400" />
            Prepare Application
          </button>
          <a
            href={scheme.official_url}
            target="_blank"
            rel="noreferrer"
            className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-blue-600 hover:bg-blue-500 text-white text-xs font-semibold shadow-xs"
          >
            Official Portal <ExternalLink className="w-3.5 h-3.5" />
          </a>
        </div>
      </div>

      {/* Main Scheme Header Card */}
      <div className="bg-white rounded-2xl border border-slate-200 p-6 sm:p-8 shadow-xs">
        <div className="flex flex-wrap items-center gap-2 mb-3">
          <span className="text-xs font-semibold px-2.5 py-0.5 rounded-full bg-slate-100 text-slate-700 border border-slate-200">
            {scheme.level}
          </span>
          <span className="text-xs px-2.5 py-0.5 rounded-full bg-blue-50 text-blue-700 font-medium border border-blue-200">
            {scheme.state_or_ministry || 'Ministry of Education'}
          </span>
          <span className="text-xs text-slate-400 font-mono ml-auto">
            Last Verified: {scheme.last_verified_at}
          </span>
        </div>

        <h1 className="text-xl sm:text-2xl font-bold text-slate-900 mb-3 leading-snug">
          {scheme.name}
        </h1>

        <p className="text-slate-600 text-sm leading-relaxed mb-6">
          {scheme.description || scheme.summary}
        </p>

        {/* Benefits Highlight Box */}
        {scheme.benefit_summary && (
          <div className="bg-slate-50 border border-slate-200 rounded-xl p-4 sm:p-5 mb-6">
            <h3 className="text-xs font-semibold uppercase tracking-wider text-slate-500 mb-1.5">
              Financial Assistance & Benefits
            </h3>
            <p className="text-sm font-medium text-slate-800 leading-relaxed">
              {scheme.benefit_summary}
            </p>
          </div>
        )}

        {/* Deterministic Eligibility Check Section */}
        <div className="pt-6 border-t border-slate-100">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-4">
            <div>
              <h3 className="text-base font-bold text-slate-900 flex items-center gap-2">
                <ShieldCheck className="w-5 h-5 text-emerald-600" />
                Deterministic Eligibility Assessment
              </h3>
              <p className="text-xs text-slate-500">
                Rule-based evaluation of your confirmed income, category, and educational status.
              </p>
            </div>

            <button
              onClick={handleCheckEligibility}
              disabled={checkingEligibility}
              className="inline-flex items-center justify-center gap-2 px-4 py-2 rounded-lg bg-emerald-600 hover:bg-emerald-500 disabled:opacity-50 text-white text-xs font-semibold transition-all shadow-xs"
            >
              <Sparkles className="w-3.5 h-3.5" />
              {checkingEligibility ? 'Evaluating Rules...' : 'Check My Eligibility'}
            </button>
          </div>

          {/* Eligibility Result Breakdown Card */}
          {eligibility && (
            <div className={`mt-4 rounded-xl border p-5 ${
              eligibility.status === 'potentially_eligible' 
                ? 'bg-emerald-50/70 border-emerald-200' 
                : eligibility.status === 'not_eligible'
                ? 'bg-rose-50/70 border-rose-200'
                : eligibility.status === 'needs_information'
                ? 'bg-amber-50/70 border-amber-200'
                : 'bg-slate-50 border-slate-200'
            }`}>
              <div className="flex items-center gap-2 mb-2">
                {eligibility.status === 'potentially_eligible' && (
                  <CheckCircle2 className="w-5 h-5 text-emerald-600" />
                )}
                {eligibility.status === 'not_eligible' && (
                  <XCircle className="w-5 h-5 text-rose-600" />
                )}
                {eligibility.status === 'needs_information' && (
                  <AlertCircle className="w-5 h-5 text-amber-600" />
                )}
                {eligibility.status === 'not_assessed' && (
                  <HelpCircle className="w-5 h-5 text-blue-600" />
                )}
                <span className="font-bold text-sm uppercase tracking-wide">
                  {eligibility.status === 'potentially_eligible' && 'Potentially Eligible'}
                  {eligibility.status === 'not_eligible' && 'Not Currently Eligible'}
                  {eligibility.status === 'needs_information' && 'Additional Information Required'}
                  {eligibility.status === 'not_assessed' && 'General Criteria / Manual Review Required'}
                </span>
              </div>

              <p className="text-xs text-slate-700 leading-relaxed mb-4">
                {eligibility.summary_explanation}
              </p>

              {/* Matched Rules */}
              {eligibility.matched_rules.length > 0 && (
                <div className="space-y-1.5 mb-3">
                  <div className="text-[11px] font-semibold text-emerald-800 uppercase">Passed Criteria:</div>
                  {eligibility.matched_rules.map((rule, idx) => (
                    <div key={idx} className="text-xs text-emerald-900 bg-white/70 p-2 rounded border border-emerald-200 flex items-start justify-between">
                      <span>✓ {rule.condition_description}</span>
                      <span className="text-[10px] text-slate-500 font-mono shrink-0 ml-2">{rule.source_section}</span>
                    </div>
                  ))}
                </div>
              )}

              {/* Failed Rules */}
              {eligibility.failed_rules.length > 0 && (
                <div className="space-y-1.5 mb-3">
                  <div className="text-[11px] font-semibold text-rose-800 uppercase">Unmet Mandatory Conditions:</div>
                  {eligibility.failed_rules.map((rule, idx) => (
                    <div key={idx} className="text-xs text-rose-900 bg-white/70 p-2 rounded border border-rose-200 flex items-start justify-between">
                      <span>✗ {rule.condition_description} (Your fact: {String(rule.user_value)})</span>
                      <span className="text-[10px] text-slate-500 font-mono shrink-0 ml-2">{rule.source_section}</span>
                    </div>
                  ))}
                </div>
              )}

              <div className="text-[11px] text-slate-500 pt-2 border-t border-slate-200/50">
                {eligibility.disclaimer}
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Eligibility Details Text */}
      {scheme.eligibility_criteria_text && (
        <div className="bg-white rounded-xl border border-slate-200 p-6 shadow-xs space-y-3">
          <h2 className="text-base font-bold text-slate-900">Official Eligibility Criteria</h2>
          <div className="text-xs text-slate-700 leading-relaxed whitespace-pre-line bg-slate-50 p-4 rounded-lg border border-slate-100">
            {scheme.eligibility_criteria_text}
          </div>
        </div>
      )}

      {/* Required Documents Section */}
      <div className="bg-white rounded-xl border border-slate-200 p-6 shadow-xs space-y-4">
        <div className="flex items-center justify-between">
          <h2 className="text-base font-bold text-slate-900 flex items-center gap-2">
            <FileText className="w-4 h-4 text-slate-500" />
            Mandatory Documents Required
          </h2>
          <button
            onClick={() => onNavigate('documents')}
            className="text-xs font-semibold text-blue-600 hover:text-blue-700"
          >
            Check My Uploaded Documents →
          </button>
        </div>

        {scheme.documents_required_text ? (
          <div className="text-xs text-slate-700 leading-relaxed bg-slate-50 p-4 rounded-lg border border-slate-100 whitespace-pre-line">
            {scheme.documents_required_text}
          </div>
        ) : (
          <p className="text-xs text-slate-500">Standard documents: Aadhaar, Income Certificate, Educational Marksheets, and Bank Details.</p>
        )}
      </div>

      {/* Application Procedure */}
      {scheme.application_process_text && (
        <div className="bg-white rounded-xl border border-slate-200 p-6 shadow-xs space-y-3">
          <h2 className="text-base font-bold text-slate-900 flex items-center gap-2">
            <Clock className="w-4 h-4 text-slate-500" />
            Official Application Procedure
          </h2>
          <div className="text-xs text-slate-700 leading-relaxed bg-slate-50 p-4 rounded-lg border border-slate-100 whitespace-pre-line">
            {scheme.application_process_text}
          </div>
        </div>
      )}

      {/* Official FAQs */}
      {scheme.faqs && (
        <div className="bg-white rounded-xl border border-slate-200 p-6 shadow-xs space-y-3">
          <h2 className="text-base font-bold text-slate-900 flex items-center gap-2">
            <HelpCircle className="w-4 h-4 text-slate-500" />
            Frequently Asked Questions (Official Ministry Q&A)
          </h2>
          <div className="text-xs text-slate-700 leading-relaxed bg-slate-50 p-4 rounded-lg border border-slate-100 whitespace-pre-line">
            {scheme.faqs}
          </div>
        </div>
      )}

      {/* Provenance Footer */}
      <div className="text-center text-xs text-slate-400 font-mono py-4">
        Source: {scheme.source_provenance} • Verified {scheme.last_verified_at}
      </div>
    </div>
  );
};

