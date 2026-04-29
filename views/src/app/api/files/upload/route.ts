import { NextResponse } from "next/server";

function getUpstreamUrl(): string | null {
  const upstream = process.env.CHAT_API_BASE_URL ?? "";
  if (!upstream) return null;
  return `${upstream.replace(/\/$/, "")}/files/upload`;
}

export async function POST(request: Request) {
  const formData = await request.formData();
  const workspaceId = String(formData.get("workspace_id") ?? "").trim();
  const uploadedFile = formData.get("uploaded_file");

  if (!workspaceId || !(uploadedFile instanceof File)) {
    return NextResponse.json({ error: "invalid_upload_payload" }, { status: 400 });
  }

  const upstreamUrl = getUpstreamUrl();
  if (!upstreamUrl) {
    return NextResponse.json({ error: "upload_upstream_not_configured" }, { status: 503 });
  }

  const upstreamFormData = new FormData();
  upstreamFormData.set("workspace_id", workspaceId);
  upstreamFormData.set("uploaded_file", uploadedFile);

  const upstreamResponse = await fetch(upstreamUrl, {
    method: "POST",
    body: upstreamFormData,
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
    file_id: payload.file_id ?? "",
    status: payload.status ?? "pending",
  });
}
