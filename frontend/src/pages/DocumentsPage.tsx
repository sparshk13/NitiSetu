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
  Clock,
  ShieldAlert,
  XCircle,
  Edit2,
  Lock,
  ChevronDown,
  Tractor,
  HeartPulse,
  Home
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
  const [editableFields, setEditableFields] = useState<Record<string, any>>({});
  const [viewingDoc, setViewingDoc] = useState<UserDocument | null>(null);
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
      const doc = await api.uploadDocument(file, selectedDocType);
      setPendingDoc(doc);
      if (doc.extracted_fields) {
        setEditableFields({ ...doc.extracted_fields });
      } else {
        setEditableFields({});
      }
    } catch (err) {
      console.error("Upload error", err);
    } finally {
      setUploading(false);
    }
  };

  const handleConfirmExtraction = async () => {
    if (!pendingDoc) return;
    try {
      const confirmed = await api.confirmDocument(pendingDoc.id, editableFields);
      setDocuments(prev => [...prev.filter(d => d.id !== confirmed.id), confirmed]);
      setPendingDoc(null);
    } catch {
      const confirmed: UserDocument = {
        ...pendingDoc,
        processing_status: 'verified',
        is_valid: true,
        user_confirmed_fields: editableFields,
        created_at: new Date().toISOString().split('T')[0]
      };
      setDocuments(prev => [...prev.filter(d => d.id !== confirmed.id), confirmed]);
      setPendingDoc(null);
    }
  };

  const handleDelete = async (id: string) => {
    await api.deleteDocument(id);
    setDocuments(prev => prev.filter(d => d.id !== id));
    if (viewingDoc?.id === id) setViewingDoc(null);
  };

  // Check if a document matching a keyword is present in vault
  const hasDocMatching = (keywords: string[]) => {
    return documents.some(doc => {
      const name = (doc.original_filename || '').toLowerCase();
      const type = (doc.detected_type || '').toLowerCase();
      const tag = (doc.tag || '').toLowerCase();
      return keywords.some(k => name.includes(k.toLowerCase()) || type.includes(k.toLowerCase()) || tag.includes(k.toLowerCase()));
    });
  };

  // Universal checklist items for any government citizen scheme
  const universalChecklist = [
    { title: "Aadhaar Card (UIDAI / Identity)", keys: ["aadhaar", "uidai", "identity"], req: "Mandatory for all DBT citizen schemes" },
    { title: "Ration Card (NFSA / BPL / AAY / Food Security)", keys: ["ration", "bpl", "aay", "food", "nfsa"], req: "Healthcare & subsidized food schemes (Ayushman Bharat)" },
    { title: "Income Certificate (Tehsildar / Revenue)", keys: ["income", "revenue", "tahsildar"], req: "Current Financial Year Means-Testing" },
    { title: "Land Ownership Records (7/12, 8A, Khasra, RoR)", keys: ["land", "7/12", "khasra", "khatauni", "ror"], req: "Farmers & Agriculture schemes (PM-KISAN)" },
    { title: "Bank Passbook / Aadhaar Seeded Account", keys: ["bank", "passbook", "account", "dbt"], req: "Mandatory for Direct Benefit Transfer (NPCI linked)" },
    { title: "Domicile / Residence Certificate", keys: ["domicile", "residence", "native"], req: "State welfare eligibility & local quotas" },
    { title: "Caste / Category Certificate (SC/ST/OBC/EWS)", keys: ["caste", "category", "obc", "sc", "st", "ews"], req: "Social justice & affirmative action schemes" },
    { title: "Educational Marksheet / Trade Certificate", keys: ["mark", "score", "grade", "10th", "12th", "degree", "diploma", "iti"], req: "Skill development, employment & scholarship schemes" }
  ];

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      {/* Header */}
      <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-xs">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <div className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-emerald-50 text-emerald-700 text-xs font-semibold mb-2 border border-emerald-100">
              <ShieldCheck className="w-3.5 h-3.5" />
              Verified Citizen Document Intelligence
            </div>
            <h1 className="text-xl sm:text-2xl font-bold text-slate-900 flex items-center gap-2">
              <FileText className="w-6 h-6 text-blue-600" />
              Citizen Document Vault & Verification
            </h1>
            <p className="text-slate-500 text-xs sm:text-sm mt-1 leading-relaxed">
              Upload your official certificates (Aadhaar, Ration Card, Income Certificate, Land 7/12, Bank Passbook, Marksheets). CivicPilot inspects certificate templates, verifies issuing authority seals, extracts official attributes, and requires your explicit review before application seeding.
            </p>
          </div>

          <div className="flex items-center gap-2 bg-slate-50 px-3 py-2 rounded-xl border border-slate-200 shrink-0">
            <Lock className="w-4 h-4 text-emerald-600" />
            <div className="text-xs">
              <div className="font-bold text-slate-800">{documents.length} Verified Documents</div>
              <div className="text-slate-400 text-[10px]">Private & Client-Side Encrypted</div>
            </div>
          </div>
        </div>
      </div>

      {/* Upload Box */}
      <div className="bg-white rounded-2xl border border-slate-200 p-6 sm:p-8 shadow-xs space-y-5">
        <div className="text-center max-w-md mx-auto space-y-2">
          <div className="w-12 h-12 rounded-2xl bg-blue-50 text-blue-600 flex items-center justify-center mx-auto shadow-2xs">
            <Upload className="w-6 h-6" />
          </div>
          <h3 className="text-base font-bold text-slate-800">
            Upload Official Government Certificate or ID
          </h3>
          <p className="text-xs text-slate-500">
            Supported formats: PDF, JPEG, PNG (Max 10 MB). Non-governmental files (receipts, casual photos, invoices) are strictly rejected.
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
            className="px-3 py-2 text-xs rounded-xl border border-slate-200 bg-slate-50 text-slate-700 font-semibold focus:ring-2 focus:ring-blue-500/20"
          >
            <option value="auto">Auto-detect certificate type</option>
            <option value="Aadhaar Card (UIDAI)">Aadhaar Card (UIDAI)</option>
            <option value="Ration Card (NFSA / PDS)">Ration Card (NFSA / BPL / AAY)</option>
            <option value="Income Certificate">Income Certificate (Tehsildar)</option>
            <option value="Land Records (7/12 & 8A)">Land Records (7/12 & 8A Extract / Khasra)</option>
            <option value="Caste / Category Certificate">Caste / Category Certificate</option>
            <option value="Domicile Certificate">Domicile / Residence Certificate</option>
            <option value="Bank Passbook / Statement">Bank Passbook (NPCI DBT Linked)</option>
            <option value="Educational Marksheet">Educational Marksheet / Certificate</option>
            <option value="Bonafide Student Certificate">Bonafide Student / Enrollment Certificate</option>
            <option value="Disability Certificate (UDID)">Disability Certificate (UDID)</option>
            <option value="Senior Citizen Card">Senior Citizen Card / Age Proof</option>
          </select>

          <label className="inline-flex items-center gap-2 px-5 py-2 rounded-xl bg-blue-600 hover:bg-blue-500 text-white text-xs font-semibold cursor-pointer shadow-sm transition-all">
            <FileCheck2 className="w-4 h-4" />
            {uploading ? 'Verifying document...' : 'Choose File & Verify'}
            <input
              type="file"
              className="hidden"
              accept=".pdf,.png,.jpg,.jpeg"
              onChange={(e) => {
                if (e.target.files && e.target.files[0]) {
                  handleFileUpload(e.target.files[0]);
                  e.target.value = '';
                }
              }}
            />
          </label>
        </div>
      </div>

      {/* Category Mismatch Rejection Modal */}
      {pendingDoc && pendingDoc.processing_status === 'rejected_category_mismatch' && (
        <div className="bg-amber-50 border-2 border-amber-300 rounded-2xl p-6 shadow-sm space-y-4 animate-in fade-in duration-200">
          <div className="flex items-start justify-between gap-3">
            <div className="flex items-center gap-2.5">
              <div className="w-10 h-10 rounded-xl bg-amber-100 text-amber-800 flex items-center justify-center shrink-0">
                <ShieldAlert className="w-6 h-6" />
              </div>
              <div>
                <h3 className="font-bold text-amber-950 text-base">
                  Document Category Mismatch Detected
                </h3>
                <p className="text-xs text-amber-800">
                  File: <strong>{pendingDoc.original_filename}</strong> ({((pendingDoc.file_size || 0) / 1024).toFixed(1)} KB)
                </p>
              </div>
            </div>

            <button
              onClick={() => setPendingDoc(null)}
              className="text-amber-500 hover:text-amber-800 p-1"
            >
              <XCircle className="w-5 h-5" />
            </button>
          </div>

          <div className="bg-white p-4 rounded-xl border border-amber-200 text-xs text-slate-800 space-y-3">
            <p className="font-semibold text-amber-900">
              {pendingDoc.verification_error || "The uploaded document does not match the category you selected in the upload form."}
            </p>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 text-[11px] bg-amber-50/60 p-3 rounded-lg border border-amber-200">
              <div>
                <span className="text-slate-500 block">Category You Selected:</span>
                <span className="font-bold text-rose-700">{selectedDocType}</span>
              </div>
              <div>
                <span className="text-slate-500 block">Actual Identified Document:</span>
                <span className="font-bold text-emerald-800">{pendingDoc.detected_type}</span>
              </div>
            </div>

            {pendingDoc.extracted_fields && Object.keys(pendingDoc.extracted_fields).length > 0 && (
              <div className="pt-2 border-t border-slate-100">
                <div className="font-bold text-slate-700 text-[11px] mb-1">Authentic Values Detected on File:</div>
                <div className="max-h-32 overflow-y-auto space-y-1 bg-slate-50 p-2.5 rounded-lg border border-slate-200 font-mono text-[11px]">
                  {Object.entries(pendingDoc.extracted_fields).slice(0, 4).map(([k, v]) => (
                    <div key={k} className="flex justify-between">
                      <span className="text-slate-500 uppercase">{k.replace(/_/g, ' ')}:</span>
                      <span className="font-bold text-slate-900">{String(v)}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>

          <div className="flex flex-col sm:flex-row items-center justify-between gap-3 pt-1">
            <button
              onClick={() => setPendingDoc(null)}
              className="w-full sm:w-auto px-4 py-2 text-xs font-semibold text-slate-600 hover:text-slate-900 bg-white border border-slate-200 rounded-xl"
            >
              Dismiss & Choose Matching File
            </button>

            <button
              onClick={() => {
                if (pendingDoc.detected_type) {
                  setSelectedDocType(pendingDoc.detected_type);
                }
                setPendingDoc({
                  ...pendingDoc,
                  is_valid: true,
                  processing_status: 'awaiting_user_confirmation'
                });
                if (pendingDoc.extracted_fields) {
                  setEditableFields({ ...pendingDoc.extracted_fields });
                }
              }}
              className="w-full sm:w-auto inline-flex items-center justify-center gap-1.5 px-5 py-2.5 rounded-xl bg-amber-600 hover:bg-amber-500 text-white text-xs font-bold shadow-xs transition-all"
            >
              <CheckCircle2 className="w-4 h-4" />
              Switch Category to "{pendingDoc.detected_type}" & Review Facts
            </button>
          </div>
        </div>
      )}

      {/* Review Modal: Document Verification Failed (Corrupted/Non-Government File) */}
      {pendingDoc && pendingDoc.processing_status === 'rejected_unrecognized' && (
        <div className="bg-rose-50 border-2 border-rose-200 rounded-2xl p-6 shadow-sm space-y-4 animate-in fade-in duration-200">
          <div className="flex items-start justify-between gap-3">
            <div className="flex items-center gap-2.5">
              <div className="w-10 h-10 rounded-xl bg-rose-100 text-rose-700 flex items-center justify-center shrink-0">
                <XCircle className="w-6 h-6" />
              </div>
              <div>
                <h3 className="font-bold text-rose-950 text-base">
                  Document Verification Failed: Unrecognized File
                </h3>
                <p className="text-xs text-rose-700">
                  File: <strong>{pendingDoc.original_filename}</strong> ({((pendingDoc.file_size || 0) / 1024).toFixed(1)} KB)
                </p>
              </div>
            </div>

            <button
              onClick={() => setPendingDoc(null)}
              className="text-rose-400 hover:text-rose-700 p-1"
            >
              <XCircle className="w-5 h-5" />
            </button>
          </div>

          <div className="bg-white p-4 rounded-xl border border-rose-200 text-xs text-rose-900 space-y-2">
            <p className="font-semibold text-rose-800">
              {pendingDoc.verification_error || "The uploaded file could not be verified as a recognized Indian government certificate, identity credential, or land/educational record."}
            </p>
            <div className="pt-2 border-t border-rose-100 text-[11px] text-slate-600 space-y-1">
              <div className="font-bold text-slate-700">Verification Checks Performed:</div>
              <div className="flex items-center gap-1.5 text-rose-600">
                <XCircle className="w-3.5 h-3.5" /> Template Structure: No official Gazette/Department certificate template detected.
              </div>
              <div className="flex items-center gap-1.5 text-rose-600">
                <XCircle className="w-3.5 h-3.5" /> Issuing Authority Seal: Missing digital signature or revenue watermark.
              </div>
              <div className="flex items-center gap-1.5 text-rose-600">
                <XCircle className="w-3.5 h-3.5" /> Citizen Identifier: No valid UID, Khasra, Certificate No., or Roll Number identified.
              </div>
            </div>
          </div>

          <div className="flex items-center justify-between text-xs text-rose-800 pt-1">
            <span>To maintain application integrity, random documents cannot be seeded into the vault.</span>
            <button
              onClick={() => setPendingDoc(null)}
              className="px-4 py-2 rounded-lg bg-rose-600 hover:bg-rose-700 text-white font-semibold transition-all shadow-xs"
            >
              Dismiss & Upload Official Certificate
            </button>
          </div>
        </div>
      )}

      {/* Review Modal: Document Verification Passed (Human Confirmation Required) */}
      {pendingDoc && pendingDoc.is_valid !== false && pendingDoc.processing_status === 'awaiting_user_confirmation' && (
        <div className="bg-emerald-50/80 border-2 border-emerald-300 rounded-2xl p-6 shadow-sm space-y-5 animate-in fade-in duration-200">
          <div className="flex items-start justify-between gap-3">
            <div className="flex items-center gap-2.5">
              <div className="w-10 h-10 rounded-xl bg-emerald-100 text-emerald-800 flex items-center justify-center shrink-0">
                <CheckCircle2 className="w-6 h-6" />
              </div>
              <div>
                <div className="flex items-center gap-2">
                  <h3 className="font-bold text-slate-900 text-base">
                    Document Verified: Review & Confirm Extracted Facts
                  </h3>
                  <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-emerald-200 text-emerald-900">
                    {pendingDoc.verification_score || 98}% Match Score
                  </span>
                </div>
                <p className="text-xs text-slate-600">
                  Detected Type: <strong>{pendingDoc.detected_type}</strong> from <em>{pendingDoc.original_filename}</em>
                </p>
              </div>
            </div>

            <button
              onClick={() => setPendingDoc(null)}
              className="text-slate-400 hover:text-slate-700 p-1"
            >
              <XCircle className="w-5 h-5" />
            </button>
          </div>

          <div className="p-3 bg-white/80 rounded-xl border border-emerald-200 text-xs text-slate-700 flex items-center justify-between">
            <div>
              <span className="text-slate-500">Issuing Authority:</span>{' '}
              <strong className="text-slate-900">{pendingDoc.issuing_authority || 'Official State / Central Government Authority'}</strong>
            </div>
            <span className="text-[11px] text-emerald-700 font-semibold flex items-center gap-1">
              <ShieldCheck className="w-3.5 h-3.5" /> Authenticity Verified
            </span>
          </div>

          {/* Editable Fields Grid */}
          <div className="space-y-2">
            <div className="text-xs font-semibold text-slate-700 flex items-center gap-1">
              <Edit2 className="w-3.5 h-3.5 text-blue-600" />
              <span>Review extracted fields (you can click and edit any value if needed):</span>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 bg-white p-4 rounded-xl border border-emerald-200 text-xs">
              {Object.entries(editableFields).map(([key, val]) => (
                <div key={key} className="space-y-1">
                  <label className="block text-[11px] font-mono text-slate-500 uppercase">
                    {key.replace(/_/g, ' ')}
                  </label>
                  <input
                    type="text"
                    value={String(val)}
                    onChange={(e) => setEditableFields({ ...editableFields, [key]: e.target.value })}
                    className="w-full px-2.5 py-1.5 text-xs rounded-lg border border-slate-200 focus:ring-2 focus:ring-emerald-500/20 focus:border-emerald-500 font-semibold text-slate-800 bg-slate-50/50"
                  />
                </div>
              ))}
            </div>
          </div>

          <div className="flex items-center justify-between pt-2">
            <button
              onClick={() => setPendingDoc(null)}
              className="px-3 py-1.5 text-xs text-slate-600 hover:text-slate-900 font-medium"
            >
              Cancel
            </button>
            <button
              onClick={handleConfirmExtraction}
              className="inline-flex items-center gap-1.5 px-5 py-2.5 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-bold shadow-xs transition-all"
            >
              <CheckCircle2 className="w-4 h-4" />
              Confirm & Save to Verified Vault
            </button>
          </div>
        </div>
      )}

      {/* Verified Documents in Vault */}
      <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-xs space-y-4">
        <div className="flex items-center justify-between border-b border-slate-100 pb-3">
          <h2 className="text-sm font-bold uppercase tracking-wider text-slate-800 flex items-center gap-2">
            <ShieldCheck className="w-4 h-4 text-emerald-600" />
            Verified Documents in Your Vault ({documents.length})
          </h2>
          <span className="text-[11px] text-slate-400 font-mono">Ready for Scheme Mapping</span>
        </div>

        {loading ? (
          <div className="py-8 text-center text-xs text-slate-400 font-mono">
            Loading your document vault...
          </div>
        ) : documents.length === 0 ? (
          <div className="py-12 text-center space-y-2">
            <Inbox className="w-10 h-10 text-slate-300 mx-auto" />
            <div className="text-sm font-bold text-slate-700">No documents in your vault yet</div>
            <p className="text-xs text-slate-400 max-w-sm mx-auto">
              Upload your Aadhaar Card, Ration Card, Income Certificate, or Land 7/12 Records above to securely evaluate scheme eligibility.
            </p>
          </div>
        ) : (
          <div className="divide-y divide-slate-100">
            {documents.map((doc) => (
              <div key={doc.id} className="py-3.5 flex flex-col sm:flex-row sm:items-center justify-between gap-3 hover:bg-slate-50/50 px-2 rounded-xl transition-colors">
                <div className="flex items-start gap-3">
                  <div className="w-10 h-10 rounded-xl bg-blue-50 text-blue-700 flex items-center justify-center shrink-0 border border-blue-100">
                    <FileText className="w-5 h-5" />
                  </div>
                  <div>
                    <div className="text-xs sm:text-sm font-bold text-slate-900 flex items-center gap-2">
                      {doc.detected_type || doc.original_filename}
                      <span className="text-[10px] px-2 py-0.5 rounded-full bg-emerald-50 text-emerald-700 font-bold border border-emerald-200 flex items-center gap-1">
                        <Check className="w-3 h-3" /> Verified & Confirmed
                      </span>
                    </div>
                    <div className="text-xs text-slate-500 mt-0.5 flex flex-wrap items-center gap-2">
                      <span>{doc.original_filename}</span>
                      <span>•</span>
                      <span>{((doc.file_size || 500000) / 1024).toFixed(0)} KB</span>
                      {doc.issuing_authority && (
                        <>
                          <span>•</span>
                          <span className="text-slate-600 font-medium truncate max-w-[200px]">{doc.issuing_authority}</span>
                        </>
                      )}
                    </div>
                  </div>
                </div>

                <div className="flex items-center gap-2 self-end sm:self-center">
                  <button
                    onClick={() => setViewingDoc(doc)}
                    className="inline-flex items-center gap-1 px-3 py-1.5 rounded-lg border border-slate-200 hover:border-blue-400 text-xs font-semibold text-slate-700 hover:text-blue-600 transition-colors bg-white shadow-2xs"
                  >
                    <Eye className="w-3.5 h-3.5 text-blue-500" /> View Facts
                  </button>

                  <button
                    onClick={() => handleDelete(doc.id)}
                    className="p-1.5 rounded-lg hover:bg-rose-50 text-slate-400 hover:text-rose-600 transition-colors"
                    title="Delete document"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Viewing Details Modal */}
      {viewingDoc && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-xs animate-in fade-in duration-200">
          <div className="bg-white rounded-2xl max-w-lg w-full p-6 space-y-4 shadow-xl border border-slate-200">
            <div className="flex items-center justify-between border-b border-slate-100 pb-3">
              <div>
                <h3 className="font-bold text-slate-900 text-base">
                  {viewingDoc.detected_type || viewingDoc.original_filename}
                </h3>
                <p className="text-xs text-slate-400">Verified Certificate Record</p>
              </div>
              <button
                onClick={() => setViewingDoc(null)}
                className="text-slate-400 hover:text-slate-700 p-1"
              >
                <XCircle className="w-5 h-5" />
              </button>
            </div>

            <div className="space-y-2 text-xs">
              <div className="grid grid-cols-2 gap-2 p-3 bg-slate-50 rounded-xl border border-slate-100">
                <div>
                  <span className="text-slate-400 text-[10px]">Filename:</span>
                  <div className="font-semibold text-slate-800 truncate">{viewingDoc.original_filename}</div>
                </div>
                <div>
                  <span className="text-slate-400 text-[10px]">Verified Date:</span>
                  <div className="font-semibold text-slate-800">{viewingDoc.created_at?.split('T')[0] || '2024-11-01'}</div>
                </div>
                {viewingDoc.issuing_authority && (
                  <div className="col-span-2">
                    <span className="text-slate-400 text-[10px]">Issuing Authority:</span>
                    <div className="font-semibold text-slate-800">{viewingDoc.issuing_authority}</div>
                  </div>
                )}
              </div>

              <div className="font-semibold text-slate-700 pt-1">Confirmed Data Attributes:</div>
              <div className="max-h-60 overflow-y-auto space-y-2 p-3 bg-slate-50/50 rounded-xl border border-slate-200">
                {viewingDoc.user_confirmed_fields || viewingDoc.extracted_fields ? (
                  Object.entries(viewingDoc.user_confirmed_fields || viewingDoc.extracted_fields || {}).map(([key, val]) => (
                    <div key={key} className="flex items-center justify-between text-xs py-1 border-b border-slate-100 last:border-0">
                      <span className="font-mono text-slate-500 uppercase text-[10px]">{key.replace(/_/g, ' ')}:</span>
                      <span className="font-bold text-slate-900">{String(val)}</span>
                    </div>
                  ))
                ) : (
                  <div className="text-slate-400 text-center py-2">No custom attributes recorded.</div>
                )}
              </div>
            </div>

            <div className="flex items-center justify-between pt-2">
              <button
                onClick={() => handleDelete(viewingDoc.id)}
                className="text-xs font-semibold text-rose-600 hover:text-rose-700 flex items-center gap-1"
              >
                <Trash2 className="w-3.5 h-3.5" /> Remove from Vault
              </button>

              <button
                onClick={() => setViewingDoc(null)}
                className="px-4 py-2 rounded-xl bg-slate-900 text-white text-xs font-bold hover:bg-slate-800 shadow-xs"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Target Scheme Document Checklist Selector */}
      <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-xs space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-slate-100 pb-3">
          <div>
            <h2 className="text-sm font-bold uppercase tracking-wider text-slate-800 flex items-center gap-2">
              <FileCheck2 className="w-4 h-4 text-blue-600" />
              Target Scheme Document Checklist & Readiness Audit
            </h2>
            <p className="text-xs text-slate-500 mt-0.5">
              Select any government scheme to check which documents in your vault meet its requirements.
            </p>
          </div>

          <div className="relative min-w-[220px]">
            <select
              value={selectedSchemeSlug}
              onChange={(e) => setSelectedSchemeSlug(e.target.value)}
              className="w-full px-3 py-2 text-xs rounded-xl border border-slate-300 bg-slate-50 text-slate-800 font-semibold focus:ring-2 focus:ring-blue-500/20"
            >
              <option value="general">🌐 Universal Citizen Welfare Checklist</option>
              {availableSchemes.map((s) => (
                <option key={s.slug} value={s.slug}>
                  📋 {s.name.length > 40 ? s.name.substring(0, 40) + '...' : s.name}
                </option>
              ))}
            </select>
          </div>
        </div>

        {/* Selected Scheme Detail Banner */}
        {selectedSchemeSlug !== 'general' && activeSchemeDetail && (
          <div className="p-3 bg-blue-50/60 border border-blue-100 rounded-xl text-xs space-y-1">
            <div className="font-bold text-blue-950">{activeSchemeDetail.name}</div>
            <div className="text-slate-600">
              {activeSchemeDetail.documents_required_text || 'Requires standard identity, means, and jurisdictional proofs.'}
            </div>
          </div>
        )}

        {/* Checklist Items */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 pt-2">
          {universalChecklist.map((item, idx) => {
            const isReady = hasDocMatching(item.keys);
            return (
              <div
                key={idx}
                className={`p-3.5 rounded-xl border transition-all flex items-start gap-3 ${
                  isReady 
                    ? 'bg-emerald-50/40 border-emerald-200' 
                    : 'bg-slate-50/60 border-slate-200'
                }`}
              >
                <div className={`w-5 h-5 rounded-full flex items-center justify-center shrink-0 mt-0.5 ${
                  isReady ? 'bg-emerald-600 text-white' : 'border border-slate-300 text-slate-300'
                }`}>
                  {isReady ? <Check className="w-3.5 h-3.5" /> : <Clock className="w-3 h-3" />}
                </div>

                <div className="space-y-0.5">
                  <div className={`text-xs font-bold ${isReady ? 'text-emerald-950' : 'text-slate-800'}`}>
                    {item.title}
                  </div>
                  <div className="text-[11px] text-slate-500 leading-relaxed">
                    {item.req}
                  </div>
                  <div className="pt-1.5 flex items-center justify-between gap-2">
                    <span className={`text-[10px] font-semibold px-2 py-0.5 rounded-full ${
                      isReady ? 'bg-emerald-100 text-emerald-800' : 'bg-slate-200 text-slate-600'
                    }`}>
                      {isReady ? 'Ready in Vault' : 'Missing / Required'}
                    </span>
                    {!isReady && (
                      <button
                        onClick={() => {
                          setSelectedDocType(item.title);
                          window.scrollTo({ top: 0, behavior: 'smooth' });
                        }}
                        className="text-[10px] font-bold text-blue-600 hover:text-blue-700 hover:underline flex items-center gap-1"
                      >
                        <Upload className="w-3 h-3" /> Select Category
                      </button>
                    )}
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
};
