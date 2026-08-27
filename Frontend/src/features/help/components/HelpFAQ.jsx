import { useState } from "react";
import { HELP_FAQS } from "../data/faqs";
import HelpFAQItem from "./HelpFAQItem";

export default function HelpFAQ({ faqs = HELP_FAQS, title = "Preguntas frecuentes" }) {
  const [openId, setOpenId] = useState(null);

  if (faqs.length === 0) return null;

  return (
    <section aria-labelledby="help-faq-heading">
      <h2 id="help-faq-heading" className="text-lg font-bold tracking-tight text-ink dark:text-ink-dark mb-3">
        {title}
      </h2>
      <div className="rounded-2xl border border-line dark:border-line-dark bg-surface dark:bg-surface-dark px-5">
        {faqs.map((faq) => (
          <HelpFAQItem
            key={faq.id}
            faq={faq}
            isOpen={openId === faq.id}
            onToggle={() => setOpenId((prev) => (prev === faq.id ? null : faq.id))}
          />
        ))}
      </div>
    </section>
  );
}
