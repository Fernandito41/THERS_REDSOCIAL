import InformationHero from "../components/InformationHero";
import EditorialCard from "../components/EditorialCard";
import InformationCta from "../components/InformationCta";
import { INFORMATION_CARDS } from "../data/informationContent";

export default function Information() {
  return (
    <div>
      <InformationHero />

      <section className="max-w-6xl mx-auto px-4 sm:px-6 py-12 sm:py-20 space-y-20 sm:space-y-28">
        {INFORMATION_CARDS.map((card, index) => (
          <EditorialCard key={card.id} {...card} reverse={index % 2 === 1} />
        ))}
      </section>

      <InformationCta />
    </div>
  );
}
