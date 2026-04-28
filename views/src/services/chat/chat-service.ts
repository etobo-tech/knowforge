export type ChatReply = {
  text: string;
};

export interface ChatService {
  ask(question: string): Promise<ChatReply>;
}
