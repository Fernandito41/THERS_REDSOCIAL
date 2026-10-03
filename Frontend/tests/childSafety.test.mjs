// Pruebas de la página pública /child-safety (ADR-038-child-safety-reports.md).
// Sin dependencias: `node --test` lee los locales y los archivos fuente. No necesita
// navegador; la comprobación de que se dibuja de verdad está en el informe de la tarea.
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { URL } from 'node:url';
import { describe, it } from 'node:test';

const read = (path) => readFileSync(new URL(`../${path}`, import.meta.url), 'utf-8');
const es = JSON.parse(read('src/shared/i18n/locales/es.json')).childSafety;
const en = JSON.parse(read('src/shared/i18n/locales/en.json')).childSafety;

const EMAIL = 'seguridadinfantil@thersweb.com';
const everyText = (block) => JSON.stringify(block).toLowerCase();

describe('contenido', () => {
  it('tiene el título pedido en español', () => {
    assert.equal(es.title, 'Estándares de Seguridad Infantil de THERS Social Network');
  });

  it('declara tolerancia cero', () => {
    assert.match(es.intro, /tolerancia cero/i);
    assert.match(en.intro, /zero tolerance/i);
  });

  it('prohíbe expresamente cada conducta exigida', () => {
    const text = es.prohibited.join(' ').toLowerCase();
    for (const keyword of [
      'material de abuso sexual infantil',
      'explotación sexual infantil',
      'grooming',
      'sextorsión',
      'solicitudes',
      'trata',
      'enlazar',
      'generado o manipulado',
    ]) {
      assert.ok(text.includes(keyword), `falta: ${keyword}`);
    }
    assert.equal(es.prohibited.length, 8);
  });

  it('nombra la categoría de reporte con el texto exacto', () => {
    assert.equal(es.reportCategory, 'Explotación o abuso de menores');
    assert.equal(en.reportCategory, 'Child exploitation or abuse');
  });

  it('explica cómo reportar y que quien reporta no es revelado', () => {
    assert.ok(es.reportSteps.some((step) => /reportar/i.test(step)));
    assert.match(es.reportAnonymous, /no sabrá quién/i);
  });

  it('dice que la prioridad es máxima, que se puede retirar y suspender', () => {
    const text = es.handling.join(' ');
    assert.match(text, /prioridad máxima/i);
    assert.match(text, /retirarse de inmediato/i);
    assert.match(text, /suspendidas/i);
  });

  it('separa contenido sensible permitido de contenido prohibido', () => {
    assert.match(es.sensitiveAllowed, /advertencia o desenfoque/i);
    assert.match(es.sensitiveForbidden, /no es «contenido sensible»/i);
    assert.match(es.sensitiveForbidden, /prohibido/i);
  });

  it('declara que es solo para mayores de 18 y que puede pedir verificación de edad', () => {
    const text = es.age.join(' ');
    assert.match(text, /18 años/);
    assert.match(text, /verificación de edad/i);
    assert.match(text, /restringirla/i);
  });

  it('da el contacto correcto sin datos personales innecesarios', () => {
    assert.equal(es.contactEmail, EMAIL);
    assert.equal(es.contactName, 'Diego Medina');
    assert.equal(es.contactRole, 'Administrador de THERS Social Network');
    const text = everyText(es);
    // Nada de domicilio ni teléfono privado.
    assert.ok(!/domicilio|tel[eé]fono|\+503|calle|colonia/.test(text));
  });

  it('avisa de no enviar material ilegal por correo y que el sistema de reportes es el mecanismo principal', () => {
    assert.match(es.contactWarning, /no envíes ni reenvíes material ilegal/i);
    assert.match(es.contactWarning, /mecanismo principal/i);
  });

  it('menciona el cumplimiento legal y la colaboración con autoridades', () => {
    assert.match(es.legal, /legislación aplicable/i);
    assert.match(es.legal, /autoridades competentes/i);
    assert.match(es.legal, /obligación legal válida/i);
  });

  it('NO afirma tecnologías ni acuerdos que no existen', () => {
    for (const block of [es, en]) {
      const text = everyText(block);
      for (const claim of [
        'photodna',
        'hash',
        'inteligencia artificial',
        'machine learning',
        'detección automática',
        'automatic detection',
        'reconocimiento de imágenes',
        'image recognition',
        'ncmec',
        'convenio',
        'acuerdo con',
        'agreement with',
        '24/7',
      ]) {
        assert.ok(!text.includes(claim), `afirma algo inexistente: ${claim}`);
      }
    }
  });
});

describe('inglés', () => {
  it('tiene exactamente las mismas claves y el mismo número de elementos que el español', () => {
    assert.deepEqual(Object.keys(en), Object.keys(es));
    for (const key of Object.keys(es)) {
      assert.equal(Array.isArray(en[key]), Array.isArray(es[key]), key);
      if (Array.isArray(es[key])) assert.equal(en[key].length, es[key].length, key);
      assert.ok(String(en[key]).trim().length > 0, `vacío: ${key}`);
    }
  });

  it('comparte el mismo contacto', () => {
    assert.equal(en.contactEmail, EMAIL);
    assert.equal(en.contactName, es.contactName);
  });
});

describe('ruta y enlaces', () => {
  const router = read('src/app/router/router.jsx');
  const page = read('src/features/legal/pages/ChildSafety.jsx');

  it('la ruta /child-safety existe', () => {
    assert.match(router, /path="\/child-safety"\s+element=\{<ChildSafety \/>\}/);
  });

  it('es pública: está dentro del layout público y fuera de las rutas protegidas', () => {
    const publicLayout = router.indexOf('<PublicLayout />');
    const route = router.indexOf('path="/child-safety"');
    const protectedRoute = router.indexOf('<ProtectedRoute />');
    assert.ok(publicLayout > -1 && route > publicLayout, 'debe ir después de abrir PublicLayout');
    assert.ok(protectedRoute < publicLayout, 'las rutas protegidas se cierran antes del layout público');
  });

  it('la página no exige sesión (no usa el contexto de autenticación)', () => {
    assert.ok(!/useAuth|ProtectedRoute|getStoredToken/.test(page));
  });

  it('la página muestra el correo como enlace y toma el texto de los locales', () => {
    assert.match(page, /href=\{`mailto:\$\{email\}`\}/);
    assert.match(page, /childSafety\.contactEmail/);
    assert.match(page, /childSafety\.reportCategory/);
  });

  it('el pie de página enlaza a «Seguridad infantil»', () => {
    const footer = read('src/shared/components/Footer/footerLinks.js');
    assert.match(footer, /label: "Seguridad infantil", to: "\/child-safety"/);
  });
});
