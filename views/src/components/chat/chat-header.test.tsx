/** @vitest-environment jsdom */
import { cleanup, fireEvent, render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, describe, expect, it, vi } from "vitest";

import { ChatHeader } from "@/components/chat/chat-header";

describe("ChatHeader", () => {
  afterEach(() => {
    cleanup();
    vi.clearAllMocks();
  });

  it("calls clear handler", () => {
    const onClear = vi.fn();
    render(
      <ChatHeader
        onClear={onClear}
        onUpload={vi.fn()}
        isUploading={false}
        canClear
      />,
    );

    fireEvent.click(screen.getByRole("button", { name: "Clear chat" }));
    expect(onClear).toHaveBeenCalled();
  });

  it("handles file upload input change", async () => {
    const onUpload = vi.fn().mockResolvedValue(undefined);
    render(
      <ChatHeader
        onClear={vi.fn()}
        onUpload={onUpload}
        isUploading={false}
        canClear={false}
      />,
    );

    const input = document.querySelector('input[type="file"]') as HTMLInputElement;
    const file = new File(["abc"], "doc.txt", { type: "text/plain" });
    await userEvent.upload(input, file);

    await waitFor(() => {
      expect(onUpload).toHaveBeenCalledWith(file);
    });
  });
});
