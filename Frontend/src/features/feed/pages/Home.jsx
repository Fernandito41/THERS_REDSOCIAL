import { useOutletContext } from "react-router-dom";
import { IoImageOutline, IoMusicalNotesOutline, IoHappyOutline, IoSparklesOutline } from "react-icons/io5";
import Avatar from "@shared/components/Avatar";
import Spinner from "@shared/components/Spinner";
import MomentsRow from "../components/MomentsRow";
import PulseBar from "../components/PulseBar";
import CapsuleCard from "../components/CapsuleCard";
import { mockSuggestions, mockTopics } from "../data/mockData";

export default function Home() {
  const { currentUser, capsules, capsulesLoading, followingIds, onToggleFollow, onOpenComposer } =
    useOutletContext();

  const firstName = currentUser.name.split(" ")[0];

  return (
    <div className="flex gap-6">
      <div className="flex-1 min-w-0 max-w-2xl mx-auto xl:mx-0 space-y-6">
        <MomentsRow currentUser={currentUser} />

        <PulseBar />

        <div className="flex items-center gap-3">
          <button
            onClick={onOpenComposer}
            className="flex-1 flex items-center gap-3 bg-surface dark:bg-surface-dark border border-line dark:border-line-dark rounded-full pl-2 pr-5 py-2 shadow-soft hover:shadow-lift transition-shadow text-left"
          >
            <Avatar name={currentUser.name} size="w-9 h-9" />
            <span className="text-muted dark:text-muted-dark text-sm">
              ¿Qué quieres expresar, {firstName}?
            </span>
            <span className="ml-auto flex items-center gap-1 text-muted">
              <IoImageOutline size={16} />
              <IoMusicalNotesOutline size={16} />
              <IoHappyOutline size={16} />
            </span>
          </button>
        </div>

        {capsulesLoading ? (
          <div className="flex items-center justify-center gap-2 text-muted dark:text-muted-dark py-16">
            <Spinner size={20} />
            <span className="text-sm">Cargando cápsulas...</span>
          </div>
        ) : capsules.length === 0 ? (
          <div className="flex flex-col items-center text-center gap-3 bg-surface dark:bg-surface-dark border border-dashed border-line dark:border-line-dark rounded-[28px] py-16 px-8">
            <span className="w-12 h-12 rounded-full bg-pulse-50 dark:bg-pulse-900/30 flex items-center justify-center text-pulse-600 dark:text-pulse-300">
              <IoSparklesOutline size={22} />
            </span>
            <p className="text-ink dark:text-ink-dark font-semibold">Todavía no hay cápsulas por acá</p>
            <p className="text-muted dark:text-muted-dark text-sm max-w-xs">
              Sé el primero en publicar algo y dale vida a este espacio.
            </p>
            <button
              onClick={onOpenComposer}
              className="mt-1 px-5 py-2.5 rounded-full text-sm font-semibold bg-pulse-600 hover:bg-pulse-700 text-white shadow-glow transition"
            >
              Sé el primero en publicar
            </button>
          </div>
        ) : (
          <div className="space-y-6">
            {capsules.map((capsule) => (
              <CapsuleCard key={capsule.id} capsule={capsule} />
            ))}
          </div>
        )}
      </div>

      <aside className="hidden xl:flex flex-col gap-6 w-80 shrink-0 sticky top-24 self-start">
        <div className="bg-surface dark:bg-surface-dark border border-line dark:border-line-dark rounded-[28px] shadow-soft p-5 flex items-center gap-3">
          <Avatar name={currentUser.name} size="w-12 h-12" />
          <div className="min-w-0">
            <p className="text-ink dark:text-ink-dark font-semibold truncate">{currentUser.name}</p>
            <p className="text-muted text-sm truncate">@{currentUser.username}</p>
          </div>
        </div>

        <div className="bg-surface dark:bg-surface-dark border border-line dark:border-line-dark rounded-[28px] shadow-soft p-5">
          <h3 className="text-ink dark:text-ink-dark font-semibold text-sm mb-4">Personas que resuenan contigo</h3>

          <div className="space-y-4">
            {mockSuggestions.map((person) => {
              const isFollowing = followingIds.has(person.id);
              return (
                <div key={person.id} className="flex items-center justify-between gap-2">
                  <div className="flex items-center gap-2 min-w-0">
                    <Avatar name={person.name} photo={person.photo} size="w-9 h-9 text-sm" />
                    <div className="min-w-0">
                      <p className="text-ink dark:text-ink-dark text-sm truncate">{person.name}</p>
                      <p className="text-muted text-xs truncate">@{person.username}</p>
                    </div>
                  </div>

                  <button
                    onClick={() => onToggleFollow(person.id)}
                    className={`shrink-0 text-xs font-semibold px-3 py-1.5 rounded-full border transition ${
                      isFollowing
                        ? "bg-canvas dark:bg-canvas-dark border-line dark:border-line-dark text-muted hover:bg-line dark:hover:bg-line-dark"
                        : "bg-pulse-600 border-pulse-600 text-white hover:bg-pulse-700"
                    }`}
                  >
                    {isFollowing ? "Siguiendo" : "Seguir"}
                  </button>
                </div>
              );
            })}
          </div>
        </div>

        <div className="bg-surface dark:bg-surface-dark border border-line dark:border-line-dark rounded-[28px] shadow-soft p-5">
          <h3 className="text-ink dark:text-ink-dark font-semibold text-sm mb-4">Temas en tendencia</h3>
          <div className="space-y-3">
            {mockTopics.map((topic) => (
              <div key={topic.id} className="flex items-center justify-between text-sm">
                <span className="text-pulse-600 dark:text-pulse-300 font-medium">#{topic.tag}</span>
                <span className="text-muted text-xs">{topic.capsules} cápsulas</span>
              </div>
            ))}
          </div>
        </div>
      </aside>
    </div>
  );
}
