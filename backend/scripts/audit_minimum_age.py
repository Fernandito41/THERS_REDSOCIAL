"""Auditoría de edad de las cuentas existentes (ADR-034-minimum-age-18.md).

SOLO LECTURA: cuenta cuentas por categoría y NO modifica, bloquea ni borra nada,
ni imprime correos, nombres ni fechas de nacimiento. Sirve para que el equipo
decida con números qué hacer con las cuentas anteriores a la regla de 18 años.

Uso (desde `backend/`, con `DATABASE_URL` apuntando a la base a revisar):

    python scripts/audit_minimum_age.py

Categorías:
  - `mayores_de_edad`     fecha de nacimiento declarada y 18 años cumplidos.
  - `menores_declarados`  fecha de nacimiento declarada y menos de 18 años.
  - `sin_fecha`           sin fecha de nacimiento (cuentas de Google que nunca
                          completaron el perfil). No se asume nada de ellas.

La fecha es la que la persona DECLARÓ: no es una verificación documental.
"""

import os
import sys
from datetime import date

# Permite correr el script desde `backend/` sin instalar el paquete.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app  # noqa: E402
from app.domain.auth.validators import MIN_AGE_YEARS, meets_minimum_age  # noqa: E402
from app.extensions import db  # noqa: E402
from app.infrastructure.persistence.models import User  # noqa: E402


def audit(today=None):
    """Devuelve el conteo por categoría. Separada de `main` para poder probarla."""
    today = today or date.today()
    counts = {"mayores_de_edad": 0, "menores_declarados": 0, "sin_fecha": 0}
    for (birth_date,) in db.session.query(User.birth_date).yield_per(500):
        if birth_date is None:
            counts["sin_fecha"] += 1
        elif meets_minimum_age(birth_date, today=today):
            counts["mayores_de_edad"] += 1
        else:
            counts["menores_declarados"] += 1
    return counts


def main():
    app = create_app()
    with app.app_context():
        counts = audit()
    total = sum(counts.values())
    print(f"Edad mínima vigente: {MIN_AGE_YEARS} años. Cuentas revisadas: {total}")
    for name, value in counts.items():
        print(f"  {name}: {value}")


if __name__ == "__main__":
    main()
