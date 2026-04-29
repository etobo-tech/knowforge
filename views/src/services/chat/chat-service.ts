import type { Citation } from "@/types/chat";

export type ChatReply = {
  text: string;
  citations: Citation[];
};

export interface ChatService {
  ask(question: string): Promise<ChatReply>;
}
