/** Local queue entry before the user confirms upload. */
export type StagedFile = {
  id: string
  file: File
  contentHash: string
}

export type UploadSessionRowPhase = 'queued' | 'uploading' | 'done' | 'error'

/** One row while a batch upload is running or showing its outcome. */
export type UploadSessionRow = {
  id: string
  file: File
  contentHash: string
  phase: UploadSessionRowPhase
  /** Server returned an existing document (not 201). */
  alreadyInDb?: boolean
  /** Skipped: same content already in the recent uploads list. */
  duplicateInList?: boolean
  errorMessage?: string
}

export function uploadSessionRowsFromStaged(
  staged: StagedFile[],
): UploadSessionRow[] {
  return staged.map((s) => ({
    id: s.id,
    file: s.file,
    contentHash: s.contentHash,
    phase: 'queued',
  }))
}
