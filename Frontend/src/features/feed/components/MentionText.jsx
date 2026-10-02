import { Link } from "react-router-dom";

// Renderiza un texto convirtiendo en enlace solo las menciones REALES
// (ADR-023-mentions.md).
//
// Por qué no basta con buscar /@\w+/ en el texto y enlazarlo todo: el servidor
// ya decidió qué @algo es una mención y qué no. Un @username que no existe, o
// cuyo dueño no autoriza menciones de quien escribió, NO es una mención y no
// debe parecer un enlace — enlazarlo prometería una cuenta que no está ahí.
// Esa decisión viaja en `mentions`, y este componente solo la obedece.
//
// El texto se conserva tal como se escribió (incluidas las mayúsculas del
// @username): lo único que cambia es que los tramos mencionados se vuelven
// enlaces.

/** Escapa los caracteres con significado en una expresión regular. */
function escapeForRegex(value) {
  return value.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
}

export default function MentionText({ content, mentions, className = "" }) {
  if (!mentions || mentions.length === 0) {
    return <span className={className}>{content}</span>;
  }

  // Un solo patrón con todos los usernames autorizados, insensible a
  // mayúsculas porque "@Ada" menciona a `ada` (ADR-023). Los más largos
  // primero: si existen `ana` y `ana_b`, buscar `ana` antes partiría `@ana_b`
  // en un enlace a `ana` seguido de "_b".
  const byLength = [...mentions].sort((a, b) => b.username.length - a.username.length);
  const pattern = new RegExp(
    `@(${byLength.map((m) => escapeForRegex(m.username)).join("|")})\\b`,
    "gi"
  );

  const byUsername = new Map(mentions.map((m) => [m.username.toLowerCase(), m]));

  const parts = [];
  let lastIndex = 0;
  let match;

  while ((match = pattern.exec(content)) !== null) {
    const mention = byUsername.get(match[1].toLowerCase());
    if (!mention) continue;

    if (match.index > lastIndex) {
      parts.push(content.slice(lastIndex, match.index));
    }
    parts.push(
      <Link
        key={`${mention.id}-${match.index}`}
        to={`/profile?user=${encodeURIComponent(mention.username)}`}
        className="font-semibold text-th-brand-fg hover:underline"
      >
        {match[0]}
      </Link>
    );
    lastIndex = match.index + match[0].length;
  }

  if (lastIndex < content.length) {
    parts.push(content.slice(lastIndex));
  }

  return <span className={className}>{parts}</span>;
}
