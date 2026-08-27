import { IoInformationCircleOutline } from "react-icons/io5";

// Id estable (no useId()) porque HelpArticlePage arma la tabla de contenidos
// con estos mismos ids en un componente separado -- deben coincidir para que
// los enlaces de anclaje funcionen.
export function sectionHeadingId(index) {
  return `article-section-${index}`;
}

function SectionHeading({ id, text }) {
  return (
    <h2 id={id} className="text-base font-bold text-ink dark:text-ink-dark mt-8 mb-3 scroll-mt-24">
      {text}
    </h2>
  );
}

export default function HelpArticleContent({ sections }) {
  return (
    <div className="space-y-1">
      {sections.map((section, index) => {
        const headingId = section.heading ? sectionHeadingId(index) : undefined;

        if (section.type === "note") {
          return (
            <div
              key={index}
              className="flex items-start gap-2.5 rounded-xl bg-pulse-50 dark:bg-pulse-900/20 px-4 py-3 my-4 text-sm text-ink dark:text-ink-dark"
            >
              <IoInformationCircleOutline size={17} className="shrink-0 mt-0.5 text-pulse-500" aria-hidden="true" />
              <p>{section.text}</p>
            </div>
          );
        }

        return (
          <div key={index}>
            {section.heading && <SectionHeading id={headingId} text={section.heading} />}

            {section.type === "p" && (
              <p className="text-sm leading-relaxed text-ink/90 dark:text-ink-dark/90">{section.text}</p>
            )}

            {section.type === "steps" && (
              <ol className="list-decimal list-outside pl-5 space-y-2 text-sm leading-relaxed text-ink/90 dark:text-ink-dark/90">
                {section.items.map((item, i) => (
                  <li key={i}>{item}</li>
                ))}
              </ol>
            )}

            {section.type === "list" && (
              <ul className="list-disc list-outside pl-5 space-y-2 text-sm leading-relaxed text-ink/90 dark:text-ink-dark/90">
                {section.items.map((item, i) => (
                  <li key={i}>{item}</li>
                ))}
              </ul>
            )}
          </div>
        );
      })}
    </div>
  );
}

export function getTableOfContents(sections) {
  return sections
    .map((section, index) => ({ heading: section.heading, id: sectionHeadingId(index) }))
    .filter((entry) => entry.heading);
}
