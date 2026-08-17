import { useState } from "react";
import { useOutletContext } from "react-router-dom";
import { IoSearchOutline, IoArrowBack, IoSend, IoChatbubblesOutline } from "react-icons/io5";
import Avatar from "@shared/components/Avatar";
import { mockConversations } from "../data/mockData";

export default function Messages() {
  const { currentUser } = useOutletContext();
  const [conversations, setConversations] = useState(mockConversations);
  const [activeId, setActiveId] = useState(null);
  const [draft, setDraft] = useState("");
  const [search, setSearch] = useState("");

  const active = conversations.find((c) => c.id === activeId) || null;
  const filtered = conversations.filter((c) =>
    c.name.toLowerCase().includes(search.toLowerCase())
  );

  const handleSend = (e) => {
    e.preventDefault();
    if (!draft.trim() || !active) return;

    setConversations((prev) =>
      prev.map((c) =>
        c.id === active.id
          ? {
              ...c,
              lastMessage: draft.trim(),
              messages: [...c.messages, { id: c.messages.length + 1, from: "me", text: draft.trim(), time: "Ahora" }],
            }
          : c
      )
    );
    setDraft("");
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
            {filtered.map((conversation) => (
              <button
                key={conversation.id}
                onClick={() => setActiveId(conversation.id)}
                className={`w-full flex items-center gap-3 px-4 py-3 text-left hover:bg-canvas dark:hover:bg-canvas-dark transition ${
                  activeId === conversation.id ? "bg-pulse-50 dark:bg-pulse-900/20" : ""
                }`}
              >
                <div className="relative shrink-0">
                  <Avatar name={conversation.name} photo={conversation.photo} size="w-11 h-11" />
                  {conversation.online && (
                    <span className="absolute bottom-0 right-0 w-3 h-3 rounded-full bg-emerald-500 border-2 border-surface dark:border-surface-dark" />
                  )}
                </div>
                <div className="min-w-0 flex-1">
                  <div className="flex items-center justify-between gap-2">
                    <p className="text-ink dark:text-ink-dark text-sm font-semibold truncate">{conversation.name}</p>
                    <span className="text-muted text-[11px] shrink-0">{conversation.time}</span>
                  </div>
                  <p className="text-muted text-xs truncate">{conversation.lastMessage}</p>
                </div>
                {conversation.unread > 0 && (
                  <span className="shrink-0 w-5 h-5 rounded-full bg-pulse-600 text-white text-[10px] font-bold flex items-center justify-center">
                    {conversation.unread}
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
                <Avatar name={active.name} photo={active.photo} size="w-9 h-9" />
                <div>
                  <p className="text-ink dark:text-ink-dark text-sm font-semibold">{active.name}</p>
                  <p className="text-muted text-xs">{active.online ? "En línea" : "Desconectado"}</p>
                </div>
              </div>

              <div className="flex-1 overflow-y-auto px-4 py-4 space-y-3">
                {active.messages.map((message) => (
                  <div
                    key={message.id}
                    className={`flex animate-float-in ${message.from === "me" ? "justify-end" : "justify-start"}`}
                  >
                    <div
                      className={`max-w-[75%] rounded-2xl px-4 py-2 text-sm ${
                        message.from === "me"
                          ? "bg-pulse-600 text-white rounded-br-md"
                          : "bg-canvas dark:bg-canvas-dark text-ink dark:text-ink-dark rounded-bl-md"
                      }`}
                    >
                      {message.text}
                    </div>
                  </div>
                ))}
              </div>

              <form onSubmit={handleSend} className="flex items-center gap-2 px-4 py-3 border-t border-line dark:border-line-dark">
                <Avatar name={currentUser.name} size="w-8 h-8" />
                <input
                  type="text"
                  value={draft}
                  onChange={(e) => setDraft(e.target.value)}
                  placeholder="Escribe un mensaje..."
                  aria-label="Escribir un mensaje"
                  className="flex-1 bg-canvas dark:bg-canvas-dark border border-transparent rounded-full px-4 py-2 text-sm text-ink dark:text-ink-dark placeholder-muted focus:outline-none focus:ring-2 focus:ring-pulse-500"
                />
                <button
                  type="submit"
                  disabled={!draft.trim()}
                  aria-label="Enviar mensaje"
                  className={`p-2.5 rounded-full transition ${
                    draft.trim() ? "bg-pulse-600 text-white hover:bg-pulse-700" : "bg-line dark:bg-line-dark text-muted"
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
