export type FileUploadResult = {
  fileId: string;
  status: "pending" | "processing" | "ready" | "failed" | "not_found" | "unknown";
};

export async function uploadKnowledgeFile({
  file,
  workspaceId,
}: {
  file: File;
  workspaceId: string;
}): Promise<FileUploadResult> {
  const formData = new FormData();
  formData.set("workspace_id", workspaceId);
  formData.set("uploaded_file", file);

  const response = await fetch("/api/files/upload", {
    method: "POST",
    body: formData,
  });

  if (!response.ok) {
    throw new Error("file_upload_failed");
  }

  const payload = (await response.json()) as {
    file_id?: string;
    status?: string;
  };

  return {
    fileId: payload.file_id ?? "",
    status:
      payload.status === "pending" ||
      payload.status === "processing" ||
      payload.status === "ready" ||
      payload.status === "failed" ||
      payload.status === "not_found"
        ? payload.status
        : "unknown",
  };
}
