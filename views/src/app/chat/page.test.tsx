/** @vitest-environment jsdom */
import { render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

vi.mock("@/components/chat/chat-page", () => ({
  ChatPage: () => <div>mock-chat-page</div>,
}));

import ChatRoutePage from "@/app/chat/page";

describe("app/chat/page", () => {
  it("renders ChatPage", () => {
    render(<ChatRoutePage />);
    expect(screen.getByText("mock-chat-page")).toBeTruthy();
  });
});
