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

export type ChatSummaryResponse = {
  id: string
  title: string
  created_at: string
  updated_at: string
}

export type ChatDetailResponse = {
  id: string
  title: string
  created_at: string
  updated_at: string
  messages: MessageResponse[]
}

import {
  getCachedChat,
  getCachedChatList,
  invalidateChatListCache,
  setCachedChat,
  setCachedChatList,
} from '@/lib/chatCache'

export { getCachedChat, getCachedChatList } from '@/lib/chatCache'

export const CHATS_UPDATED_EVENT = 'knowforge:chats-updated'

export function notifyChatsUpdated(): void {
  invalidateChatListCache()
  window.dispatchEvent(new Event(CHATS_UPDATED_EVENT))
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

export async function listChats(options?: {
  force?: boolean
}): Promise<ChatSummaryResponse[]> {
  if (!options?.force) {
    const cached = getCachedChatList()
    if (cached) return cached
  }

  const response = await fetch(`${API_BASE}/api/chats`, { cache: 'no-store' })
  if (!response.ok) {
    const detail = await parseJsonError(response)
    throw new Error(detail ?? `Failed to list chats (${response.status})`)
  }
  const items = (await response.json()) as ChatSummaryResponse[]
  setCachedChatList(items)
  return items
}

export async function getChat(
  chatId: string,
  options?: { force?: boolean },
): Promise<ChatDetailResponse | null> {
  if (!options?.force) {
    const cached = getCachedChat(chatId)
    if (cached) return cached
  }

  const response = await fetch(
    `${API_BASE}/api/chats/${encodeURIComponent(chatId)}`,
    { cache: 'no-store' },
  )
  if (response.status === 404) return null
  if (!response.ok) {
    const detail = await parseJsonError(response)
    throw new Error(detail ?? `Failed to load chat (${response.status})`)
  }
  const chat = (await response.json()) as ChatDetailResponse
  setCachedChat(chat)
  return chat
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
  const chat = (await response.json()) as ChatDetailResponse
  setCachedChat(chat)
  invalidateChatListCache()
  return chat
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
  const chat = (await response.json()) as ChatDetailResponse
  setCachedChat(chat)
  invalidateChatListCache()
  return chat
}

function messagesKeptAfterDeletion(
  messages: MessageResponse[],
  messageId: string,
): MessageResponse[] {
  const target = messages.find((message) => message.id === messageId)
  if (!target) {
    return messages.filter((message) => message.id !== messageId)
  }

  const cutoff = new Date(target.created_at).getTime()
  return messages.filter(
    (message) => new Date(message.created_at).getTime() < cutoff,
  )
}

/** Matches backend truncation: prior turns + edited user message only. */
export function truncateMessagesForEdit(
  messages: MessageResponse[],
  messageId: string,
  newContent: string,
): MessageResponse[] {
  const target = messages.find((message) => message.id === messageId)
  if (!target) return messages

  const cutoff = new Date(target.created_at).getTime()
  return messages
    .filter((message) => {
      const messageTime = new Date(message.created_at).getTime()
      return messageTime < cutoff || message.id === messageId
    })
    .map((message) =>
      message.id === messageId ? { ...message, content: newContent } : message,
    )
}

export async function deleteChatMessage(
  chatId: string,
  messageId: string,
): Promise<void> {
  const response = await fetch(
    `${API_BASE}/api/chats/${encodeURIComponent(chatId)}/messages/${encodeURIComponent(messageId)}`,
    { method: 'DELETE', cache: 'no-store' },
  )
  if (response.status === 204) {
    const cached = getCachedChat(chatId)
    if (cached) {
      setCachedChat({
        ...cached,
        messages: messagesKeptAfterDeletion(cached.messages, messageId),
      })
    }
    invalidateChatListCache()
    return
  }
  if (response.status === 404) {
    throw new Error('Message not found')
  }
  const detail = await parseJsonError(response)
  throw new Error(detail ?? `Failed to delete message (${response.status})`)
}

export async function updateChatMessage(
  chatId: string,
  messageId: string,
  content: string,
): Promise<ChatDetailResponse> {
  const response = await fetch(
    `${API_BASE}/api/chats/${encodeURIComponent(chatId)}/messages/${encodeURIComponent(messageId)}`,
    {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ content }),
      cache: 'no-store',
    },
  )
  if (!response.ok) {
    const detail = await parseJsonError(response)
    throw new Error(detail ?? `Failed to update message (${response.status})`)
  }
  const chat = (await response.json()) as ChatDetailResponse
  setCachedChat(chat)
  invalidateChatListCache()
  return chat
}
