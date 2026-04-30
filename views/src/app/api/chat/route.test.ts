import { afterEach, describe, expect, it, vi } from "vitest";

import { POST } from "@/app/api/chat/route";

function jsonRequest(payload: unknown): Request {
  return new Request("http://localhost/api/chat", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
}

describe("app/api/chat POST", () => {
  afterEach(() => {
    vi.unstubAllGlobals();
    delete process.env.CHAT_API_BASE_URL;
    delete process.env.NEXT_PUBLIC_WORKSPACE_ID;
  });

  it("rejects invalid question", async () => {
    const response = await POST(jsonRequest({ question: " " }));
    expect(response.status).toBe(400);
    await expect(response.json()).resolves.toEqual({ error: "invalid_question" });
  });

  it("rejects when workspace is not configured", async () => {
    process.env.CHAT_API_BASE_URL = "http://upstream";
    const response = await POST(jsonRequest({ question: "hola" }));
    expect(response.status).toBe(500);
    await expect(response.json()).resolves.toEqual({ error: "workspace_not_configured" });
  });

  it("maps upstream error payload and preserves status", async () => {
    process.env.CHAT_API_BASE_URL = "http://upstream";
    process.env.NEXT_PUBLIC_WORKSPACE_ID = "ws-1";
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue({
        ok: false,
        status: 422,
        json: vi.fn().mockResolvedValue({ detail: "invalid_question" }),
      }),
    );

    const response = await POST(jsonRequest({ question: "hola" }));
    expect(response.status).toBe(422);
    await expect(response.json()).resolves.toEqual({ error: "invalid_question" });
  });

  it("returns normalized chat payload on success", async () => {
    process.env.CHAT_API_BASE_URL = "http://upstream";
    process.env.NEXT_PUBLIC_WORKSPACE_ID = "ws-1";
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue({
        ok: true,
        json: vi.fn().mockResolvedValue({ answer: "ok", citations: [{ file_id: "f", chunk_id: "c" }] }),
      }),
    );

    const response = await POST(jsonRequest({ question: "hola" }));
    expect(response.status).toBe(200);
    await expect(response.json()).resolves.toEqual({
      answer: "ok",
      citations: [{ file_id: "f", chunk_id: "c" }],
    });
  });
});
