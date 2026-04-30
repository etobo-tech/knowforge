import { afterEach, describe, expect, it, vi } from "vitest";

import { uploadKnowledgeFile } from "@/services/files/file-upload-service";

describe("uploadKnowledgeFile", () => {
  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("throws file_too_large before making the request", async () => {
    const fetchMock = vi.fn();
    vi.stubGlobal("fetch", fetchMock);

    const oversized = new File(["x"], "doc.txt");
    Object.defineProperty(oversized, "size", { value: 3 * 1024 * 1024 });

    await expect(
      uploadKnowledgeFile({ file: oversized, workspaceId: "ws-1" }),
    ).rejects.toThrow("file_too_large");

    expect(fetchMock).not.toHaveBeenCalled();
  });

  it("returns normalized status from successful payload", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue({
        ok: true,
        json: vi.fn().mockResolvedValue({ file_id: "file-1", status: "ready" }),
      }),
    );

    const result = await uploadKnowledgeFile({
      file: new File(["hello"], "doc.txt"),
      workspaceId: "ws-1",
    });

    expect(result).toEqual({ fileId: "file-1", status: "ready" });
  });

  it("throws backend error code when upload fails", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue({
        ok: false,
        json: vi.fn().mockResolvedValue({ error: "unsupported_file_type" }),
      }),
    );

    await expect(
      uploadKnowledgeFile({
        file: new File(["hello"], "doc.pdf"),
        workspaceId: "ws-1",
      }),
    ).rejects.toThrow("unsupported_file_type");
  });
});
