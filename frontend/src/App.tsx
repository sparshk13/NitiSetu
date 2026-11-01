import React, { useState, useEffect } from 'react';
import { 
  Building2, 
  GraduationCap, 
  Bot, 
  FileText, 
  User, 
  FileCheck2, 
  ShieldCheck, 
  Menu, 
  X,
  ExternalLink,
  LogOut,
  ChevronDown
} from 'lucide-react';
import { DashboardPage } from './pages/DashboardPage';
import { SchemeDiscoveryPage } from './pages/SchemeDiscoveryPage';
import { SchemeDetailPage } from './pages/SchemeDetailPage';
import { AssistantPage } from './pages/AssistantPage';
import { ProfilePage } from './pages/ProfilePage';
import { DocumentsPage } from './pages/DocumentsPage';
import { ApplicationPage } from './pages/ApplicationPage';
import { AuthModal } from './components/AuthModal';
import { api, ProfileData, AuthUser } from './api/client';

export const App: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'dashboard' | 'discovery' | 'detail' | 'assistant' | 'documents' | 'application' | 'profile'>('dashboard');
  const [selectedSchemeSlug, setSelectedSchemeSlug] = useState<string | undefined>(undefined);
  const [profile, setProfile] = useState<ProfileData>({});
  const [currentUser, setCurrentUser] = useState<AuthUser | null>(null);
  const [showAuthModal, setShowAuthModal] = useState(false);
  const [userDropdownOpen, setUserDropdownOpen] = useState(false);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  useEffect(() => {
    // Check if citizen is logged in
    const stored = api.getStoredUser();
    if (stored) {
      setCurrentUser(stored);
      loadCitizenProfile(stored.full_name);
    } else {
      // Require registration / sign-in for first-time visitors
      setShowAuthModal(true);
    }
  }, []);

  const loadCitizenProfile = async (fallbackName?: string) => {
    const data = await api.getProfile();
    if (fallbackName && !data.full_name) {
      data.full_name = fallbackName;
    }
    setProfile(data);
  };

  const handleAuthSuccess = (user: AuthUser) => {
    setCurrentUser(user);
    setShowAuthModal(false);
    loadCitizenProfile(user.full_name);
  };

  const handleLogout = () => {
    api.logout();
    setCurrentUser(null);
    setProfile({});
    setUserDropdownOpen(false);
    setShowAuthModal(true);
  };

  const handleNavigate = (tab: string, schemeSlug?: string) => {
    if (schemeSlug) {
      setSelectedSchemeSlug(schemeSlug);
    }
    setActiveTab(tab as any);
    setMobileMenuOpen(false);
    setUserDropdownOpen(false);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col text-slate-800">
      {/* Authentication Modal */}
      <AuthModal
        isOpen={showAuthModal}
        onSuccess={handleAuthSuccess}
      />

      {/* Top Portal Header */}
      <header className="sticky top-0 z-40 bg-white/95 backdrop-blur-md border-b border-slate-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            {/* Emblem & Portal Brand */}
            <div 
              onClick={() => handleNavigate('dashboard')}
              className="flex items-center gap-3 cursor-pointer group"
            >
              <div className="w-9 h-9 rounded-xl bg-slate-900 text-white flex items-center justify-center shadow-xs group-hover:bg-blue-600 transition-colors">
                <Building2 className="w-5 h-5 text-blue-400 group-hover:text-white transition-colors" />
              </div>
              <div>
                <div className="flex items-center gap-2">
                  <span className="font-bold text-base sm:text-lg tracking-tight text-slate-900">CivicPilot</span>
                  <span className="text-[10px] font-semibold px-2 py-0.5 rounded bg-slate-100 text-slate-700 border border-slate-200">
                    Public Welfare Discovery
                  </span>
                </div>
                <div className="text-[11px] text-slate-400 font-medium hidden sm:block">
                  Unified Citizen Gateway for Central & State Welfare Schemes
                </div>
              </div>
            </div>

            {/* Desktop Navigation */}
            <nav className="hidden md:flex items-center gap-1">
              <button
                onClick={() => handleNavigate('dashboard')}
                className={`px-3.5 py-2 rounded-lg text-xs font-semibold transition-all ${
                  activeTab === 'dashboard'
                    ? 'bg-slate-100 text-slate-900 font-bold'
                    : 'text-slate-600 hover:text-slate-900 hover:bg-slate-50'
                }`}
              >
                Dashboard
              </button>
              <button
                onClick={() => handleNavigate('discovery')}
                className={`px-3.5 py-2 rounded-lg text-xs font-semibold transition-all ${
                  activeTab === 'discovery' || activeTab === 'detail'
                    ? 'bg-slate-100 text-slate-900 font-bold'
                    : 'text-slate-600 hover:text-slate-900 hover:bg-slate-50'
                }`}
              >
                Find Schemes
              </button>
              <button
                onClick={() => handleNavigate('assistant')}
                className={`px-3.5 py-2 rounded-lg text-xs font-semibold transition-all flex items-center gap-1.5 ${
                  activeTab === 'assistant'
                    ? 'bg-blue-50 text-blue-700 font-bold border border-blue-200'
                    : 'text-slate-600 hover:text-slate-900 hover:bg-slate-50'
                }`}
              >
                <Bot className="w-3.5 h-3.5 text-blue-600" />
                Guidelines Explainer
              </button>
              <button
                onClick={() => handleNavigate('documents')}
                className={`px-3.5 py-2 rounded-lg text-xs font-semibold transition-all ${
                  activeTab === 'documents'
                    ? 'bg-slate-100 text-slate-900 font-bold'
                    : 'text-slate-600 hover:text-slate-900 hover:bg-slate-50'
                }`}
              >
                Document Vault
              </button>
              <button
                onClick={() => handleNavigate('application')}
                className={`px-3.5 py-2 rounded-lg text-xs font-semibold transition-all ${
                  activeTab === 'application'
                    ? 'bg-slate-100 text-slate-900 font-bold'
                    : 'text-slate-600 hover:text-slate-900 hover:bg-slate-50'
                }`}
              >
                Application Prep
              </button>
            </nav>

            {/* Citizen Account Dropdown */}
            <div className="hidden md:flex items-center gap-3 relative">
              {currentUser ? (
                <div>
                  <button
                    onClick={() => setUserDropdownOpen(!userDropdownOpen)}
                    className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full border border-slate-200 hover:border-slate-300 bg-white text-xs font-medium text-slate-700 shadow-2xs"
                  >
                    <div className="w-6 h-6 rounded-full bg-blue-600 text-white flex items-center justify-center text-[10px] font-bold">
                      {currentUser.full_name ? currentUser.full_name[0] : 'C'}
                    </div>
                    <span className="max-w-[120px] truncate">{currentUser.full_name}</span>
                    <ChevronDown className="w-3 h-3 text-slate-400" />
                  </button>

                  {/* Dropdown Menu */}
                  {userDropdownOpen && (
                    <div className="absolute right-0 mt-2 w-56 bg-white rounded-xl shadow-lg border border-slate-200 py-1.5 z-50 text-xs">
                      <div className="px-3 py-2 border-b border-slate-100">
                        <div className="font-semibold text-slate-900 truncate">{currentUser.full_name}</div>
                        <div className="text-[10px] text-slate-400 truncate">{currentUser.email_or_mobile}</div>
                        {currentUser.is_demo_user && (
                          <span className="inline-block mt-1 text-[9px] font-semibold px-1.5 py-0.5 rounded bg-blue-50 text-blue-700">
                            Demo Citizen Persona
                          </span>
                        )}
                      </div>

                      <button
                        onClick={() => handleNavigate('profile')}
                        className="w-full text-left px-3 py-2 text-slate-700 hover:bg-slate-50 flex items-center gap-2"
                      >
                        <User className="w-3.5 h-3.5 text-slate-400" />
                        <span>Citizen Profile</span>
                      </button>

                      <button
                        onClick={handleLogout}
                        className="w-full text-left px-3 py-2 text-rose-600 hover:bg-rose-50 flex items-center gap-2 border-t border-slate-100 mt-1"
                      >
                        <LogOut className="w-3.5 h-3.5" />
                        <span>Sign Out / Switch Account</span>
                      </button>
                    </div>
                  )}
                </div>
              ) : (
                <button
                  onClick={() => setShowAuthModal(true)}
                  className="px-3.5 py-1.5 rounded-lg bg-blue-600 hover:bg-blue-500 text-white text-xs font-semibold shadow-xs"
                >
                  Citizen Sign In
                </button>
              )}
            </div>

            {/* Mobile Menu Button */}
            <div className="md:hidden flex items-center">
              <button
                onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
                className="p-2 rounded-lg border border-slate-200 text-slate-600 hover:text-slate-900"
              >
                {mobileMenuOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
              </button>
            </div>
          </div>
        </div>

        {/* Mobile Dropdown */}
        {mobileMenuOpen && (
          <div className="md:hidden border-t border-slate-200 bg-white px-4 pt-2 pb-4 space-y-1">
            <div className="px-3 py-2 mb-2 bg-slate-50 rounded-lg text-xs">
              <span className="text-slate-400">Signed in as:</span>
              <div className="font-semibold text-slate-800">{currentUser?.full_name || 'Citizen'}</div>
            </div>
            <button
              onClick={() => handleNavigate('dashboard')}
              className="w-full text-left px-3 py-2 text-sm font-medium rounded-lg text-slate-700 hover:bg-slate-50"
            >
              Dashboard
            </button>
            <button
              onClick={() => handleNavigate('discovery')}
              className="w-full text-left px-3 py-2 text-sm font-medium rounded-lg text-slate-700 hover:bg-slate-50"
            >
              Find Schemes
            </button>
            <button
              onClick={() => handleNavigate('assistant')}
              className="w-full text-left px-3 py-2 text-sm font-medium rounded-lg text-blue-600 hover:bg-blue-50"
            >
              Guidelines Explainer
            </button>
            <button
              onClick={() => handleNavigate('documents')}
              className="w-full text-left px-3 py-2 text-sm font-medium rounded-lg text-slate-700 hover:bg-slate-50"
            >
              Document Vault
            </button>
            <button
              onClick={() => handleNavigate('application')}
              className="w-full text-left px-3 py-2 text-sm font-medium rounded-lg text-slate-700 hover:bg-slate-50"
            >
              Application Prep
            </button>
            <button
              onClick={() => handleNavigate('profile')}
              className="w-full text-left px-3 py-2 text-sm font-medium rounded-lg text-slate-700 hover:bg-slate-50"
            >
              My Profile
            </button>
            <button
              onClick={handleLogout}
              className="w-full text-left px-3 py-2 text-sm font-medium rounded-lg text-rose-600 hover:bg-rose-50 border-t border-slate-100"
            >
              Sign Out
            </button>
          </div>
        )}
      </header>

      {/* Main Body Content */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {activeTab === 'dashboard' && <DashboardPage onNavigate={handleNavigate} profile={profile} />}
        {activeTab === 'discovery' && <SchemeDiscoveryPage onNavigate={handleNavigate} />}
        {activeTab === 'detail' && selectedSchemeSlug && (
          <SchemeDetailPage 
            slug={selectedSchemeSlug} 
            onBack={() => setActiveTab('discovery')} 
            onNavigate={handleNavigate} 
          />
        )}
        {activeTab === 'assistant' && (
          <AssistantPage 
            initialSchemeSlug={selectedSchemeSlug} 
            onNavigate={handleNavigate} 
          />
        )}
        {activeTab === 'documents' && <DocumentsPage profile={profile} initialSchemeSlug={selectedSchemeSlug} />}
        {activeTab === 'application' && <ApplicationPage profile={profile} initialSchemeSlug={selectedSchemeSlug} onNavigate={handleNavigate} />}
        {activeTab === 'profile' && <ProfilePage onProfileUpdated={(updated) => setProfile(updated)} />}
      </main>

      {/* Refined Public Information Footer */}
      <footer className="border-t border-slate-200 bg-white py-8 text-xs text-slate-500">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex flex-col sm:flex-row items-center justify-between gap-4">
          <div className="flex items-center gap-2">
            <ShieldCheck className="w-4 h-4 text-emerald-600" />
            <span>CivicPilot • Independent Citizen Information Assistant</span>
          </div>
          <div className="flex items-center gap-4 text-slate-400 font-mono text-[11px]">
            <span>Sources: myScheme.gov.in, DBT Bharat & National Portals</span>
            <span>•</span>
            <span>Deterministic Rule Evaluation</span>
            <span>•</span>
            <span>Zero Hallucinations</span>
          </div>
        </div>
      </footer>
    </div>
  );
};
