import React, { useState, useEffect } from 'react';
import { 
  FileText, 
  Upload, 
  CheckCircle2, 
  AlertCircle, 
  Trash2, 
  ShieldCheck, 
  Eye, 
  Building2,
  FileCheck2,
  Sparkles,
  Inbox,
  Filter,
  Check,
  Clock
} from 'lucide-react';
import { api, UserDocument, ProfileData, SchemeItem, SchemeDetail } from '../api/client';

interface DocumentsPageProps {
  profile?: ProfileData;
  initialSchemeSlug?: string;
}

export const DocumentsPage: React.FC<DocumentsPageProps> = ({ profile, initialSchemeSlug }) => {
  const [documents, setDocuments] = useState<UserDocument[]>([]);
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [pendingDoc, setPendingDoc] = useState<UserDocument | null>(null);
  const [selectedDocType, setSelectedDocType] = useState<string>('auto');

  // Scheme checklist selector
  const [selectedSchemeSlug, setSelectedSchemeSlug] = useState<string>(initialSchemeSlug || 'general');
  const [availableSchemes, setAvailableSchemes] = useState<SchemeItem[]>([]);
  const [activeSchemeDetail, setActiveSchemeDetail] = useState<SchemeDetail | null>(null);

  useEffect(() => {
    loadDocuments();
    loadSchemes();
  }, []);

  useEffect(() => {
    if (initialSchemeSlug) {
      setSelectedSchemeSlug(initialSchemeSlug);
    }
  }, [initialSchemeSlug]);

  useEffect(() => {
    if (selectedSchemeSlug !== 'general') {
      api.getSchemeDetail(selectedSchemeSlug).then(detail => {
        setActiveSchemeDetail(detail);
      });
    } else {
      setActiveSchemeDetail(null);
    }
  }, [selectedSchemeSlug]);

  const loadDocuments = async () => {
    setLoading(true);
    const docs = await api.listDocuments();
    setDocuments(docs);
    setLoading(false);
  };

  const loadSchemes = async () => {
    const res = await api.listSchemes({ page_size: 50 });
    setAvailableSchemes(res.items);
  };

  const handleFileUpload = async (file: File) => {
    setUploading(true);
    try {
      const doc = await api.uploadDocument(file);
      // If user pre-selected a document type, use it
      if (selectedDocType !== 'auto') {
        doc.detected_type = selectedDocType;
      }
      // Ensure candidate name matches active citizen profile
      if (doc.extracted_fields && profile?.full_name) {
        if (doc.extracted_fields.candidate_name) doc.extracted_fields.candidate_name = profile.full_name;
        if (doc.extracted_fields.holder_name) doc.extracted_fields.holder_name = profile.full_name;
      }
      setPendingDoc(doc);
    } catch (err) {
      console.error("Upload error", err);
    } finally {
      setUploading(false);
    }
  };

  const handleConfirmExtraction = async () => {
    if (!pendingDoc) return;
    try {
      const confirmed = await api.confirmDocument(pendingDoc.id, pendingDoc.extracted_fields || {});
      setDocuments(prev => [...prev.filter(d => d.id !== confirmed.id), confirmed]);
      setPendingDoc(null);
    } catch {
      const confirmed: UserDocument = {
        ...pendingDoc,
        processing_status: 'verified',
        user_confirmed_fields: pendingDoc.extracted_fields,
        created_at: new Date().toISOString().split('T')[0]
      };
      setDocuments(prev => [...prev.filter(d => d.id !== confirmed.id), confirmed]);
      setPendingDoc(null);
    }
  };

  const handleDelete = (id: string) => {
    setDocuments(prev => prev.filter(d => d.id !== id));
  };

  // Check if a document matching a keyword is present in vault
  const hasDocMatching = (keywords: string[]) => {
    return documents.some(doc => {
      const name = (doc.original_filename || '').toLowerCase();
      const type = (doc.detected_type || '').toLowerCase();
      return keywords.some(k => name.includes(k.toLowerCase()) || type.includes(k.toLowerCase()));
    });
  };

  // Universal checklist items for any government scheme
  const universalChecklist = [
    { title: "Aadhaar Card (UIDAI / Identity)", keys: ["aadhaar", "uidai", "identity"], req: "Mandatory for all DBT schemes" },
    { title: "Income Certificate (Tehsildar / Revenue)", keys: ["income", "revenue", "tahsildar"], req: "Current Financial Year" },
    { title: "Academic Marksheet / Certificate", keys: ["mark", "score", "grade", "10th", "12th", "degree"], req: "Prior qualifying examination" },
    { title: "Domicile / Residence Certificate", keys: ["domicile", "residence", "native"], req: "State welfare eligibility" },
    { title: "Caste / Category Certificate (SC/ST/OBC/EWS)", keys: ["caste", "category", "obc", "sc", "st", "ews"], req: "Affirmative action / category schemes" },
    { title: "Bank Passbook / Aadhaar Seeded Account", keys: ["bank", "passbook", "account", "dbt"], req: "Mandatory for Direct Benefit Transfer" },
    { title: "Bonafide Student / Enrollment Certificate", keys: ["bonafide", "enrollment", "study", "college"], req: "Higher education & scholarship schemes" }
  ];

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      {/* Title */}
      <div>
        <h1 className="text-2xl font-bold text-slate-900 flex items-center gap-2">
          <FileText className="w-6 h-6 text-blue-600" />
          Citizen Document Vault & Verification
        </h1>
        <p className="text-slate-500 text-sm mt-1">
          Store and verify your official citizen documents. Extracted facts require your explicit confirmation before being used in government scheme applications.
        </p>
      </div>

      {/* Upload Box */}
      <div className="bg-white rounded-2xl border border-slate-200 p-6 sm:p-8 shadow-xs space-y-5">
        <div className="text-center max-w-md mx-auto space-y-2">
          <div className="w-12 h-12 rounded-2xl bg-blue-50 text-blue-600 flex items-center justify-center mx-auto shadow-2xs">
            <Upload className="w-6 h-6" />
          </div>
          <h3 className="text-base font-bold text-slate-800">
            Upload Official Certificate or Document
          </h3>
          <p className="text-xs text-slate-500">
            Supported formats: PDF, JPEG, PNG (Max 10 MB per file). Stored with strict privacy controls.
          </p>
        </div>

        {/* Document Type Selector before upload */}
        <div className="flex flex-col sm:flex-row items-center justify-center gap-3 pt-2">
          <div className="flex items-center gap-2 text-xs font-semibold text-slate-600">
            <Filter className="w-3.5 h-3.5 text-slate-400" /> Document Category:
          </div>
          <select
            value={selectedDocType}
            onChange={(e) => setSelectedDocType(e.target.value)}
            className="px-3 py-1.5 text-xs rounded-lg border border-slate-200 bg-slate-50 text-slate-700 font-medium focus:ring-2 focus:ring-blue-500/20"
          >
            <option value="auto">Auto-detect from file</option>
            <option value="Aadhaar Card (UIDAI)">Aadhaar Card (UIDAI)</option>
            <option value="Income Certificate">Income Certificate (Tehsildar)</option>
            <option value="Educational Marksheet">Educational Marksheet</option>
            <option value="Bonafide Student Certificate">Bonafide Student Certificate</option>
            <option value="Caste / Category Certificate">Caste / Category Certificate</option>
            <option value="Domicile Certificate">Domicile / Residence Certificate</option>
            <option value="Bank Passbook / Statement">Bank Passbook (DBT Enabled)</option>
            <option value="Disability Certificate (UDID)">Disability Certificate (UDID)</option>
            <option value="Ration Card / Food Security Card">Ration Card</option>
            <option value="Land Records / 7-12 Extract">Land Records (7/12 Extract)</option>
          </select>

          <label className="inline-flex items-center gap-2 px-4 py-2 rounded-lg bg-blue-600 hover:bg-blue-500 text-white text-xs font-semibold cursor-pointer shadow-xs transition-all">
            <FileCheck2 className="w-3.5 h-3.5" />
            {uploading ? 'Extracting document facts...' : 'Choose File to Inspect'}
            <input
              type="file"
              className="hidden"
              accept=".pdf,.png,.jpg,.jpeg"
              onChange={(e) => {
                if (e.target.files && e.target.files[0]) {
                  handleFileUpload(e.target.files[0]);
                }
              }}
            />
          </label>
        </div>
      </div>

      {/* Extracted Facts Review Modal / Card */}
      {pendingDoc && (
        <div className="bg-blue-50/70 border border-blue-200 rounded-2xl p-6 shadow-sm space-y-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Sparkles className="w-5 h-5 text-blue-600" />
              <h3 className="font-bold text-slate-900 text-sm">
                Human Confirmation Required: Review Extracted Facts
              </h3>
            </div>
            <span className="text-xs font-semibold px-2 py-0.5 rounded bg-blue-100 text-blue-800">
              {pendingDoc.detected_type}
            </span>
          </div>

          <p className="text-xs text-slate-600">
            Document intelligence extracted the following values from <strong>{pendingDoc.original_filename}</strong>. Please confirm they match your official document before saving.
          </p>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 bg-white p-4 rounded-xl border border-blue-100 text-xs">
            {pendingDoc.extracted_fields && Object.entries(pendingDoc.extracted_fields).map(([key, val]) => (
              <div key={key} className="space-y-0.5">
                <span className="text-slate-400 font-mono capitalize">{key.replace('_', ' ')}:</span>
                <div className="font-semibold text-slate-800">{String(val)}</div>
              </div>
            ))}
          </div>

          <div className="flex items-center justify-end gap-3 pt-2">
            <button
              onClick={() => setPendingDoc(null)}
              className="px-3 py-1.5 text-xs text-slate-600 hover:text-slate-900"
            >
              Cancel
            </button>
            <button
              onClick={handleConfirmExtraction}
              className="inline-flex items-center gap-1.5 px-4 py-2 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-semibold shadow-xs"
            >
              <CheckCircle2 className="w-3.5 h-3.5" />
              Confirm & Save Extracted Facts
            </button>
          </div>
        </div>
      )}

      {/* Uploaded Documents List */}
      <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-xs space-y-4">
        <h2 className="text-sm font-semibold uppercase tracking-wider text-slate-500 flex items-center justify-between">
          <span>Verified Documents in Your Vault ({documents.length})</span>
          <span className="text-[11px] text-slate-400 font-mono font-normal">Encrypted & Private</span>
        </h2>

        {loading ? (
          <div className="py-8 text-center text-xs text-slate-400 font-mono">
            Loading your document vault...
          </div>
        ) : documents.length === 0 ? (
          <div className="py-10 text-center space-y-2">
            <Inbox className="w-8 h-8 text-slate-300 mx-auto" />
            <div className="text-sm font-medium text-slate-700">No documents in your vault yet</div>
            <p className="text-xs text-slate-400 max-w-sm mx-auto">
              Upload your Aadhaar Card, Income Certificate, or Marksheets above to securely verify eligibility conditions.
            </p>
          </div>
        ) : (
          <div className="divide-y divide-slate-100">
            {documents.map((doc) => (
              <div key={doc.id} className="py-3 flex flex-col sm:flex-row sm:items-center justify-between gap-3">
                <div className="flex items-start gap-3">
                  <div className="w-8 h-8 rounded-lg bg-slate-100 text-slate-600 flex items-center justify-center shrink-0">
                    <FileText className="w-4 h-4" />
                  </div>
                  <div>
                    <div className="text-xs sm:text-sm font-semibold text-slate-900 flex items-center gap-2">
                      {doc.detected_type || doc.original_filename}
                      <span className="text-[10px] px-1.5 py-0.5 rounded-full bg-emerald-50 text-emerald-700 font-medium border border-emerald-200">
                        User Confirmed
                      </span>
                    </div>
                    <div className="text-[11px] text-slate-400 font-mono mt-0.5">
                      {doc.original_filename} • {(doc.file_size / 1024).toFixed(0)} KB • Verified {doc.created_at?.split('T')[0]}
                    </div>
                  </div>
                </div>

                <div className="flex items-center gap-2">
                  <button
                    onClick={() => handleDelete(doc.id)}
                    className="p-1.5 rounded-lg text-slate-400 hover:text-rose-600 hover:bg-rose-50"
                    title="Delete Document"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Dynamic Scheme Document Checklist */}
      <div className="bg-slate-50 border border-slate-200 rounded-2xl p-6 text-xs text-slate-600 space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-2 border-b border-slate-200">
          <div className="flex items-center gap-2">
            <ShieldCheck className="w-5 h-5 text-emerald-600" />
            <div>
              <h3 className="font-bold text-slate-900 text-sm">
                Scheme Document Verification Checklist
              </h3>
              <p className="text-[11px] text-slate-500">
                Check whether your uploaded documents meet the official requirements for any target scheme.
              </p>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <span className="text-[11px] font-semibold text-slate-500 uppercase">Target Policy:</span>
            <select
              value={selectedSchemeSlug}
              onChange={(e) => setSelectedSchemeSlug(e.target.value)}
              className="px-3 py-1.5 text-xs rounded-lg border border-slate-200 bg-white text-slate-800 font-medium focus:ring-2 focus:ring-blue-500/20 max-w-xs"
            >
              <option value="general">🌐 Universal Citizen Welfare Checklist</option>
              {availableSchemes.map((s) => (
                <option key={s.slug} value={s.slug}>
                  {s.name.length > 45 ? s.name.substring(0, 45) + '...' : s.name}
                </option>
              ))}
            </select>
          </div>
        </div>

        {/* If Specific Scheme Selected */}
        {activeSchemeDetail ? (
          <div className="space-y-3">
            <div className="p-3 bg-white rounded-xl border border-slate-200 space-y-1">
              <div className="font-semibold text-slate-900 text-xs">
                Official Requirements for: {activeSchemeDetail.name}
              </div>
              <p className="text-slate-600 text-[11px] leading-relaxed whitespace-pre-line">
                {activeSchemeDetail.documents_required_text || "Aadhaar Card, Income Certificate, Academic Marksheets, and Bank Account Details."}
              </p>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 pt-1 font-mono text-[11px]">
              {activeSchemeDetail.detected_document_tags && activeSchemeDetail.detected_document_tags.length > 0 ? (
                activeSchemeDetail.detected_document_tags.map((tag) => {
                  const isPresent = hasDocMatching([tag.replace('_', ' ')]);
                  return (
                    <div
                      key={tag}
                      className={`p-2 bg-white rounded border flex items-center justify-between gap-1.5 ${isPresent ? 'border-emerald-200 text-emerald-700' : 'border-slate-200 text-slate-700'}`}
                    >
                      <div className="flex items-center gap-1.5 capitalize">
                        {isPresent ? (
                          <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600 shrink-0" />
                        ) : (
                          <Clock className="w-3.5 h-3.5 text-slate-400 shrink-0" />
                        )}
                        <span>{tag.replace(/_/g, ' ')}</span>
                      </div>
                      <span className={`text-[10px] px-1.5 py-0.2 rounded font-sans ${isPresent ? 'bg-emerald-50 text-emerald-700' : 'bg-slate-100 text-slate-500'}`}>
                        {isPresent ? 'Verified' : 'Pending'}
                      </span>
                    </div>
                  );
                })
              ) : (
                universalChecklist.slice(0, 4).map((item, idx) => {
                  const isPresent = hasDocMatching(item.keys);
                  return (
                    <div
                      key={idx}
                      className={`p-2 bg-white rounded border flex items-center justify-between gap-1.5 ${isPresent ? 'border-emerald-200 text-emerald-700' : 'border-slate-200 text-slate-700'}`}
                    >
                      <div className="flex items-center gap-1.5">
                        {isPresent ? (
                          <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600 shrink-0" />
                        ) : (
                          <Clock className="w-3.5 h-3.5 text-slate-400 shrink-0" />
                        )}
                        <span>{item.title}</span>
                      </div>
                      <span className={`text-[10px] px-1.5 py-0.2 rounded font-sans ${isPresent ? 'bg-emerald-50 text-emerald-700' : 'bg-slate-100 text-slate-500'}`}>
                        {isPresent ? 'Verified' : 'Pending'}
                      </span>
                    </div>
                  );
                })
              )}
            </div>
          </div>
        ) : (
          /* Universal Government Checklist */
          <div className="space-y-3">
            <p className="text-[11px] text-slate-500">
              Most central and state government schemes (scholarships, welfare, health, agriculture) verify your eligibility using these standard documents:
            </p>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 pt-1 font-mono text-[11px]">
              {universalChecklist.map((item, idx) => {
                const isPresent = hasDocMatching(item.keys);
                return (
                  <div
                    key={idx}
                    className={`p-2.5 bg-white rounded-xl border flex items-center justify-between gap-2 ${isPresent ? 'border-emerald-200 text-emerald-800' : 'border-slate-200 text-slate-700'}`}
                  >
                    <div className="flex items-center gap-2">
                      {isPresent ? (
                        <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0" />
                      ) : (
                        <span className="w-2.5 h-2.5 rounded-full bg-slate-300 shrink-0"></span>
                      )}
                      <div>
                        <div className="font-semibold text-slate-900">{item.title}</div>
                        <div className="text-[10px] text-slate-400 font-sans">{item.req}</div>
                      </div>
                    </div>
                    <span className={`text-[10px] px-2 py-0.5 rounded-full font-sans font-semibold shrink-0 ${isPresent ? 'bg-emerald-50 text-emerald-700 border border-emerald-200' : 'bg-slate-100 text-slate-500'}`}>
                      {isPresent ? 'Ready in Vault' : 'Upload Needed'}
                    </span>
                  </div>
                );
              })}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
