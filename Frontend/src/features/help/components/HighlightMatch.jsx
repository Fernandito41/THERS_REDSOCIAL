function escapeRegExp(value) {
  return value.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
}

// Resalta la primera coincidencia de `query` dentro de `text` -- usado en
// resultados de búsqueda para mostrar por qué un artículo coincidió.
export default function HighlightMatch({ text, query }) {
  const trimmed = (query || "").trim();
  if (!trimmed) return <>{text}</>;

  const pattern = new RegExp(`(${escapeRegExp(trimmed)})`, "ig");
  const parts = text.split(pattern);

  if (parts.length === 1) return <>{text}</>;

  return (
    <>
      {parts.map((part, index) =>
        part.toLowerCase() === trimmed.toLowerCase() ? (
          <mark
            key={index}
            className="bg-pulse-100 dark:bg-pulse-900/50 text-pulse-800 dark:text-pulse-200 rounded-sm px-0.5"
          >
            {part}
          </mark>
        ) : (
          <span key={index}>{part}</span>
        )
      )}
    </>
  );
}
