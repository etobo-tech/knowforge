import type { ChatService } from "@/services/chat/chat-service";
import { HttpChatService } from "@/services/chat/http-chat-service";
import { MockChatService } from "@/services/chat/mock-chat-service";

const chatMode = process.env.NEXT_PUBLIC_CHAT_MODE ?? "mock";
const chatApiBaseUrl = process.env.NEXT_PUBLIC_CHAT_API_BASE_URL ?? "";

const chatService: ChatService =
  chatMode === "http" && chatApiBaseUrl
    ? new HttpChatService({ baseUrl: chatApiBaseUrl })
    : new MockChatService();

export function getChatService(): ChatService {
  return chatService;
}
