/** @vitest-environment jsdom */
import { fireEvent, render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import { ChatInput } from "@/components/chat/chat-input";

describe("ChatInput", () => {
  it("forwards value changes and submits with Enter", async () => {
    const onInputChange = vi.fn();
    const onSubmit = vi.fn().mockResolvedValue(undefined);

    render(
      <ChatInput
        input=""
        canSend
        isThinking={false}
        onInputChange={onInputChange}
        onSubmit={onSubmit}
      />,
    );

    const textarea = screen.getByPlaceholderText("Write your question here...");
    fireEvent.change(textarea, { target: { value: "hola" } });
    expect(onInputChange).toHaveBeenCalledWith("hola");

    fireEvent.keyDown(textarea, { key: "Enter" });
    expect(onSubmit).toHaveBeenCalled();
  });
});
