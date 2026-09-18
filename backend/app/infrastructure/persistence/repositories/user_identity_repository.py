# Adaptador SQLAlchemy del puerto `UserIdentityRepository`
# (domain/auth/user_identity_repository.py, ADR-012-google-sign-in.md).
# Mismo patrón que el resto de repositorios de infrastructure/persistence/.

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app.domain.auth.exceptions import IdentityAlreadyLinkedError
from app.domain.auth.user_identity_repository import UserIdentityRepository
from app.extensions import db
from app.infrastructure.persistence.models import UserIdentity


class SQLAlchemyUserIdentityRepository(UserIdentityRepository):
    def find_by_provider_and_subject(self, provider, provider_subject):
        return db.session.execute(
            select(UserIdentity).where(
                UserIdentity.provider == provider,
                UserIdentity.provider_subject == provider_subject,
            )
        ).scalar_one_or_none()

    def create(self, user_id, provider, provider_subject):
        identity = UserIdentity(
            user_id=user_id, provider=provider, provider_subject=provider_subject
        )
        db.session.add(identity)
        try:
            db.session.commit()
        except IntegrityError as exc:
            db.session.rollback()
            raise IdentityAlreadyLinkedError() from exc
        return identity
