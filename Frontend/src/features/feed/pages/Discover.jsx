import { useOutletContext } from "react-router-dom";
import { IoMusicalNotes, IoPeopleOutline, IoPricetagOutline } from "react-icons/io5";
import Avatar from "@shared/components/Avatar";
import { MOODS, mockCapsules, mockDiscoverPeople, mockTopics } from "../data/mockData";

const photoCapsules = mockCapsules.filter((c) => c.type === "photo" || c.type === "video");
const musicCapsule = mockCapsules.find((c) => c.type === "music");
const moodEntries = Object.entries(MOODS).slice(0, 4);

export default function Discover() {
  const { followingIds, onToggleFollow } = useOutletContext();

  return (
    <div className="max-w-5xl mx-auto space-y-6">
      <div>
        <h1 className="text-2xl font-extrabold tracking-tight text-ink dark:text-ink-dark">Descubrir</h1>
        <p className="text-muted dark:text-muted-dark text-sm mt-1">
          Cápsulas populares, personas, temas y moods de todo THERS.
        </p>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 auto-rows-[150px]">
        {photoCapsules.map((capsule, index) => (
          <div
            key={`capsule-${capsule.id}`}
            className={`group relative rounded-[24px] overflow-hidden shadow-soft hover:shadow-lift transition-shadow ${
              index === 0 ? "col-span-2 row-span-2" : "col-span-1 row-span-1"
            }`}
          >
            <img
              src={capsule.image}
              alt={capsule.alt || ""}
              loading="lazy"
              className="absolute inset-0 w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
            />
            <div className="absolute inset-0 bg-gradient-to-t from-black/70 via-black/5 to-transparent" />
            <div className="absolute top-3 left-3">
              <Avatar name={capsule.user.name} photo={capsule.user.photo} size="w-8 h-8 text-xs" ring />
            </div>
            <div className="absolute bottom-3 left-3 right-3">
              <p className="text-white text-sm font-semibold drop-shadow truncate">{capsule.user.name}</p>
              <p className="text-white/70 text-xs">{capsule.likes} likes</p>
            </div>
          </div>
        ))}

        {mockDiscoverPeople.map((person) => {
          const isFollowing = followingIds.has(person.id);
          return (
            <div
              key={`person-${person.id}`}
              className="rounded-[24px] bg-surface dark:bg-surface-dark border border-line dark:border-line-dark shadow-soft p-4 flex flex-col items-center justify-center text-center gap-2"
            >
              <Avatar name={person.name} photo={person.photo} size="w-12 h-12" />
              <div>
                <p className="text-ink dark:text-ink-dark text-sm font-semibold truncate max-w-[9rem]">{person.name}</p>
                <p className="text-muted text-xs">@{person.username}</p>
              </div>
              <button
                onClick={() => onToggleFollow(person.id)}
                className={`text-xs font-semibold px-3 py-1 rounded-full border transition ${
                  isFollowing
                    ? "bg-canvas dark:bg-canvas-dark border-line dark:border-line-dark text-muted"
                    : "bg-pulse-600 border-pulse-600 text-white hover:bg-pulse-700"
                }`}
              >
                {isFollowing ? "Siguiendo" : "Seguir"}
              </button>
            </div>
          );
        })}

        {musicCapsule && (
          <div className="col-span-2 row-span-1 rounded-[24px] bg-gradient-to-tr from-ink to-[#2A2A38] p-4 flex items-center gap-3 shadow-soft">
            <div className="w-12 h-12 rounded-full bg-white/10 flex items-center justify-center shrink-0">
              <IoMusicalNotes size={20} className="text-pulse-400" />
            </div>
            <div className="min-w-0">
              <p className="text-white text-sm font-semibold truncate">{musicCapsule.track.title}</p>
              <p className="text-white/60 text-xs truncate">{musicCapsule.track.artist}</p>
            </div>
          </div>
        )}

        {moodEntries.map(([id, mood]) => (
          <div
            key={`mood-${id}`}
            className="rounded-[24px] border border-line dark:border-line-dark shadow-soft p-4 flex flex-col items-center justify-center text-center gap-1"
            style={{ backgroundColor: `${mood.color}14` }}
          >
            <span
              className="w-3 h-3 rounded-full"
              aria-hidden="true"
              style={{ backgroundColor: mood.color }}
            />
            <p className="text-sm font-semibold" style={{ color: mood.color }}>
              {mood.label}
            </p>
          </div>
        ))}
      </div>

      <div className="grid md:grid-cols-2 gap-4">
        <div className="bg-surface dark:bg-surface-dark border border-line dark:border-line-dark rounded-[24px] shadow-soft p-5">
          <h2 className="flex items-center gap-2 text-ink dark:text-ink-dark font-semibold text-sm mb-4">
            <IoPricetagOutline size={18} /> Temas en tendencia
          </h2>
          <div className="flex flex-wrap gap-2">
            {mockTopics.map((topic) => (
              <span
                key={topic.id}
                className="text-sm font-medium px-3 py-1.5 rounded-full bg-pulse-50 dark:bg-pulse-900/30 text-pulse-700 dark:text-pulse-300"
              >
                #{topic.tag} · {topic.capsules}
              </span>
            ))}
          </div>
        </div>

        <div className="bg-surface dark:bg-surface-dark border border-line dark:border-line-dark rounded-[24px] shadow-soft p-5">
          <h2 className="flex items-center gap-2 text-ink dark:text-ink-dark font-semibold text-sm mb-4">
            <IoPeopleOutline size={18} /> Sugerencias para ti
          </h2>
          <p className="text-muted dark:text-muted-dark text-sm">
            Sigue a más personas para que Tu Espacio se llene de Cápsulas que resuenen contigo.
          </p>
        </div>
      </div>
    </div>
  );
}
