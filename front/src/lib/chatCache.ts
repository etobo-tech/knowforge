import type { ChatDetailResponse, ChatSummaryResponse } from './api'

let chatListCache: ChatSummaryResponse[] | null = null
const chatDetailCache = new Map<string, ChatDetailResponse>()

export function getCachedChatList(): ChatSummaryResponse[] | null {
  return chatListCache
}

export function setCachedChatList(chats: ChatSummaryResponse[]): void {
  chatListCache = chats
}

export function invalidateChatListCache(): void {
  chatListCache = null
}

export function getCachedChat(chatId: string): ChatDetailResponse | null {
  return chatDetailCache.get(chatId) ?? null
}

export function setCachedChat(chat: ChatDetailResponse): void {
  chatDetailCache.set(chat.id, chat)
}

export function invalidateChatCache(chatId?: string): void {
  if (chatId) {
    chatDetailCache.delete(chatId)
    return
  }
  chatDetailCache.clear()
}
