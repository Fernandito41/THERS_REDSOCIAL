import { IoClose, IoChevronBack, IoChevronForward } from "react-icons/io5";
import Avatar from "@shared/components/Avatar";
import MoodBadge from "./MoodBadge";

export default function MomentViewer({ moments, index, onClose, onPrev, onNext }) {
  const moment = moments[index];

  return (
    <div
      className="fixed inset-0 z-50 bg-ink/90 backdrop-blur-sm flex items-center justify-center px-4"
      onClick={onClose}
    >
      <div
        className="relative w-full max-w-sm h-[80vh] rounded-[32px] overflow-hidden animate-float-in"
        onClick={(e) => e.stopPropagation()}
      >
        <img src={moment.image} alt="" className="absolute inset-0 w-full h-full object-cover" />
        <div className="absolute inset-0 bg-gradient-to-b from-black/50 via-transparent to-black/60" />

        <div className="absolute top-0 inset-x-0 flex gap-1 p-4">
          {moments.map((_, i) => (
            <div key={i} className="flex-1 h-1 rounded-full bg-white/25 overflow-hidden">
              <div className={`h-full bg-white transition-all ${i <= index ? "w-full" : "w-0"}`} />
            </div>
          ))}
        </div>

        <div className="absolute top-8 left-4 flex items-center gap-2">
          <Avatar name={moment.name} photo={moment.photo} size="w-9 h-9 text-sm" ring />
          <div>
            <p className="text-white font-semibold text-sm drop-shadow">{moment.name}</p>
            <p className="text-white/70 text-xs">{moment.time}</p>
          </div>
        </div>

        <div className="absolute bottom-6 left-4">
          <MoodBadge mood={moment.mood} />
        </div>

        <button
          onClick={onClose}
          aria-label="Cerrar momento"
          className="absolute top-7 right-4 text-white bg-black/25 hover:bg-black/40 p-2 rounded-full transition"
        >
          <IoClose size={20} />
        </button>

        {index > 0 && (
          <button
            onClick={onPrev}
            aria-label="Momento anterior"
            className="absolute left-2 top-1/2 -translate-y-1/2 text-white bg-black/25 hover:bg-black/40 p-2 rounded-full transition"
          >
            <IoChevronBack size={20} />
          </button>
        )}

        {index < moments.length - 1 && (
          <button
            onClick={onNext}
            aria-label="Siguiente momento"
            className="absolute right-2 top-1/2 -translate-y-1/2 text-white bg-black/25 hover:bg-black/40 p-2 rounded-full transition"
          >
            <IoChevronForward size={20} />
          </button>
        )}
      </div>
    </div>
  );
}
