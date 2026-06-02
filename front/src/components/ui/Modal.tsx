'use client'

import { useEffect, useId, type ReactNode } from 'react'
import { Loader2, X } from 'lucide-react'

type ModalProps = {
  open: boolean
  onClose: () => void
  title: string
  children: ReactNode
  footer?: ReactNode
  disableClose?: boolean
}

export function Modal({
  open,
  onClose,
  title,
  children,
  footer,
  disableClose = false,
}: ModalProps) {
  const titleId = useId()

  useEffect(() => {
    if (!open || disableClose) return

    const onKeyDown = (event: KeyboardEvent) => {
      if (event.key === 'Escape') onClose()
    }

    window.addEventListener('keydown', onKeyDown)
    return () => window.removeEventListener('keydown', onKeyDown)
  }, [open, disableClose, onClose])

  if (!open) return null

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      <button
        type="button"
        aria-label="Close dialog"
        disabled={disableClose}
        onClick={onClose}
        className="absolute inset-0 bg-overlay disabled:cursor-not-allowed"
      />
      <div
        role="dialog"
        aria-modal="true"
        aria-labelledby={titleId}
        className="relative z-10 w-full max-w-md rounded-2xl border border-card-border bg-card-bg shadow-xl"
      >
        <div className="flex items-start justify-between gap-4 border-b border-card-border px-5 py-4">
          <h2 id={titleId} className="text-lg font-semibold text-text-primary">
            {title}
          </h2>
          <button
            type="button"
            onClick={onClose}
            disabled={disableClose}
            className="rounded-md p-1 text-text-secondary hover:text-text-primary disabled:opacity-50"
            aria-label="Close"
          >
            <X size={18} />
          </button>
        </div>
        <div className="px-5 py-4 text-sm text-text-secondary">{children}</div>
        {footer ? (
          <div className="flex justify-end gap-2 border-t border-card-border px-5 py-4">
            {footer}
          </div>
        ) : null}
      </div>
    </div>
  )
}

type ConfirmModalProps = {
  open: boolean
  onClose: () => void
  onConfirm: () => void | Promise<void>
  title: string
  description: ReactNode
  confirmLabel?: string
  cancelLabel?: string
  confirmVariant?: 'primary' | 'danger'
  isLoading?: boolean
}

export function ConfirmModal({
  open,
  onClose,
  onConfirm,
  title,
  description,
  confirmLabel = 'Confirm',
  cancelLabel = 'Cancel',
  confirmVariant = 'primary',
  isLoading = false,
}: ConfirmModalProps) {
  const confirmClassName =
    confirmVariant === 'danger'
      ? 'bg-error hover:bg-error/90 text-white'
      : 'bg-primary hover:bg-primary-hover text-white'

  return (
    <Modal
      open={open}
      onClose={onClose}
      title={title}
      disableClose={isLoading}
      footer={
        <>
          <button
            type="button"
            onClick={onClose}
            disabled={isLoading}
            className="rounded-lg border border-card-border px-4 py-2 text-sm font-medium text-text-primary hover:bg-content-bg disabled:opacity-50"
          >
            {cancelLabel}
          </button>
          <button
            type="button"
            onClick={() => void onConfirm()}
            disabled={isLoading}
            className={`inline-flex items-center justify-center gap-2 rounded-lg px-4 py-2 text-sm font-medium transition-colors disabled:opacity-50 ${confirmClassName}`}
          >
            {isLoading ? <Loader2 size={16} className="animate-spin" /> : null}
            {confirmLabel}
          </button>
        </>
      }
    >
      {description}
    </Modal>
  )
}
