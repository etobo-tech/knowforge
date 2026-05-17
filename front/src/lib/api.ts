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

export type MessageResponse = {
  id: string
  role: string
  content: string
  created_at: string
  sources: unknown[]
}

export type ChatDetailResponse = {
  id: string
  title: string
  created_at: string
  updated_at: string
  messages: MessageResponse[]
}

/** e.g. `2026-05-16 14:30-New chat` */
export function formatNewChatTitle(now: Date = new Date()): string {
  const pad = (n: number) => String(n).padStart(2, '0')
  const y = now.getFullYear()
  const mo = pad(now.getMonth() + 1)
  const d = pad(now.getDate())
  const h = pad(now.getHours())
  const min = pad(now.getMinutes())
  return `${y}-${mo}-${d} ${h}:${min}-New chat`
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

export async function getChat(chatId: string): Promise<ChatDetailResponse | null> {
  const response = await fetch(
    `${API_BASE}/api/chats/${encodeURIComponent(chatId)}`,
    { cache: 'no-store' },
  )
  if (response.status === 404) return null
  if (!response.ok) {
    const detail = await parseJsonError(response)
    throw new Error(detail ?? `Failed to load chat (${response.status})`)
  }
  return (await response.json()) as ChatDetailResponse
}

export async function createChat(title: string): Promise<ChatDetailResponse> {
  const response = await fetch(`${API_BASE}/api/chats`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ title }),
    cache: 'no-store',
  })
  if (!response.ok) {
    const detail = await parseJsonError(response)
    throw new Error(detail ?? `Failed to create chat (${response.status})`)
  }
  return (await response.json()) as ChatDetailResponse
}

export async function appendChatMessage(
  chatId: string,
  content: string,
): Promise<ChatDetailResponse> {
  const response = await fetch(
    `${API_BASE}/api/chats/${encodeURIComponent(chatId)}/messages`,
    {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ content }),
      cache: 'no-store',
    },
  )
  if (!response.ok) {
    const detail = await parseJsonError(response)
    throw new Error(detail ?? `Failed to send message (${response.status})`)
  }
  return (await response.json()) as ChatDetailResponse
}