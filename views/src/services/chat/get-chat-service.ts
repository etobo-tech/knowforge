import type { ChatService } from "@/services/chat/chat-service";
import { HttpChatService } from "@/services/chat/http-chat-service";
import { MockChatService } from "@/services/chat/mock-chat-service";

const chatMode = process.env.NEXT_PUBLIC_CHAT_MODE ?? "mock";
const chatEndpoint = process.env.NEXT_PUBLIC_CHAT_ENDPOINT ?? "/api/chat";

const chatService: ChatService =
  chatMode === "http"
    ? new HttpChatService({ endpoint: chatEndpoint })
    : new MockChatService();

export function getChatService(): ChatService {
  return chatService;
}
