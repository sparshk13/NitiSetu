-- ====================================================================
-- CivicPilot Supabase PostgreSQL Schema & Security Policies
-- CivicPilot Supabase Relational & Vector Schema
-- ====================================================================

-- 1. Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";
CREATE EXTENSION IF NOT EXISTS "vector";

-- 2. Profiles Table
CREATE TABLE IF NOT EXISTS public.profiles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    full_name TEXT,
    state_code TEXT,
    education_level TEXT,
    course TEXT,
    study_year INTEGER,
    institution_name TEXT,
    annual_family_income NUMERIC(12, 2),
    caste_category TEXT,
    gender TEXT,
    is_differently_abled BOOLEAN DEFAULT false,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- 3. Schemes Master Table
CREATE TABLE IF NOT EXISTS public.schemes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    slug TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    summary TEXT,
    description TEXT,
    scheme_type TEXT NOT NULL DEFAULT 'scholarship',
    state_code TEXT,
    central_or_state TEXT NOT NULL DEFAULT 'Central Government',
    benefit_summary TEXT,
    official_url TEXT NOT NULL,
    application_url TEXT,
    deadline DATE,
    status TEXT NOT NULL DEFAULT 'active',
    last_verified_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- 4. Structured Scheme Rules Table
CREATE TABLE IF NOT EXISTS public.scheme_rules (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    scheme_id UUID NOT NULL REFERENCES public.schemes(id) ON DELETE CASCADE,
    rule_key TEXT NOT NULL,
    operator TEXT NOT NULL, -- 'eq', 'neq', 'lt', 'lte', 'gt', 'gte', 'in', 'not_in'
    expected_value JSONB NOT NULL,
    required BOOLEAN NOT NULL DEFAULT true,
    source_section TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- 5. Source Policy Documents Table
CREATE TABLE IF NOT EXISTS public.source_documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    scheme_id UUID REFERENCES public.schemes(id) ON DELETE SET NULL,
    title TEXT NOT NULL,
    source_url TEXT,
    storage_path TEXT,
    document_type TEXT NOT NULL DEFAULT 'guideline',
    last_verified_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    content_hash TEXT,
    processing_status TEXT NOT NULL DEFAULT 'completed',
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- 6. Document Chunks & pgvector Embeddings Table
CREATE TABLE IF NOT EXISTS public.document_chunks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    source_document_id UUID NOT NULL REFERENCES public.source_documents(id) ON DELETE CASCADE,
    scheme_id UUID REFERENCES public.schemes(id) ON DELETE CASCADE,
    chunk_index INTEGER NOT NULL,
    content TEXT NOT NULL,
    page_number INTEGER,
    section_title TEXT,
    embedding vector(768),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT uq_doc_chunk UNIQUE(source_document_id, chunk_index)
);

-- 7. User Uploaded Documents Table
CREATE TABLE IF NOT EXISTS public.user_documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    storage_path TEXT NOT NULL,
    original_filename TEXT NOT NULL,
    detected_type TEXT,
    file_size INTEGER NOT NULL,
    processing_status TEXT NOT NULL DEFAULT 'pending',
    extracted_fields JSONB,
    user_confirmed_fields JSONB,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- 8. Application Drafts Table
CREATE TABLE IF NOT EXISTS public.application_drafts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    scheme_id UUID NOT NULL REFERENCES public.schemes(id) ON DELETE CASCADE,
    status TEXT NOT NULL DEFAULT 'draft',
    form_data JSONB NOT NULL DEFAULT '{}'::jsonb,
    automation_log JSONB,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Indexes for high-performance querying
CREATE INDEX IF NOT EXISTS idx_schemes_slug ON public.schemes(slug);
CREATE INDEX IF NOT EXISTS idx_schemes_state_type ON public.schemes(state_code, scheme_type);
CREATE INDEX IF NOT EXISTS idx_scheme_rules_scheme_id ON public.scheme_rules(scheme_id);
CREATE INDEX IF NOT EXISTS idx_document_chunks_scheme_id ON public.document_chunks(scheme_id);
CREATE INDEX IF NOT EXISTS idx_user_documents_user_id ON public.user_documents(user_id);
CREATE INDEX IF NOT EXISTS idx_app_drafts_user_scheme ON public.application_drafts(user_id, scheme_id);

-- Vector Cosine Similarity Index (IVFFlat or HNSW)
CREATE INDEX IF NOT EXISTS idx_document_chunks_embedding
    ON public.document_chunks USING hnsw (embedding vector_cosine_ops);

-- Row Level Security (RLS)
ALTER TABLE public.profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.user_documents ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.application_drafts ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.schemes ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.scheme_rules ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.source_documents ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.document_chunks ENABLE ROW LEVEL SECURITY;

-- Public read access for schemes and policy guidelines
DROP POLICY IF EXISTS "Public schemes are viewable by everyone" ON public.schemes;
CREATE POLICY "Public schemes are viewable by everyone" ON public.schemes
    FOR SELECT USING (true);

DROP POLICY IF EXISTS "Public scheme rules are viewable by everyone" ON public.scheme_rules;
CREATE POLICY "Public scheme rules are viewable by everyone" ON public.scheme_rules
    FOR SELECT USING (true);

DROP POLICY IF EXISTS "Public source documents are viewable by everyone" ON public.source_documents;
CREATE POLICY "Public source documents are viewable by everyone" ON public.source_documents
    FOR SELECT USING (true);

DROP POLICY IF EXISTS "Public document chunks are viewable by everyone" ON public.document_chunks;
CREATE POLICY "Public document chunks are viewable by everyone" ON public.document_chunks
    FOR SELECT USING (true);

-- User-specific access for profiles, uploaded docs, and application drafts
DROP POLICY IF EXISTS "Users can access own profile" ON public.profiles;
CREATE POLICY "Users can access own profile" ON public.profiles
    FOR ALL USING (auth.uid() = id);

DROP POLICY IF EXISTS "Users can access own documents" ON public.user_documents;
CREATE POLICY "Users can access own documents" ON public.user_documents
    FOR ALL USING (auth.uid() = user_id);

DROP POLICY IF EXISTS "Users can access own application drafts" ON public.application_drafts;
CREATE POLICY "Users can access own application drafts" ON public.application_drafts
    FOR ALL USING (auth.uid() = user_id);

