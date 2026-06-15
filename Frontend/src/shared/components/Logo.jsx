export default function Logo({ size = "text-4xl" }) {
  return (
    <div className={`flex items-center gap-1 ${size}`}>
      
      <span className="font-extrabold text-white">
        T
      </span>

      <div className="relative">
        <span className="font-extrabold text-white">
          H
        </span>

        <div
          className="absolute top-1/2 left-0 w-full h-1 rounded-full"
          style={{
            background: "linear-gradient(90deg, #7B2CBF, #C77DFF)",
            transform: "translateY(-50%) rotate(20deg)",
          }}
        />
      </div>

    </div>
  );
}