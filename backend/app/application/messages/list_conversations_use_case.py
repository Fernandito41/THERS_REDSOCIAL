# Caso de uso: listar las conversaciones del usuario autenticado
# (GET /api/conversations, ADR-013-messages-minimal-model.md). Es lo que
# alimenta Messages.jsx (lista de conversaciones) y el badge de no-leídos
# de Sidebar/Topbar (sumando `unread_count` de cada una).

from app.application.messages.message_presenter import to_public_conversation


def list_conversations(user_id, message_repository):
    conversations = message_repository.list_conversations(user_id)
    return [to_public_conversation(conversation) for conversation in conversations]
