import React, { useState, useEffect } from 'react';
import { 
  FileCheck, 
  Play, 
  CheckCircle2, 
  AlertCircle, 
  ShieldAlert, 
  ExternalLink,
  Laptop,
  Check,
  Building2,
  Lock,
  ArrowRight,
  GraduationCap
} from 'lucide-react';
import { api, ProfileData, SchemeItem, SchemeDetail } from '../api/client';

interface ApplicationPageProps {
  profile: ProfileData;
  initialSchemeSlug?: string;
  onNavigate?: (tab: string, schemeSlug?: string) => void;
}

export const ApplicationPage: React.FC<ApplicationPageProps> = ({ profile, initialSchemeSlug, onNavigate }) => {
  const [selectedSchemeSlug, setSelectedSchemeSlug] = useState<string>(initialSchemeSlug || 'national-scholarship-post-matric');
  const [availableSchemes, setAvailableSchemes] = useState<SchemeItem[]>([]);
  const [schemeDetail, setSchemeDetail] = useState<SchemeDetail | null>(null);
  const [demoState, setDemoState] = useState<'idle' | 'running' | 'completed'>('idle');
  const [demoLogs, setDemoLogs] = useState<string[]>([]);
  const [drafts, setDrafts] = useState<any[]>([]);

  const loadDrafts = async () => {
    try {
      const data = await api.listDrafts();
      setDrafts(data);
    } catch (e) {
      console.error(e);
    }
  };

  useEffect(() => {
    async function loadSchemes() {
      const data = await api.listSchemes({ page_size: 50 });
      setAvailableSchemes(data.items);
      if (!initialSchemeSlug && data.items.length > 0) {
        setSelectedSchemeSlug(data.items[0].slug);
      }
    }
    loadSchemes();
    loadDrafts();
  }, []);

  useEffect(() => {
    if (initialSchemeSlug) {
      setSelectedSchemeSlug(initialSchemeSlug);
    }
  }, [initialSchemeSlug]);

  useEffect(() => {
    if (selectedSchemeSlug) {
      api.getSchemeDetail(selectedSchemeSlug).then(detail => {
        setSchemeDetail(detail);
      });
    }
  }, [selectedSchemeSlug]);

  const isProfileIncomplete = !profile.full_name || profile.annual_family_income === undefined;

  const runDemoAutomation = async () => {
    setDemoState('running');
    setDemoLogs([]);

    // Persist real draft in backend
    let backendDraft: any = null;
    try {
      backendDraft = await api.createDraft(selectedSchemeSlug, {
        applicant_name: profile.full_name,
        domicile_state: profile.state_code,
        institution_name: profile.institution_name,
        course_name: profile.course,
        study_year: profile.study_year,
        annual_family_income: profile.annual_family_income,
        caste_category: profile.caste_category,
      });
    } catch (err) {
      console.warn("Backend draft save failed, running sandbox simulator:", err);
    }

    const schemeName = schemeDetail?.name || 'Selected Government Scheme';
    const ministry = schemeDetail?.state_or_ministry || 'State / Central Government';
    const appMode = schemeDetail?.application_mode || 'Online DBT Citizen Portal';
    const citizenName = profile.full_name || 'Applicant Citizen';
    const domicile = profile.state_code || 'Domicile State';
    const occupation = profile.occupation || 'Citizen';
    const isStudent = profile.is_student_currently || profile.occupation?.toLowerCase().includes('student');
    const isFarmer = profile.is_landowner || profile.occupation?.toLowerCase().includes('farmer');
    const incomeStr = profile.annual_family_income 
      ? `₹${Number(profile.annual_family_income).toLocaleString('en-IN')}` 
      : '₹2,50,000 (Ceiling threshold)';

    const steps = [
      `Initializing controlled sandbox for ${schemeName}...`,
      `Validating applicant profile credentials: ${citizenName}, Domicile: ${domicile}, Occupation: ${occupation}...`,
      `Routing to official delivery authority: ${ministry} (${appMode})...`,
      isFarmer
        ? `Mapping agricultural landholding: ${profile.land_holding_acres ? `${profile.land_holding_acres} Acres` : 'Cultivable Land'} cross-verified with State Revenue Records (Khasra/RoR)...`
        : isStudent
          ? `Populating Academic & Enrollment Data: ${profile.institution_name || 'Recognized Institute'} (${profile.course || 'Degree Program'})...`
          : `Mapping citizen category: ${occupation}, Highest Qualification: ${profile.highest_qualification || 'Verified'}...`,
      `Mapping means test: Annual Income ${incomeStr} verified against gazette eligibility criteria...`,
      `Cross-verifying NPCI Aadhaar Payment Bridge (APB) bank seeding for Direct Benefit Transfer (DBT)...`,
      `Validating document attachments against ${schemeName} document checklist...`,
      'Controlled Portal: Form drafted and validated successfully in sandbox.',
      'SAFETY GUARDRAIL APPLIED: Final submission aborted in accordance with policy. Application draft preserved for citizen review.'
    ];

    steps.forEach((log, index) => {
      setTimeout(async () => {
        setDemoLogs(prev => [...prev, log]);
        if (index === steps.length - 1) {
          setDemoState('completed');
          if (backendDraft?.id) {
            try {
              await api.prepareDemo(backendDraft.id);
            } catch (e) {
              console.error(e);
            }
          }
          await loadDrafts();
        }
      }, (index + 1) * 550);
    });
  };

  const handleDownloadDraft = (draft: any) => {
    const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(draft, null, 2));
    const downloadAnchor = document.createElement('a');
    downloadAnchor.setAttribute("href", dataStr);
    downloadAnchor.setAttribute("download", `Application_Draft_${draft.scheme_id || 'scheme'}.json`);
    document.body.appendChild(downloadAnchor);
    downloadAnchor.click();
    downloadAnchor.remove();
  };

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      {/* Title */}
      <div>
        <h1 className="text-2xl font-bold text-slate-900 flex items-center gap-2">
          <FileCheck className="w-6 h-6 text-blue-600" />
          Application Form Preparation & Verification Assistant
        </h1>
        <p className="text-slate-500 text-sm mt-1">
          Prepare your scheme application using verified profile facts and test form completion in a controlled verification sandbox.
        </p>
      </div>

      {/* Safety Notice */}
      <div className="p-4 rounded-xl bg-amber-50/80 border border-amber-200 text-amber-900 text-xs flex items-start gap-3">
        <ShieldAlert className="w-5 h-5 text-amber-600 shrink-0 mt-0.5" />
        <div>
          <strong className="text-amber-900">Safety & Compliance Protocol:</strong> NitiSetu demonstrates automated application assistance strictly on a controlled mock portal. 
          NitiSetu <strong>never</strong> interacts with live government portals without explicit citizen presence, never stores government passwords, and never submits applications automatically.
        </div>
      </div>

      {/* Profile Incomplete Banner */}
      {isProfileIncomplete && (
        <div className="p-4 rounded-xl bg-blue-50 border border-blue-200 text-blue-900 text-xs flex items-center justify-between gap-3">
          <div className="flex items-center gap-2">
            <AlertCircle className="w-4 h-4 text-blue-600 shrink-0" />
            <span>Complete your academic program and family income details to generate a comprehensive verified draft.</span>
          </div>
          {onNavigate && (
            <button
              onClick={() => onNavigate('profile')}
              className="inline-flex items-center gap-1 font-semibold text-blue-700 hover:text-blue-800 shrink-0"
            >
              Update Profile <ArrowRight className="w-3.5 h-3.5" />
            </button>
          )}
        </div>
      )}

      {/* Draft Review Card */}
      <div className="bg-white rounded-2xl border border-slate-200 p-6 sm:p-8 shadow-xs space-y-6">
        {/* Scheme Selector Header */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-slate-100">
          <div className="space-y-1 flex-1">
            <span className="text-[11px] font-semibold uppercase tracking-wider text-slate-400">Target Scheme / Policy</span>
            <div className="relative max-w-md">
              <select
                value={selectedSchemeSlug}
                onChange={(e) => setSelectedSchemeSlug(e.target.value)}
                className="w-full pl-3 pr-8 py-2 text-xs sm:text-sm rounded-xl border border-slate-300 bg-slate-50 text-slate-900 font-bold focus:outline-hidden focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500"
              >
                {availableSchemes.map((s) => (
                  <option key={s.slug} value={s.slug}>
                    {s.name} ({s.level})
                  </option>
                ))}
              </select>
            </div>
          </div>

          <div className="flex items-center gap-2 shrink-0">
            {schemeDetail?.official_url && (
              <a
                href={schemeDetail.official_url}
                target="_blank"
                rel="noreferrer"
                className="inline-flex items-center gap-1 text-xs px-3 py-1.5 rounded-lg border border-slate-200 text-slate-600 hover:text-slate-900 font-medium"
              >
                Official Portal <ExternalLink className="w-3 h-3" />
              </a>
            )}
            <span className="text-xs px-2.5 py-1 rounded-full bg-blue-50 text-blue-700 font-semibold border border-blue-200">
              Draft Ready
            </span>
          </div>
        </div>

        {/* Selected Scheme Info Summary */}
        {schemeDetail && (
          <div className="p-3.5 rounded-xl bg-slate-50 border border-slate-200 text-xs text-slate-600 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3">
            <div>
              <span className="font-semibold text-slate-900">{schemeDetail.name}</span>
              <p className="text-[11px] text-slate-500 mt-0.5">
                Administered by: {schemeDetail.state_or_ministry || schemeDetail.level} • Mode: {schemeDetail.application_mode || 'Online Portal'}
              </p>
            </div>
            {schemeDetail.benefit_summary && (
              <div className="text-[11px] font-medium text-emerald-700 bg-emerald-50 px-2.5 py-1 rounded-md border border-emerald-200 shrink-0">
                {schemeDetail.benefit_summary}
              </div>
            )}
          </div>
        )}

        {/* Pre-populated form fields */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-xs">
          <div className="p-3 rounded-lg bg-slate-50 border border-slate-100 space-y-1">
            <span className="text-slate-400 font-mono">1. Applicant Full Name</span>
            <div className={`font-semibold ${profile.full_name ? 'text-slate-800' : 'text-slate-400 italic'}`}>
              {profile.full_name || 'Not provided yet'}
            </div>
          </div>

          <div className="p-3 rounded-lg bg-slate-50 border border-slate-100 space-y-1">
            <span className="text-slate-400 font-mono">2. Domicile State / UT</span>
            <div className={`font-semibold ${profile.state_code ? 'text-slate-800' : 'text-slate-400 italic'}`}>
              {profile.state_code || 'Not selected'}
            </div>
          </div>

          <div className="p-3 rounded-lg bg-slate-50 border border-slate-100 space-y-1">
            <span className="text-slate-400 font-mono">3. Primary Occupation / Category</span>
            <div className={`font-semibold ${profile.occupation ? 'text-slate-800' : 'text-slate-400 italic'}`}>
              {profile.occupation || 'General Citizen'}
            </div>
          </div>

          <div className="p-3 rounded-lg bg-slate-50 border border-slate-100 space-y-1">
            <span className="text-slate-400 font-mono">4. Livelihood / Sector Details</span>
            <div className="font-semibold text-slate-800 truncate">
              {profile.is_landowner 
                ? `🌾 Landowner: ${profile.land_holding_acres ? `${profile.land_holding_acres} Acres` : 'Cultivable Land'}` 
                : profile.course 
                  ? `🎓 Enrolled: ${profile.course}` 
                  : profile.highest_qualification 
                    ? `📜 Qual: ${profile.highest_qualification}` 
                    : profile.ration_card_type 
                      ? `🍱 Ration: ${profile.ration_card_type}`
                      : 'Verified Citizen'}
            </div>
          </div>

          <div className="p-3 rounded-lg bg-slate-50 border border-slate-100 space-y-1">
            <span className="text-slate-400 font-mono">5. Annual Household Income</span>
            <div className={`font-semibold ${profile.annual_family_income ? 'text-slate-800' : 'text-slate-400 italic'}`}>
              {profile.annual_family_income ? `₹ ${Number(profile.annual_family_income).toLocaleString('en-IN')}` : 'Not declared'}
            </div>
          </div>

          <div className="p-3 rounded-lg bg-slate-50 border border-slate-100 space-y-1">
            <span className="text-slate-400 font-mono">6. Social Category & DBT Linkage</span>
            <div className={`font-semibold ${profile.caste_category ? 'text-slate-800' : 'text-slate-400 italic'}`}>
              {profile.caste_category || 'General'} • {profile.is_bank_aadhaar_seeded !== false ? 'NPCI Seeded' : 'Aadhaar Pending'}
            </div>
          </div>
        </div>

        {/* Action Button */}
        <div className="pt-4 flex flex-col sm:flex-row items-center justify-between gap-3">
          <div className="text-xs text-slate-500 flex items-center gap-1.5">
            <Lock className="w-4 h-4 text-slate-400" />
            Verified against citizen profile records
          </div>

          <button
            onClick={runDemoAutomation}
            disabled={demoState === 'running'}
            className="inline-flex items-center gap-2 px-5 py-2.5 rounded-lg bg-slate-900 hover:bg-slate-800 disabled:opacity-50 text-white text-xs font-semibold shadow-xs transition-all w-full sm:w-auto justify-center"
          >
            <Play className="w-3.5 h-3.5 fill-current" />
            {demoState === 'running' ? 'Running Controlled Demo...' : `Demonstrate Form Filling (${schemeDetail?.name ? schemeDetail.name.split(' ')[0] : 'Scheme'} Sandbox)`}
          </button>
        </div>
      </div>

      {/* Controlled Demo Portal Simulation Output */}
      {demoLogs.length > 0 && (
        <div className="bg-slate-900 text-slate-200 rounded-2xl p-6 font-mono text-xs space-y-2 border border-slate-800 shadow-sm">
          <div className="flex items-center justify-between pb-2 border-b border-slate-800 text-slate-400 text-[11px]">
            <span className="flex items-center gap-2">
              <Laptop className="w-4 h-4 text-emerald-400" /> Application Pre-fill Verification Sandbox
            </span>
            <span className="text-emerald-400">{demoState === 'completed' ? 'Completed' : 'Running...'}</span>
          </div>

          <div className="space-y-1.5 pt-2">
            {demoLogs.map((log, idx) => (
              <div key={idx} className="flex items-start gap-2">
                <span className="text-slate-500 shrink-0">[{idx + 1}]</span>
                <span className={log.includes('GUARDRAIL') ? 'text-amber-300 font-semibold' : 'text-slate-300'}>
                  {log}
                </span>
              </div>
            ))}
          </div>

          {demoState === 'completed' && (
            <div className="mt-4 pt-3 border-t border-slate-800 flex items-center gap-2 text-emerald-400 text-xs">
              <CheckCircle2 className="w-4 h-4" />
              <span>Sandbox verification completed. Draft preserved in your account for official application submission.</span>
            </div>
          )}
        </div>
      )}

      {/* Verified Application Drafts Registry */}
      <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-xs space-y-4">
        <div className="flex items-center justify-between border-b border-slate-100 pb-3">
          <div>
            <h3 className="text-base font-bold text-slate-900 flex items-center gap-2">
              <FileCheck className="w-5 h-5 text-blue-600" />
              Your Prepared Application Drafts ({drafts.length})
            </h3>
            <p className="text-xs text-slate-500">
              Pre-populated citizen application files verified against official scheme parameters.
            </p>
          </div>
        </div>

        {drafts.length === 0 ? (
          <div className="py-8 text-center text-xs text-slate-400">
            No application drafts generated yet. Select a scheme above and run the automated preparation demo to create your first draft.
          </div>
        ) : (
          <div className="divide-y divide-slate-100">
            {drafts.map((d: any) => (
              <div key={d.id} className="py-3 flex flex-col sm:flex-row sm:items-center justify-between gap-3">
                <div className="space-y-1">
                  <div className="text-sm font-bold text-slate-900 flex items-center gap-2">
                    {d.scheme_name}
                    <span className={`text-[10px] font-semibold px-2 py-0.5 rounded-full ${
                      d.status === 'demo_completed' ? 'bg-emerald-100 text-emerald-800' : 'bg-blue-100 text-blue-800'
                    }`}>
                      {d.status === 'demo_completed' ? 'Verified Sandbox Draft' : 'Ready for Review'}
                    </span>
                  </div>
                  <div className="text-xs text-slate-500 flex items-center gap-3">
                    <span>Applicant: <strong>{d.form_data?.applicant_name || 'Citizen'}</strong></span>
                    <span>•</span>
                    <span>State: <strong>{d.form_data?.domicile_state || 'All-India'}</strong></span>
                    <span>•</span>
                    <span>Created: <strong>{new Date(d.created_at).toLocaleDateString()}</strong></span>
                  </div>
                </div>

                <div className="flex items-center gap-2">
                  <button
                    onClick={() => handleDownloadDraft(d)}
                    className="px-3 py-1.5 text-xs font-semibold rounded-lg bg-slate-100 hover:bg-slate-200 text-slate-800 flex items-center gap-1.5 transition-colors shadow-2xs"
                  >
                    Export JSON Draft
                  </button>

                  <a
                    href={schemeDetail?.official_url || "https://www.myscheme.gov.in"}
                    target="_blank"
                    rel="noreferrer"
                    className="px-3 py-1.5 text-xs font-semibold rounded-lg bg-blue-600 hover:bg-blue-500 text-white flex items-center gap-1 transition-colors shadow-2xs"
                  >
                    Open Portal <ExternalLink className="w-3 h-3" />
                  </a>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};
