export function mapUploadErrorToMessage(error: unknown): string {
  const errorCode = error instanceof Error ? error.message : "";

  if (errorCode === "unsupported_file_type") {
    return "Only .txt and .md files are supported right now.";
  }

  if (errorCode === "filename_required") {
    return "Please select a valid file before uploading.";
  }

  if (errorCode === "upload_upstream_not_configured") {
    return "Upload service is not configured yet. Please try again later.";
  }

  return "File upload failed. Please try again.";
}
