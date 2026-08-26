import { Link } from "react-router-dom";
import MediaPlaceholder from "./MediaPlaceholder";
import RevealOnScroll from "./RevealOnScroll";

export default function EditorialCard({
  title,
  description,
  tag,
  mediaType,
  mediaSrc,
  mediaPoster,
  mediaAlt,
  reverse,
  ctaLabel,
  ctaTo,
}) {
  const media = (
    <MediaPlaceholder
      type={mediaType}
      src={mediaSrc}
      poster={mediaPoster}
      alt={mediaAlt || title}
      className="aspect-[4/3] w-full"
    />
  );

  const content = (
    <div>
      <span className="inline-block text-xs font-semibold text-pulse-600 dark:text-pulse-300 bg-pulse-50 dark:bg-pulse-900/30 rounded-full px-3 py-1">
        {tag}
      </span>
      <h3 className="mt-4 text-2xl sm:text-3xl font-extrabold tracking-tight text-ink dark:text-ink-dark">
        {title}
      </h3>
      <p className="mt-3 text-muted dark:text-muted-dark max-w-md">{description}</p>
      {ctaLabel && ctaTo && (
        <Link
          to={ctaTo}
          className="mt-5 inline-flex items-center gap-1.5 text-sm font-semibold text-pulse-600 dark:text-pulse-300 hover:underline"
        >
          {ctaLabel} <span aria-hidden="true">→</span>
        </Link>
      )}
    </div>
  );

  return (
    <RevealOnScroll className="grid gap-8 md:grid-cols-2 items-center">
      {reverse ? (
        <>
          <div className="md:order-2">{media}</div>
          <div className="md:order-1">{content}</div>
        </>
      ) : (
        <>
          {media}
          {content}
        </>
      )}
    </RevealOnScroll>
  );
}
