// Pruebas de la edad mínima (18) y del cálculo por fecha COMPLETA.
// Sin dependencias: `node --test` y el soporte nativo de TypeScript de Node.
import assert from 'node:assert/strict';
import { describe, it } from 'node:test';

import {
  MIN_AGE_YEARS,
  calculateAge,
  isValidISODate,
  meetsMinimumAge,
} from '../src/features/auth/lib/age.ts';

// Fecha de referencia fija (mediodía local: evita bordes por zona horaria).
const TODAY = new Date(2026, 9, 2, 12, 0, 0); // 2 de octubre de 2026

describe('edad mínima', () => {
  it('es 18', () => assert.equal(MIN_AGE_YEARS, 18));

  it('cumplir 18 hoy califica', () => {
    assert.equal(meetsMinimumAge('2008-10-02', TODAY), true);
  });

  it('cumplir 18 mañana NO califica', () => {
    assert.equal(meetsMinimumAge('2008-10-03', TODAY), false);
  });

  it('un día después del cumpleaños califica', () => {
    assert.equal(meetsMinimumAge('2008-10-01', TODAY), true);
  });

  it('compara mes y día, no solo el año', () => {
    assert.equal(meetsMinimumAge('2008-12-31', TODAY), false); // aún tiene 17
    assert.equal(meetsMinimumAge('2008-01-01', TODAY), true);
  });

  it('una fecha futura no califica', () => {
    assert.equal(meetsMinimumAge('2027-01-01', TODAY), false);
  });

  it('29 de febrero: cumple años el 1 de marzo en un año no bisiesto', () => {
    assert.equal(meetsMinimumAge('2008-02-29', new Date(2026, 1, 28, 12)), false);
    assert.equal(meetsMinimumAge('2008-02-29', new Date(2026, 2, 1, 12)), true);
  });
});

describe('calculateAge', () => {
  it('devuelve los años cumplidos', () => {
    assert.equal(calculateAge('2008-10-02', TODAY), 18);
    assert.equal(calculateAge('2008-10-03', TODAY), 17);
    assert.equal(calculateAge('1990-01-01', TODAY), 36);
  });

  it('devuelve null si la fecha no es válida', () => {
    assert.equal(calculateAge('no-es-fecha', TODAY), null);
    assert.equal(calculateAge('2008-13-01', TODAY), null);
  });
});

describe('isValidISODate', () => {
  it('acepta fechas reales', () => {
    assert.equal(isValidISODate('2000-02-29'), true); // bisiesto
    assert.equal(isValidISODate('1999-12-31'), true);
  });

  it('rechaza días que no existen', () => {
    assert.equal(isValidISODate('2001-02-29'), false); // no bisiesto
    assert.equal(isValidISODate('2001-04-31'), false);
    assert.equal(isValidISODate('2001-00-10'), false);
    assert.equal(isValidISODate('2001-01-00'), false);
  });

  it('rechaza formatos que no son yyyy-mm-dd', () => {
    assert.equal(isValidISODate('2001-1-1'), false);
    assert.equal(isValidISODate('01/01/2001'), false);
    assert.equal(isValidISODate(''), false);
  });
});
