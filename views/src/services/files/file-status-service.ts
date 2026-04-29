import type { FileProcessingStatus } from "@/services/files/file-upload-service";

type FileStatusResult = {
  fileId: string;
  status: FileProcessingStatus;
};

function normalizeStatus(value: string | undefined): FileProcessingStatus {
  if (
    value === "pending" ||
    value === "processing" ||
    value === "ready" ||
    value === "failed" ||
    value === "not_found"
  ) {
    return value;
  }

  return "unknown";
}

async function sleep(ms: number): Promise<void> {
  await new Promise((resolve) => setTimeout(resolve, ms));
}

export async function getKnowledgeFileStatus(fileId: string): Promise<FileStatusResult> {
  const response = await fetch(`/api/files/${fileId}/status`, { method: "GET" });
  if (!response.ok) {
    throw new Error("file_status_failed");
  }

  const payload = (await response.json()) as {
    file_id?: string;
    status?: string;
  };

  return {
    fileId: payload.file_id ?? fileId,
    status: normalizeStatus(payload.status),
  };
}

export async function waitForKnowledgeFileStatus({
  fileId,
  maxAttempts = 4,
  intervalMs = 1000,
}: {
  fileId: string;
  maxAttempts?: number;
  intervalMs?: number;
}): Promise<FileStatusResult> {
  let latest = await getKnowledgeFileStatus(fileId);

  for (let attempt = 1; attempt < maxAttempts; attempt += 1) {
    if (latest.status === "ready" || latest.status === "failed" || latest.status === "not_found") {
      return latest;
    }
    await sleep(intervalMs);
    latest = await getKnowledgeFileStatus(fileId);
  }

  return latest;
}
