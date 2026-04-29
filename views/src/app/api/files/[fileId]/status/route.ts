import { NextResponse } from "next/server";

function getUpstreamBaseUrl(): string | null {
  const upstream = process.env.CHAT_API_BASE_URL ?? "";
  if (!upstream) return null;
  return upstream.replace(/\/$/, "");
}

export async function GET(
  _: Request,
  context: { params: Promise<{ fileId: string }> },
) {
  const { fileId } = await context.params;
  if (!fileId.trim()) {
    return NextResponse.json({ error: "invalid_file_id" }, { status: 400 });
  }

  const upstreamBaseUrl = getUpstreamBaseUrl();
  if (!upstreamBaseUrl) {
    return NextResponse.json({ error: "status_upstream_not_configured" }, { status: 503 });
  }

  const upstreamResponse = await fetch(`${upstreamBaseUrl}/files/${fileId}/status`, {
    method: "GET",
    cache: "no-store",
  });

  if (!upstreamResponse.ok) {
    return NextResponse.json({ error: "upstream_error" }, { status: 502 });
  }

  const payload = (await upstreamResponse.json()) as {
    file_id?: string;
    status?: string;
  };

  return NextResponse.json({
    file_id: payload.file_id ?? fileId,
    status: payload.status ?? "unknown",
  });
}
