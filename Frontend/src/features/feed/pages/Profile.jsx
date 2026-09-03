import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { useNavigate, useOutletContext, useSearchParams } from "react-router-dom";
import {
  IoBookmarkOutline,
  IoChatbubbleOutline,
  IoHeartOutline,
  IoImagesOutline,
  IoMusicalNotesOutline,
  IoSparklesOutline,
} from "react-icons/io5";
import { getErrorMessage } from "@shared/lib/api";
import { useToast } from "@shared/components/Toast";
import { useLanguage } from "@shared/i18n";
import CapsuleCard from "../components/CapsuleCard";
import EditProfileModal from "../components/EditProfileModal";
import ProfileHeader from "../components/ProfileHeader";
import ProfileTabs, { DEFAULT_TAB, isProfileTab } from "../components/ProfileTabs";
import ProfileTopBar from "../components/ProfileTopBar";
import { loadProfile, moveProfile } from "../lib/profileStorage";

// Perfil de THERS con la identidad visual monocroma definida por producto
// (Frontend/src/assets/ideas_perfil.jpeg), la estructura de secciones de una
// red social (perfil_idea.png) y la hoja de edición de editar.png.
//
// Qué es real y qué no, para no mostrar datos falsos:
//   - Publicaciones      -> posts reales (GET /api/posts, ADR-004).
//   - Nombre / usuario   -> reales (PATCH /api/users/me, ADR-003).
//   - Bio, ubicación, sitio web, mood, intereses, portada, acento -> locales
//     (localStorage): no hay columnas ratificadas (DATABASE_ARCHITECTURE.md §4.B).
//   - Seguidores         -> 0 de verdad: no existe la funcionalidad todavía.
//   - Respuestas / Media / Guardados / Me gusta -> secciones vacías declaradas
//     como no disponibles, nunca rellenadas con contenido inventado.
//   - Sin insignia de verificado: no existe como funcionalidad.

function EmptyState({ Icon, title, description }) {
  return (
    <div className="rounded-[28px] border border-line bg-surface px-6 py-14 text-center shadow-soft dark:border-line-dark dark:bg-surface-dark">
      <Icon size={26} className="mx-auto text-muted dark:text-muted-dark" aria-hidden="true" />
      <p className="mt-3 text-sm font-semibold text-ink dark:text-ink-dark">{title}</p>
      <p className="mx-auto mt-1 max-w-sm text-sm text-muted dark:text-muted-dark">{description}</p>
    </div>
  );
}

function PostsSkeleton() {
  return (
    <div className="space-y-4" aria-hidden="true">
      {[0, 1].map((key) => (
        <div
          key={key}
          className="h-40 animate-pulse rounded-[28px] border border-line bg-surface motion-reduce:animate-none dark:border-line-dark dark:bg-surface-dark"
        />
      ))}
    </div>
  );
}

export default function Profile() {
  const { currentUser, capsules, capsulesLoading, followingIds, notifications, onUpdateUser } =
    useOutletContext();
  const toast = useToast();
  const { t } = useLanguage();
  const navigate = useNavigate();
  const editButtonRef = useRef(null);

  const unreadCount = useMemo(
    () => notifications.filter((notification) => !notification.read).length,
    [notifications]
  );

  const [profile, setProfile] = useState(() => loadProfile(currentUser.username));
  const [isEditing, setEditing] = useState(false);
  const [searchParams, setSearchParams] = useSearchParams();

  // La sección activa vive en la URL para que el perfil se pueda compartir y
  // recargar en la sección en la que estaba (?tab=saved).
  const tabParam = searchParams.get("tab");
  const activeTab = isProfileTab(tabParam) ? tabParam : DEFAULT_TAB;

  const handleTabChange = useCallback(
    (id) => {
      const next = new URLSearchParams(searchParams);
      if (id === DEFAULT_TAB) next.delete("tab");
      else next.set("tab", id);
      setSearchParams(next, { replace: true });
    },
    [searchParams, setSearchParams]
  );

  // Si el username cambia (o se abre la sesión con otra cuenta), el perfil
  // extendido que se lee es el de esa cuenta, no el que quedó en memoria.
  useEffect(() => {
    setProfile(loadProfile(currentUser.username));
  }, [currentUser.username]);

  // `capsules` son posts reales (ADR-004): el autor se identifica por
  // `author.id` contra el usuario actual.
  const ownCapsules = useMemo(
    () => capsules.filter((capsule) => capsule.author.id === currentUser.id),
    [capsules, currentUser.id]
  );

  const stats = {
    posts: ownCapsules.length,
    followers: 0,
    following: followingIds.size,
  };

  const closeEditor = () => {
    setEditing(false);
    // El foco vuelve al botón que abrió la hoja, no al principio del documento.
    requestAnimationFrame(() => editButtonRef.current?.focus());
  };

  // name/username los persiste el backend; el resto es local y solo se guarda
  // si el PATCH tuvo éxito, para que la pantalla nunca muestre un cambio que
  // el servidor rechazó. Si el username cambió, el perfil extendido se muda
  // con él (la clave de localStorage lo incluye).
  const handleSave = async ({ name, username, profile: nextProfile }) => {
    const previousUsername = currentUser.username;

    try {
      await onUpdateUser({ name, username });
    } catch (error) {
      toast.error(getErrorMessage(error, t));
      return;
    }

    moveProfile(previousUsername, username, nextProfile);
    setProfile(nextProfile);
    closeEditor();
    toast.success("Perfil actualizado");
  };

  // Copia la URL de esta misma página, no un enlace público inventado: los
  // perfiles de otras personas todavía no tienen ruta propia en THERS.
  const handleShare = async () => {
    try {
      await navigator.clipboard.writeText(window.location.href);
      toast.success("Enlace del perfil copiado");
    } catch {
      toast.error("No se pudo copiar el enlace");
    }
  };

  const hasAbout = profile.interests.length > 0 || Boolean(profile.favoriteTrack);

  const panels = {
    posts: capsulesLoading ? (
      <PostsSkeleton />
    ) : ownCapsules.length > 0 ? (
      <div className="space-y-4">
        {ownCapsules.map((capsule) => (
          <CapsuleCard key={capsule.id} capsule={capsule} />
        ))}
      </div>
    ) : (
      <EmptyState
        Icon={IoSparklesOutline}
        title="Todavía no publicaste nada"
        description="Tu primera Cápsula aparecerá acá y abrirá tu perfil al resto de THERS."
      />
    ),
    replies: (
      <EmptyState
        Icon={IoChatbubbleOutline}
        title="Respuestas"
        description="Responder Cápsulas todavía no está disponible en THERS. Cuando lo esté, tus respuestas se verán en esta sección."
      />
    ),
    media: (
      <EmptyState
        Icon={IoImagesOutline}
        title="Media"
        description="Las Cápsulas todavía son solo texto. Cuando se puedan publicar fotos y videos, aparecerán acá."
      />
    ),
    saved: (
      <EmptyState
        Icon={IoBookmarkOutline}
        title="Guardados"
        description="Guardar Cápsulas todavía no está disponible. Lo que guardes se verá acá, y solo vos podés verlo."
      />
    ),
    likes: (
      <EmptyState
        Icon={IoHeartOutline}
        title="Me gusta"
        description="Los Me gusta todavía no están disponibles en THERS. Cuando lo estén, los tuyos se listarán acá."
      />
    ),
  };

  return (
    <div className="mx-auto max-w-3xl space-y-4">
      {/* Todo el perfil vive en una sola caja -- barra superior, portada,
          identidad, métricas y secciones -- y cada publicación en la suya
          (Frontend/src/assets/ideas_perfil.jpeg). Sin `overflow-hidden` acá:
          recortaría el menú desplegable de la barra superior. */}
      <section className="rounded-[28px] border border-line bg-surface shadow-soft dark:border-line-dark dark:bg-surface-dark">
        <ProfileTopBar
          onOpenSearch={() => navigate("/discover")}
          onCopyLink={handleShare}
          unreadCount={unreadCount}
        />

        <ProfileHeader
          user={currentUser}
          profile={profile}
          stats={stats}
          onEdit={() => setEditing(true)}
          onShare={handleShare}
          editButtonRef={editButtonRef}
        />

        <ProfileTabs active={activeTab} onChange={handleTabChange} />
      </section>

      {hasAbout && (
        <section className="rounded-[28px] border border-line bg-surface p-5 shadow-soft dark:border-line-dark dark:bg-surface-dark">
          <h2 className="text-[11px] font-semibold uppercase tracking-wider text-muted dark:text-muted-dark">
            Acerca de
          </h2>

          {profile.interests.length > 0 && (
            <ul className="mt-3 flex flex-wrap gap-2">
              {profile.interests.map((interest) => (
                <li
                  key={interest}
                  className="rounded-full bg-canvas px-3 py-1.5 text-xs font-medium text-ink dark:bg-canvas-dark dark:text-ink-dark"
                >
                  {interest}
                </li>
              ))}
            </ul>
          )}

          {profile.favoriteTrack && (
            <p className="mt-3 flex items-center gap-2 text-sm text-muted dark:text-muted-dark">
              <IoMusicalNotesOutline size={16} className="shrink-0" aria-hidden="true" />
              <span className="[overflow-wrap:anywhere]">{profile.favoriteTrack}</span>
            </p>
          )}
        </section>
      )}

      <div
        role="tabpanel"
        id={`profile-panel-${activeTab}`}
        aria-labelledby={`profile-tab-${activeTab}`}
        tabIndex={0}
        className="focus:outline-none"
      >
        {panels[activeTab]}
      </div>

      {isEditing && (
        <EditProfileModal
          user={currentUser}
          profile={profile}
          onSave={handleSave}
          onClose={closeEditor}
        />
      )}
    </div>
  );
}
