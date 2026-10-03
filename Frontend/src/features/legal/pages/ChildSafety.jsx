import { useLanguage } from "@shared/i18n";

// Estándares de seguridad infantil (ADR-038-child-safety-reports.md). Página PÚBLICA
// (sin sesión): es el recurso web que Google Play exige a las apps de redes sociales.
//
// Todo el texto vive en los locales (`childSafety.*`, español e inglés) y se prueba
// sin navegador en `Frontend/tests/childSafety.test.mjs`.
//
// Lo que la página AFIRMA debe ser cierto: no menciona detección automática, hash
// matching, IA ni acuerdos con organizaciones, porque nada de eso existe.

function Section({ title, children }) {
  return (
    <section className="mt-10">
      <h2 className="text-lg sm:text-xl font-bold text-ink dark:text-ink-dark">{title}</h2>
      <div className="mt-3 space-y-3 text-muted dark:text-muted-dark leading-relaxed">{children}</div>
    </section>
  );
}

function BulletList({ items }) {
  return (
    <ul className="list-disc pl-6 space-y-1.5">
      {items.map((item) => (
        <li key={item}>{item}</li>
      ))}
    </ul>
  );
}

export default function ChildSafety() {
  const { t, tList } = useLanguage();
  const email = t("childSafety.contactEmail");

  return (
    <div className="max-w-3xl mx-auto px-4 sm:px-6 py-16 sm:py-24">
      <h1 className="text-2xl sm:text-3xl font-extrabold tracking-tight text-ink dark:text-ink-dark">
        {t("childSafety.title")}
      </h1>
      <p className="mt-4 text-muted dark:text-muted-dark leading-relaxed">{t("childSafety.intro")}</p>

      <Section title={t("childSafety.prohibitedTitle")}>
        <p>{t("childSafety.prohibitedIntro")}</p>
        <BulletList items={tList("childSafety.prohibited")} />
      </Section>

      <Section title={t("childSafety.reportTitle")}>
        <p>{t("childSafety.reportIntro")}</p>
        <ol className="list-decimal pl-6 space-y-1.5">
          {tList("childSafety.reportSteps").map((step) => (
            <li key={step}>{step}</li>
          ))}
        </ol>
        <p>
          {t("childSafety.reportCategoryLabel")}:{" "}
          <strong className="text-ink dark:text-ink-dark">{t("childSafety.reportCategory")}</strong>
        </p>
        <p>{t("childSafety.reportAnonymous")}</p>
      </Section>

      <Section title={t("childSafety.handlingTitle")}>
        <BulletList items={tList("childSafety.handling")} />
      </Section>

      <Section title={t("childSafety.sensitiveTitle")}>
        <p>{t("childSafety.sensitiveAllowed")}</p>
        <p className="font-semibold text-ink dark:text-ink-dark">{t("childSafety.sensitiveForbidden")}</p>
      </Section>

      <Section title={t("childSafety.ageTitle")}>
        {tList("childSafety.age").map((paragraph) => (
          <p key={paragraph}>{paragraph}</p>
        ))}
      </Section>

      <Section title={t("childSafety.contactTitle")}>
        <p>
          <strong className="text-ink dark:text-ink-dark">{t("childSafety.contactName")}</strong>
          <br />
          {t("childSafety.contactRole")}
          <br />
          <a
            href={`mailto:${email}`}
            className="text-pulse-600 dark:text-pulse-300 font-semibold hover:underline"
          >
            {email}
          </a>
        </p>
        <p>{t("childSafety.contactWarning")}</p>
      </Section>

      <Section title={t("childSafety.legalTitle")}>
        <p>{t("childSafety.legal")}</p>
      </Section>
    </div>
  );
}
