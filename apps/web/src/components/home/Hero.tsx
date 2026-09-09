import Image from "next/image";

export default function Hero() {
  return (
    <section className="relative w-full h-[460px] sm:h-[500px] md:h-[552px] overflow-hidden bg-white">
      {/* Background Hero Image */}
      <Image
        src="/images/hero.jpg"
        alt="Deutscher Bundestag Plenarsaal"
        fill
        priority
        sizes="100vw"
        className="object-cover object-center"
      />

      {/* Figma Rectangle 3: Dark Overlay with 0.22 (22%) opacity */}
      <div
        className="absolute inset-0 pointer-events-none"
        style={{ backgroundColor: "rgba(0, 0, 0, 0.22)" }}
        aria-hidden="true"
      />

      {/* Centered Hero Content */}
      <div
        className="relative z-10 w-full max-w-[1024px] mx-auto px-4 flex flex-col items-center text-center pt-[130px] sm:pt-[150px] md:pt-[180px] font-['Inter',sans-serif]"
        style={{ fontFamily: "var(--font-inter), 'Inter', sans-serif" }}
      >
        {/* Main Headline (Figma: 64px, bold, leading 77px, top 180px) */}
        <h1 className="text-white font-bold text-[32px] sm:text-[48px] md:text-[64px] leading-tight md:leading-[77px] tracking-normal drop-shadow-sm select-none">
          Politik. Klar. Verstehen.
        </h1>

        {/* Subtitle (Figma: 24px, medium, leading 29px, top 261px -> mt 4px) */}
        <p className="mt-2 md:mt-[4px] text-white font-medium text-[16px] sm:text-[20px] md:text-[24px] leading-snug md:leading-[29px] tracking-normal drop-shadow-sm max-w-[700px] select-none">
          Tiefgründige Analysen und Fakten zur deutschen Politik
        </p>
      </div>
    </section>
  );
}
