import { useEffect, useId, useMemo, useRef, useState } from "react";
import { IoAdd, IoClose, IoMusicalNotesOutline } from "react-icons/io5";
import Avatar from "@shared/components/Avatar";
import { isValidUsername } from "@features/auth";
import { ACCENTS, COVERS } from "../data/profileIdentity";
import {
  BIO_MAX,
  INTEREST_MAX,
  INTERESTS_MAX_COUNT,
  LOCATION_MAX,
  TRACK_MAX,
  WEBSITE_MAX,
} from "../lib/profileStorage";
import { MOODS } from "../data/mockData";

// Hoja de edición del perfil, inspirada en el "Editar perfil" de Instagram
// (Frontend/src/assets/editar.png): identidad arriba, campos agrupados,
// contador de caracteres en la presentación.
//
// name/username se persisten de verdad (PATCH /api/users/me, ADR-003); el
// resto es local (ver lib/profileStorage.js). "Cambiar foto" no existe como
// tal: no hay almacenamiento de archivos en el backend, así que lo editable
// es el color del avatar y la portada -- no se simula una subida que no
// funciona.

const NAME_MAX = 120; // Mismo límite que valida el backend (_MAX_NAME_LENGTH).

const inputClass =
  "w-full rounded-xl border border-line bg-canvas px-3.5 py-2.5 text-sm text-ink placeholder-muted transition focus:border-ink focus:outline-none dark:border-line-dark dark:bg-canvas-dark dark:text-ink-dark dark:focus:border-ink-dark";

function Field({ id, label, hint, error, children }) {
  return (
    <div>
      <label htmlFor={id} className="mb-1.5 block text-sm font-semibold text-ink dark:text-ink-dark">
        {label}
      </label>
      {children}
      {error ? (
        <p id={`${id}-error`} role="alert" className="mt-1.5 text-xs font-medium text-ember-600">
          {error}
        </p>
      ) : (
        hint && (
          <p id={`${id}-hint`} className="mt-1.5 text-xs text-muted dark:text-muted-dark">
            {hint}
          </p>
        )
      )}
    </div>
  );
}

export default function EditProfileModal({ user, profile, onSave, onClose }) {
  const uid = useId();
  const panelRef = useRef(null);
  const summaryRef = useRef(null);

  const [draft, setDraft] = useState(() => ({
    name: user.name,
    username: user.username,
    bio: profile.bio,
    location: profile.location,
    website: profile.website,
    favoriteTrack: profile.favoriteTrack,
    mood: profile.mood,
    interests: profile.interests,
    cover: profile.cover,
    accent: profile.accent,
  }));
  const [interestDraft, setInterestDraft] = useState("");
  const [errors, setErrors] = useState({});
  const [isSaving, setSaving] = useState(false);
  const [confirmingClose, setConfirmingClose] = useState(false);

  const set = (patch) => setDraft((prev) => ({ ...prev, ...patch }));

  const isDirty = useMemo(
    () =>
      draft.name !== user.name ||
      draft.username !== user.username ||
      draft.bio !== profile.bio ||
      draft.location !== profile.location ||
      draft.website !== profile.website ||
      draft.favoriteTrack !== profile.favoriteTrack ||
      draft.mood !== profile.mood ||
      draft.cover !== profile.cover ||
      draft.accent !== profile.accent ||
      draft.interests.join("|") !== profile.interests.join("|"),
    [draft, user, profile]
  );

  // El scroll de la página se bloquea mientras la hoja está abierta, para que
  // el fondo no se mueva bajo el dedo en móvil.
  useEffect(() => {
    const previous = document.body.style.overflow;
    document.body.style.overflow = "hidden";
    return () => {
      document.body.style.overflow = previous;
    };
  }, []);

  const requestClose = () => {
    if (isSaving) return;
    if (isDirty) setConfirmingClose(true);
    else onClose();
  };

  // Escape siempre ofrece salida, y Tab queda contenido dentro del panel: sin
  // esto el foco se va al contenido de atrás, que está tapado para la vista
  // pero sigue siendo alcanzable con teclado.
  useEffect(() => {
    const onKeyDown = (event) => {
      if (event.key === "Escape") {
        event.stopPropagation();
        // Escape sobre la confirmación vuelve a la edición, no la salta: si
        // saliera de las dos capas de una vez, descartaría los cambios sin
        // que nadie lo confirmara.
        if (confirmingClose) setConfirmingClose(false);
        else requestClose();
        return;
      }
      if (event.key !== "Tab" || !panelRef.current) return;

      const focusables = panelRef.current.querySelectorAll(
        "a[href], button:not([disabled]), input:not([disabled]), textarea:not([disabled])"
      );
      if (!focusables.length) return;

      const first = focusables[0];
      const last = focusables[focusables.length - 1];

      if (event.shiftKey && document.activeElement === first) {
        event.preventDefault();
        last.focus();
      } else if (!event.shiftKey && document.activeElement === last) {
        event.preventDefault();
        first.focus();
      }
    };

    document.addEventListener("keydown", onKeyDown, true);
    return () => document.removeEventListener("keydown", onKeyDown, true);
  });

  const validate = () => {
    const next = {};
    const name = draft.name.trim();
    const username = draft.username.trim();

    if (!name) next.name = "El nombre no puede estar vacío.";
    else if (name.length > NAME_MAX) next.name = `El nombre no puede superar ${NAME_MAX} caracteres.`;

    if (!username) next.username = "El nombre de usuario no puede estar vacío.";
    else if (!isValidUsername(username))
      next.username = "Usa entre 3 y 20 caracteres: letras, números o guion bajo.";

    return next;
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    if (isSaving) return;

    const found = validate();
    setErrors(found);

    // Con más de un error el foco va al resumen (que enlaza cada campo); el
    // error inline se mantiene igualmente junto a su campo.
    if (Object.keys(found).length) {
      requestAnimationFrame(() => summaryRef.current?.focus());
      return;
    }

    setSaving(true);
    try {
      await onSave({
        name: draft.name.trim(),
        username: draft.username.trim(),
        profile: {
          bio: draft.bio.trim(),
          location: draft.location.trim(),
          website: draft.website.trim(),
          favoriteTrack: draft.favoriteTrack.trim(),
          mood: draft.mood,
          interests: draft.interests,
          cover: draft.cover,
          accent: draft.accent,
        },
      });
    } finally {
      setSaving(false);
    }
  };

  const addInterest = () => {
    const value = interestDraft.trim().slice(0, INTEREST_MAX);
    if (!value || draft.interests.includes(value) || draft.interests.length >= INTERESTS_MAX_COUNT) return;
    set({ interests: [...draft.interests, value] });
    setInterestDraft("");
  };

  const errorList = Object.entries(errors);
  const interestsFull = draft.interests.length >= INTERESTS_MAX_COUNT;

  return (
    <div
      className="fixed inset-0 z-50 flex items-end justify-center bg-black/60 backdrop-blur-sm sm:items-center sm:p-4"
      onMouseDown={(event) => {
        if (event.target === event.currentTarget) requestClose();
      }}
    >
      <div
        ref={panelRef}
        role="dialog"
        aria-modal="true"
        aria-labelledby={`${uid}-title`}
        className="animate-float-in relative flex max-h-[92vh] motion-reduce:animate-none w-full max-w-lg flex-col overflow-hidden rounded-t-[28px] border border-line bg-surface shadow-lift dark:border-line-dark dark:bg-surface-dark sm:rounded-[28px]"
      >
        <header className="flex shrink-0 items-center justify-between gap-3 border-b border-line px-3 py-3 dark:border-line-dark">
          <button
            type="button"
            onClick={requestClose}
            disabled={isSaving}
            aria-label="Cerrar sin guardar"
            className="flex h-11 w-11 shrink-0 cursor-pointer items-center justify-center rounded-full text-ink transition hover:bg-canvas disabled:opacity-50 dark:text-ink-dark dark:hover:bg-canvas-dark"
          >
            <IoClose size={20} aria-hidden="true" />
          </button>

          <h2 id={`${uid}-title`} className="text-base font-bold text-ink dark:text-ink-dark">
            Editar perfil
          </h2>

          <button
            type="submit"
            form={`${uid}-form`}
            disabled={isSaving}
            className="h-11 shrink-0 cursor-pointer rounded-full bg-ink px-5 text-sm font-semibold text-surface transition hover:opacity-90 active:scale-[0.98] disabled:opacity-50 dark:bg-ink-dark dark:text-surface-dark"
          >
            {isSaving ? "Guardando..." : "Guardar"}
          </button>
        </header>

        <form
          id={`${uid}-form`}
          onSubmit={handleSubmit}
          className="min-h-0 flex-1 space-y-6 overflow-y-auto px-5 py-5"
        >
          {errorList.length > 1 && (
            <div
              ref={summaryRef}
              tabIndex={-1}
              role="alert"
              className="rounded-2xl border border-ember-300 bg-ember-50 p-3.5 text-sm dark:border-ember-700 dark:bg-ember-700/15"
            >
              <p className="font-semibold text-ember-700 dark:text-ember-300">
                Revisa {errorList.length} campos antes de guardar:
              </p>
              <ul className="mt-1.5 space-y-1">
                {errorList.map(([field, message]) => (
                  <li key={field}>
                    <a
                      href={`#${uid}-${field}`}
                      onClick={(event) => {
                        event.preventDefault();
                        document.getElementById(`${uid}-${field}`)?.focus();
                      }}
                      className="text-ember-700 underline underline-offset-2 dark:text-ember-300"
                    >
                      {message}
                    </a>
                  </li>
                ))}
              </ul>
            </div>
          )}

          <section className="flex items-center gap-4 rounded-2xl bg-canvas p-4 dark:bg-canvas-dark">
            <Avatar name={draft.name || user.name} size="w-16 h-16 text-xl" color={draft.accent} />
            <fieldset className="min-w-0">
              <legend className="mb-2 text-sm font-semibold text-ink dark:text-ink-dark">
                Color de tu avatar
              </legend>
              <div className="flex flex-wrap gap-2">
                {ACCENTS.map(({ value, label }) => {
                  const selected = draft.accent === value;
                  return (
                    <button
                      key={value}
                      type="button"
                      onClick={() => set({ accent: value })}
                      aria-pressed={selected}
                      title={label}
                      className={`h-9 w-9 cursor-pointer rounded-full border-2 transition ${
                        selected
                          ? "border-ink dark:border-ink-dark"
                          : "border-transparent hover:border-line dark:hover:border-line-dark"
                      }`}
                      style={{ backgroundColor: value }}
                    >
                      <span className="sr-only">{label}</span>
                    </button>
                  );
                })}
              </div>
            </fieldset>
          </section>

          <fieldset>
            <legend className="mb-2 text-sm font-semibold text-ink dark:text-ink-dark">Portada</legend>
            <div className="grid grid-cols-5 gap-2">
              {Object.entries(COVERS).map(([id, cover]) => {
                const selected = draft.cover === id;
                return (
                  <button
                    key={id}
                    type="button"
                    onClick={() => set({ cover: id })}
                    aria-pressed={selected}
                    title={cover.label}
                    className={`h-12 cursor-pointer rounded-xl border-2 transition ${
                      selected ? "border-ink dark:border-ink-dark" : "border-line dark:border-line-dark"
                    }`}
                    style={{ backgroundImage: cover.gradient }}
                  >
                    <span className="sr-only">{cover.label}</span>
                  </button>
                );
              })}
            </div>
          </fieldset>

          <Field id={`${uid}-name`} label="Nombre" error={errors.name}>
            <input
              id={`${uid}-name`}
              type="text"
              value={draft.name}
              maxLength={NAME_MAX}
              autoComplete="name"
              aria-invalid={Boolean(errors.name)}
              aria-describedby={errors.name ? `${uid}-name-error` : undefined}
              onChange={(event) => set({ name: event.target.value })}
              className={inputClass}
            />
          </Field>

          <Field
            id={`${uid}-username`}
            label="Nombre de usuario"
            hint="Entre 3 y 20 caracteres: letras, números o guion bajo."
            error={errors.username}
          >
            <div className="flex items-center gap-1.5 rounded-xl border border-line bg-canvas px-3.5 transition focus-within:border-ink dark:border-line-dark dark:bg-canvas-dark dark:focus-within:border-ink-dark">
              <span aria-hidden="true" className="text-sm text-muted dark:text-muted-dark">
                @
              </span>
              <input
                id={`${uid}-username`}
                type="text"
                value={draft.username}
                maxLength={20}
                autoComplete="username"
                aria-invalid={Boolean(errors.username)}
                aria-describedby={errors.username ? `${uid}-username-error` : `${uid}-username-hint`}
                onChange={(event) => set({ username: event.target.value })}
                className="w-full bg-transparent py-2.5 text-sm text-ink placeholder-muted focus:outline-none dark:text-ink-dark"
              />
            </div>
          </Field>

          <Field id={`${uid}-bio`} label="Presentación">
            <textarea
              id={`${uid}-bio`}
              rows={3}
              value={draft.bio}
              maxLength={BIO_MAX}
              placeholder="Cuenta quién eres en THERS..."
              onChange={(event) => set({ bio: event.target.value })}
              className={`${inputClass} resize-none`}
            />
            <p className="mt-1.5 text-right text-xs tabular-nums text-muted dark:text-muted-dark">
              {draft.bio.length} / {BIO_MAX}
            </p>
          </Field>

          <Field id={`${uid}-location`} label="Ubicación">
            <input
              id={`${uid}-location`}
              type="text"
              value={draft.location}
              maxLength={LOCATION_MAX}
              autoComplete="address-level2"
              placeholder="San Salvador, El Salvador"
              onChange={(event) => set({ location: event.target.value })}
              className={inputClass}
            />
          </Field>

          <Field id={`${uid}-website`} label="Sitio web">
            <input
              id={`${uid}-website`}
              type="text"
              inputMode="url"
              value={draft.website}
              maxLength={WEBSITE_MAX}
              autoComplete="url"
              placeholder="thers.app/tu-usuario"
              onChange={(event) => set({ website: event.target.value })}
              className={inputClass}
            />
          </Field>

          <fieldset>
            <legend className="mb-2 text-sm font-semibold text-ink dark:text-ink-dark">Mood actual</legend>
            <div className="flex flex-wrap gap-2">
              {Object.entries(MOODS).map(([id, mood]) => {
                const selected = draft.mood === id;
                return (
                  <button
                    key={id}
                    type="button"
                    onClick={() => set({ mood: selected ? null : id })}
                    aria-pressed={selected}
                    className={`flex cursor-pointer items-center gap-1.5 rounded-full border px-3 py-2 text-xs font-medium transition ${
                      selected
                        ? "border-ink bg-ink text-surface dark:border-ink-dark dark:bg-ink-dark dark:text-surface-dark"
                        : "border-line text-muted hover:text-ink dark:border-line-dark dark:text-muted-dark dark:hover:text-ink-dark"
                    }`}
                  >
                    <span
                      aria-hidden="true"
                      className="h-1.5 w-1.5 rounded-full"
                      style={{ backgroundColor: mood.color }}
                    />
                    {mood.label}
                  </button>
                );
              })}
            </div>
          </fieldset>

          <div>
            <label
              htmlFor={`${uid}-interest`}
              className="mb-1.5 block text-sm font-semibold text-ink dark:text-ink-dark"
            >
              Intereses
            </label>

            {draft.interests.length > 0 && (
              <ul className="mb-2 flex flex-wrap gap-2">
                {draft.interests.map((interest) => (
                  <li
                    key={interest}
                    className="flex items-center gap-1 rounded-full bg-canvas py-1 pl-3 pr-1 text-xs font-medium text-ink dark:bg-canvas-dark dark:text-ink-dark"
                  >
                    <span className="[overflow-wrap:anywhere]">{interest}</span>
                    <button
                      type="button"
                      onClick={() => set({ interests: draft.interests.filter((item) => item !== interest) })}
                      aria-label={`Quitar interés ${interest}`}
                      className="flex h-6 w-6 shrink-0 cursor-pointer items-center justify-center rounded-full text-muted transition hover:text-ember-600"
                    >
                      <IoClose size={13} aria-hidden="true" />
                    </button>
                  </li>
                ))}
              </ul>
            )}

            <div className="flex gap-2">
              <input
                id={`${uid}-interest`}
                type="text"
                value={interestDraft}
                maxLength={INTEREST_MAX}
                placeholder="Agregar un interés (ej: fotografía)"
                disabled={interestsFull}
                onChange={(event) => setInterestDraft(event.target.value)}
                onKeyDown={(event) => {
                  // Enter agrega el interés en vez de enviar el formulario
                  // completo -- si no, escribir un interés guardaría el perfil.
                  if (event.key === "Enter") {
                    event.preventDefault();
                    addInterest();
                  }
                }}
                className={`${inputClass} disabled:opacity-50`}
              />
              <button
                type="button"
                onClick={addInterest}
                disabled={!interestDraft.trim() || interestsFull}
                aria-label="Agregar interés"
                className="flex h-11 w-11 shrink-0 cursor-pointer items-center justify-center rounded-xl bg-ink text-surface transition hover:opacity-90 disabled:opacity-40 dark:bg-ink-dark dark:text-surface-dark"
              >
                <IoAdd size={20} aria-hidden="true" />
              </button>
            </div>

            <p className="mt-1.5 text-xs tabular-nums text-muted dark:text-muted-dark">
              {draft.interests.length} / {INTERESTS_MAX_COUNT}
            </p>
          </div>

          <Field id={`${uid}-track`} label="Música favorita">
            <div className="flex items-center gap-2 rounded-xl border border-line bg-canvas px-3.5 transition focus-within:border-ink dark:border-line-dark dark:bg-canvas-dark dark:focus-within:border-ink-dark">
              <IoMusicalNotesOutline size={17} className="shrink-0 text-muted" aria-hidden="true" />
              <input
                id={`${uid}-track`}
                type="text"
                value={draft.favoriteTrack}
                maxLength={TRACK_MAX}
                placeholder="Canción o artista favorito"
                onChange={(event) => set({ favoriteTrack: event.target.value })}
                className="w-full bg-transparent py-2.5 text-sm text-ink placeholder-muted focus:outline-none dark:text-ink-dark"
              />
            </div>
          </Field>
        </form>

        {confirmingClose && (
          <div className="absolute inset-0 flex items-center justify-center bg-black/50 p-6">
            <div
              role="alertdialog"
              aria-modal="true"
              aria-labelledby={`${uid}-confirm`}
              className="animate-float-in w-full max-w-xs motion-reduce:animate-none rounded-3xl border border-line bg-surface p-5 shadow-lift dark:border-line-dark dark:bg-surface-dark"
            >
              <h3 id={`${uid}-confirm`} className="text-base font-bold text-ink dark:text-ink-dark">
                ¿Descartar cambios?
              </h3>
              <p className="mt-1.5 text-sm text-muted dark:text-muted-dark">
                Lo que escribiste no se guardará.
              </p>
              <div className="mt-4 flex flex-col gap-2">
                <button
                  type="button"
                  autoFocus
                  onClick={onClose}
                  className="h-11 cursor-pointer rounded-full bg-ember-600 text-sm font-semibold text-white transition hover:bg-ember-700"
                >
                  Descartar
                </button>
                <button
                  type="button"
                  onClick={() => setConfirmingClose(false)}
                  className="h-11 cursor-pointer rounded-full border border-line text-sm font-semibold text-ink transition hover:bg-canvas dark:border-line-dark dark:text-ink-dark dark:hover:bg-canvas-dark"
                >
                  Seguir editando
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
