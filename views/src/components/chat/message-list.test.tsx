/** @vitest-environment jsdom */
import { createRef } from "react";
import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { MessageList } from "@/components/chat/message-list";

describe("MessageList", () => {
  it("renders messages and thinking indicator", () => {
    const endRef = createRef<HTMLDivElement>();
    render(
      <MessageList
        messages={[
          {
            id: "m1",
            role: "assistant",
            text: "welcome",
            createdAt: Date.now(),
          },
        ]}
        isThinking
        endRef={endRef}
      />,
    );

    expect(screen.getByText("welcome")).toBeTruthy();
    expect(screen.getByText("Thinking...")).toBeTruthy();
  });
});
