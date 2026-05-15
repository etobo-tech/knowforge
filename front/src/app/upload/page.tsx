'use client'

import { useDocumentUpload } from '@/hooks/useDocumentUpload'

import { UploadDropzone } from './UploadDropzone'
import { UploadPageHeader } from './UploadPageHeader'
import { UploadRecentList } from './UploadRecentList'

export default function UploadPage() {
  const { uploads, isUploading, uploadFiles } = useDocumentUpload()

  return (
    <div className="h-full flex flex-col">
      <UploadPageHeader />
      <div className="flex-1 p-8 overflow-y-auto">
        <UploadDropzone
          isUploading={isUploading}
          onFilesSelected={(files) => void uploadFiles(files)}
        />
        <UploadRecentList uploads={uploads} />
      </div>
    </div>
  )
}
