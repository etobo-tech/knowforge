/** @vitest-environment jsdom */
import { cleanup, fireEvent, render, screen, waitFor } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";

const addAssistantMessage = vi.fn();
const uploadKnowledgeFile = vi.fn();
const waitForKnowledgeFileStatus = vi.fn();
const mapUploadErrorToMessage = vi.fn().mockReturnValue("friendly_error");

vi.mock("@/hooks/use-chat", () => ({
  useChat: () => ({
    messages: [],
    input: "",
    isThinking: false,
    canSend: false,
    canClear: false,
    setInput: vi.fn(),
    sendMessage: vi.fn(),
    clearMessages: vi.fn(),
    addAssistantMessage,
  }),
}));

vi.mock("@/services/files/file-upload-service", () => ({
  uploadKnowledgeFile: (...args: unknown[]) => uploadKnowledgeFile(...args),
}));

vi.mock("@/services/files/file-status-service", () => ({
  waitForKnowledgeFileStatus: (...args: unknown[]) => waitForKnowledgeFileStatus(...args),
}));

vi.mock("@/services/files/upload-error-message", () => ({
  mapUploadErrorToMessage: (...args: unknown[]) => mapUploadErrorToMessage(...args),
}));

vi.mock("@/components/chat/chat-input", () => ({
  ChatInput: () => <div>chat-input</div>,
}));

vi.mock("@/components/chat/message-list", () => ({
  MessageList: () => <div>message-list</div>,
}));

vi.mock("@/components/chat/chat-header", () => ({
  ChatHeader: ({ onUpload }: { onUpload: (file: File) => Promise<void> }) => (
    <button
      type="button"
      onClick={() => {
        void onUpload(new File(["x"], "doc.txt"));
      }}
    >
      upload
    </button>
  ),
}));

import { ChatPage } from "@/components/chat/chat-page";

describe("ChatPage", () => {
  afterEach(() => {
    cleanup();
    vi.clearAllMocks();
  });

  it("adds upload and status messages on successful flow", async () => {
    uploadKnowledgeFile.mockResolvedValue({ fileId: "f1", status: "processing" });
    waitForKnowledgeFileStatus.mockResolvedValue({ fileId: "f1", status: "ready" });

    render(<ChatPage />);
    fireEvent.click(screen.getByRole("button", { name: "upload" }));

    await waitFor(() => {
      expect(addAssistantMessage).toHaveBeenCalledWith(
        expect.objectContaining({
          text: expect.stringContaining("File uploaded: doc.txt"),
        }),
      );
    });
    expect(addAssistantMessage).toHaveBeenCalledWith(
      expect.objectContaining({
        text: "File status update: ready (id: f1)",
        kind: "normal",
      }),
    );
  });

  it("adds mapped error message when upload fails", async () => {
    uploadKnowledgeFile.mockRejectedValue(new Error("file_too_large"));

    render(<ChatPage />);
    fireEvent.click(screen.getByRole("button", { name: "upload" }));

    await waitFor(() => {
      expect(addAssistantMessage).toHaveBeenCalledWith({
        text: "friendly_error",
        kind: "error",
      });
    });
  });
});
