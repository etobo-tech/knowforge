import { NextResponse } from "next/server";

type ChatRequest = {
  question?: string;
};

type ChatResponse = {
  answer?: string;
  citations?: Array<{ file_id?: string; chunk_id?: string }>;
};

function getUpstreamUrl(): string | null {
  const upstream = process.env.CHAT_API_BASE_URL ?? "";
  if (!upstream) return null;
  return `${upstream.replace(/\/$/, "")}/chat`;
}

export async function POST(request: Request) {
  let payload: ChatRequest;

  try {
    payload = (await request.json()) as ChatRequest;
  } catch {
    return NextResponse.json({ error: "invalid_json" }, { status: 400 });
  }

  const question = payload.question?.trim();
  if (!question) {
    return NextResponse.json({ error: "invalid_question" }, { status: 400 });
  }

  const workspaceId = (process.env.NEXT_PUBLIC_WORKSPACE_ID ?? "").trim();
  if (!workspaceId) {
    return NextResponse.json({ error: "workspace_not_configured" }, { status: 500 });
  }

  const upstreamUrl = getUpstreamUrl();
  if (!upstreamUrl) {
    return NextResponse.json({ error: "chat_upstream_not_configured" }, { status: 503 });
  }

  const upstreamResponse = await fetch(upstreamUrl, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ workspace_id: workspaceId, question }),
    cache: "no-store",
  });

  if (!upstreamResponse.ok) {
    return NextResponse.json({ error: "upstream_error" }, { status: 502 });
  }

  const upstreamPayload = (await upstreamResponse.json()) as ChatResponse;
  return NextResponse.json({
    answer: upstreamPayload.answer ?? "No answer available.",
    citations: upstreamPayload.citations ?? [],
  });
}
