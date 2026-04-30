/** @vitest-environment jsdom */
import { act, renderHook } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import { useChat } from "@/hooks/use-chat";

describe("useChat", () => {
  it("sends question and appends assistant reply", async () => {
    vi.spyOn(crypto, "randomUUID").mockReturnValue("id-1");
    const chatService = {
      ask: vi.fn().mockResolvedValue({
        text: "respuesta",
        citations: [{ fileId: "f1", chunkId: "c1" }],
      }),
    };

    const { result } = renderHook(() => useChat(chatService));
    act(() => result.current.setInput(" hola "));
    await act(async () => {
      await result.current.sendMessage();
    });

    expect(chatService.ask).toHaveBeenCalledWith("hola");
    expect(result.current.messages.at(-1)).toMatchObject({
      role: "assistant",
      text: "respuesta",
      citations: [{ fileId: "f1", chunkId: "c1" }],
    });
  });

  it("appends mapped error when ask fails", async () => {
    vi.spyOn(crypto, "randomUUID").mockReturnValue("id-2");
    const chatService = {
      ask: vi.fn().mockRejectedValue(new Error("invalid_json")),
    };

    const { result } = renderHook(() => useChat(chatService));
    act(() => result.current.setInput("hola"));
    await act(async () => {
      await result.current.sendMessage();
    });

    expect(result.current.messages.at(-1)).toMatchObject({
      role: "assistant",
      kind: "error",
      text: "Could not send that message. Please try again.",
    });
  });

  it("clears chat back to welcome message", () => {
    const chatService = {
      ask: vi.fn().mockResolvedValue({ text: "ok", citations: [] }),
    };
    const { result } = renderHook(() => useChat(chatService));
    act(() => result.current.addAssistantMessage({ text: "extra" }));
    expect(result.current.canClear).toBe(true);

    act(() => result.current.clearMessages());
    expect(result.current.messages).toHaveLength(1);
    expect(result.current.messages[0].id).toBe("welcome");
  });
});
