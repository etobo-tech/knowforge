'use client'

import { useEffect, useId } from 'react'
import { Download, Loader2, Trash2, X } from 'lucide-react'

type Props = {
  open: boolean
  filename: string
  previewUrl: string
  downloadUrl: string | null
  onClose: () => void
  onDelete?: () => void
  isDeleting?: boolean
}

export function ImagePreviewDialog({
  open,
  filename,
  previewUrl,
  downloadUrl,
  onClose,
  onDelete,
  isDeleting = false,
}: Props) {
  const titleId = useId()

  useEffect(() => {
    if (!open) return

    const onKeyDown = (event: KeyboardEvent) => {
      if (event.key === 'Escape') onClose()
    }

    window.addEventListener('keydown', onKeyDown)
    return () => window.removeEventListener('keydown', onKeyDown)
  }, [open, onClose])

  if (!open) return null

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 md:p-8">
      <button
        type="button"
        aria-label="Close preview"
        onClick={onClose}
        className="absolute inset-0 bg-black/60"
      />
      <div
        role="dialog"
        aria-modal="true"
        aria-labelledby={titleId}
        className="relative z-10 flex max-h-[90vh] w-full max-w-5xl flex-col overflow-hidden rounded-2xl border border-card-border bg-white shadow-xl"
      >
        <div className="flex items-center gap-3 border-b border-card-border px-5 py-3">
          <h2
            id={titleId}
            className="min-w-0 flex-1 truncate text-sm font-semibold text-text-primary"
          >
            {filename}
          </h2>
          <div className="flex shrink-0 items-center gap-2">
            {downloadUrl ? (
              <a
                href={downloadUrl}
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center gap-1.5 rounded-lg border border-card-border px-3 py-1.5 text-xs font-medium text-primary hover:bg-primary/5 transition-colors"
              >
                <Download size={14} aria-hidden />
                Download
              </a>
            ) : null}
            {onDelete ? (
              <button
                type="button"
                onClick={() => void onDelete()}
                disabled={isDeleting}
                className="inline-flex items-center gap-1.5 rounded-lg border border-card-border px-3 py-1.5 text-xs font-medium text-error hover:bg-error/5 transition-colors disabled:opacity-50"
              >
                {isDeleting ? (
                  <Loader2 size={14} className="animate-spin" aria-hidden />
                ) : (
                  <Trash2 size={14} aria-hidden />
                )}
                {isDeleting ? 'Deleting…' : 'Delete'}
              </button>
            ) : null}
            <button
              type="button"
              onClick={onClose}
              disabled={isDeleting}
              className="rounded-md p-1 text-text-secondary hover:text-text-primary disabled:opacity-50"
              aria-label="Close"
            >
              <X size={20} />
            </button>
          </div>
        </div>
        <div className="flex min-h-0 flex-1 items-center justify-center bg-content-bg p-4">
          {/* eslint-disable-next-line @next/next/no-img-element */}
          <img
            src={previewUrl}
            alt={filename}
            className="max-h-[calc(90vh-5rem)] max-w-full object-contain"
          />
        </div>
      </div>
    </div>
  )
}
