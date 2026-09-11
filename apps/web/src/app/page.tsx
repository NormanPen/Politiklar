import Hero from "@/components/home/Hero";
import Button from "@/components/ui/Button";

export default function Home() {
  return (
    <>
      <Hero />
      <div className="max-w-4xl mx-auto px-6 py-16 space-y-8 text-center">
        <div className="space-y-4">
          <h2 className="text-3xl sm:text-4xl font-extrabold text-gray-900 tracking-tight">
            Willkommen bei <span className="text-[#A0E9ED]">Politiklar</span>
          </h2>
          <p className="text-lg text-gray-600 max-w-2xl mx-auto">
            Civic-Tech-Plattform für transparente und lückenlos nachvollziehbare Informationen aus offiziellen politischen Primärquellen des Deutschen Bundestages.
          </p>
        </div>

        {/* Schnellzugriff auf Test-Routen */}
        <div className="pt-4 flex flex-wrap justify-center gap-4">
          <Button href="/politicians" variant="cta">
            Politiker-Demo (Jan van Aken) →
          </Button>
          <Button href="/state-test" variant="secondary">
            State-Management Test
          </Button>
          <Button href="/about" variant="secondary">
            Über uns
          </Button>
        </div>
      </div>
    </>
  );
}
