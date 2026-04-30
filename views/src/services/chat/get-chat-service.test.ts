import { afterEach, describe, expect, it, vi } from "vitest";

describe("getChatService", () => {
  afterEach(() => {
    delete process.env.NEXT_PUBLIC_CHAT_MODE;
    delete process.env.NEXT_PUBLIC_CHAT_ENDPOINT;
    vi.resetModules();
    vi.clearAllMocks();
  });

  it("returns MockChatService by default", async () => {
    const { getChatService } = await import("@/services/chat/get-chat-service");
    const service = getChatService();
    expect(service.constructor.name).toBe("MockChatService");
  });

  it("returns HttpChatService when mode is http", async () => {
    process.env.NEXT_PUBLIC_CHAT_MODE = "http";
    process.env.NEXT_PUBLIC_CHAT_ENDPOINT = "/api/custom-chat";

    const { getChatService } = await import("@/services/chat/get-chat-service");
    const service = getChatService();

    expect(service.constructor.name).toBe("HttpChatService");
  });
});
