import { useMemo, useState } from "react";
import { useOutletContext } from "react-router-dom";
import { IoAdd, IoClose, IoMusicalNotesOutline, IoPencilOutline } from "react-icons/io5";
import Avatar from "@shared/components/Avatar";
import MoodBadge from "../components/MoodBadge";
import CapsuleCard from "../components/CapsuleCard";
import { MOODS } from "../data/mockData";

const BANNERS = [
  "from-pulse-500 to-pulse-300",
  "from-pulse-800 to-pulse-400",
  "from-pulse-700 to-pulse-400",
  "from-pulse-900 to-pulse-600",
];

// Tonos verificados con contraste >= 4.5:1 sobre texto blanco (WCAG AA).
const ACCENTS = ["#9333ea", "#7e22ce", "#a21caf", "#3b5bdb"];

// Perfil editable, exclusivamente local (localStorage) -- no hay backend/columnas
// ratificadas para bio/mood/intereses todavía (DATABASE_ARCHITECTURE.md §4.B).
// Nunca se precarga con datos inventados: todo empieza vacío hasta que la persona
// lo completa ella misma.
function loadProfile(username) {
  try {
    const raw = localStorage.getItem(`thers_profile_${username}`);
    return raw ? JSON.parse(raw) : null;
  } catch {
    return null;
  }
}

function saveProfile(username, profile) {
  localStorage.setItem(`thers_profile_${username}`, JSON.stringify(profile));
}

export default function Profile() {
  const { currentUser, capsules, followingIds, onUpdateUser } = useOutletContext();

  const [profile, setProfile] = useState(
    () =>
      loadProfile(currentUser.username) || {
        bio: "",
        mood: null,
        interests: [],
        favoriteTrack: "",
        banner: BANNERS[0],
        accent: ACCENTS[0],
      }
  );
  const [editingIdentity, setEditingIdentity] = useState(false);
  const [nameDraft, setNameDraft] = useState(currentUser.name);
  const [usernameDraft, setUsernameDraft] = useState(currentUser.username);
  const [bioDraft, setBioDraft] = useState(profile.bio);
  const [interestDraft, setInterestDraft] = useState("");

  const update = (patch) => {
    setProfile((prev) => {
      const next = { ...prev, ...patch };
      saveProfile(currentUser.username, next);
      return next;
    });
  };

  const openEditIdentity = () => {
    setNameDraft(currentUser.name);
    setUsernameDraft(currentUser.username);
    setBioDraft(profile.bio);
    setEditingIdentity(true);
  };

  // Sin backend todavía para persistir esto (DATABASE_ARCHITECTURE.md §4.B) --
  // se actualiza la sesión local real (misma que useAuth.getStoredUser lee) y,
  // si cambia el username, se migra la clave del perfil extendido con él para
  // no perder bio/mood/intereses ya guardados.
  const handleSaveIdentity = (e) => {
    e.preventDefault();
    const name = nameDraft.trim();
    const username = usernameDraft.trim();
    if (!name || !username) return;

    const usernameChanged = username !== currentUser.username;
    onUpdateUser({ name, username });

    const bio = bioDraft.trim();
    setProfile((prev) => {
      const next = { ...prev, bio };
      if (usernameChanged) {
        localStorage.removeItem(`thers_profile_${currentUser.username}`);
      }
      saveProfile(username, next);
      return next;
    });

    setEditingIdentity(false);
  };

  const ownCapsules = useMemo(() => capsules.filter((c) => c.own), [capsules]);
  const featured = ownCapsules[0] || null;

  const addInterest = (e) => {
    e.preventDefault();
    const value = interestDraft.trim();
    if (!value || profile.interests.includes(value)) return;
    update({ interests: [...profile.interests, value] });
    setInterestDraft("");
  };

  return (
    <div className="max-w-3xl mx-auto space-y-6">
      <div className="rounded-[28px] overflow-hidden bg-surface dark:bg-surface-dark border border-line dark:border-line-dark shadow-soft">
        <div className={`h-36 bg-gradient-to-tr ${profile.banner} relative`}>
          <div className="absolute bottom-3 right-3 flex gap-1.5">
            {BANNERS.map((banner) => (
              <button
                key={banner}
                onClick={() => update({ banner })}
                aria-label="Cambiar ambiente del perfil"
                className={`w-6 h-6 rounded-full bg-gradient-to-tr ${banner} border-2 ${
                  profile.banner === banner ? "border-white" : "border-white/40"
                }`}
              />
            ))}
          </div>
        </div>

        <div className="px-6 pb-6">
          <div className="-mt-10 flex items-end justify-between">
            <div className="ring-4 ring-surface dark:ring-surface-dark rounded-full">
              <Avatar name={currentUser.name} size="w-20 h-20 text-2xl" color={profile.accent} />
            </div>

            <div className="flex items-center gap-2 mb-1">
              <div className="flex gap-1.5" aria-label="Color de acento">
                {ACCENTS.map((color) => (
                  <button
                    key={color}
                    onClick={() => update({ accent: color })}
                    aria-label={`Elegir acento ${color}`}
                    className="w-6 h-6 rounded-full border-2"
                    style={{ backgroundColor: color, borderColor: profile.accent === color ? profile.accent : "transparent" }}
                  />
                ))}
              </div>

              {!editingIdentity && (
                <button
                  onClick={openEditIdentity}
                  className="flex items-center gap-1 text-xs font-semibold px-3 py-1.5 rounded-full border border-line dark:border-line-dark text-ink dark:text-ink-dark hover:bg-canvas dark:hover:bg-canvas-dark transition"
                >
                  <IoPencilOutline size={13} /> Editar perfil
                </button>
              )}
            </div>
          </div>

          {editingIdentity ? (
            <form onSubmit={handleSaveIdentity} className="mt-3 space-y-2 animate-float-in">
              <input
                autoFocus
                type="text"
                value={nameDraft}
                onChange={(e) => setNameDraft(e.target.value)}
                placeholder="Nombre"
                aria-label="Nombre"
                className="w-full bg-canvas dark:bg-canvas-dark border border-line dark:border-line-dark rounded-xl px-3 py-2 text-sm font-semibold text-ink dark:text-ink-dark placeholder-muted focus:outline-none focus:ring-2"
                style={{ "--tw-ring-color": profile.accent }}
              />
              <input
                type="text"
                value={usernameDraft}
                onChange={(e) => setUsernameDraft(e.target.value)}
                placeholder="Nombre de usuario"
                aria-label="Nombre de usuario"
                className="w-full bg-canvas dark:bg-canvas-dark border border-line dark:border-line-dark rounded-xl px-3 py-2 text-sm text-ink dark:text-ink-dark placeholder-muted focus:outline-none focus:ring-2"
                style={{ "--tw-ring-color": profile.accent }}
              />
              <textarea
                value={bioDraft}
                onChange={(e) => setBioDraft(e.target.value)}
                placeholder="Cuenta quién eres en THERS..."
                rows={2}
                className="w-full bg-canvas dark:bg-canvas-dark border border-line dark:border-line-dark rounded-xl px-3 py-2 text-sm text-ink dark:text-ink-dark placeholder-muted focus:outline-none focus:ring-2"
                style={{ "--tw-ring-color": profile.accent }}
              />
              <div className="flex gap-2">
                <button
                  type="submit"
                  disabled={!nameDraft.trim() || !usernameDraft.trim()}
                  className="text-xs font-semibold px-3 py-1.5 rounded-full text-white disabled:opacity-50"
                  style={{ backgroundColor: profile.accent }}
                >
                  Guardar cambios
                </button>
                <button
                  type="button"
                  onClick={() => setEditingIdentity(false)}
                  className="text-xs font-semibold px-3 py-1.5 rounded-full border border-line dark:border-line-dark text-muted"
                >
                  Cancelar
                </button>
              </div>
            </form>
          ) : (
            <>
              <div className="mt-3 flex items-center gap-2 flex-wrap">
                <h1 className="text-xl font-extrabold text-ink dark:text-ink-dark">{currentUser.name}</h1>
                {profile.mood && <MoodBadge mood={profile.mood} glow />}
              </div>
              <p className="text-muted text-sm">@{currentUser.username}</p>
              <p className="mt-3 text-sm text-ink/80 dark:text-ink-dark/80">
                {profile.bio || <span className="text-muted italic">Agrega una biografía para tu perfil →</span>}
              </p>
            </>
          )}

          <div className="flex gap-6 mt-5 text-sm">
            <div>
              <span className="font-bold text-ink dark:text-ink-dark">0</span>{" "}
              <span className="text-muted">Seguidores</span>
            </div>
            <div>
              <span className="font-bold text-ink dark:text-ink-dark">{followingIds.size}</span>{" "}
              <span className="text-muted">Siguiendo</span>
            </div>
            <div>
              <span className="font-bold text-ink dark:text-ink-dark">{ownCapsules.length}</span>{" "}
              <span className="text-muted">Cápsulas</span>
            </div>
          </div>
        </div>
      </div>

      <div className="grid sm:grid-cols-2 gap-4">
        <div className="bg-surface dark:bg-surface-dark border border-line dark:border-line-dark rounded-[24px] shadow-soft p-5">
          <h2 className="text-sm font-semibold text-ink dark:text-ink-dark mb-3">Mood actual</h2>
          <div className="flex flex-wrap gap-2">
            {Object.entries(MOODS).map(([id, mood]) => (
              <button
                key={id}
                onClick={() => update({ mood: profile.mood === id ? null : id })}
                className={`flex items-center gap-1.5 text-xs font-medium px-2.5 py-1.5 rounded-full border transition ${
                  profile.mood === id
                    ? "text-white"
                    : "border-line dark:border-line-dark text-muted hover:bg-canvas dark:hover:bg-canvas-dark"
                }`}
                style={profile.mood === id ? { backgroundColor: mood.color, borderColor: mood.color } : {}}
              >
                <span
                  aria-hidden="true"
                  className="w-1.5 h-1.5 rounded-full"
                  style={{ backgroundColor: profile.mood === id ? "#fff" : mood.color }}
                />
                {mood.label}
              </button>
            ))}
          </div>
        </div>

        <div className="bg-surface dark:bg-surface-dark border border-line dark:border-line-dark rounded-[24px] shadow-soft p-5">
          <h2 className="flex items-center gap-2 text-sm font-semibold text-ink dark:text-ink-dark mb-3">
            <IoMusicalNotesOutline size={16} /> Música favorita
          </h2>
          <input
            type="text"
            value={profile.favoriteTrack}
            onChange={(e) => update({ favoriteTrack: e.target.value })}
            placeholder="Canción o artista favorito"
            className="w-full bg-canvas dark:bg-canvas-dark border border-transparent rounded-lg px-3 py-2 text-sm text-ink dark:text-ink-dark placeholder-muted focus:outline-none focus:ring-2"
            style={{ "--tw-ring-color": profile.accent }}
          />
        </div>
      </div>

      <div className="bg-surface dark:bg-surface-dark border border-line dark:border-line-dark rounded-[24px] shadow-soft p-5">
        <h2 className="text-sm font-semibold text-ink dark:text-ink-dark mb-3">Intereses</h2>
        <div className="flex flex-wrap gap-2 mb-3">
          {profile.interests.map((interest) => (
            <span
              key={interest}
              className="flex items-center gap-1 text-xs font-medium pl-3 pr-2 py-1.5 rounded-full bg-canvas dark:bg-canvas-dark text-ink dark:text-ink-dark"
            >
              {interest}
              <button
                onClick={() => update({ interests: profile.interests.filter((i) => i !== interest) })}
                aria-label={`Quitar interés ${interest}`}
                className="hover:text-ember-500"
              >
                <IoClose size={13} />
              </button>
            </span>
          ))}
        </div>
        <form onSubmit={addInterest} className="flex gap-2">
          <input
            type="text"
            value={interestDraft}
            onChange={(e) => setInterestDraft(e.target.value)}
            placeholder="Agregar un interés (ej: fotografía)"
            className="flex-1 bg-canvas dark:bg-canvas-dark border border-transparent rounded-lg px-3 py-2 text-sm text-ink dark:text-ink-dark placeholder-muted focus:outline-none focus:ring-2"
            style={{ "--tw-ring-color": profile.accent }}
          />
          <button
            type="submit"
            aria-label="Agregar interés"
            className="p-2 rounded-lg text-white"
            style={{ backgroundColor: profile.accent }}
          >
            <IoAdd size={18} />
          </button>
        </form>
      </div>

      <div>
        <h2 className="text-[11px] font-semibold uppercase tracking-wider text-muted dark:text-muted-dark mb-3">
          Cápsula destacada
        </h2>
        {featured ? (
          <CapsuleCard capsule={featured} currentUser={currentUser} />
        ) : (
          <div className="bg-surface dark:bg-surface-dark border border-dashed border-line dark:border-line-dark rounded-[24px] p-8 text-center text-muted text-sm">
            Crea tu primera Cápsula para destacarla en tu perfil.
          </div>
        )}
      </div>
    </div>
  );
}
