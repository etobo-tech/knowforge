import type { UploadedFile } from '@/lib/documents'

import { UploadRow } from './UploadRow'

type Props = {
  uploads: UploadedFile[]
}

export function UploadRecentList({ uploads }: Props) {
  if (uploads.length === 0) return null

  return (
    <div className="mt-10">
      <h2 className="text-lg font-bold text-text-primary mb-4">Recent uploads</h2>
      <div className="space-y-3">
        {uploads.map((file) => (
          <UploadRow key={file.id} file={file} />
        ))}
      </div>
    </div>
  )
}
