import { statusColors, type UploadedFile } from '@/lib/documents'

type Props = {
  file: UploadedFile
}

export function UploadRow({ file }: Props) {
  return (
    <div className="flex items-center justify-between px-6 py-4 bg-card-bg border border-card-border rounded-xl">
      <div>
        <p className="text-sm font-semibold text-text-primary">{file.name}</p>
        <p className="text-xs text-text-secondary mt-0.5">
          {file.size} &middot; {file.type}
          {file.error && (
            <span className="text-error"> &middot; {file.error}</span>
          )}
        </p>
      </div>
      <span
        className={`w-14 h-6 rounded-full shrink-0 ${statusColors[file.status]}`}
        title={file.status}
      />
    </div>
  )
}
