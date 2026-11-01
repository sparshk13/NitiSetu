import React, { useEffect, useState } from 'react';
import { 
  User, 
  GraduationCap, 
  Building2, 
  IndianRupee, 
  ShieldCheck, 
  CheckCircle2, 
  Info,
  Save,
  Briefcase,
  Tractor,
  Home,
  Check
} from 'lucide-react';
import { api, ProfileData } from '../api/client';

const COMMON_STATES = [
  "Andhra Pradesh", "Arunachal Pradesh", "Assam", "Bihar", "Chhattisgarh", "Goa", "Gujarat",
  "Haryana", "Himachal Pradesh", "Jharkhand", "Karnataka", "Kerala", "Madhya Pradesh", "Maharashtra",
  "Manipur", "Meghalaya", "Mizoram", "Nagaland", "Odisha", "Punjab", "Rajasthan", "Sikkim",
  "Tamil Nadu", "Telangana", "Tripura", "Uttar Pradesh", "Uttarakhand", "West Bengal",
  "Andaman and Nicobar Islands", "Chandigarh", "Dadra and Nagar Haveli and Daman and Diu",
  "Delhi (NCT)", "Jammu and Kashmir", "Ladakh", "Lakshadweep", "Puducherry"
];

const CITIZEN_OCCUPATIONS = [
  "Farmer (Cultivator / Landowner)",
  "Agricultural Labourer",
  "Traditional Artisan / Craftsman (PM Vishwakarma)",
  "Street Vendor / Micro-vendor (PM SVANidhi)",
  "Construction Worker / Daily Wage Laborer",
  "Salaried Employee (Private Sector)",
  "Government / PSU / Defense Employee",
  "Self-Employed / MSME Owner / Shopkeeper",
  "Homemaker / Women Self-Help Group (SHG) Member",
  "Retired / Senior Citizen / Pensioner",
  "Unemployed / Job Seeker",
  "Student / Scholar"
];

const HIGHEST_QUALIFICATIONS = [
  "No Formal Education",
  "Primary Education (Class 1 - 5)",
  "Middle School (Class 6 - 8)",
  "Class 10th Passed (Secondary)",
  "Class 12th Passed (Higher Secondary)",
  "ITI / Vocational Trade Certificate",
  "Polytechnic Diploma in Engineering",
  "Undergraduate / Bachelor's Degree (B.Tech, B.Sc, B.Com, BA, MBBS)",
  "Postgraduate / Master's Degree (M.Tech, MBA, MCA, M.Sc, MA, MD)",
  "Doctorate / Ph.D."
];

const COMMON_COURSES = [
  // Engineering & Technology
  "B.Tech Computer Science & Engineering",
  "B.Tech Artificial Intelligence & Machine Learning",
  "B.Tech Data Science",
  "B.Tech Information Technology",
  "B.Tech Electronics & Communication Engineering",
  "B.Tech Mechanical Engineering",
  "B.Tech Civil Engineering",
  "B.Tech Electrical & Electronics Engineering",
  "B.Tech Chemical Engineering",
  "B.Tech Aerospace Engineering",
  "B.Tech Biotechnology",
  "B.Tech Agricultural Engineering",
  "Bachelor of Computer Applications (BCA)",

  // Sciences & Agriculture
  "B.Sc Computer Science",
  "B.Sc Information Technology",
  "B.Sc Mathematics",
  "B.Sc Physics",
  "B.Sc Chemistry",
  "B.Sc Agriculture (Honours)",
  "B.Sc Horticulture",
  "B.Sc Nursing",
  "B.Sc Biotechnology",
  "B.Sc Forestry",

  // Medical & Allied Health
  "MBBS (Bachelor of Medicine & Bachelor of Surgery)",
  "Bachelor of Dental Surgery (BDS)",
  "Bachelor of Ayurvedic Medicine & Surgery (BAMS)",
  "Bachelor of Homeopathic Medicine & Surgery (BHMS)",
  "Bachelor of Pharmacy (B.Pharm)",
  "Bachelor of Physiotherapy (BPT)",
  "B.Sc Medical Laboratory Technology (BMLT)",
  "B.Sc Radiography & Imaging Technology",

  // Commerce & Management
  "Bachelor of Commerce (B.Com General)",
  "B.Com (Honours)",
  "B.Com Accounting & Finance",
  "Bachelor of Business Administration (BBA)",
  "Bachelor of Management Studies (BMS)",

  // Arts, Humanities & Law
  "Bachelor of Arts (Economics)",
  "Bachelor of Arts (Political Science)",
  "Bachelor of Arts (English Literature)",
  "Bachelor of Arts (Psychology)",
  "Bachelor of Arts (History)",
  "Bachelor of Arts (Journalism & Mass Communication)",
  "Bachelor of Social Work (BSW)",
  "Bachelor of Laws (LL.B - 3 Year)",
  "B.A. LL.B (5 Year Integrated)",
  "B.B.A. LL.B (5 Year Integrated)",
  "Bachelor of Design (B.Des)",
  "Bachelor of Architecture (B.Arch)",
  "Bachelor of Education (B.Ed)",

  // Polytechnic Diplomas & ITI Trades
  "Polytechnic Diploma in Mechanical Engineering",
  "Polytechnic Diploma in Civil Engineering",
  "Polytechnic Diploma in Electrical Engineering",
  "Polytechnic Diploma in Computer Engineering",
  "Polytechnic Diploma in Automobile Engineering",
  "Polytechnic Diploma in Electronics & Communication",
  "Diploma in Pharmacy (D.Pharm)",
  "ITI Electrician Trade Certificate",
  "ITI Fitter Trade Certificate",
  "ITI Welder Trade Certificate",
  "ITI Computer Operator & Programming Assistant (COPA)",
  "ITI Draughtsman (Civil / Mechanical)",

  // Higher Secondary
  "Class 11 / 12 (Science Stream - PCM)",
  "Class 11 / 12 (Science Stream - PCB)",
  "Class 11 / 12 (Commerce Stream)",
  "Class 11 / 12 (Arts & Humanities)",

  // Postgraduate Programs
  "Master of Technology (M.Tech CSE / IT)",
  "Master of Technology (M.Tech VLSI & Embedded)",
  "Master of Business Administration (MBA)",
  "Master of Computer Applications (MCA)",
  "M.Sc Computer Science / IT",
  "M.Sc Mathematics / Statistics",
  "M.Sc Physics / Chemistry",
  "M.Sc Agriculture / Agronomy",
  "Master of Commerce (M.Com)",
  "Master of Arts (Economics / Public Policy)",
  "Master of Social Work (MSW)",
  "Master of Pharmacy (M.Pharm)",
  "Doctor of Medicine / Master of Surgery (MD / MS)",
  "Master of Laws (LL.M)",
  "Doctor of Philosophy (Ph.D.)"
];

const COMMON_INSTITUTIONS = [
  // Central Universities & Institutes of National Importance
  "University of Delhi (DU), New Delhi",
  "Jawaharlal Nehru University (JNU), New Delhi",
  "Banaras Hindu University (BHU), Varanasi, Uttar Pradesh",
  "Aligarh Muslim University (AMU), Aligarh, Uttar Pradesh",
  "Jamia Millia Islamia, New Delhi",
  "University of Hyderabad (UoH), Hyderabad, Telangana",
  "Visva-Bharati University, Santiniketan, West Bengal",
  "Pondicherry University, Puducherry",
  "Central University of Gujarat (CUG), Gandhinagar",
  "Central University of Rajasthan (CURAJ), Ajmer",
  "Central University of Punjab, Bathinda",

  // IITs, IISc & NITs
  "Indian Institute of Technology (IIT) Bombay, Maharashtra",
  "Indian Institute of Technology (IIT) Delhi, New Delhi",
  "Indian Institute of Technology (IIT) Madras, Tamil Nadu",
  "Indian Institute of Technology (IIT) Kharagpur, West Bengal",
  "Indian Institute of Technology (IIT) Kanpur, Uttar Pradesh",
  "Indian Institute of Technology (IIT) Roorkee, Uttarakhand",
  "Indian Institute of Technology (IIT) Guwahati, Assam",
  "Indian Institute of Technology (IIT) Hyderabad, Telangana",
  "Indian Institute of Technology (IIT) Gandhinagar, Gujarat",
  "Indian Institute of Technology (IIT) Indore, Madhya Pradesh",
  "Indian Institute of Science (IISc), Bengaluru, Karnataka",
  "BITS Pilani, Pilani Campus, Rajasthan",
  "BITS Pilani, K.K. Birla Goa Campus",
  "BITS Pilani, Hyderabad Campus",
  "National Institute of Technology (NIT) Tiruchirappalli, Tamil Nadu",
  "National Institute of Technology (NIT) Karnataka, Surathkal",
  "National Institute of Technology (NIT) Rourkela, Odisha",
  "National Institute of Technology (NIT) Warangal, Telangana",
  "National Institute of Technology (NIT) Calicut, Kerala",
  "Sardar Vallabhbhai National Institute of Technology (SVNIT), Surat, Gujarat",
  "Visvesvaraya National Institute of Technology (VNIT), Nagpur, Maharashtra",
  "Malaviya National Institute of Technology (MNIT), Jaipur, Rajasthan",
  "Motilal Nehru National Institute of Technology (MNNIT), Prayagraj, UP",

  // Medical Institutions
  "All India Institute of Medical Sciences (AIIMS), New Delhi",
  "All India Institute of Medical Sciences (AIIMS), Jodhpur, Rajasthan",
  "All India Institute of Medical Sciences (AIIMS), Bhopal, Madhya Pradesh",
  "All India Institute of Medical Sciences (AIIMS), Rishikesh, Uttarakhand",
  "All India Institute of Medical Sciences (AIIMS), Bhubaneswar, Odisha",
  "Postgraduate Institute of Medical Education and Research (PGIMER), Chandigarh",
  "Christian Medical College (CMC), Vellore, Tamil Nadu",
  "King George's Medical University (KGMU), Lucknow, Uttar Pradesh",
  "B.J. Medical College, Ahmedabad, Gujarat",
  "Grant Government Medical College & Sir JJ Group of Hospitals, Mumbai",
  "Madras Medical College (MMC), Chennai, Tamil Nadu",

  // State Technical & Public Universities - Gujarat
  "Gujarat Technological University (GTU), Ahmedabad, Gujarat",
  "Gujarat University, Ahmedabad, Gujarat",
  "Maharaja Sayajirao University of Baroda (MSU), Vadodara, Gujarat",
  "Sardar Patel University (SPU), Vallabh Vidyanagar, Anand, Gujarat",
  "Pandit Deendayal Energy University (PDEU), Gandhinagar, Gujarat",
  "Nirma University, Ahmedabad, Gujarat",
  "Dhirubhai Ambani Institute of Information and Communication Technology (DA-IICT), Gandhinagar",
  "Dharamsinh Desai University (DDU), Nadiad, Gujarat",
  "Veer Narmad South Gujarat University (VNSGU), Surat, Gujarat",
  "Saurashtra University, Rajkot, Gujarat",
  "Hemchandracharya North Gujarat University (HNGU), Patan, Gujarat",
  "Anand Agricultural University (AAU), Anand, Gujarat",

  // State Universities - Maharashtra
  "University of Mumbai, Mumbai, Maharashtra",
  "Savitribai Phule Pune University (SPPU), Pune, Maharashtra",
  "College of Engineering Pune (COEP), Pune, Maharashtra",
  "Veermata Jijabai Technological Institute (VJTI), Mumbai, Maharashtra",
  "Rashtrasant Tukadoji Maharaj Nagpur University, Nagpur, Maharashtra",
  "Dr. Babasaheb Ambedkar Marathwada University, Chhatrapati Sambhajinagar",
  "SNDT Women's University, Mumbai, Maharashtra",

  // State Universities - Delhi & NCR
  "Guru Gobind Singh Indraprastha University (GGSIPU), New Delhi",
  "Delhi Technological University (DTU), New Delhi",
  "Netaji Subhas University of Technology (NSUT), New Delhi",
  "Indira Gandhi Delhi Technical University for Women (IGDTUW), New Delhi",

  // State Universities - Uttar Pradesh
  "Dr. A.P.J. Abdul Kalam Technical University (AKTU), Lucknow, UP",
  "University of Lucknow, Lucknow, Uttar Pradesh",
  "Chhatrapati Shahu Ji Maharaj University (CSJMU), Kanpur, Uttar Pradesh",
  "Deen Dayal Upadhyaya Gorakhpur University, Gorakhpur, Uttar Pradesh",

  // State Universities - Karnataka
  "Visvesvaraya Technological University (VTU), Belagavi, Karnataka",
  "Bangalore University, Bengaluru, Karnataka",
  "Manipal Academy of Higher Education (MAHE), Manipal, Karnataka",
  "Rajiv Gandhi University of Health Sciences (RGUHS), Bengaluru, Karnataka",
  "University of Mysore, Mysuru, Karnataka",

  // State Universities - Tamil Nadu
  "Anna University, Chennai, Tamil Nadu",
  "University of Madras, Chennai, Tamil Nadu",
  "Madurai Kamaraj University, Madurai, Tamil Nadu",
  "Vellore Institute of Technology (VIT), Vellore, Tamil Nadu",
  "SRM Institute of Science and Technology, Chennai, Tamil Nadu",
  "PSG College of Technology, Coimbatore, Tamil Nadu",

  // State Universities - West Bengal
  "University of Calcutta, Kolkata, West Bengal",
  "Jadavpur University, Kolkata, West Bengal",
  "Maulana Abul Kalam Azad University of Technology (MAKAUT), Kolkata",
  "Presidency University, Kolkata, West Bengal",

  // State Universities - Telangana & Andhra Pradesh
  "Osmania University, Hyderabad, Telangana",
  "Jawaharlal Nehru Technological University (JNTU), Hyderabad, Telangana",
  "Andhra University, Visakhapatnam, Andhra Pradesh",
  "Sri Venkateswara University, Tirupati, Andhra Pradesh",

  // State Universities - Rajasthan, Punjab, Haryana, Kerala, MP, Bihar, Odisha
  "University of Rajasthan, Jaipur, Rajasthan",
  "Rajasthan Technical University (RTU), Kota, Rajasthan",
  "Panjab University, Chandigarh",
  "I.K. Gujral Punjab Technical University (IKGPTU), Jalandhar, Punjab",
  "Kurukshetra University, Kurukshetra, Haryana",
  "University of Kerala, Thiruvananthapuram, Kerala",
  "APJ Abdul Kalam Technological University (KTU), Thiruvananthapuram, Kerala",
  "Cochin University of Science and Technology (CUSAT), Kochi, Kerala",
  "Rajiv Gandhi Proudyogiki Vishwavidyalaya (RGPV), Bhopal, Madhya Pradesh",
  "Devi Ahilya Vishwavidyalaya (DAVV), Indore, Madhya Pradesh",
  "Patna University, Patna, Bihar",
  "Aryabhatta Knowledge University, Patna, Bihar",
  "Birla Institute of Technology (BIT) Mesra, Ranchi, Jharkhand",
  "Utkal University, Bhubaneswar, Odisha",
  "Gauhati University, Guwahati, Assam"
];

interface ProfilePageProps {
  onProfileUpdated?: (updated: ProfileData) => void;
}

export const ProfilePage: React.FC<ProfilePageProps> = ({ onProfileUpdated }) => {
  const [profile, setProfile] = useState<ProfileData>({
    full_name: '',
    age: undefined,
    gender: 'Male',
    marital_status: 'Single',
    state_code: '',
    district: '',
    area_type: 'Rural',
    occupation: 'Farmer (Cultivator / Landowner)',
    annual_family_income: 180000,
    ration_card_type: 'BPL / Priority Household (PHH)',
    caste_category: 'OBC',
    is_minority_community: false,
    is_differently_abled: false,
    is_landowner: false,
    land_holding_acres: 0,
    has_bank_account: true,
    is_bank_aadhaar_seeded: true,
    highest_qualification: 'Class 12th Passed (Higher Secondary)',
    is_student_currently: false,
    education_level: 'Undergraduate',
    course: '',
    study_year: 1,
    institution_name: ''
  });

  const [saving, setSaving] = useState(false);
  const [saveSuccess, setSaveSuccess] = useState(false);

  useEffect(() => {
    async function load() {
      const data = await api.getProfile();
      setProfile(prev => ({
        ...prev,
        ...data,
        is_student_currently: data.is_student_currently ?? (data.occupation?.toLowerCase().includes('student') || Boolean(data.course))
      }));
    }
    load();
  }, []);

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    setSaveSuccess(false);
    try {
      const updated = await api.updateProfile(profile);
      setProfile(updated);
      setSaveSuccess(true);
      if (onProfileUpdated) onProfileUpdated(updated);
      setTimeout(() => setSaveSuccess(false), 4000);
    } catch (err) {
      console.error(err);
    } finally {
      setSaving(false);
    }
  };

  const isStudent = profile.is_student_currently || profile.occupation?.toLowerCase().includes('student');
  const isFarmer = profile.occupation?.toLowerCase().includes('farmer') || profile.occupation?.toLowerCase().includes('agri');

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      {/* Header */}
      <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-xs">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <div className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-blue-50 text-blue-700 text-xs font-semibold mb-2 border border-blue-100">
              <ShieldCheck className="w-3.5 h-3.5" />
              Universal Citizen Profile & Entitlements Registry
            </div>
            <h1 className="text-xl sm:text-2xl font-bold text-slate-900 flex items-center gap-2">
              <User className="w-6 h-6 text-blue-600" />
              Citizen Profile & Demographics
            </h1>
            <p className="text-slate-500 text-xs sm:text-sm mt-1 leading-relaxed">
              NitiSetu matches your demographic facts, livelihood, and economic indicators deterministically against official Central & State Government scheme rules (Gazette & DBT Bharat).
            </p>
          </div>

          <div className="flex items-center gap-3">
            <div className="text-right">
              <div className="text-xs text-slate-400 font-medium">Profile Completeness</div>
              <div className="text-lg font-bold text-emerald-600">
                {profile.completeness_percentage || (profile.full_name ? 40 : 0)}%
              </div>
            </div>
            <div className="w-12 h-12 rounded-full bg-emerald-50 border-2 border-emerald-500 flex items-center justify-center font-bold text-emerald-700 text-sm">
              {profile.completeness_percentage || 40}%
            </div>
          </div>
        </div>
      </div>

      {saveSuccess && (
        <div className="p-4 rounded-xl bg-emerald-50 border border-emerald-200 text-emerald-800 flex items-center gap-2 text-sm shadow-xs animate-in fade-in duration-300">
          <CheckCircle2 className="w-5 h-5 text-emerald-600 shrink-0" />
          <div>
            <span className="font-semibold">Profile updated successfully!</span> Your scheme eligibility ratings and recommended benefits have been recalibrated across all sectors.
          </div>
        </div>
      )}

      {/* Main Profile Form */}
      <form onSubmit={handleSave} className="bg-white p-6 sm:p-8 rounded-2xl border border-slate-200 shadow-xs space-y-8">
        
        {/* Section 1: Demographics & Identity */}
        <div className="space-y-4">
          <div className="flex items-center justify-between border-b border-slate-100 pb-2">
            <h2 className="text-sm font-bold uppercase tracking-wider text-slate-800 flex items-center gap-2">
              <User className="w-4 h-4 text-blue-600" />
              1. Citizen Identity & Demographics
            </h2>
            <span className="text-[11px] text-slate-400 font-medium">Aadhaar / Government ID Verified</span>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-4">
            <div className="sm:col-span-2">
              <label className="block text-xs font-semibold text-slate-700 mb-1">
                Full Legal Name (as per Aadhaar / Official Record) *
              </label>
              <input
                type="text"
                required
                value={profile.full_name || ''}
                onChange={(e) => setProfile({ ...profile, full_name: e.target.value })}
                className="w-full px-3 py-2 text-sm rounded-lg border border-slate-200 focus:outline-hidden focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500"
                placeholder="e.g. Ramesh Patel, Sunita Sharma"
              />
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">
                Age (Completed Years)
              </label>
              <input
                type="number"
                min="0"
                max="120"
                value={profile.age ?? ''}
                onChange={(e) => setProfile({ ...profile, age: e.target.value ? parseInt(e.target.value) : undefined })}
                className="w-full px-3 py-2 text-sm rounded-lg border border-slate-200 focus:outline-hidden focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500"
                placeholder="e.g. 28, 45, 62"
              />
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">
                Gender
              </label>
              <select
                value={profile.gender || 'Male'}
                onChange={(e) => setProfile({ ...profile, gender: e.target.value })}
                className="w-full px-3 py-2 text-sm rounded-lg border border-slate-200 bg-white"
              >
                <option value="Male">Male</option>
                <option value="Female">Female</option>
                <option value="Transgender">Transgender</option>
                <option value="Other">Other</option>
              </select>
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">
                Marital Status
              </label>
              <select
                value={profile.marital_status || 'Single'}
                onChange={(e) => setProfile({ ...profile, marital_status: e.target.value })}
                className="w-full px-3 py-2 text-sm rounded-lg border border-slate-200 bg-white"
              >
                <option value="Single">Single / Unmarried</option>
                <option value="Married">Married</option>
                <option value="Widowed">Widowed</option>
                <option value="Divorced">Divorced / Separated</option>
              </select>
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">
                Permanent State / UT of Residence *
              </label>
              <select
                value={profile.state_code || ''}
                onChange={(e) => setProfile({ ...profile, state_code: e.target.value })}
                className="w-full px-3 py-2 text-sm rounded-lg border border-slate-200 bg-white"
              >
                <option value="">Select State / UT</option>
                {COMMON_STATES.map((state) => (
                  <option key={state} value={state}>{state}</option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">
                District / City (Optional)
              </label>
              <input
                type="text"
                value={profile.district || ''}
                onChange={(e) => setProfile({ ...profile, district: e.target.value })}
                className="w-full px-3 py-2 text-sm rounded-lg border border-slate-200"
                placeholder="e.g. Ahmedabad, Pune, Patna"
              />
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">
                Area Classification
              </label>
              <select
                value={profile.area_type || 'Rural'}
                onChange={(e) => setProfile({ ...profile, area_type: e.target.value })}
                className="w-full px-3 py-2 text-sm rounded-lg border border-slate-200 bg-white"
              >
                <option value="Rural">Rural (Village / Gram Panchayat)</option>
                <option value="Urban">Urban (Municipality / Municipal Corp)</option>
                <option value="Semi-Urban">Semi-Urban / Peri-Urban</option>
              </select>
            </div>
          </div>
        </div>

        {/* Section 2: Socio-Economic Profile & Welfare Entitlements */}
        <div className="space-y-4 pt-4 border-t border-slate-100">
          <div className="flex items-center justify-between border-b border-slate-100 pb-2">
            <h2 className="text-sm font-bold uppercase tracking-wider text-slate-800 flex items-center gap-2">
              <IndianRupee className="w-4 h-4 text-emerald-600" />
              2. Socio-Economic Status & Welfare Entitlements
            </h2>
            <span className="text-[11px] text-slate-400 font-medium">Means-Testing & Priority Norms</span>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-4">
            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">
                Social Category / Caste Group *
              </label>
              <select
                value={profile.caste_category || 'General'}
                onChange={(e) => setProfile({ ...profile, caste_category: e.target.value })}
                className="w-full px-3 py-2 text-sm rounded-lg border border-slate-200 bg-white"
              >
                <option value="General">General / Open Category</option>
                <option value="EWS">EWS (Economically Weaker Section)</option>
                <option value="OBC">OBC (Other Backward Classes)</option>
                <option value="SC">SC (Scheduled Caste)</option>
                <option value="ST">ST (Scheduled Tribe)</option>
                <option value="Minority">Religious Minority Community</option>
              </select>
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">
                Annual Gross Household Income (INR) *
              </label>
              <div className="relative">
                <span className="absolute left-3 top-2.5 text-slate-400 font-semibold text-sm">₹</span>
                <input
                  type="number"
                  required
                  min="0"
                  step="5000"
                  value={profile.annual_family_income ?? ''}
                  onChange={(e) => setProfile({ ...profile, annual_family_income: parseFloat(e.target.value) || 0 })}
                  className="w-full pl-7 pr-3 py-2 text-sm rounded-lg border border-slate-200 focus:outline-hidden focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500"
                  placeholder="e.g. 180000"
                />
              </div>
              <p className="text-[11px] text-slate-400 mt-1">Total family income from all sources (used for BPL & means ceilings)</p>
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">
                Ration Card / Food Security Classification
              </label>
              <select
                value={profile.ration_card_type || 'None'}
                onChange={(e) => setProfile({ ...profile, ration_card_type: e.target.value })}
                className="w-full px-3 py-2 text-sm rounded-lg border border-slate-200 bg-white"
              >
                <option value="None">None / General Ration Card</option>
                <option value="Antyodaya (AAY)">Antyodaya Anna Yojana (AAY - Poorest of Poor)</option>
                <option value="BPL / Priority Household (PHH)">BPL / Priority Household (PHH / NFSA)</option>
                <option value="APL / Non-NFSA">APL (Above Poverty Line / Non-NFSA)</option>
              </select>
            </div>
          </div>

          {/* Checkboxes row */}
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 pt-2">
            <div className="flex items-center gap-2 p-3 rounded-lg border border-slate-200 bg-slate-50/50">
              <input
                type="checkbox"
                id="minority"
                checked={profile.is_minority_community || false}
                onChange={(e) => setProfile({ ...profile, is_minority_community: e.target.checked })}
                className="w-4 h-4 rounded text-blue-600 focus:ring-blue-500 border-slate-300"
              />
              <label htmlFor="minority" className="text-xs font-medium text-slate-700">
                Notified Religious Minority (Muslim, Christian, Sikh, Buddhist, Jain, Parsi)
              </label>
            </div>

            <div className="flex items-center gap-2 p-3 rounded-lg border border-slate-200 bg-slate-50/50">
              <input
                type="checkbox"
                id="disability"
                checked={profile.is_differently_abled || false}
                onChange={(e) => setProfile({ ...profile, is_differently_abled: e.target.checked })}
                className="w-4 h-4 rounded text-blue-600 focus:ring-blue-500 border-slate-300"
              />
              <label htmlFor="disability" className="text-xs font-medium text-slate-700">
                Person with Disability (UDID / 40%+ benchmark PwD)
              </label>
            </div>

            <div className="flex items-center gap-2 p-3 rounded-lg border border-slate-200 bg-slate-50/50">
              <input
                type="checkbox"
                id="aadhaar-seeded"
                checked={profile.is_bank_aadhaar_seeded ?? true}
                onChange={(e) => setProfile({ ...profile, is_bank_aadhaar_seeded: e.target.checked })}
                className="w-4 h-4 rounded text-emerald-600 focus:ring-emerald-500 border-slate-300"
              />
              <label htmlFor="aadhaar-seeded" className="text-xs font-medium text-slate-700">
                Bank Account is NPCI Aadhaar-Seeded (Ready for Direct Benefit Transfer DBT)
              </label>
            </div>
          </div>
        </div>

        {/* Section 3: Occupation & Livelihood */}
        <div className="space-y-4 pt-4 border-t border-slate-100">
          <div className="flex items-center justify-between border-b border-slate-100 pb-2">
            <h2 className="text-sm font-bold uppercase tracking-wider text-slate-800 flex items-center gap-2">
              <Briefcase className="w-4 h-4 text-amber-600" />
              3. Livelihood, Occupation & Landholding
            </h2>
            <span className="text-[11px] text-slate-400 font-medium">Core Eligibility for Welfare, Farmer & Business Schemes</span>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">
                Primary Occupation / Citizen Category *
              </label>
              <select
                value={profile.occupation || 'Farmer (Cultivator / Landowner)'}
                onChange={(e) => {
                  const val = e.target.value;
                  const isStud = val.toLowerCase().includes('student');
                  const isFarm = val.toLowerCase().includes('farmer');
                  setProfile({ 
                    ...profile, 
                    occupation: val,
                    is_student_currently: isStud ? true : profile.is_student_currently,
                    is_landowner: isFarm ? true : profile.is_landowner
                  });
                }}
                className="w-full px-3 py-2 text-sm rounded-lg border border-slate-200 bg-white font-medium"
              >
                {CITIZEN_OCCUPATIONS.map((occ) => (
                  <option key={occ} value={occ}>{occ}</option>
                ))}
              </select>
              <p className="text-[11px] text-slate-400 mt-1">NitiSetu prioritizes central and state welfare benefits specific to your profession.</p>
            </div>

            {/* Conditional Farmer / Landowner fields */}
            <div className={`p-4 rounded-xl border transition-all ${isFarmer || profile.is_landowner ? 'bg-amber-50/50 border-amber-200' : 'bg-slate-50 border-slate-200'}`}>
              <div className="flex items-center gap-2 mb-2">
                <input
                  type="checkbox"
                  id="landowner"
                  checked={profile.is_landowner || false}
                  onChange={(e) => setProfile({ ...profile, is_landowner: e.target.checked })}
                  className="w-4 h-4 rounded text-amber-600 focus:ring-amber-500 border-slate-300"
                />
                <label htmlFor="landowner" className="text-xs font-bold text-slate-800 flex items-center gap-1.5">
                  <Tractor className="w-3.5 h-3.5 text-amber-600" />
                  Citizen owns cultivable agricultural land (PM-KISAN / PMFBY)
                </label>
              </div>

              {(isFarmer || profile.is_landowner) && (
                <div className="mt-3">
                  <label className="block text-xs font-semibold text-slate-700 mb-1">
                    Cultivable Agricultural Landholding (Acres)
                  </label>
                  <input
                    type="number"
                    min="0"
                    step="0.1"
                    value={profile.land_holding_acres ?? ''}
                    onChange={(e) => setProfile({ ...profile, land_holding_acres: parseFloat(e.target.value) || 0 })}
                    className="w-full px-3 py-1.5 text-sm rounded-lg border border-slate-200 bg-white"
                    placeholder="e.g. 2.5 (Marginal: < 2.5, Small: 2.5 - 5)"
                  />
                  <p className="text-[11px] text-slate-500 mt-1">Marginal/small farmers get 100% priority for PM-KISAN & input subsidies.</p>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Section 4: Educational Qualifications & Enrollment */}
        <div className="space-y-4 pt-4 border-t border-slate-100">
          <div className="flex items-center justify-between border-b border-slate-100 pb-2">
            <h2 className="text-sm font-bold uppercase tracking-wider text-slate-800 flex items-center gap-2">
              <GraduationCap className="w-4 h-4 text-purple-600" />
              4. Educational Qualifications & Current Enrollment
            </h2>
            <span className="text-[11px] text-slate-400 font-medium">Universal Qualification & Student Options</span>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">
                Highest Educational Qualification Attained *
              </label>
              <select
                value={profile.highest_qualification || 'Class 12th Passed (Higher Secondary)'}
                onChange={(e) => setProfile({ ...profile, highest_qualification: e.target.value })}
                className="w-full px-3 py-2 text-sm rounded-lg border border-slate-200 bg-white"
              >
                {HIGHEST_QUALIFICATIONS.map((q) => (
                  <option key={q} value={q}>{q}</option>
                ))}
              </select>
              <p className="text-[11px] text-slate-400 mt-1">Applicable to all citizens (farmers, professionals, artisans, and job seekers).</p>
            </div>

            <div className="flex items-center gap-2 p-3 rounded-lg border border-slate-200 bg-purple-50/40">
              <input
                type="checkbox"
                id="is-student"
                checked={isStudent}
                onChange={(e) => setProfile({ ...profile, is_student_currently: e.target.checked })}
                className="w-4 h-4 rounded text-purple-600 focus:ring-purple-500 border-slate-300"
              />
              <label htmlFor="is-student" className="text-xs font-medium text-slate-800 cursor-pointer">
                <strong>Currently studying or enrolled in training?</strong> Enable this to access scholarships, fellowship grants, and higher education benefits.
              </label>
            </div>
          </div>

          {/* Conditional Student Section */}
          {isStudent && (
            <div className="p-4 sm:p-5 rounded-xl border border-purple-200 bg-purple-50/20 space-y-4 mt-2">
              <div className="text-xs font-bold text-purple-900 uppercase tracking-wider flex items-center gap-1.5">
                <GraduationCap className="w-4 h-4 text-purple-700" />
                Active Academic Program & University Details
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-4">
                <div>
                  <label className="block text-xs font-semibold text-slate-700 mb-1">
                    Education Stage
                  </label>
                  <select
                    value={profile.education_level || 'Undergraduate'}
                    onChange={(e) => setProfile({ ...profile, education_level: e.target.value })}
                    className="w-full px-3 py-2 text-sm rounded-lg border border-slate-200 bg-white"
                  >
                    <option value="Class 10">Class 10 (Secondary)</option>
                    <option value="Class 11-12">Class 11 / 12 (Higher Secondary)</option>
                    <option value="Diploma / ITI">Diploma / Polytechnic / ITI</option>
                    <option value="Undergraduate">Undergraduate (B.Tech / B.Sc / BA / MBBS)</option>
                    <option value="Postgraduate">Postgraduate (M.Tech / M.Sc / MBA / MA)</option>
                    <option value="PhD">Doctorate / Ph.D.</option>
                  </select>
                </div>

                <div>
                  <label className="block text-xs font-semibold text-slate-700 mb-1">
                    Course / Degree / Trade (80+ options with auto-suggest)
                  </label>
                  <div className="relative">
                    <input
                      type="text"
                      list="course-options"
                      value={profile.course || ''}
                      onChange={(e) => setProfile({ ...profile, course: e.target.value })}
                      className="w-full px-3 py-2 text-sm rounded-lg border border-slate-200 bg-white focus:outline-hidden focus:ring-2 focus:ring-purple-500/20 focus:border-purple-500"
                      placeholder="Type or select degree / course..."
                    />
                    <datalist id="course-options">
                      {COMMON_COURSES.map((c) => (
                        <option key={c} value={c} />
                      ))}
                    </datalist>
                  </div>
                  <p className="text-[11px] text-slate-400 mt-1">Type to filter degrees or click arrow to choose</p>
                </div>

                <div>
                  <label className="block text-xs font-semibold text-slate-700 mb-1">
                    Year of Study
                  </label>
                  <select
                    value={profile.study_year || 1}
                    onChange={(e) => setProfile({ ...profile, study_year: parseInt(e.target.value) || 1 })}
                    className="w-full px-3 py-2 text-sm rounded-lg border border-slate-200 bg-white"
                  >
                    <option value={1}>1st Year</option>
                    <option value={2}>2nd Year</option>
                    <option value={3}>3rd Year</option>
                    <option value={4}>4th Year</option>
                    <option value={5}>5th Year</option>
                  </select>
                </div>

                <div className="sm:col-span-2 md:col-span-3">
                  <label className="block text-xs font-semibold text-slate-700 mb-1">
                    Educational Institution / University (100+ recognized institutes with auto-suggest)
                  </label>
                  <div className="relative">
                    <input
                      type="text"
                      list="institution-options"
                      value={profile.institution_name || ''}
                      onChange={(e) => setProfile({ ...profile, institution_name: e.target.value })}
                      className="w-full px-3 py-2 text-sm rounded-lg border border-slate-200 bg-white focus:outline-hidden focus:ring-2 focus:ring-purple-500/20 focus:border-purple-500"
                      placeholder="Type or select university / college / institute..."
                    />
                    <datalist id="institution-options">
                      {COMMON_INSTITUTIONS.map((inst) => (
                        <option key={inst} value={inst} />
                      ))}
                    </datalist>
                  </div>
                  <p className="text-[11px] text-slate-400 mt-1">Recognized universities, IITs, NITs, and State colleges (AISHE / UGC accredited)</p>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Action Button */}
        <div className="flex items-center justify-between pt-4 border-t border-slate-100">
          <p className="text-xs text-slate-400">
            All profile information remains private and is only used to evaluate scheme eligibility rules.
          </p>

          <button
            type="submit"
            disabled={saving}
            className="inline-flex items-center gap-2 px-6 py-2.5 rounded-xl bg-blue-600 hover:bg-blue-500 text-white text-sm font-semibold transition-all shadow-sm disabled:opacity-50"
          >
            <Save className="w-4 h-4" />
            {saving ? 'Saving Profile...' : 'Save Citizen Profile'}
          </button>
        </div>
      </form>
    </div>
  );
};
