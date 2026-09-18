import { useOutletContext } from "react-router-dom";
import Icon from "@shared/components/Icon";
import Spinner from "@shared/components/Spinner";
import MomentsRow from "../components/MomentsRow";
import PulseBar from "../components/PulseBar";
import FeedComposer from "../components/FeedComposer";
import DiscoveryRail from "../components/DiscoveryRail";
import CapsuleCard from "../components/CapsuleCard";

/**
 * Inicio / Feed — REF-FEED-01.
 *
 * Orden de secciones tomado literalmente de la referencia:
 *   1. Momentos (carrusel)
 *   2. PULSE (franja de actividad)
 *   3. Compositor
 *   4. Stream de publicaciones
 *   + rail derecho de descubrimiento (≈340px)
 *
 * MEDIDAS: columna central `max-w-th-feed` (700px, el valor literal
 * `xl:max-w-[700px]` de la referencia) y rail `w-th-rail` (340px). Ambas
 * salen de tokens.css, no de valores sueltos.
 *
 * EXCEPCIÓN DOCUMENTADA: la captura de REF-FEED-01 muestra el rail derecho
 * recortado porque el prototipo fuerza tres columnas antes de que quepan.
 * Aquí el rail solo se coloca al lado a partir de `xl` (1280px), donde
 * 288 + 700 + 340 + separaciones sí caben; por debajo se apila. El archivo
 * maestro §6.2 pide expresamente calcular el espacio útil y §1 prohíbe
 * reproducir un desbordamiento del prototipo como si fuera un requisito.
 */
export default function Home() {
  const {
    currentUser,
    capsules,
    capsulesLoading,
    followingIds,
    onToggleFollow,
    onOpenComposer,
    onToggleLike,
    onLoadComments,
    onPostComment,
    onToggleFollowAuthor,
  } = useOutletContext();

  return (
    <div className="mx-auto flex w-full max-w-[1400px] flex-col gap-6 py-4 xl:flex-row">
      <div className="flex w-full min-w-0 flex-1 flex-col gap-6 xl:max-w-th-feed">
        <MomentsRow currentUser={currentUser} />

        <PulseBar />

        <FeedComposer currentUser={currentUser} onOpenComposer={onOpenComposer} />

        <div className="flex flex-col gap-6">
          {capsulesLoading ? (
            <div
              className="flex items-center justify-center gap-2 py-16 text-th-fg-muted"
              role="status"
            >
              <Spinner size={20} />
              <span className="text-body-md">Cargando cápsulas...</span>
            </div>
          ) : capsules.length === 0 ? (
            <div className="flex flex-col items-center gap-3 rounded-th-card border border-dashed border-th-border bg-th-surface px-8 py-16 text-center">
              <span className="flex h-12 w-12 items-center justify-center rounded-th-pill bg-th-brand-soft text-th-brand">
                <Icon name="auto_awesome" size={24} />
              </span>
              <p className="text-headline-sm text-th-fg-strong">
                Todavía no hay cápsulas por acá
              </p>
              <p className="max-w-xs text-body-md text-th-fg-muted">
                Sé el primero en publicar algo y dale vida a este espacio.
              </p>
              <button
                type="button"
                onClick={onOpenComposer}
                className="mt-1 rounded-th-pill bg-th-brand px-5 py-2.5 text-label-lg font-bold text-th-on-brand shadow-th-card transition-colors th-focus-ring hover:bg-th-brand-hover"
              >
                Sé el primero en publicar
              </button>
            </div>
          ) : (
            capsules.map((capsule) => (
              <CapsuleCard
                key={capsule.id}
                capsule={capsule}
                currentUserId={currentUser.id}
                onToggleLike={onToggleLike}
                onLoadComments={onLoadComments}
                onPostComment={onPostComment}
                onToggleFollowAuthor={onToggleFollowAuthor}
              />
            ))
          )}
        </div>
      </div>

      <DiscoveryRail
        currentUser={currentUser}
        capsules={capsules}
        followingIds={followingIds}
        onToggleFollow={onToggleFollow}
      />
    </div>
  );
}
