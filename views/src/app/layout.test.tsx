/** @vitest-environment jsdom */
import { render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

vi.mock("next/font/google", () => ({
  Geist: () => ({ variable: "geist-sans" }),
  Geist_Mono: () => ({ variable: "geist-mono" }),
}));

import RootLayout from "@/app/layout";

describe("RootLayout", () => {
  it("renders children content", () => {
    render(
      <RootLayout>
        <div>child-content</div>
      </RootLayout>,
    );
    expect(screen.getByText("child-content")).toBeTruthy();
  });
});
