import { describe, expect, it, vi } from "vitest";

import { MockChatService } from "@/services/chat/mock-chat-service";

describe("MockChatService", () => {
  it("returns deterministic mock answer", async () => {
    vi.useFakeTimers();
    const service = new MockChatService();

    const promise = service.ask("hola");
    await vi.advanceTimersByTimeAsync(700);
    const result = await promise;

    expect(result.text).toContain('Mock answer: I received "hola"');
    expect(result.citations).toEqual([]);
    vi.useRealTimers();
  });
});
