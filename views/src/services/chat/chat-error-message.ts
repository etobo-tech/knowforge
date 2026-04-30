export function mapChatErrorToMessage(error: unknown): string {
  const errorCode = error instanceof Error ? error.message : "";

  if (errorCode === "chat_upstream_not_configured") {
    return "Chat service is not configured yet. Please try again later.";
  }

  if (errorCode === "workspace_not_configured") {
    return "Workspace is not configured. Set NEXT_PUBLIC_WORKSPACE_ID.";
  }

  if (errorCode === "invalid_question" || errorCode === "invalid_json") {
    return "Could not send that message. Please try again.";
  }

  if (errorCode === "upstream_error") {
    return "The chat service returned an error. Please try again.";
  }

  return "I could not generate an answer right now. Please try again.";
}
