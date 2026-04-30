import { describe, expect, it, vi } from "vitest";

vi.mock("@/config/upload-limits", () => ({
  getMaxUploadSizeMibForUi: () => 4,
}));

import { mapUploadErrorToMessage } from "@/services/files/upload-error-message";

describe("mapUploadErrorToMessage", () => {
  it("maps unsupported file extension", () => {
    expect(mapUploadErrorToMessage(new Error("unsupported_file_type"))).toBe(
      "Only .txt and .md files are supported right now.",
    );
  });

  it("maps file too large with dynamic limit", () => {
    expect(mapUploadErrorToMessage(new Error("file_too_large"))).toBe(
      "The selected file is too large. Max size is 4 MiB.",
    );
  });

  it("returns fallback message for unknown errors", () => {
    expect(mapUploadErrorToMessage(new Error("unexpected_code"))).toBe(
      "File upload failed. Please try again.",
    );
  });
});
