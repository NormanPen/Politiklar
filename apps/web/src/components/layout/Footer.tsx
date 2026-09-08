import Link from "next/link";

const navLinks = [
  { label: "Inhaltsübersicht", href: "/inhaltsuebersicht" },
  { label: "Kontakt", href: "/kontakt" },
  { label: "Verwendung von Cookies", href: "/cookies" },
  { label: "Datenschutz", href: "/datenschutz" },
  { label: "Impressum", href: "/impressum" },
];

export default function Footer() {
  return (
    <footer className="w-full bg-[#FFFFFF] mt-auto">
      {/* 1024px zentrierter Container gemäß Figma-Vorgaben */}
      <div className="max-w-[1024px] mx-auto px-4 sm:px-6 pt-[64px] pb-[64px]">
        {/* Line 1: 1024px, 1px solid #878787 */}
        <div className="w-full border-t border-[#878787]" />

        {/* Group 5: 976px Breite (bei 1024px - 2x24px Padding), 64px Abstand zur Linie */}
        <div className="pt-[64px] flex flex-col md:flex-row items-center justify-between gap-y-6 text-[12px] leading-[15px] font-normal text-[#000000]">
          <p className="order-2 md:order-1 select-none">
            © 2026 Politiklar
          </p>

          <nav
            aria-label="Footer-Navigation"
            className="order-1 md:order-2 flex flex-wrap items-center justify-center md:justify-end gap-x-6 lg:gap-x-[64px] gap-y-3"
          >
            {navLinks.map((link) => (
              <Link
                key={link.label}
                href={link.href}
                className="text-[#000000] hover:opacity-70 transition-opacity"
              >
                {link.label}
              </Link>
            ))}
          </nav>
        </div>
      </div>
    </footer>
  );
}