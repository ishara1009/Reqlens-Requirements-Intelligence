export type User = { id: string; name: string; email: string; created_at: string }
export type Project = { id: string; name: string; description: string; domain: string; status: 'active' | 'archived'; owner_id: string; created_at: string; updated_at: string; document_count: number; finding_count: number }
export type Summary = { total_projects: number; total_documents: number; processed_documents: number; total_findings: number; pending_reviews: number }
export type Document = { id: string; project_id: string; filename: string; file_type: string; document_type: string; version: string; processing_status: string; uploaded_at: string; chunk_count: number; error?: string }
export type Evidence = { document_id: string; filename: string; chunk_id: string; text: string; page_number?: number; section?: string; score?: number }
export type Finding = { id: string; project_id: string; issue_type: string; title: string; explanation: string; confidence: number; grounded: boolean; review_status: string; evidence: Evidence[]; created_at: string; review_comment?: string }
export type ChatResult = { answer: string; thread_id: string; grounded: boolean; evidence: Evidence[]; external_sources: { title: string; url: string; content: string }[]; retrieval_query: string }

