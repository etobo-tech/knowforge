import { afterEach, describe, expect, it, vi } from "vitest";

import {
  getKnowledgeFileStatus,
  waitForKnowledgeFileStatus,
} from "@/services/files/file-status-service";

describe("file-status-service", () => {
  afterEach(() => {
    vi.unstubAllGlobals();
    vi.useRealTimers();
  });

  it("normalizes successful status payload", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue({
        ok: true,
        json: vi.fn().mockResolvedValue({ file_id: "file-1", status: "ready" }),
      }),
    );

    const result = await getKnowledgeFileStatus("file-1");
    expect(result).toEqual({ fileId: "file-1", status: "ready" });
  });

  it("throws when status request fails", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue({
        ok: false,
      }),
    );

    await expect(getKnowledgeFileStatus("file-2")).rejects.toThrow("file_status_failed");
  });

  it("waitForKnowledgeFileStatus stops once terminal status is reached", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn()
        .mockResolvedValueOnce({
          ok: true,
          json: vi.fn().mockResolvedValue({ file_id: "file-3", status: "processing" }),
        })
        .mockResolvedValueOnce({
          ok: true,
          json: vi.fn().mockResolvedValue({ file_id: "file-3", status: "ready" }),
        }),
    );
    vi.useFakeTimers();

    const pending = waitForKnowledgeFileStatus({
      fileId: "file-3",
      maxAttempts: 4,
      intervalMs: 10,
    });
    await vi.advanceTimersByTimeAsync(10);
    const result = await pending;

    expect(result).toEqual({ fileId: "file-3", status: "ready" });
  });
});
