import { getMaxUploadBytes } from "@/config/upload-limits";

export type FileProcessingStatus =
  | "pending"
  | "processing"
  | "ready"
  | "failed"
  | "not_found"
  | "unknown";

export type FileUploadResult = {
  fileId: string;
  status: FileProcessingStatus;
};

export async function uploadKnowledgeFile({
  file,
  workspaceId,
}: {
  file: File;
  workspaceId: string;
}): Promise<FileUploadResult> {
  if (file.size > getMaxUploadBytes()) {
    throw new Error("file_too_large");
  }

  const formData = new FormData();
  formData.set("workspace_id", workspaceId);
  formData.set("uploaded_file", file);

  const response = await fetch("/api/files/upload", {
    method: "POST",
    body: formData,
  });

  if (!response.ok) {
    const payload = (await response.json().catch(() => ({}))) as {
      error?: string;
      detail?: string;
    };
    throw new Error(payload.error ?? payload.detail ?? "file_upload_failed");
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
