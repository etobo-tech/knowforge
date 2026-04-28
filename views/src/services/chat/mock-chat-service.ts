import type { ChatReply, ChatService } from "@/services/chat/chat-service";

export class MockChatService implements ChatService {
  async ask(question: string): Promise<ChatReply> {
    await new Promise((resolve) => setTimeout(resolve, 700));

    return {
      text: `Mock answer: I received "${question}". Backend integration comes next.`,
    };
  }
}
