import type { DocumentResponse } from './api'

export type FileStatus = 'processing' | 'indexed' | 'error'

export type UploadedFile = {
  id: string
  name: string
  size: string
  type: string
  status: FileStatus
  /** Set for pending rows (client hash) and completed rows (from API). */
  content_hash?: string | null
  error?: string
}

export function formatShortDate(iso: string): string {
  const d = new Date(iso)
  if (Number.isNaN(d.getTime())) return '—'
  return d.toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
  })
}

export function formatFileSize(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`
}

export function formatDateTime(iso: string | null | undefined): string {
  if (!iso) return '—'
  const d = new Date(iso)
  if (Number.isNaN(d.getTime())) return '—'
  return d.toLocaleString('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
    hour: 'numeric',
    minute: '2-digit',
  })
}

export function mimeToLabel(mimeType: string): string {
  const map: Record<string, string> = {
    'application/pdf': 'PDF',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document':
      'DOCX',
    'text/plain': 'TXT',
    'text/markdown': 'MD',
  }
  return map[mimeType] ?? mimeType.split('/').pop()?.toUpperCase() ?? 'FILE'
}

export function mapDocumentStatus(apiStatus: string): FileStatus {
  if (apiStatus === 'indexed') return 'indexed'
  if (apiStatus === 'failed') return 'error'
  return 'processing'
}

export function documentToUploadedFile(doc: DocumentResponse): UploadedFile {
  return {
    id: doc.id,
    name: doc.filename,
    size: formatFileSize(doc.size_bytes),
    type: mimeToLabel(doc.mime_type),
    status: mapDocumentStatus(doc.status),
    content_hash: doc.content_hash,
  }
}

/** Optimistic row while a local `File` is uploading (pendingId until API returns). */
export function pendingRowFromLocalFile(
  file: File,
  pendingId: string,
  contentHash: string,
): UploadedFile {
  const ext = file.name.split('.').pop()?.toUpperCase()
  return {
    id: pendingId,
    name: file.name,
    size: formatFileSize(file.size),
    type: mimeToLabel(file.type) || ext || 'FILE',
    status: 'processing',
    content_hash: contentHash,
  }
}

export const statusColors: Record<FileStatus, string> = {
  processing: 'bg-warning',
  indexed: 'bg-success',
  error: 'bg-error',
}
