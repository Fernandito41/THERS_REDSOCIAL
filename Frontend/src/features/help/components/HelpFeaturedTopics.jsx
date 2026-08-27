import { Link } from "react-router-dom";
import { IoArrowForward } from "react-icons/io5";
import { HELP_FEATURED_TOPICS } from "../data/featuredTopics";
import { getCategoryIcon } from "./helpIcons";

function targetPath(topic) {
  return topic.type === "article" ? `/help/article/${topic.target}` : `/help/category/${topic.target}`;
}

export default function HelpFeaturedTopics() {
  return (
    <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-3">
      {HELP_FEATURED_TOPICS.map((topic) => {
        const Icon = getCategoryIcon(topic.icon);
        return (
          <Link
            key={topic.id}
            to={targetPath(topic)}
            className="group relative overflow-hidden rounded-2xl border border-line dark:border-line-dark bg-surface dark:bg-surface-dark p-4 h-32 flex flex-col justify-between hover:shadow-lift transition-shadow"
          >
            <Icon size={20} className="text-pulse-500" aria-hidden="true" />
            <span>
              <span className="block text-sm font-semibold text-ink dark:text-ink-dark leading-snug">
                {topic.title}
              </span>
              <span className="mt-1 flex items-center gap-1 text-xs text-muted dark:text-muted-dark group-hover:text-pulse-600 dark:group-hover:text-pulse-300 transition-colors">
                Explorar <IoArrowForward size={12} aria-hidden="true" />
              </span>
            </span>
          </Link>
        );
      })}
    </div>
  );
}
