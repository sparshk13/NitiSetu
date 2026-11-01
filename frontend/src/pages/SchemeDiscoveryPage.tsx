import React, { useEffect, useState } from 'react';
import { 
  Search, 
  Filter, 
  Building2, 
  ExternalLink, 
  Bot, 
  CheckCircle2, 
  ChevronRight, 
  ShieldCheck, 
  RotateCcw,
  Tractor,
  HeartPulse,
  Home,
  Briefcase,
  GraduationCap
} from 'lucide-react';
import { api, SchemeItem } from '../api/client';

const COMMON_STATES = [
  "Andhra Pradesh", "Arunachal Pradesh", "Assam", "Bihar", "Chhattisgarh", "Goa", "Gujarat",
  "Haryana", "Himachal Pradesh", "Jharkhand", "Karnataka", "Kerala", "Madhya Pradesh", "Maharashtra",
  "Manipur", "Meghalaya", "Mizoram", "Nagaland", "Odisha", "Punjab", "Rajasthan", "Sikkim",
  "Tamil Nadu", "Telangana", "Tripura", "Uttar Pradesh", "Uttarakhand", "West Bengal",
  "Andaman and Nicobar Islands", "Chandigarh", "Dadra and Nagar Haveli and Daman and Diu",
  "Delhi (NCT)", "Jammu and Kashmir", "Ladakh", "Lakshadweep", "Puducherry"
];

const SCHEME_CATEGORIES = [
  { label: "All Schemes", query: "" },
  { label: "🌾 Agriculture & Farmers", query: "farmer" },
  { label: "🏥 Healthcare & Wellness", query: "health" },
  { label: "🏠 Housing & Shelter", query: "housing" },
  { label: "👵 Pensions & Social Security", query: "pension" },
  { label: "👩 Women & Child Welfare", query: "women" },
  { label: "💼 MSME, Loans & Business", query: "business" },
  { label: "🔨 Artisans, Skills & Labor", query: "worker" },
  { label: "🎓 Education & Scholarships", query: "scholarship" }
];

interface SchemeDiscoveryProps {
  onNavigate: (tab: string, schemeSlug?: string) => void;
}

export const SchemeDiscoveryPage: React.FC<SchemeDiscoveryProps> = ({ onNavigate }) => {
  const [schemes, setSchemes] = useState<SchemeItem[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('');
  const [selectedLevel, setSelectedLevel] = useState('');
  const [selectedState, setSelectedState] = useState('');

  const fetchSchemes = async () => {
    setLoading(true);
    // Combine search query and category keyword if selected
    const activeQuery = [searchQuery, selectedCategory].filter(Boolean).join(' ');
    const data = await api.listSchemes({
      q: activeQuery || undefined,
      level: selectedLevel || undefined,
      state: selectedState || undefined,
      page_size: 24
    });
    setSchemes(data.items);
    setTotal(data.total);
    setLoading(false);
  };

  useEffect(() => {
    const timer = setTimeout(() => {
      fetchSchemes();
    }, 200);
    return () => clearTimeout(timer);
  }, [searchQuery, selectedCategory, selectedLevel, selectedState]);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-slate-900 flex items-center gap-2">
          <Building2 className="w-6 h-6 text-blue-600" />
          Government Welfare Schemes & Citizen Benefits
        </h1>
        <p className="text-slate-500 text-sm mt-1">
          Explore authentic Central and State Government welfare schemes across agriculture, health, housing, livelihood, pensions, and education (sourced from myScheme.gov.in & DBT Bharat).
        </p>
      </div>

      {/* Category Pills Bar */}
      <div className="flex items-center gap-2 overflow-x-auto pb-1 scrollbar-thin">
        {SCHEME_CATEGORIES.map((cat) => {
          const isActive = selectedCategory === cat.query;
          return (
            <button
              key={cat.label}
              onClick={() => setSelectedCategory(cat.query)}
              className={`px-3 py-1.5 rounded-full text-xs font-semibold whitespace-nowrap transition-all shrink-0 ${
                isActive
                  ? 'bg-blue-600 text-white shadow-xs'
                  : 'bg-white border border-slate-200 text-slate-700 hover:bg-slate-50 hover:border-slate-300'
              }`}
            >
              {cat.label}
            </button>
          );
        })}
      </div>

      {/* Filter and Search Bar */}
      <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-xs flex flex-col md:flex-row gap-3 items-center justify-between">
        <div className="relative w-full md:w-96">
          <Search className="w-4 h-4 text-slate-400 absolute left-3 top-3" />
          <input
            type="text"
            placeholder="Search schemes by name, keyword, or benefit..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full pl-9 pr-4 py-2 text-sm rounded-lg border border-slate-200 focus:outline-hidden focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 transition-all"
          />
        </div>

        <div className="flex flex-wrap w-full md:w-auto items-center gap-3">
          <div className="flex items-center gap-1.5 text-xs text-slate-500 font-medium">
            <Filter className="w-3.5 h-3.5 text-slate-400" /> Filters:
          </div>

          <select
            value={selectedLevel}
            onChange={(e) => setSelectedLevel(e.target.value)}
            className="px-3 py-2 text-xs rounded-lg border border-slate-200 bg-slate-50 text-slate-700 font-medium focus:outline-hidden focus:ring-2 focus:ring-blue-500/20"
          >
            <option value="">All Government Levels</option>
            <option value="Central Government">Central Government</option>
            <option value="State">State Government</option>
          </select>

          <select
            value={selectedState}
            onChange={(e) => setSelectedState(e.target.value)}
            className="px-3 py-2 text-xs rounded-lg border border-slate-200 bg-slate-50 text-slate-700 font-medium focus:outline-hidden focus:ring-2 focus:ring-blue-500/20"
          >
            <option value="">All 36 States & UTs</option>
            {COMMON_STATES.map((st) => (
              <option key={st} value={st}>{st}</option>
            ))}
          </select>

          {(searchQuery || selectedCategory || selectedLevel || selectedState) && (
            <button
              onClick={() => {
                setSearchQuery('');
                setSelectedCategory('');
                setSelectedLevel('');
                setSelectedState('');
              }}
              className="px-2.5 py-1.5 text-xs text-slate-500 hover:text-slate-800 flex items-center gap-1"
            >
              <RotateCcw className="w-3 h-3" /> Reset
            </button>
          )}
        </div>
      </div>

      {/* Results Count Banner */}
      <div className="flex items-center justify-between text-xs text-slate-500 px-1">
        <span>Showing <strong>{schemes.length}</strong> of <strong>{total}</strong> verified government schemes</span>
        <span className="flex items-center gap-1 font-mono text-slate-400">
          <ShieldCheck className="w-3.5 h-3.5 text-emerald-500" /> Sourced from official gazettes & myScheme.gov.in
        </span>
      </div>

      {/* Scheme Cards Grid */}
      {loading ? (
        <div className="py-16 text-center text-slate-400 text-sm">
          Loading authentic government schemes...
        </div>
      ) : schemes.length === 0 ? (
        <div className="py-16 text-center bg-white rounded-xl border border-slate-200 p-8 space-y-3">
          <p className="text-slate-700 font-semibold">No schemes matched your search parameters.</p>
          <p className="text-slate-400 text-xs max-w-md mx-auto">
            Try adjusting your search terms, clearing category pills, or selecting "All 36 States & UTs" to view nationwide Central Government welfare programs.
          </p>
          <button
            onClick={() => {
              setSearchQuery('');
              setSelectedCategory('');
              setSelectedLevel('');
              setSelectedState('');
            }}
            className="px-4 py-2 rounded-lg bg-blue-600 text-white text-xs font-semibold hover:bg-blue-500 transition-all shadow-xs"
          >
            Clear All Filters
          </button>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
          {schemes.map((scheme) => (
            <div
              key={scheme.id}
              className="bg-white rounded-xl border border-slate-200 p-5 shadow-xs hover:border-blue-400 transition-all flex flex-col justify-between group"
            >
              <div>
                <div className="flex items-center justify-between gap-2 mb-2">
                  <span className="text-[11px] font-semibold px-2 py-0.5 rounded bg-slate-100 text-slate-700 border border-slate-200">
                    {scheme.level}
                  </span>
                  {scheme.state_or_ministry && (
                    <span className="text-[11px] text-slate-500 truncate max-w-[150px]">
                      {scheme.state_or_ministry}
                    </span>
                  )}
                </div>

                <h3 className="font-semibold text-slate-900 text-base line-clamp-2 mb-2 group-hover:text-blue-600 transition-colors">
                  {scheme.name}
                </h3>

                <p className="text-xs text-slate-600 line-clamp-3 mb-4 leading-relaxed">
                  {scheme.summary || 'Official Government welfare initiative delivering financial support and benefits to eligible citizens.'}
                </p>

                {scheme.benefit_summary && (
                  <div className="bg-slate-50 border border-slate-100 rounded-lg p-2.5 mb-4 text-[11px] text-slate-700">
                    <strong className="text-slate-900">Benefits:</strong> {scheme.benefit_summary}
                  </div>
                )}
              </div>

              <div className="pt-3 border-t border-slate-100 flex items-center justify-between gap-2">
                <button
                  onClick={() => onNavigate('detail', scheme.slug)}
                  className="inline-flex items-center gap-1 text-xs font-semibold text-blue-600 hover:text-blue-800"
                >
                  View Details & Criteria <ChevronRight className="w-3.5 h-3.5" />
                </button>

                <button
                  onClick={() => onNavigate('assistant', scheme.slug)}
                  className="px-2.5 py-1.5 rounded-lg border border-slate-200 text-slate-600 hover:text-blue-600 hover:border-blue-300 text-xs font-medium flex items-center gap-1 transition-colors"
                >
                  <Bot className="w-3.5 h-3.5 text-blue-500" /> Ask AI
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
