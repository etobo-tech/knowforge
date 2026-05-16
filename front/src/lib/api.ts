export type DocumentResponse = {
  id: string
  filename: string
  mime_type: string
  size_bytes: number
  status: string
  chunks_count: number
  content_hash: string | null
  created_at: string
  indexed_at?: string | null
}

const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:8000'

async function parseJsonError(response: Response): Promise<string | null> {
  const body = (await response.json().catch(() => null)) as {
    detail?: string | unknown
  } | null
  if (!body?.detail) return null
  if (typeof body.detail === 'string') return body.detail
  return null
}

export async function listDocuments(): Promise<DocumentResponse[]> {
  const response = await fetch(`${API_BASE}/api/documents`, {
    cache: 'no-store',
  })
  if (!response.ok) {
    const detail = await parseJsonError(response)
    throw new Error(detail ?? `Failed to list documents (${response.status})`)
  }
  return (await response.json()) as DocumentResponse[]
}

/** API responds 302 → S3 presigned URL. Use as `<a href>` (optionally `target="_blank"`). */
export function documentDownloadHref(documentId: string): string {
  return `${API_BASE}/api/documents/${encodeURIComponent(documentId)}/download`
}

export async function deleteDocument(id: string): Promise<void> {
  const response = await fetch(
    `${API_BASE}/api/documents/${encodeURIComponent(id)}`,
    { method: 'DELETE' },
  )
  if (response.status === 204) return
  if (response.status === 404) {
    throw new Error('Document not found')
  }
  const detail = await parseJsonError(response)
  throw new Error(detail ?? `Delete failed (${response.status})`)
}

export async function uploadDocument(
  file: File,
): Promise<{ document: DocumentResponse; created: boolean }> {
  const formData = new FormData()
  formData.append('file', file)

  const response = await fetch(`${API_BASE}/api/documents/upload`, {
    method: 'POST',
    body: formData,
  })

  if (!response.ok) {
    const body = (await response.json().catch(() => null)) as {
      detail?: string
    } | null
    throw new Error(body?.detail ?? `Upload failed (${response.status})`)
  }

  return {
    document: (await response.json()) as DocumentResponse,
    created: response.status === 201,
  }
}
