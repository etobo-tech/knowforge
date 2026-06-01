from llama_index.core.llms import ChatMessage, MessageRole as LlamaMessageRole
from llama_index.core.memory import ChatMemoryBuffer

from db.models import Message, MessageRole


def _message_to_chat_message(message: Message) -> ChatMessage | None:
    if message.role == MessageRole.USER:
        return ChatMessage(role=LlamaMessageRole.USER, content=message.content)
    if message.role == MessageRole.ASSISTANT:
        return ChatMessage(
            role=LlamaMessageRole.ASSISTANT,
            content=message.content,
        )
    return None


def build_memory(prior_messages: list[Message]) -> ChatMemoryBuffer:
    memory = ChatMemoryBuffer.from_defaults(token_limit=3000)
    for message in prior_messages:
        chat_message = _message_to_chat_message(message)
        if chat_message is not None:
            memory.put(chat_message)
    return memory


def prior_chat_messages(prior_messages: list[Message]) -> list[ChatMessage]:
    return [
        chat_message
        for message in prior_messages
        if (chat_message := _message_to_chat_message(message)) is not None
    ]
