import Avatar from "@shared/components/Avatar";
import BrandMark from "@shared/components/BrandMark";

// Ilustración abstracta del feed de THERS construida solo con los tokens del
// Design System (Avatar real reutilizado + barras de color) -- no es una
// captura de pantalla real, no simula contenido/usuarios existentes.
export default function PhoneMockup() {
  return (
    <div className="relative mx-auto w-64 sm:w-72">
      <div className="rounded-[40px] border-8 border-ink dark:border-surface-dark bg-canvas dark:bg-canvas-dark shadow-lift overflow-hidden aspect-[9/19]">
        <div className="h-full flex flex-col">
          <div className="flex items-center px-4 py-3 border-b border-line dark:border-line-dark shrink-0">
            <BrandMark size="text-sm" iconSize="w-4 h-4" />
          </div>

          <div className="flex-1 p-3 space-y-3 overflow-hidden">
            <div className="flex items-center gap-2">
              <Avatar name="Ana Ríos" size="w-8 h-8 text-[10px]" />
              <div className="flex-1 space-y-1.5">
                <div className="h-2 w-20 rounded-full bg-line dark:bg-line-dark" />
                <div className="h-1.5 w-14 rounded-full bg-line dark:bg-line-dark" />
              </div>
            </div>

            <div className="rounded-2xl bg-gradient-to-br from-pulse-500 to-pulse-700 aspect-[4/3] shadow-soft" />

            <div className="flex items-center gap-3">
              <div className="h-2 w-8 rounded-full bg-line dark:bg-line-dark" />
              <div className="h-2 w-8 rounded-full bg-line dark:bg-line-dark" />
              <div className="h-2 w-8 rounded-full bg-line dark:bg-line-dark" />
            </div>

            <div className="flex items-center gap-2">
              <Avatar name="Leo Martín" size="w-8 h-8 text-[10px]" />
              <div className="flex-1 space-y-1.5">
                <div className="h-2 w-24 rounded-full bg-line dark:bg-line-dark" />
                <div className="h-1.5 w-16 rounded-full bg-line dark:bg-line-dark" />
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
