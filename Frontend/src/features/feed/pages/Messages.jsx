import { useEffect, useRef, useState } from "react";
import { useOutletContext, useSearchParams } from "react-router-dom";
import { IoSearchOutline, IoArrowBack, IoSend, IoChatbubblesOutline, IoTrashOutline } from "react-icons/io5";
import Avatar from "@shared/components/Avatar";
import { api, getErrorMessage } from "@shared/lib/api";
import { getStoredToken } from "@features/auth";
import { useToast } from "@shared/components/Toast";
import { useLanguage } from "@shared/i18n";
import { formatRelativeTime } from "../lib/formatRelativeTime";

// Mensajes directos reales (POST/GET/DELETE .../messages, GET /api/conversations
// -- ADR-013-messages-minimal-model.md, ADR-014-messages-ux-improvements.md).
// `conversations` llega por contexto desde AppShell.jsx (mismo patrón que
// `capsules`/`notifications`: se carga una sola vez ahí, no en cada página).
// El hilo abierto, su envío/borrado y el indicador de "escribiendo" son
// estado propio de esta página.
//
// Sin presencia en línea: `mockConversations` tenía un campo `online`
// inventado -- no existe ningún dato real de eso todavía, así que se quita
// en vez de dejar un valor falso fijo.

function authHeaders() {
  return { Authorization: `Bearer ${getStoredToken()}` };
}

// Mientras un hilo está abierto, se vuelve a pedir cada pocos segundos para
// recibir mensajes nuevos de la otra persona -- sin WebSockets/SSE todavía
// (ADR-013 §No objetivos), este es el único mecanismo de "tiempo real".
const THREAD_POLL_MS = 4000;
// "Escribiendo..." necesita sentirse más inmediato que el resto del chat
// para no parecer roto -- mismo motivo por el que ADR-014 eligió un
// intervalo más corto para esto que para el hilo en sí.
const TYPING_POLL_MS = 2000;
const TYPING_PING_MIN_INTERVAL_MS = 2000;

export default function Messages() {
  const { currentUser, conversations, onReloadConversations } = useOutletContext();
  const toast = useToast();
  const { t } = useLanguage();
  const [searchParams, setSearchParams] = useSearchParams();

  const [activeId, setActiveId] = useState(null);
  const [thread, setThread] = useState([]);
  const [threadLoading, setThreadLoading] = useState(false);
  const [draft, setDraft] = useState("");
  const [sending, setSending] = useState(false);
  const [search, setSearch] = useState("");
  // Id del primer mensaje sin leer al abrir el hilo -- calculado una sola
  // vez con la primera respuesta (ADR-014 §Decisión: `read` refleja el
  // estado ANTES de marcar como leído solo en esa primera llamada), no en
  // cada refresco del polling siguiente, para que el separador no
  // desaparezca mientras la persona sigue mirando la pantalla.
  const [unreadDividerId, setUnreadDividerId] = useState(null);
  const [otherIsTyping, setOtherIsTyping] = useState(false);
  const threadEndRef = useRef(null);
  const lastTypingPingRef = useRef(0);
  // Hilo nuevo abierto desde el botón "Mensaje" de CapsuleCard (?to=/&name=/
  // &username=) -- GET /api/conversations solo lista gente con la que ya
  // hay al menos un mensaje, así que esto rellena el panel mientras el
  // primer mensaje todavía no se mandó. Una vez enviado, `conversations`
  // (real, del backend) pasa a incluirlo y este estado deja de usarse para
  // ese usuario.
  const [draftConversation, setDraftConversation] = useState(null);

  useEffect(() => {
    const to = searchParams.get("to");
    if (!to) return;

    setActiveId(to);
    const alreadyReal = conversations.some((c) => c.user.id === to);
    if (!alreadyReal) {
      setDraftConversation({
        user: {
          id: to,
          name: searchParams.get("name") || "Usuario",
          username: searchParams.get("username") || "",
        },
        last_message: { content: "", sender_id: null, created_at: new Date().toISOString() },
        unread_count: 0,
      });
    }
    setSearchParams({}, { replace: true });
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [searchParams]);

  const realActive = conversations.find((c) => c.user.id === activeId) || null;
  const active = realActive || (draftConversation?.user.id === activeId ? draftConversation : null);
  const list =
    draftConversation && !conversations.some((c) => c.user.id === draftConversation.user.id)
      ? [draftConversation, ...conversations]
      : conversations;
  const filtered = list.filter((c) => c.user.name.toLowerCase().includes(search.toLowerCase()));

  useEffect(() => {
    if (!activeId) return undefined;
    let cancelled = false;
    let firstLoad = true;

    async function loadThread() {
      try {
        const res = await api.get(`/users/${activeId}/messages`, { headers: authHeaders() });
        if (cancelled) return;
        setThread(res.data.messages);
        if (firstLoad) {
          const firstUnread = res.data.messages.find(
            (m) => !m.read && m.sender_id !== currentUser.id
          );
          setUnreadDividerId(firstUnread ? firstUnread.id : null);
          firstLoad = false;
        }
      } catch (error) {
        if (!cancelled) toast.error(getErrorMessage(error, t));
      } finally {
        if (!cancelled) setThreadLoading(false);
      }
    }

    async function pollTypingStatus() {
      try {
        const res = await api.get(`/users/${activeId}/typing`, { headers: authHeaders() });
        if (!cancelled) setOtherIsTyping(res.data.typing);
      } catch {
        // Silencioso: "escribiendo" es un detalle cosmético, no amerita
        // interrumpir al usuario con un Toast si un poll puntual falla.
      }
    }

    setThreadLoading(true);
    setUnreadDividerId(null);
    setOtherIsTyping(false);
    loadThread();
    // Abrir el hilo marca como leídos los mensajes recibidos (efecto
    // secundario del GET, ADR-013) -- refresca la lista para que el
    // `unread_count` de esta conversación y el badge del shell bajen.
    onReloadConversations();

    const threadInterval = setInterval(loadThread, THREAD_POLL_MS);
    const typingInterval = setInterval(pollTypingStatus, TYPING_POLL_MS);
    return () => {
      cancelled = true;
      clearInterval(threadInterval);
      clearInterval(typingInterval);
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [activeId]);

  // Hace scroll al mensaje más reciente cada vez que el hilo cambia (al
  // abrirlo, al recibir uno nuevo por polling, o al mandar uno propio) --
  // sin esto, un hilo largo se abría mostrando el mensaje más viejo primero.
  useEffect(() => {
    threadEndRef.current?.scrollIntoView({ block: "end" });
  }, [thread]);

  const handleDraftChange = (e) => {
    setDraft(e.target.value);
    if (!activeId) return;

    const now = Date.now();
    if (now - lastTypingPingRef.current < TYPING_PING_MIN_INTERVAL_MS) return;
    lastTypingPingRef.current = now;
    api.post(`/users/${activeId}/typing`, null, { headers: authHeaders() }).catch(() => {
      // Mismo criterio que pollTypingStatus: un ping perdido no es un error
      // que el usuario necesite ver.
    });
  };

  const handleSend = async (e) => {
    e.preventDefault();
    const content = draft.trim();
    if (!content || !active || sending) return;

    setSending(true);
    try {
      const res = await api.post(
        `/users/${activeId}/messages`,
        { content },
        { headers: authHeaders() }
      );
      setThread((prev) => [...prev, res.data.message]);
      setDraft("");
      setDraftConversation(null);
      onReloadConversations();
    } catch (error) {
      toast.error(getErrorMessage(error, t));
    } finally {
      setSending(false);
    }
  };

  const handleDelete = async (messageId) => {
    if (!window.confirm("¿Eliminar este mensaje? No se puede deshacer.")) return;

    const previous = thread;
    setThread((prev) => prev.filter((m) => m.id !== messageId));
    try {
      await api.delete(`/messages/${messageId}`, { headers: authHeaders() });
      onReloadConversations();
    } catch (error) {
      setThread(previous);
      toast.error(getErrorMessage(error, t));
    }
  };

  return (
    <div className="max-w-5xl mx-auto h-[calc(100vh-9rem)]">
      <div className="bg-surface dark:bg-surface-dark border border-line dark:border-line-dark rounded-[28px] shadow-soft h-full flex overflow-hidden">
        <div className={`w-full md:w-80 shrink-0 border-r border-line dark:border-line-dark flex-col ${active ? "hidden md:flex" : "flex"}`}>
          <div className="p-4 border-b border-line dark:border-line-dark">
            <h1 className="text-lg font-extrabold text-ink dark:text-ink-dark mb-3">Mensajes</h1>
            <div className="relative">
              <IoSearchOutline className="absolute left-3 top-1/2 -translate-y-1/2 text-muted" size={16} />
              <input
                type="text"
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                placeholder="Buscar conversaciones..."
                aria-label="Buscar conversaciones"
                className="w-full bg-canvas dark:bg-canvas-dark border border-transparent rounded-full pl-9 pr-3 py-2 text-sm text-ink dark:text-ink-dark placeholder-muted focus:outline-none focus:ring-2 focus:ring-pulse-500"
              />
            </div>
          </div>

          <div className="flex-1 overflow-y-auto">
            {filtered.length === 0 && (
              <div className="flex flex-col items-center gap-2 px-4 py-10 text-center text-muted">
                <IoChatbubblesOutline size={28} />
                <p className="text-sm">
                  {conversations.length === 0
                    ? "Todavía no tenés conversaciones. Tocá el ícono de mensaje junto a una publicación para empezar una."
                    : "Ninguna conversación coincide con la búsqueda."}
                </p>
              </div>
            )}
            {filtered.map((conversation) => (
              <button
                key={conversation.user.id}
                onClick={() => setActiveId(conversation.user.id)}
                className={`w-full flex items-center gap-3 px-4 py-3 text-left hover:bg-canvas dark:hover:bg-canvas-dark transition ${
                  activeId === conversation.user.id ? "bg-pulse-50 dark:bg-pulse-900/20" : ""
                }`}
              >
                <Avatar name={conversation.user.name} size="w-11 h-11" />
                <div className="min-w-0 flex-1">
                  <div className="flex items-center justify-between gap-2">
                    <p className="text-ink dark:text-ink-dark text-sm font-semibold truncate">
                      {conversation.user.name}
                    </p>
                    <span className="text-muted text-[11px] shrink-0">
                      {formatRelativeTime(conversation.last_message.created_at)}
                    </span>
                  </div>
                  <p className="text-muted text-xs truncate">{conversation.last_message.content}</p>
                </div>
                {conversation.unread_count > 0 && (
                  <span className="shrink-0 w-5 h-5 rounded-full bg-pulse-600 text-white text-[10px] font-bold flex items-center justify-center">
                    {conversation.unread_count}
                  </span>
                )}
              </button>
            ))}
          </div>
        </div>

        <div className={`flex-1 flex-col min-w-0 ${active ? "flex" : "hidden md:flex"}`}>
          {active ? (
            <>
              <div className="flex items-center gap-3 px-4 py-3 border-b border-line dark:border-line-dark">
                <button
                  onClick={() => setActiveId(null)}
                  aria-label="Volver a conversaciones"
                  className="md:hidden text-muted p-1 -ml-1"
                >
                  <IoArrowBack size={20} />
                </button>
                <Avatar name={active.user.name} size="w-9 h-9" />
                <div className="min-w-0">
                  <p className="text-ink dark:text-ink-dark text-sm font-semibold truncate">
                    {active.user.name}
                  </p>
                  {otherIsTyping && (
                    <p className="text-pulse-600 text-xs animate-pulse">Escribiendo...</p>
                  )}
                </div>
              </div>

              <div className="flex-1 overflow-y-auto px-4 py-4 space-y-3">
                {threadLoading ? (
                  <p className="text-center text-muted text-sm">Cargando...</p>
                ) : (
                  thread.map((message) => (
                    <div key={message.id}>
                      {message.id === unreadDividerId && (
                        <div className="flex items-center gap-3 py-2" role="separator">
                          <span className="h-px flex-1 bg-line dark:bg-line-dark" />
                          <span className="text-[11px] font-semibold uppercase tracking-wide text-muted">
                            Mensajes no leídos
                          </span>
                          <span className="h-px flex-1 bg-line dark:bg-line-dark" />
                        </div>
                      )}
                      <div
                        className={`group flex items-center gap-1.5 animate-float-in ${
                          message.sender_id === currentUser.id ? "justify-end" : "justify-start"
                        }`}
                      >
                        {message.sender_id === currentUser.id && (
                          <button
                            type="button"
                            onClick={() => handleDelete(message.id)}
                            aria-label="Eliminar mensaje"
                            className="shrink-0 rounded-full p-1 text-muted opacity-0 transition group-hover:opacity-100 hover:text-red-500"
                          >
                            <IoTrashOutline size={14} />
                          </button>
                        )}
                        <div
                          className={`max-w-[75%] rounded-2xl px-4 py-2 text-sm ${
                            message.sender_id === currentUser.id
                              ? "bg-pulse-600 text-white rounded-br-md"
                              : "bg-canvas dark:bg-canvas-dark text-ink dark:text-ink-dark rounded-bl-md"
                          }`}
                        >
                          {message.content}
                        </div>
                      </div>
                    </div>
                  ))
                )}
                <div ref={threadEndRef} />
              </div>

              <form onSubmit={handleSend} className="flex items-center gap-2 px-4 py-3 border-t border-line dark:border-line-dark">
                <Avatar name={currentUser.name} size="w-8 h-8" />
                <input
                  type="text"
                  value={draft}
                  onChange={handleDraftChange}
                  placeholder="Escribe un mensaje..."
                  aria-label="Escribir un mensaje"
                  className="flex-1 bg-canvas dark:bg-canvas-dark border border-transparent rounded-full px-4 py-2 text-sm text-ink dark:text-ink-dark placeholder-muted focus:outline-none focus:ring-2 focus:ring-pulse-500"
                />
                <button
                  type="submit"
                  disabled={!draft.trim() || sending}
                  aria-label="Enviar mensaje"
                  className={`p-2.5 rounded-full transition ${
                    draft.trim() && !sending
                      ? "bg-pulse-600 text-white hover:bg-pulse-700"
                      : "bg-line dark:bg-line-dark text-muted"
                  }`}
                >
                  <IoSend size={16} />
                </button>
              </form>
            </>
          ) : (
            <div className="flex-1 flex flex-col items-center justify-center gap-2 text-muted">
              <IoChatbubblesOutline size={40} />
              <p className="text-sm">Elige una conversación para empezar a chatear</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
