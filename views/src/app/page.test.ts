import { describe, expect, it, vi } from "vitest";

const redirectMock = vi.fn();

vi.mock("next/navigation", () => ({
  redirect: redirectMock,
}));

describe("app/page", () => {
  it("redirects to chat route", async () => {
    const module = await import("@/app/page");
    module.default();
    expect(redirectMock).toHaveBeenCalledWith("/chat");
  });
});
