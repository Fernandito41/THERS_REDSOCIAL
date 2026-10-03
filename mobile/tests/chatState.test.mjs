// Pruebas de la lógica pura del chat: combinar páginas, deduplicar, reconciliar los
// mensajes locales y el ritmo de consulta (ADR-035).
import assert from 'node:assert/strict';
import { describe, it } from 'node:test';

import {
  latestConfirmedAt,
  makePending,
  mergeMessages,
  nextPollDelayMs,
  oldestConfirmedAt,
  removeLocal,
  setLocalState,
} from '../src/features/messages/chatState.ts';

function msg(id, createdAt, extra = {}) {
  return {
    id,
    sender_id: 'a',
    recipient_id: 'b',
    content: `texto ${id}`,
    read: false,
    created_at: createdAt,
    edited: false,
    client_id: null,
    ...extra,
  };
}

describe('mergeMessages', () => {
  it('ordena por instante', () => {
    const merged = mergeMessages([], [
      msg('3', '2026-10-02T10:00:03+00:00'),
      msg('1', '2026-10-02T10:00:01+00:00'),
      msg('2', '2026-10-02T10:00:02+00:00'),
    ]);
    assert.deepEqual(merged.map((m) => m.id), ['1', '2', '3']);
  });

  it('no duplica un mensaje que el servidor devuelve otra vez (cursor inclusivo)', () => {
    const current = [msg('1', '2026-10-02T10:00:01+00:00'), msg('2', '2026-10-02T10:00:02+00:00')];
    const merged = mergeMessages(current, [
      msg('2', '2026-10-02T10:00:02+00:00'),
      msg('3', '2026-10-02T10:00:03+00:00'),
    ]);
    assert.deepEqual(merged.map((m) => m.id), ['1', '2', '3']);
  });

  it('el estado que manda el servidor reemplaza al local con el mismo id', () => {
    const current = [msg('1', '2026-10-02T10:00:01+00:00', { read: false })];
    const merged = mergeMessages(current, [msg('1', '2026-10-02T10:00:01+00:00', { read: true })]);
    assert.equal(merged[0].read, true);
  });

  it('un mensaje confirmado reemplaza al local con el mismo client_id (sin duplicar)', () => {
    const pending = makePending('m-1', 'a', 'b', 'hola', new Date('2026-10-02T10:00:00Z'));
    const merged = mergeMessages(
      [pending],
      [msg('srv-1', '2026-10-02T10:00:01+00:00', { client_id: 'm-1', content: 'hola' })],
    );
    assert.equal(merged.length, 1);
    assert.equal(merged[0].id, 'srv-1');
    assert.equal(merged[0].local, undefined);
  });

  it('conserva un local que el servidor todavía no confirmó', () => {
    const pending = makePending('m-2', 'a', 'b', 'pendiente', new Date('2026-10-02T10:00:05Z'));
    const merged = mergeMessages([pending], [msg('1', '2026-10-02T10:00:01+00:00')]);
    assert.deepEqual(merged.map((m) => m.id), ['1', 'local:m-2']);
  });
});

describe('cursores', () => {
  it('latestConfirmedAt ignora los mensajes locales', () => {
    const list = [
      msg('1', '2026-10-02T10:00:01+00:00'),
      msg('2', '2026-10-02T10:00:02+00:00'),
      makePending('m-3', 'a', 'b', 'x', new Date('2026-10-02T11:00:00Z')),
    ];
    assert.equal(latestConfirmedAt(list), '2026-10-02T10:00:02+00:00');
  });

  it('oldestConfirmedAt devuelve el más antiguo confirmado', () => {
    const list = [msg('1', '2026-10-02T10:00:01+00:00'), msg('2', '2026-10-02T10:00:02+00:00')];
    assert.equal(oldestConfirmedAt(list), '2026-10-02T10:00:01+00:00');
  });

  it('sin confirmados no hay cursor', () => {
    const list = [makePending('m-1', 'a', 'b', 'x')];
    assert.equal(latestConfirmedAt(list), undefined);
    assert.equal(oldestConfirmedAt(list), undefined);
    assert.equal(latestConfirmedAt([]), undefined);
  });
});

describe('mensajes locales', () => {
  it('marca como fallido y vuelve a en vuelo solo el que corresponde', () => {
    const list = [makePending('m-1', 'a', 'b', 'uno'), makePending('m-2', 'a', 'b', 'dos')];
    const failed = setLocalState(list, 'm-1', 'failed');
    assert.equal(failed[0].local, 'failed');
    assert.equal(failed[1].local, 'sending');
    assert.equal(setLocalState(failed, 'm-1', 'sending')[0].local, 'sending');
  });

  it('removeLocal quita solo el local indicado', () => {
    const list = [makePending('m-1', 'a', 'b', 'uno'), makePending('m-2', 'a', 'b', 'dos')];
    assert.deepEqual(removeLocal(list, 'm-1').map((m) => m.client_id), ['m-2']);
  });
});

describe('nextPollDelayMs', () => {
  it('arranca corto', () => assert.equal(nextPollDelayMs(0, 0), 3000));

  it('se alarga mientras el chat está en silencio, con tope', () => {
    assert.ok(nextPollDelayMs(2, 0) > nextPollDelayMs(0, 0));
    assert.equal(nextPollDelayMs(100, 0), 12000);
  });

  it('tras errores retrocede de forma exponencial, con tope', () => {
    assert.equal(nextPollDelayMs(0, 1), 6000);
    assert.equal(nextPollDelayMs(0, 2), 12000);
    assert.equal(nextPollDelayMs(0, 10), 30000);
  });
});
