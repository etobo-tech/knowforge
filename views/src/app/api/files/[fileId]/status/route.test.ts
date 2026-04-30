import { afterEach, describe, expect, it, vi } from "vitest";

import { GET } from "@/app/api/files/[fileId]/status/route";

describe("app/api/files/[fileId]/status GET", () => {
  afterEach(() => {
    vi.unstubAllGlobals();
    delete process.env.CHAT_API_BASE_URL;
  });

  it("rejects empty file id", async () => {
    const response = await GET(new Request("http://localhost"), {
      params: Promise.resolve({ fileId: " " }),
    });
    expect(response.status).toBe(400);
    await expect(response.json()).resolves.toEqual({ error: "invalid_file_id" });
  });

  it("rejects when upstream is missing", async () => {
    const response = await GET(new Request("http://localhost"), {
      params: Promise.resolve({ fileId: "file-1" }),
    });
    expect(response.status).toBe(503);
    await expect(response.json()).resolves.toEqual({ error: "status_upstream_not_configured" });
  });

  it("returns upstream_error when upstream fails", async () => {
    process.env.CHAT_API_BASE_URL = "http://upstream";
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue({
        ok: false,
      }),
    );
    const response = await GET(new Request("http://localhost"), {
      params: Promise.resolve({ fileId: "file-2" }),
    });
    expect(response.status).toBe(502);
    await expect(response.json()).resolves.toEqual({ error: "upstream_error" });
  });

  it("returns normalized status payload", async () => {
    process.env.CHAT_API_BASE_URL = "http://upstream";
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue({
        ok: true,
        json: vi.fn().mockResolvedValue({ status: "ready" }),
      }),
    );
    const response = await GET(new Request("http://localhost"), {
      params: Promise.resolve({ fileId: "file-3" }),
    });
    expect(response.status).toBe(200);
    await expect(response.json()).resolves.toEqual({ file_id: "file-3", status: "ready" });
  });
});
