import { AlertCircle, Check, Loader2 } from 'lucide-react'

import { formatFileSize, mimeToLabel } from '@/lib/documents'
import type { UploadSessionRow } from '@/lib/uploadQueue'

type Props = {
  rows: UploadSessionRow[]
  isUploading: boolean
  onDismiss: () => void
}

export function UploadSessionPanel({
  rows,
  isUploading,
  onDismiss,
}: Props) {
  if (rows.length === 0) return null

  const allFinished = rows.every(
    (r) => r.phase === 'done' || r.phase === 'error',
  )

  return (
    <div className="mt-8 rounded-2xl border border-card-border bg-card-bg p-6">
      <div className="flex items-center justify-between gap-4 mb-4">
        <h2 className="text-lg font-bold text-text-primary">
          {isUploading ? 'Uploading…' : 'Upload results'}
        </h2>
        {allFinished ? (
          <button
            type="button"
            onClick={onDismiss}
            className="rounded-lg border border-card-border bg-card-bg px-4 py-2 text-sm font-medium text-text-primary hover:bg-content-bg"
          >
            Dismiss
          </button>
        ) : null}
      </div>
      <ul className="space-y-2">
        {rows.map((row) => (
          <li
            key={row.id}
            className="flex items-start justify-between gap-3 rounded-xl border border-card-border bg-content-bg px-4 py-3"
          >
            <div className="min-w-0 flex-1">
              <p className="truncate text-sm font-medium text-text-primary">
                {row.file.name}
              </p>
              <p className="text-xs text-text-secondary">
                {formatFileSize(row.file.size)} &middot;{' '}
                {mimeToLabel(row.file.type) ||
                  row.file.name.split('.').pop()?.toUpperCase() ||
                  'FILE'}
              </p>
              {row.phase === 'done' && row.alreadyInDb ? (
                <p className="mt-2 text-xs font-medium text-warning">
                  This document already existed in the knowledge base.
                </p>
              ) : null}
              {row.phase === 'done' && row.duplicateInList ? (
                <p className="mt-2 text-xs font-medium text-warning">
                  This file was already uploaded in this session — skipped.
                </p>
              ) : null}
              {row.phase === 'error' && row.errorMessage ? (
                <p className="mt-2 text-xs font-medium text-error">
                  {row.errorMessage}
                </p>
              ) : null}
            </div>
            <div className="flex h-9 min-w-[5.5rem] shrink-0 items-center justify-end">
              {row.phase === 'queued' ? (
                <span className="text-xs text-text-secondary">Queued</span>
              ) : null}
              {row.phase === 'uploading' ? (
                <Loader2
                  className="h-6 w-6 shrink-0 animate-spin text-primary"
                  aria-label="Uploading"
                />
              ) : null}
              {row.phase === 'done' &&
              !row.alreadyInDb &&
              !row.duplicateInList ? (
                <Check
                  className="h-6 w-6 shrink-0 text-success"
                  aria-label="Uploaded"
                />
              ) : null}
              {row.phase === 'done' &&
              (row.alreadyInDb || row.duplicateInList) ? (
                <span
                  className="text-lg leading-none text-warning"
                  aria-label="Notice"
                >
                  !
                </span>
              ) : null}
              {row.phase === 'error' ? (
                <AlertCircle
                  className="h-6 w-6 shrink-0 text-error"
                  aria-label="Error"
                />
              ) : null}
            </div>
          </li>
        ))}
      </ul>
    </div>
  )
}
