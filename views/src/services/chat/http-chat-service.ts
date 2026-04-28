import type { ChatReply, ChatService } from "@/services/chat/chat-service";

type HttpChatServiceOptions = {
  endpoint: string;
};

export class HttpChatService implements ChatService {
  private readonly endpoint: string;

  constructor(options: HttpChatServiceOptions) {
    this.endpoint = options.endpoint;
  }

  async ask(question: string): Promise<ChatReply> {
    const response = await fetch(this.endpoint, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question }),
    });

    if (!response.ok) {
      throw new Error("chat_request_failed");
    }

    const payload = (await response.json()) as { answer?: string };
    return { text: payload.answer ?? "No answer available." };
  }
}
