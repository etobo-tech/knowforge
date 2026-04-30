import { afterEach, describe, expect, it, vi } from "vitest";

import { HttpChatService } from "@/services/chat/http-chat-service";

describe("HttpChatService", () => {
  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("returns normalized chat payload on success", async () => {
    const json = vi.fn().mockResolvedValue({
      answer: "Hola",
      citations: [
        { file_id: "file-1", chunk_id: "chunk-1" },
        { file_id: "", chunk_id: "chunk-2" },
      ],
    });
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue({
        ok: true,
        json,
      }),
    );

    const service = new HttpChatService({ endpoint: "/api/chat" });
    const reply = await service.ask("pregunta");

    expect(reply.text).toBe("Hola");
    expect(reply.citations).toEqual([{ fileId: "file-1", chunkId: "chunk-1" }]);
  });

  it("throws parsed api error code on failure", async () => {
    const json = vi.fn().mockResolvedValue({ detail: "invalid_json" });
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue({
        ok: false,
        json,
      }),
    );

    const service = new HttpChatService({ endpoint: "/api/chat" });
    await expect(service.ask("pregunta")).rejects.toThrow("invalid_json");
  });
});
