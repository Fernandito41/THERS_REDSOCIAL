import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { useOutletContext, useSearchParams } from "react-router-dom";
import Icon from "@shared/components/Icon";
import { getErrorMessage } from "@shared/lib/api";
import { useToast } from "@shared/components/Toast";
import { useLanguage } from "@shared/i18n";
import CapsuleCard from "../components/CapsuleCard";
import EditProfileModal from "../components/EditProfileModal";
import ProfileCover from "../components/ProfileCover";
import ProfileIdentity from "../components/ProfileIdentity";
import ProfileCollections from "../components/ProfileCollections";
import ProfileRail from "../components/ProfileRail";
import ProfileTabs, { DEFAULT_TAB, isProfileTab } from "../components/ProfileTabs";
import { loadProfile, moveProfile } from "../lib/profileStorage";

// Perfil propio — REF-PROFILE-01.
//
// Orden de secciones tomado de la referencia:
//   1. Portada, con acción de cambiarla
//   2. Avatar superpuesto + identidad + Editar/Compartir/Más
//   3. Biografía, metadatos y métricas
//   4. Colecciones Destacadas
//   5. Tabs Publicaciones / Destacadas / Me gusta
//   6. Stream de contenido
//   + rail derecho de actividad
//
// QUÉ ES REAL — el archivo maestro §8.3 exige que la cuenta propia venga de
// la sesión, nunca de la maqueta de «Cristopher Stanley»:
//   · Publicaciones          GET /api/posts (ADR-004), filtradas por autor
//   · Nombre / usuario       GET/PATCH /api/users/me (ADR-002/003)
//   · Seguidores / Siguiendo GET /api/users/me (ADR-007)
//   · Likes y comentarios    reales en cada tarjeta (ADR-005/006)
//   · Bio, ubicación, enlace, portada, acento -> LOCALES (localStorage),
//     porque PATCH /api/users/me solo acepta name/username/phone/
//     country_code/birth_date y no hay columnas ratificadas para el resto
//     (DATABASE_ARCHITECTURE.md §4.B). Ya era así; no se inventa contrato.
//
// La referencia aparece con la tab «Me gusta» seleccionada. La pestaña
// inicial de la aplicación sigue siendo «Publicaciones» —comportamiento de
// producto ya definido por la URL `?tab=`, que el archivo maestro §8.3
// permite conservar—; el estado de la captura se reproduce en QA con
// `?tab=likes`.

export default function Profile() {
  const {
    currentUser,
    capsules,
    capsulesLoading,
    onUpdateUser,
    onToggleLike,
    onLoadComments,
    onPostComment,
    onToggleFollowAuthor,
  } = useOutletContext();
  const toast = useToast();
  const { t } = useLanguage();
  const editButtonRef = useRef(null);

  const [profile, setProfile] = useState(() => loadProfile(currentUser.username));
  const [isEditing, setEditing] = useState(false);
  const [searchParams, setSearchParams] = useSearchParams();

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

  useEffect(() => {
    setProfile(loadProfile(currentUser.username));
  }, [currentUser.username]);

  const ownCapsules = useMemo(
    () => capsules.filter((capsule) => capsule.author.id === currentUser.id),
    [capsules, currentUser.id]
  );

  const stats = {
    posts: ownCapsules.length,
    followers: currentUser.followers_count ?? 0,
    following: currentUser.following_count ?? 0,
  };

  const closeEditor = () => {
    setEditing(false);
    requestAnimationFrame(() => editButtonRef.current?.focus());
  };

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

  const hasAbout = profile.interests.length > 0 || Boolean(profile.favoriteTrack);

  // Copia la URL de esta misma página, no un enlace público inventado.
  const handleShare = async () => {
    try {
      await navigator.clipboard.writeText(window.location.href);
      toast.success("Enlace del perfil copiado");
    } catch {
      toast.error("No se pudo copiar el enlace");
    }
  };

  const panels = {
    posts: capsulesLoading ? (
      <PostsSkeleton />
    ) : ownCapsules.length > 0 ? (
      <div className="flex flex-col gap-6">
        {ownCapsules.map((capsule) => (
          <CapsuleCard
            key={capsule.id}
            capsule={capsule}
            currentUserId={currentUser.id}
            onToggleLike={onToggleLike}
            onLoadComments={onLoadComments}
            onPostComment={onPostComment}
            onToggleFollowAuthor={onToggleFollowAuthor}
          />
        ))}
      </div>
    ) : (
      <EmptyState
        icon="auto_awesome"
        title="Todavía no publicaste nada"
        description="Tu primera Cápsula aparecerá acá y abrirá tu perfil al resto de THERS."
      />
    ),

    featured: (
      <EmptyState
        icon="star"
        title="Destacadas"
        description="Destacar publicaciones todavía no está disponible: no existe el modelo que las guardaría."
      />
    ),

    likes: (
      <div className="flex flex-col gap-4">
        {/* Aviso «Solo tú»: está en la referencia y es una etiqueta de
            privacidad, no un adorno. El archivo maestro §8.3 recuerda que la
            privacidad de favoritos debe aplicarse también en el servidor, no
            solo ocultando elementos -- aquí no hay nada que ocultar todavía
            porque la capacidad no existe. */}
        <div className="flex items-start gap-3 rounded-th-card border border-th-border bg-th-surface-subtle p-4">
          <Icon name="lock" size={18} className="mt-0.5 shrink-0 text-th-fg-muted" />
          <div className="flex flex-col gap-1">
            <p className="text-body-md text-th-fg">
              <span className="font-bold">Tu archivo personal de favoritos.</span> Aquí verías las
              publicaciones y cápsulas a las que les diste «Me gusta».
            </p>
            <span className="inline-flex w-fit items-center gap-1 rounded-th-pill bg-th-surface-raised px-2.5 py-0.5 text-label-md font-bold text-th-fg-muted">
              <Icon name="visibility_off" size={14} />
              Solo tú
            </span>
          </div>
        </div>

        <EmptyState
          icon="favorite"
          title="Me gusta"
          description="No hay endpoint que liste tus me gusta: el backend registra el like sobre cada publicación (ADR-005), pero todavía no permite recuperarlos como colección."
        />
      </div>
    ),
  };

  return (
    <div className="mx-auto flex w-full max-w-[1400px] flex-col gap-6 py-4 xl:flex-row">
      <div className="flex w-full min-w-0 flex-1 flex-col gap-6">
        <ProfileCover cover={profile.cover} onChangeCover={() => setEditing(true)} />

        <ProfileIdentity
          user={currentUser}
          profile={profile}
          stats={stats}
          onEdit={() => setEditing(true)}
          onShare={handleShare}
          editButtonRef={editButtonRef}
        />

        {hasAbout && (
          <section className="rounded-th-card border border-th-border bg-th-surface p-5 shadow-th-card">
            <h2 className="text-label-sm font-bold uppercase tracking-wider text-th-fg-muted">
              Acerca de
            </h2>

            {profile.interests.length > 0 && (
              <ul className="mt-3 flex flex-wrap gap-2">
                {profile.interests.map((interest) => (
                  <li
                    key={interest}
                    className="rounded-th-pill bg-th-surface-raised px-3 py-1.5 text-label-md text-th-fg"
                  >
                    {interest}
                  </li>
                ))}
              </ul>
            )}

            {profile.favoriteTrack && (
              <p className="mt-3 flex items-center gap-2 text-body-sm text-th-fg-muted">
                <Icon name="music_note" size={16} className="shrink-0" />
                <span className="[overflow-wrap:anywhere]">{profile.favoriteTrack}</span>
              </p>
            )}
          </section>
        )}

        <ProfileCollections />

        <div className="flex flex-col gap-6">
          <ProfileTabs active={activeTab} onChange={handleTabChange} counts={{ posts: stats.posts }} />

          <div
            role="tabpanel"
            id={`profile-panel-${activeTab}`}
            aria-labelledby={`profile-tab-${activeTab}`}
            tabIndex={0}
            className="focus:outline-none"
          >
            {panels[activeTab]}
          </div>
        </div>
      </div>

      <ProfileRail ownCapsules={ownCapsules} />

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

function EmptyState({ icon, title, description }) {
  return (
    <div className="flex flex-col items-center gap-2 rounded-th-card border border-dashed border-th-border bg-th-surface px-6 py-14 text-center">
      <Icon name={icon} size={26} className="text-th-fg-subtle" />
      <p className="text-label-lg font-bold text-th-fg-strong">{title}</p>
      <p className="max-w-md text-body-md text-th-fg-muted">{description}</p>
    </div>
  );
}

function PostsSkeleton() {
  return (
    <div className="flex flex-col gap-6" aria-hidden="true">
      {[0, 1].map((key) => (
        <div
          key={key}
          className="h-40 animate-pulse rounded-th-card border border-th-border bg-th-surface motion-reduce:animate-none"
        />
      ))}
    </div>
  );
}
