# Pruebas unitarias puras de domain/auth/username_policy.py (ADR-003
# §Evolución futura — "Cambios de username"). A diferencia del resto de
# tests/, estas no usan `app`/`client` ni tocan PostgreSQL -- la función
# bajo prueba es determinista y no depende de Flask ni del reloj del
# sistema (se le inyecta `today`).

from datetime import date, datetime, timedelta, timezone

from app.domain.auth.username_policy import (
    USERNAME_CHANGE_COOLDOWN_DAYS,
    can_change_username,
)


def test_never_changed_allows_change():
    assert can_change_username(None) is True


def test_change_today_blocks_immediate_second_change():
    today = date(2026, 8, 28)
    last_changed_at = datetime(2026, 8, 28, tzinfo=timezone.utc)

    assert can_change_username(last_changed_at, today=today) is False


def test_change_before_window_is_blocked():
    today = date(2026, 8, 28)
    last_changed_at = datetime(2026, 8, 28, tzinfo=timezone.utc) - timedelta(
        days=USERNAME_CHANGE_COOLDOWN_DAYS - 1
    )

    assert can_change_username(last_changed_at, today=today) is False


def test_change_exactly_at_window_is_allowed():
    today = date(2026, 8, 28)
    last_changed_at = datetime(2026, 8, 28, tzinfo=timezone.utc) - timedelta(
        days=USERNAME_CHANGE_COOLDOWN_DAYS
    )

    assert can_change_username(last_changed_at, today=today) is True


def test_change_after_window_is_allowed():
    today = date(2026, 8, 28)
    last_changed_at = datetime(2026, 8, 28, tzinfo=timezone.utc) - timedelta(
        days=USERNAME_CHANGE_COOLDOWN_DAYS + 5
    )

    assert can_change_username(last_changed_at, today=today) is True
