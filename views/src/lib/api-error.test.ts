import { describe, expect, it } from "vitest";

import { errorCodeFromPayload } from "@/lib/api-error";

describe("errorCodeFromPayload", () => {
  it("returns direct error when available", () => {
    expect(errorCodeFromPayload({ error: "upstream_error" })).toBe("upstream_error");
  });

  it("returns detail string when error is missing", () => {
    expect(errorCodeFromPayload({ detail: "invalid_json" })).toBe("invalid_json");
  });

  it("returns first detail message from validation list", () => {
    expect(errorCodeFromPayload({ detail: [{ msg: "invalid_question" }] })).toBe(
      "invalid_question",
    );
  });

  it("returns null for unsupported payload shapes", () => {
    expect(errorCodeFromPayload({ detail: [{ foo: "bar" }] })).toBeNull();
    expect(errorCodeFromPayload(null)).toBeNull();
  });
});
