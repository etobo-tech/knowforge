/** @vitest-environment jsdom */
import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { MessageBubble } from "@/components/chat/message-bubble";

describe("MessageBubble", () => {
  it("renders citations for assistant messages", () => {
    render(
      <MessageBubble
        message={{
          id: "m1",
          role: "assistant",
          text: "answer",
          createdAt: Date.now(),
          citations: [{ fileId: "f1", chunkId: "c1" }],
        }}
      />,
    );

    expect(screen.getByText("answer")).toBeTruthy();
    expect(screen.getByText("Sources: f1:c1")).toBeTruthy();
  });
});
