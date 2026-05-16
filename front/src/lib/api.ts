export type DocumentResponse = {
  id: string
  filename: string
  mime_type: string
  size_bytes: number
  status: string
  chunks_count: number
  content_hash: string | null
  created_at: string
}

const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:8000'

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
