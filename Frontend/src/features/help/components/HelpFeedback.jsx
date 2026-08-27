import { useState } from "react";
import { IoThumbsUpOutline, IoThumbsDownOutline, IoFlagOutline, IoCheckmarkCircle } from "react-icons/io5";
import { useToast } from "@shared/components/Toast";
import { useArticleFeedback } from "../hooks/useArticleFeedback";

export default function HelpFeedback({ slug }) {
  const { vote, submitVote } = useArticleFeedback(slug);
  const toast = useToast();
  const [reported, setReported] = useState(false);

  const handleVote = (value) => {
    submitVote(value);
  };

  const handleReport = () => {
    setReported(true);
    toast.info("Muy pronto vas a poder reportar un problema de este artículo directamente desde acá.", {
      title: "Función en construcción",
    });
  };

  return (
    <div className="rounded-2xl border border-line dark:border-line-dark bg-surface dark:bg-surface-dark p-5">
      {vote ? (
        <p role="status" className="flex items-center gap-2 text-sm text-ink dark:text-ink-dark font-medium">
          <IoCheckmarkCircle size={18} className="text-success-500" aria-hidden="true" />
          Gracias por tu feedback.
        </p>
      ) : (
        <>
          <p className="text-sm font-semibold text-ink dark:text-ink-dark">¿Te resultó útil este artículo?</p>
          <div className="mt-3 flex items-center gap-2">
            <button
              type="button"
              onClick={() => handleVote("yes")}
              className="flex items-center gap-1.5 text-sm font-medium px-4 py-2 rounded-full border border-line dark:border-line-dark text-ink dark:text-ink-dark hover:bg-canvas dark:hover:bg-canvas-dark transition"
            >
              <IoThumbsUpOutline size={15} aria-hidden="true" /> Sí
            </button>
            <button
              type="button"
              onClick={() => handleVote("no")}
              className="flex items-center gap-1.5 text-sm font-medium px-4 py-2 rounded-full border border-line dark:border-line-dark text-ink dark:text-ink-dark hover:bg-canvas dark:hover:bg-canvas-dark transition"
            >
              <IoThumbsDownOutline size={15} aria-hidden="true" /> No
            </button>
          </div>
        </>
      )}

      <button
        type="button"
        onClick={handleReport}
        disabled={reported}
        className="mt-4 flex items-center gap-1.5 text-xs text-muted dark:text-muted-dark hover:text-ember-500 disabled:opacity-60 disabled:hover:text-muted transition-colors"
      >
        <IoFlagOutline size={13} aria-hidden="true" />
        {reported ? "Problema reportado" : "Reportar un problema con este artículo"}
      </button>
    </div>
  );
}
