import { useCallback, useState } from 'react'

import { uploadDocument } from '@/lib/api'
import {
  documentToUploadedFile,
  pendingRowFromLocalFile,
  type UploadedFile,
} from '@/lib/documents'

export function useDocumentUpload() {
  const [uploads, setUploads] = useState<UploadedFile[]>([])
  const [isUploading, setIsUploading] = useState(false)

  const uploadFiles = useCallback(async (fileList: FileList | File[]) => {
    const files = Array.from(fileList)
    if (files.length === 0) return

    setIsUploading(true)

    for (const file of files) {
      const pendingId = crypto.randomUUID()
      const pending = pendingRowFromLocalFile(file, pendingId)
      setUploads((prev) => [pending, ...prev])

      try {
        const { document } = await uploadDocument(file)
        const done = documentToUploadedFile(document)
        setUploads((prev) =>
          prev.map((row) => (row.id === pendingId ? done : row)),
        )
      } catch (err) {
        const message = err instanceof Error ? err.message : 'Upload failed'
        setUploads((prev) =>
          prev.map((row) =>
            row.id === pendingId
              ? { ...row, status: 'error', error: message }
              : row,
          ),
        )
      }
    }

    setIsUploading(false)
  }, [])

  return { uploads, isUploading, uploadFiles }
}
