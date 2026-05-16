'use client'

import { useDocumentUpload } from '@/hooks/useDocumentUpload'

import { StagedFilesPanel } from './StagedFilesPanel'
import { UploadSessionPanel } from './UploadSessionPanel'
import { UploadDropzone } from './UploadDropzone'
import { UploadNoticeBanner } from './UploadNoticeBanner'
import { UploadPageHeader } from './UploadPageHeader'

export default function UploadPage() {
  const {
    stagedFiles,
    uploadSessionRows,
    isUploading,
    uploadNotice,
    addStagedFiles,
    removeStaged,
    clearStaged,
    commitStaged,
    dismissUploadSession,
  } = useDocumentUpload()

  return (
    <div className="h-full flex flex-col">
      <UploadPageHeader />
      <div className="flex-1 p-8 overflow-y-auto">
        <UploadNoticeBanner message={uploadNotice} />
        <UploadDropzone
          disabled={isUploading}
          onFilesQueued={(files) => void addStagedFiles(files)}
        />
        <StagedFilesPanel
          staged={stagedFiles}
          isUploading={isUploading}
          onRemove={removeStaged}
          onUpload={() => void commitStaged()}
          onCancelAll={clearStaged}
        />
        <UploadSessionPanel
          rows={uploadSessionRows}
          isUploading={isUploading}
          onDismiss={dismissUploadSession}
        />
      </div>
    </div>
  )
}
