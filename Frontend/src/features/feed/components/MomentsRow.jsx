import { useState } from "react";
import { IoAdd } from "react-icons/io5";
import Avatar from "@shared/components/Avatar";
import MomentViewer from "./MomentViewer";
import { MOODS, mockMoments } from "../data/mockData";

export default function MomentsRow({ currentUser }) {
  const [activeIndex, setActiveIndex] = useState(null);

  return (
    <section aria-label="Momentos">
      <div className="flex items-baseline justify-between mb-3">
        <h2 className="text-[11px] font-semibold uppercase tracking-wider text-muted dark:text-muted-dark">
          Momentos
        </h2>
      </div>

      <div className="flex gap-3 overflow-x-auto no-scrollbar pb-1 -mx-1 px-1">
        <div className="relative shrink-0 w-32 h-48 rounded-[24px] overflow-hidden bg-surface dark:bg-surface-dark border border-line dark:border-line-dark flex flex-col items-center justify-center cursor-pointer group shadow-soft hover:shadow-lift transition-shadow">
          <div className="relative">
            <Avatar name={currentUser.name} size="w-14 h-14 text-lg" />
            <span className="absolute -bottom-1 -right-1 bg-pulse-500 group-hover:bg-pulse-600 transition rounded-full w-7 h-7 flex items-center justify-center border-2 border-surface dark:border-surface-dark">
              <IoAdd size={16} className="text-white" />
            </span>
          </div>
          <span className="text-xs text-ink dark:text-ink-dark mt-3 font-semibold">Tu momento</span>
        </div>

        {mockMoments.map((moment, index) => (
          <button
            key={moment.id}
            onClick={() => setActiveIndex(index)}
            aria-label={`Ver el momento de ${moment.name}, mood ${MOODS[moment.mood]?.label || ""}`}
            className="group relative shrink-0 w-32 h-48 rounded-[24px] overflow-hidden ring-2 ring-transparent hover:ring-pulse-400 transition-all animate-capsule-in shadow-soft"
          >
            <img
              src={moment.image}
              alt=""
              loading="lazy"
              className="absolute inset-0 w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
            />
            <div className="absolute inset-0 bg-gradient-to-t from-black/70 via-black/10 to-black/10" />

            <div className="absolute top-3 left-3">
              <Avatar name={moment.name} photo={moment.photo} size="w-9 h-9 text-xs" ring />
            </div>

            <span
              className="absolute top-3 right-3 w-2.5 h-2.5 rounded-full ring-2 ring-white/80"
              aria-hidden="true"
              style={{ backgroundColor: MOODS[moment.mood]?.color }}
            />

            <div className="absolute bottom-3 left-3 right-3 text-left">
              <p className="text-white text-sm font-semibold drop-shadow">{moment.name}</p>
              <p className="text-white/70 text-[11px]">{moment.time}</p>
            </div>
          </button>
        ))}
      </div>

      {activeIndex !== null && (
        <MomentViewer
          moments={mockMoments}
          index={activeIndex}
          onClose={() => setActiveIndex(null)}
          onPrev={() => setActiveIndex((i) => Math.max(0, i - 1))}
          onNext={() => setActiveIndex((i) => Math.min(mockMoments.length - 1, i + 1))}
        />
      )}
    </section>
  );
}
