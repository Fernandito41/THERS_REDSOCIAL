import { IoLinkOutline, IoLocationOutline, IoPencilOutline, IoShareOutline } from "react-icons/io5";
import Avatar from "@shared/components/Avatar";
import MoodBadge from "./MoodBadge";
import { coverGradient } from "../data/profileIdentity";
import { websiteHref } from "../lib/profileStorage";

// Cabecera del perfil: portada + avatar montado sobre ella + identidad +
// métricas, siguiendo la identidad monocroma de THERS
// (Frontend/src/assets/ideas_perfil.jpeg). Sin insignia de verificado: no
// existe como funcionalidad y mostrarla sería un dato falso.
//
// No se muestra fecha de alta ("se unió en...") a propósito: el usuario
// público que devuelve el backend (to_public_user, API_CONTRACT.md §5) no
// incluye `created_at`, y no se inventa.

function Stat({ value, label }) {
  return (
    <div className="flex flex-col">
      <span className="text-lg font-bold leading-tight tabular-nums text-ink dark:text-ink-dark">
        {value.toLocaleString()}
      </span>
      <span className="text-xs text-muted dark:text-muted-dark">{label}</span>
    </div>
  );
}

export default function ProfileHeader({ user, profile, stats, onEdit, onShare, editButtonRef }) {
  const href = websiteHref(profile.website);

  return (
    <>
      <div
        className="h-32 sm:h-44"
        style={{ backgroundImage: coverGradient(profile.cover) }}
        aria-hidden="true"
      />

      <div className="px-5 pb-5 sm:px-7">
        <div className="flex items-end justify-between gap-3">
          <div className="-mt-12 rounded-full ring-4 ring-surface dark:ring-surface-dark sm:-mt-16">
            <Avatar
              name={user.name}
              size="w-24 h-24 sm:w-28 sm:h-28 text-3xl sm:text-4xl"
              color={profile.accent}
            />
          </div>

          <div className="mb-1 flex items-center gap-2">
            <button
              ref={editButtonRef}
              type="button"
              onClick={onEdit}
              className="flex h-11 cursor-pointer items-center gap-1.5 rounded-full border border-line px-4 text-sm font-semibold text-ink transition hover:bg-canvas active:scale-[0.98] dark:border-line-dark dark:text-ink-dark dark:hover:bg-canvas-dark"
            >
              <IoPencilOutline size={15} aria-hidden="true" /> Editar perfil
            </button>

            <button
              type="button"
              onClick={onShare}
              aria-label="Copiar enlace del perfil"
              className="flex h-11 w-11 shrink-0 cursor-pointer items-center justify-center rounded-full border border-line text-ink transition hover:bg-canvas active:scale-[0.98] dark:border-line-dark dark:text-ink-dark dark:hover:bg-canvas-dark"
            >
              <IoShareOutline size={18} aria-hidden="true" />
            </button>
          </div>
        </div>

        <div className="mt-4 flex flex-wrap items-center gap-x-2 gap-y-1">
          <h1 className="text-2xl font-extrabold tracking-tight text-ink dark:text-ink-dark">
            {user.name}
          </h1>
          {profile.mood && <MoodBadge mood={profile.mood} glow />}
        </div>
        <p className="text-sm text-muted dark:text-muted-dark">@{user.username}</p>

        {profile.bio ? (
          <p className="mt-3 max-w-prose whitespace-pre-line text-[15px] leading-relaxed text-ink/90 dark:text-ink-dark/90">
            {profile.bio}
          </p>
        ) : (
          <button
            type="button"
            onClick={onEdit}
            className="mt-3 cursor-pointer text-left text-sm text-muted underline underline-offset-4 transition hover:text-ink dark:text-muted-dark dark:hover:text-ink-dark"
          >
            Agrega una presentación a tu perfil
          </button>
        )}

        {(profile.location || href) && (
          <div className="mt-3 flex flex-wrap items-center gap-x-5 gap-y-1.5 text-sm text-muted dark:text-muted-dark">
            {profile.location && (
              <span className="flex min-w-0 items-center gap-1.5">
                <IoLocationOutline size={16} className="shrink-0" aria-hidden="true" />
                <span className="truncate">{profile.location}</span>
              </span>
            )}
            {href && (
              <a
                href={href}
                target="_blank"
                rel="noopener noreferrer"
                className="flex min-w-0 items-center gap-1.5 text-ink transition hover:underline dark:text-ink-dark"
              >
                <IoLinkOutline size={16} className="shrink-0" aria-hidden="true" />
                <span className="truncate [overflow-wrap:anywhere]">{profile.website.trim()}</span>
              </a>
            )}
          </div>
        )}

        <div className="mt-5 flex flex-wrap gap-x-8 gap-y-3">
          <Stat value={stats.posts} label="Publicaciones" />
          <Stat value={stats.followers} label="Seguidores" />
          <Stat value={stats.following} label="Siguiendo" />
        </div>
      </div>
    </>
  );
}
