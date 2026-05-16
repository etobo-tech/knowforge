import { formatFileSize, mimeToLabel } from '@/lib/documents'
import type { StagedFile } from '@/lib/uploadQueue'

type Props = {
  staged: StagedFile[]
  isUploading: boolean
  onRemove: (id: string) => void
  onUpload: () => void
  onCancelAll: () => void
}

export function StagedFilesPanel({
  staged,
  isUploading,
  onRemove,
  onUpload,
  onCancelAll,
}: Props) {
  if (staged.length === 0) return null

  return (
    <div className="mt-8 rounded-2xl border border-card-border bg-card-bg p-6">
      <div className="flex items-center justify-between gap-4 mb-4">
        <h2 className="text-lg font-bold text-text-primary">
          Ready to upload ({staged.length})
        </h2>
        <div className="flex flex-wrap items-center justify-end gap-2">
          <button
            type="button"
            disabled={isUploading}
            onClick={onCancelAll}
            className="rounded-lg border border-card-border bg-white px-4 py-2 text-sm font-medium text-text-primary hover:bg-content-bg disabled:opacity-50"
          >
            Cancel all
          </button>
          <button
            type="button"
            disabled={isUploading}
            onClick={() => void onUpload()}
            className="rounded-lg bg-primary px-4 py-2 text-sm font-medium text-white hover:bg-primary-hover disabled:opacity-50"
          >
            {isUploading ? 'Uploading…' : 'Upload'}
          </button>
        </div>
      </div>
      <ul className="space-y-2">
        {staged.map((entry) => (
          <li
            key={entry.id}
            className="flex items-center justify-between gap-3 rounded-xl border border-card-border bg-white px-4 py-3"
          >
            <div className="min-w-0 flex-1">
              <p className="truncate text-sm font-medium text-text-primary">
                {entry.file.name}
              </p>
              <p className="text-xs text-text-secondary">
                {formatFileSize(entry.file.size)} &middot;{' '}
                {mimeToLabel(entry.file.type) ||
                  entry.file.name.split('.').pop()?.toUpperCase() ||
                  'FILE'}
              </p>
            </div>
            <button
              type="button"
              disabled={isUploading}
              onClick={() => onRemove(entry.id)}
              className="shrink-0 rounded-lg px-3 py-1.5 text-sm text-text-secondary hover:bg-content-bg hover:text-text-primary disabled:opacity-50"
            >
              Remove
            </button>
          </li>
        ))}
      </ul>
    </div>
  )
}
