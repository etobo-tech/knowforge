import { describe, expect, it } from "vitest";

import { mapChatErrorToMessage } from "@/services/chat/chat-error-message";

describe("mapChatErrorToMessage", () => {
  it("maps known upstream config error", () => {
    expect(mapChatErrorToMessage(new Error("chat_upstream_not_configured"))).toBe(
      "Chat service is not configured yet. Please try again later.",
    );
  });

  it("maps invalid_question and invalid_json into same friendly message", () => {
    expect(mapChatErrorToMessage(new Error("invalid_question"))).toBe(
      "Could not send that message. Please try again.",
    );
    expect(mapChatErrorToMessage(new Error("invalid_json"))).toBe(
      "Could not send that message. Please try again.",
    );
  });

  it("uses fallback message for unknown errors", () => {
    expect(mapChatErrorToMessage(new Error("anything_else"))).toBe(
      "I could not generate an answer right now. Please try again.",
    );
  });
});
