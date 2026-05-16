from db.models import Chat, Message, MessageRole, MessageSource


def test_chat_message_and_source_models_construct() -> None:
    chat = Chat(title="Support")
    message = Message(role=MessageRole.USER, content="Hello")
    source = MessageSource(score=0.9, quoted_text="snippet")

    chat.messages.append(message)
    message.sources.append(source)

    assert chat.title == "Support"
    assert message.role == MessageRole.USER
    assert source.score == 0.9
