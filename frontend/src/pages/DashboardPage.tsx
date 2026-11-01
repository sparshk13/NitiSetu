import React, { useEffect, useState } from 'react';
import { 
  Building2, 
  FileCheck2, 
  Bot, 
  ArrowRight, 
  CheckCircle2, 
  Clock, 
  AlertCircle,
  ExternalLink,
  Sparkles,
  ShieldCheck,
  User,
  IndianRupee,
  Tractor,
  HeartPulse,
  Home,
  Briefcase
} from 'lucide-react';
import { api, ProfileData, SchemeItem, UserDocument } from '../api/client';

interface DashboardProps {
  onNavigate: (tab: string, schemeSlug?: string) => void;
  profile?: ProfileData;
}

export const DashboardPage: React.FC<DashboardProps> = ({ onNavigate, profile: initialProfile }) => {
  const [profile, setProfile] = useState<ProfileData | null>(initialProfile || null);
  const [schemes, setSchemes] = useState<SchemeItem[]>([]);
  const [documents, setDocuments] = useState<UserDocument[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function load() {
      setLoading(true);
      const [profData, schemesData, docsData] = await Promise.all([
        initialProfile ? Promise.resolve(initialProfile) : api.getProfile(),
        api.listSchemes({ level: 'Central Government', page_size: 6 }),
        api.listDocuments()
      ]);
      setProfile(profData);
      setSchemes(schemesData.items.slice(0, 3));
      setDocuments(docsData);
      setLoading(false);
    }
    load();
  }, [initialProfile]);

  const hasIncome = profile?.annual_family_income !== undefined && profile?.annual_family_income !== null;
  const incomeValue = profile?.annual_family_income || 0;
  const isIncomeWithinLimit = hasIncome && incomeValue <= 250000;

  return (
    <div className="space-y-8">
      {/* Top Banner / Hero */}
      <div className="bg-gradient-to-r from-slate-900 to-slate-800 text-white rounded-2xl p-6 sm:p-8 shadow-sm border border-slate-700 relative overflow-hidden">
        <div className="relative z-10 max-w-3xl">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-slate-800/80 border border-slate-700 text-xs font-medium text-emerald-400 mb-4">
            <ShieldCheck className="w-3.5 h-3.5" />
            Unified Citizen Welfare & Scheme Gateway
          </div>
          <h1 className="text-2xl sm:text-3xl font-bold tracking-tight text-white mb-2">
            Welcome back, {profile?.full_name || 'Citizen'}
          </h1>
          <p className="text-slate-300 text-sm sm:text-base leading-relaxed mb-6">
            NitiSetu connects citizens across India to 2,000+ official Central and State Government schemes — covering agriculture, healthcare, housing, pensions, livelihoods, and education. Evaluate your eligibility deterministically against official Gazette guidelines, verify documents, and prepare validated applications.
          </p>

          <div className="flex flex-wrap gap-3">
            <button
              onClick={() => onNavigate('discovery')}
              className="inline-flex items-center gap-2 px-4 py-2.5 rounded-lg bg-blue-600 hover:bg-blue-500 text-white text-sm font-semibold transition-all shadow-sm"
            >
              <Building2 className="w-4 h-4" />
              Discover Schemes & Benefits
            </button>
            <button
              onClick={() => onNavigate('assistant')}
              className="inline-flex items-center gap-2 px-4 py-2.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 text-sm font-semibold transition-all"
            >
              <Bot className="w-4 h-4 text-blue-400" />
              Policy Guidelines Explainer
            </button>
          </div>
        </div>
      </div>

      {/* Citizen Key Sectors Banner */}
      <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-6 gap-3">
        <div 
          onClick={() => onNavigate('discovery')}
          className="p-3 bg-white rounded-xl border border-slate-200 hover:border-blue-400 transition-all cursor-pointer text-center group"
        >
          <div className="w-8 h-8 rounded-lg bg-emerald-50 text-emerald-700 mx-auto flex items-center justify-center mb-1.5 group-hover:scale-110 transition-transform">
            <Tractor className="w-4 h-4" />
          </div>
          <div className="text-xs font-bold text-slate-800">Agriculture</div>
          <div className="text-[10px] text-slate-400">PM-KISAN, PMFBY</div>
        </div>

        <div 
          onClick={() => onNavigate('discovery')}
          className="p-3 bg-white rounded-xl border border-slate-200 hover:border-blue-400 transition-all cursor-pointer text-center group"
        >
          <div className="w-8 h-8 rounded-lg bg-rose-50 text-rose-700 mx-auto flex items-center justify-center mb-1.5 group-hover:scale-110 transition-transform">
            <HeartPulse className="w-4 h-4" />
          </div>
          <div className="text-xs font-bold text-slate-800">Healthcare</div>
          <div className="text-[10px] text-slate-400">Ayushman Bharat</div>
        </div>

        <div 
          onClick={() => onNavigate('discovery')}
          className="p-3 bg-white rounded-xl border border-slate-200 hover:border-blue-400 transition-all cursor-pointer text-center group"
        >
          <div className="w-8 h-8 rounded-lg bg-blue-50 text-blue-700 mx-auto flex items-center justify-center mb-1.5 group-hover:scale-110 transition-transform">
            <Home className="w-4 h-4" />
          </div>
          <div className="text-xs font-bold text-slate-800">Housing</div>
          <div className="text-[10px] text-slate-400">PMAY Urban/Gramin</div>
        </div>

        <div 
          onClick={() => onNavigate('discovery')}
          className="p-3 bg-white rounded-xl border border-slate-200 hover:border-blue-400 transition-all cursor-pointer text-center group"
        >
          <div className="w-8 h-8 rounded-lg bg-amber-50 text-amber-700 mx-auto flex items-center justify-center mb-1.5 group-hover:scale-110 transition-transform">
            <Briefcase className="w-4 h-4" />
          </div>
          <div className="text-xs font-bold text-slate-800">Livelihood</div>
          <div className="text-[10px] text-slate-400">Vishwakarma, Mudra</div>
        </div>

        <div 
          onClick={() => onNavigate('discovery')}
          className="p-3 bg-white rounded-xl border border-slate-200 hover:border-blue-400 transition-all cursor-pointer text-center group"
        >
          <div className="w-8 h-8 rounded-lg bg-indigo-50 text-indigo-700 mx-auto flex items-center justify-center mb-1.5 group-hover:scale-110 transition-transform">
            <ShieldCheck className="w-4 h-4" />
          </div>
          <div className="text-xs font-bold text-slate-800">Pensions</div>
          <div className="text-[10px] text-slate-400">Atal Pension, IGNOAPS</div>
        </div>

        <div 
          onClick={() => onNavigate('discovery')}
          className="p-3 bg-white rounded-xl border border-slate-200 hover:border-blue-400 transition-all cursor-pointer text-center group"
        >
          <div className="w-8 h-8 rounded-lg bg-purple-50 text-purple-700 mx-auto flex items-center justify-center mb-1.5 group-hover:scale-110 transition-transform">
            <Building2 className="w-4 h-4" />
          </div>
          <div className="text-xs font-bold text-slate-800">Education</div>
          <div className="text-[10px] text-slate-400">Scholarships & Skills</div>
        </div>
      </div>

      {/* Profile Overview & Quick Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
        <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-xs flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between mb-3">
              <span className="text-xs font-semibold uppercase tracking-wider text-slate-500">Citizen Profile</span>
              <span className="text-xs px-2 py-0.5 rounded-full bg-emerald-50 text-emerald-700 font-medium border border-emerald-200">
                {profile?.completeness_percentage || (profile?.full_name ? 40 : 0)}% Complete
              </span>
            </div>
            <div className="text-lg font-bold text-slate-900">
              {profile?.occupation || 'Primary Occupation Not Set'}
            </div>
            <p className="text-xs text-slate-500 mt-1">
              {profile?.state_code ? `${profile.state_code} Domicile` : 'State not set'} • {profile?.caste_category || 'General'}
              {profile?.age ? ` • ${profile.age} years` : ''}
            </p>
            {profile?.course && (
              <p className="text-[11px] text-blue-600 font-medium mt-1 truncate">
                📚 Studying: {profile.course}
              </p>
            )}
            {profile?.is_landowner && (
              <p className="text-[11px] text-emerald-600 font-medium mt-1">
                🌾 Landowner: {profile.land_holding_acres ? `${profile.land_holding_acres} Acres` : 'Cultivable Land'}
              </p>
            )}
          </div>
          <div className="pt-4 border-t border-slate-100 mt-4 flex items-center justify-between text-xs">
            <span className="text-slate-500">{profile?.ration_card_type || 'General Citizen'}</span>
            <button 
              onClick={() => onNavigate('profile')} 
              className="font-medium text-blue-600 hover:text-blue-700"
            >
              Edit Profile →
            </button>
          </div>
        </div>

        <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-xs flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between mb-3">
              <span className="text-xs font-semibold uppercase tracking-wider text-slate-500">Means & Income Status</span>
              <span className={`text-xs px-2 py-0.5 rounded-full font-medium border ${hasIncome ? 'bg-blue-50 text-blue-700 border-blue-200' : 'bg-slate-100 text-slate-600 border-slate-200'}`}>
                {hasIncome ? 'Means-Tested' : 'Not Declared'}
              </span>
            </div>
            <div className="text-lg font-bold text-slate-900">
              {hasIncome ? `₹${Number(profile?.annual_family_income).toLocaleString('en-IN')} / year` : 'Income Not Set'}
            </div>
            <p className="text-xs text-slate-500 mt-1">
              {hasIncome 
                ? 'Evaluated against Gazette welfare income criteria & DBT ceilings' 
                : 'Add annual income to evaluate means-tested eligibility'}
            </p>
          </div>
          <div className="pt-4 border-t border-slate-100 mt-4 flex items-center justify-between text-xs">
            <span className="text-slate-500">Cap: ≤ ₹2.5L / ₹4.5L</span>
            {hasIncome ? (
              <span className={`font-medium flex items-center gap-1 ${isIncomeWithinLimit ? 'text-emerald-600' : 'text-amber-600'}`}>
                <CheckCircle2 className="w-3.5 h-3.5" /> {isIncomeWithinLimit ? 'Within Limits' : 'Above Basic Cap'}
              </span>
            ) : (
              <button 
                onClick={() => onNavigate('profile')} 
                className="font-medium text-blue-600 hover:text-blue-700"
              >
                Set Income →
              </button>
            )}
          </div>
        </div>

        <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-xs flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between mb-3">
              <span className="text-xs font-semibold uppercase tracking-wider text-slate-500">Document Readiness</span>
              <span className={`text-xs px-2 py-0.5 rounded-full font-medium border ${documents.length > 0 ? 'bg-emerald-50 text-emerald-700 border-emerald-200' : 'bg-amber-50 text-amber-700 border-amber-200'}`}>
                {documents.length} / 4 Ready
              </span>
            </div>
            <div className="text-lg font-bold text-slate-900">
              {documents.length > 0 ? `${documents.length} Document${documents.length > 1 ? 's' : ''} in Vault` : 'Vault is Empty'}
            </div>
            <p className="text-xs text-slate-500 mt-1">
              {documents.length > 0 
                ? 'Verified certificates ready for scheme application mapping' 
                : 'Upload Aadhaar, Ration Card & Income Certificate'}
            </p>
          </div>
          <div className="pt-4 border-t border-slate-100 mt-4 flex items-center justify-between text-xs">
            <span className="text-slate-500">{documents.length > 0 ? 'Private & Encrypted' : 'Verification Pending'}</span>
            <button 
              onClick={() => onNavigate('documents')} 
              className="font-medium text-blue-600 hover:text-blue-700"
            >
              Upload Docs →
            </button>
          </div>
        </div>
      </div>

      {/* Recommended Schemes Section */}
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-lg font-bold text-slate-900 flex items-center gap-2">
              <Sparkles className="w-5 h-5 text-amber-500" />
              Recommended Schemes for Your Profile
            </h2>
            <p className="text-xs text-slate-500">Derived deterministically from your occupation, domicile state, household income, and social category.</p>
          </div>
          <button
            onClick={() => onNavigate('discovery')}
            className="text-xs sm:text-sm font-semibold text-blue-600 hover:text-blue-700 flex items-center gap-1"
          >
            Explore all 2,000+ Schemes <ArrowRight className="w-4 h-4" />
          </button>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
          {schemes.map((scheme) => (
            <div
              key={scheme.id}
              className="bg-white rounded-xl border border-slate-200 p-5 shadow-xs hover:border-slate-300 transition-all flex flex-col justify-between"
            >
              <div>
                <div className="flex items-center justify-between gap-2 mb-2">
                  <span className="text-[11px] font-semibold px-2 py-0.5 rounded bg-slate-100 text-slate-700 border border-slate-200">
                    {scheme.level}
                  </span>
                  <span className="text-[11px] text-slate-400 font-mono">
                    Verified {scheme.last_verified_at}
                  </span>
                </div>
                <h3 className="font-semibold text-slate-900 text-sm sm:text-base line-clamp-2 mb-2">
                  {scheme.name}
                </h3>
                <p className="text-xs text-slate-600 line-clamp-3 mb-3 leading-relaxed">
                  {scheme.summary}
                </p>

                {scheme.recommendation_reason && (
                  <div className="bg-emerald-50/60 border border-emerald-100 rounded-lg p-2.5 mb-4 text-[11px] text-emerald-800 flex items-start gap-1.5">
                    <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600 shrink-0 mt-0.5" />
                    <span><strong>Match Reason:</strong> {scheme.recommendation_reason}</span>
                  </div>
                )}
              </div>

              <div className="pt-3 border-t border-slate-100 flex items-center justify-between">
                <button
                  onClick={() => onNavigate('detail', scheme.slug)}
                  className="text-xs font-semibold text-blue-600 hover:text-blue-800"
                >
                  View Details & Criteria
                </button>
                <button
                  onClick={() => onNavigate('assistant', scheme.slug)}
                  className="text-xs font-medium text-slate-500 hover:text-slate-800 flex items-center gap-1"
                >
                  <Bot className="w-3.5 h-3.5 text-blue-500" /> Ask AI
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Trust & Provenance Notice */}
      <div className="p-4 rounded-xl bg-slate-100/80 border border-slate-200 text-xs text-slate-600 flex items-start gap-3">
        <Building2 className="w-5 h-5 text-slate-500 shrink-0 mt-0.5" />
        <div>
          <strong className="text-slate-800">Public Information Notice & Provenance:</strong> NitiSetu is an independent civic discovery platform designed to assist every citizen across India. 
          All scheme rules, eligibility caps, benefits, and guidelines are mirrored directly from official government gazette sources (including <a href="https://www.myscheme.gov.in" target="_blank" rel="noreferrer" className="text-blue-600 underline">myScheme.gov.in</a> and <a href="https://scholarships.gov.in" target="_blank" rel="noreferrer" className="text-blue-600 underline">scholarships.gov.in</a>). 
          NitiSetu does not grant or guarantee welfare benefits.
        </div>
      </div>
    </div>
  );
};
