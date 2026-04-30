import { afterEach, describe, expect, it, vi } from "vitest";

import { POST } from "@/app/api/files/upload/route";

function uploadRequest(formData: FormData): Request {
  return new Request("http://localhost/api/files/upload", {
    method: "POST",
    body: formData,
  });
}

describe("app/api/files/upload POST", () => {
  afterEach(() => {
    vi.unstubAllGlobals();
    delete process.env.CHAT_API_BASE_URL;
  });

  it("rejects invalid payload", async () => {
    const formData = new FormData();
    formData.set("workspace_id", "ws-1");
    const response = await POST(uploadRequest(formData));
    expect(response.status).toBe(400);
    await expect(response.json()).resolves.toEqual({ error: "invalid_upload_payload" });
  });

  it("rejects when upstream is not configured", async () => {
    const formData = new FormData();
    formData.set("workspace_id", "ws-1");
    formData.set("uploaded_file", new File(["hello"], "doc.txt"));
    const response = await POST(uploadRequest(formData));
    expect(response.status).toBe(503);
    await expect(response.json()).resolves.toEqual({ error: "upload_upstream_not_configured" });
  });

  it("propagates upstream upload error payload", async () => {
    process.env.CHAT_API_BASE_URL = "http://upstream";
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue({
        ok: false,
        status: 400,
        json: vi.fn().mockResolvedValue({ detail: "unsupported_file_type" }),
      }),
    );

    const formData = new FormData();
    formData.set("workspace_id", "ws-1");
    formData.set("uploaded_file", new File(["hello"], "doc.pdf"));
    const response = await POST(uploadRequest(formData));

    expect(response.status).toBe(400);
    await expect(response.json()).resolves.toEqual({ error: "unsupported_file_type" });
  });

  it("returns normalized upload response", async () => {
    process.env.CHAT_API_BASE_URL = "http://upstream";
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue({
        ok: true,
        json: vi.fn().mockResolvedValue({ file_id: "f-1", status: "processing" }),
      }),
    );

    const formData = new FormData();
    formData.set("workspace_id", "ws-1");
    formData.set("uploaded_file", new File(["hello"], "doc.txt"));
    const response = await POST(uploadRequest(formData));

    expect(response.status).toBe(200);
    await expect(response.json()).resolves.toEqual({ file_id: "f-1", status: "processing" });
  });
});
