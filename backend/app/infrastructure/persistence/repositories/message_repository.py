# Adaptador SQLAlchemy del puerto `MessageRepository` (domain/messages/repositories.py).
# Único punto del backend que traduce entre `messages` (PostgreSQL) y el
# resto de las capas -- domain/ y application/ no importan SQLAlchemy
# directamente (BACKEND_ARCHITECTURE.md §17), mismo patrón que
# follow_repository.py/notification_repository.py.

from sqlalchemy import and_, case, delete as sa_delete, func, or_, select, update

from app.domain.messages.repositories import MessageRepository
from app.extensions import db
from app.infrastructure.persistence.models import Message, User


class SQLAlchemyMessageRepository(MessageRepository):
    def create(self, sender_id, recipient_id, content):
        message = Message(sender_id=sender_id, recipient_id=recipient_id, content=content)
        db.session.add(message)
        db.session.commit()
        return message

    def list_thread(self, user_a_id, user_b_id, limit):
        # DESC + limit trae los `limit` más recientes; se revierte en Python
        # para devolver el hilo en orden cronológico (más viejo primero,
        # ADR-013 §Contrato API) sin pedirle a PostgreSQL un ORDER BY sobre
        # un subconjunto ya limitado en el otro sentido.
        rows = (
            db.session.execute(
                select(Message)
                .where(
                    or_(
                        and_(Message.sender_id == user_a_id, Message.recipient_id == user_b_id),
                        and_(Message.sender_id == user_b_id, Message.recipient_id == user_a_id),
                    )
                )
                .order_by(Message.created_at.desc())
                .limit(limit)
            )
            .scalars()
            .all()
        )
        return list(reversed(rows))

    def mark_thread_as_read(self, recipient_id, sender_id):
        # `func.coalesce`: solo fija read_at la primera vez -- una segunda
        # llamada (otra visita al mismo hilo) no le "renueva" la marca de
        # tiempo de lectura, mismo criterio que
        # NotificationRepository.mark_as_read (ADR-008).
        db.session.execute(
            update(Message)
            .where(Message.sender_id == sender_id, Message.recipient_id == recipient_id)
            .values(read_at=func.coalesce(Message.read_at, func.now()))
        )
        db.session.commit()

    def list_conversations(self, user_id):
        # "La otra persona" del mensaje, resuelta con CASE -- necesaria para
        # poder agrupar por ella con un único DISTINCT ON (PostgreSQL).
        other_id = case(
            (Message.sender_id == user_id, Message.recipient_id),
            else_=Message.sender_id,
        ).label("other_id")

        # DISTINCT ON (other_id) + ORDER BY (other_id, created_at DESC):
        # una fila por conversación, la más reciente -- construcción nativa
        # de PostgreSQL para "último mensaje por grupo" sin sub-consulta
        # correlacionada ni ventana (ADR-013 §Riesgos: la consulta más cara
        # de esta entidad, aceptable al volumen de esta tarea).
        last_message_rows = db.session.execute(
            select(Message, other_id)
            .where(or_(Message.sender_id == user_id, Message.recipient_id == user_id))
            .distinct(other_id)
            .order_by(other_id, Message.created_at.desc())
        ).all()

        unread_counts = dict(
            db.session.execute(
                select(Message.sender_id, func.count())
                .where(Message.recipient_id == user_id, Message.read_at.is_(None))
                .group_by(Message.sender_id)
            ).all()
        )

        other_user_ids = [row.other_id for row in last_message_rows]
        other_users = {}
        if other_user_ids:
            other_users = {
                user.id: user
                for user in db.session.execute(
                    select(User).where(User.id.in_(other_user_ids))
                ).scalars()
            }

        conversations = [
            {
                "other_user": other_users[row.other_id],
                "last_message": row.Message,
                "unread_count": unread_counts.get(row.other_id, 0),
            }
            for row in last_message_rows
        ]
        # Más reciente primero -- DISTINCT ON exige que el ORDER BY empiece
        # por la columna de distinción (other_id), así que el orden final
        # por fecha se resuelve acá, sobre el resultado ya reducido a una
        # fila por conversación (pocas filas, orden en Python es aceptable).
        conversations.sort(key=lambda c: c["last_message"].created_at, reverse=True)
        return conversations

    def delete(self, message_id, sender_id):
        # `sender_id` en el propio WHERE, no un chequeo aparte después de
        # leer la fila -- confirma existencia y pertenencia en la misma
        # sentencia (mismo principio que NotificationRepository.mark_as_read,
        # ADR-014-messages-ux-improvements.md).
        result = db.session.execute(
            sa_delete(Message).where(Message.id == message_id, Message.sender_id == sender_id)
        )
        db.session.commit()
        return result.rowcount > 0
