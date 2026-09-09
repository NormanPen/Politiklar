"use client";

import { useState } from "react";
import Image from "next/image";
import Link from "next/link";

const navItems = [
  { label: "Dossier", href: "/dossier" },
  { label: "Gesetze", href: "/gesetze" },
  { label: "Kompass", href: "/kompass" },
  { label: "Daten", href: "/daten" },
  { label: "Klartext", href: "/klartext" },
];

export default function Header() {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  return (
    <header className="sticky top-0 z-50 w-full bg-[#FFFFFF] border-b border-gray-100 transition-colors">
      <div className="relative max-w-[1024px] mx-auto h-[48px] px-4 sm:px-6 flex items-center justify-between">
        {/* Logo (Left: 232px in 1440px frame, align to 1024px container left padding) */}
        <div className="flex-shrink-0 flex items-center">
          <Link
            href="/"
            className="flex items-center hover:opacity-90 transition-opacity focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-black rounded"
            aria-label="Politiklar Startseite"
          >
            <Image
              src="/images/logos/politiklar-logo.png"
              alt="Politiklar"
              width={141}
              height={32}
              priority
              className="h-[32px] w-auto object-contain"
            />
          </Link>
        </div>

        {/* Center Navigation (477px width, perfectly centered at 50% with 64px gap) */}
        <nav
          aria-label="Hauptnavigation"
          className="hidden md:flex absolute left-1/2 -translate-x-1/2 items-center md:gap-8 lg:gap-[64px] font-['Inter',sans-serif]"
          style={{ fontFamily: "var(--font-inter), 'Inter', sans-serif" }}
        >
          {navItems.map((item) => (
            <Link
              key={item.label}
              href={item.href}
              className="text-[#000000] text-[12px] leading-[15px] font-normal hover:opacity-60 transition-opacity tracking-normal"
            >
              {item.label}
            </Link>
          ))}
        </nav>

        {/* Right Actions: Search & Profile Icons (24px gap, 16x16 icon sizes) */}
        <div className="flex items-center gap-6">
          {/* Search Icon */}
          <Link
            href="#"
            className="p-1 text-black hover:opacity-60 transition-opacity focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-black rounded"
            aria-label="Suche"
          >
            <svg
              width="16"
              height="16"
              viewBox="0 0 16 16"
              fill="none"
              xmlns="http://www.w3.org/2000/svg"
              className="w-4 h-4 text-black block"
              aria-hidden="true"
            >
              <circle
                cx="6.5"
                cy="6.5"
                r="4.75"
                stroke="currentColor"
                strokeWidth="1.25"
              />
              <path
                d="M10.2 10.2L14 14"
                stroke="currentColor"
                strokeWidth="1.25"
                strokeLinecap="round"
              />
            </svg>
          </Link>

          {/* Profile / Account Icon */}
          <Link
            href="#"
            className="p-1 text-black hover:opacity-60 transition-opacity focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-black rounded"
            aria-label="Benutzerkonto"
          >
            <svg
              width="16"
              height="16"
              viewBox="0 0 16 16"
              fill="none"
              xmlns="http://www.w3.org/2000/svg"
              className="w-4 h-4 text-black block"
              aria-hidden="true"
            >
              <circle
                cx="8"
                cy="8"
                r="7"
                stroke="currentColor"
                strokeWidth="1.2"
              />
              <circle
                cx="8"
                cy="6.2"
                r="2.2"
                stroke="currentColor"
                strokeWidth="1.2"
              />
              <path
                d="M3.7 12.7C4.5 10.5 6.1 9.4 8 9.4C9.9 9.4 11.5 10.5 12.3 12.7"
                stroke="currentColor"
                strokeWidth="1.2"
                strokeLinecap="round"
              />
            </svg>
          </Link>

          {/* Mobile Menu Toggle Button (visible only on small screens) */}
          <button
            type="button"
            onClick={() => setMobileMenuOpen((prev) => !prev)}
            className="p-1 md:hidden text-black hover:opacity-60 transition-opacity focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-black rounded"
            aria-label={mobileMenuOpen ? "Menü schließen" : "Menü öffnen"}
            aria-expanded={mobileMenuOpen}
          >
            {mobileMenuOpen ? (
              <svg
                width="16"
                height="16"
                viewBox="0 0 16 16"
                fill="none"
                xmlns="http://www.w3.org/2000/svg"
                className="w-4 h-4 text-black"
                aria-hidden="true"
              >
                <path
                  d="M3 3L13 13M13 3L3 13"
                  stroke="currentColor"
                  strokeWidth="1.25"
                  strokeLinecap="round"
                />
              </svg>
            ) : (
              <svg
                width="16"
                height="16"
                viewBox="0 0 16 16"
                fill="none"
                xmlns="http://www.w3.org/2000/svg"
                className="w-4 h-4 text-black"
                aria-hidden="true"
              >
                <path
                  d="M2.5 4H13.5M2.5 8H13.5M2.5 12H13.5"
                  stroke="currentColor"
                  strokeWidth="1.25"
                  strokeLinecap="round"
                />
              </svg>
            )}
          </button>
        </div>
      </div>

      {/* Mobile Navigation Dropdown */}
      {mobileMenuOpen && (
        <div className="md:hidden border-t border-gray-100 bg-white/95 backdrop-blur-md px-6 py-4 shadow-sm animate-in fade-in slide-in-from-top-1 duration-150">
          <nav
            aria-label="Mobile Navigation"
            className="flex flex-col space-y-3 font-['Inter',sans-serif]"
            style={{ fontFamily: "var(--font-inter), 'Inter', sans-serif" }}
          >
            {navItems.map((item) => (
              <Link
                key={item.label}
                href={item.href}
                onClick={() => setMobileMenuOpen(false)}
                className="text-[#000000] text-[13px] leading-[18px] py-1 font-normal hover:opacity-60 transition-opacity"
              >
                {item.label}
              </Link>
            ))}
          </nav>
        </div>
      )}
    </header>
  );
}
