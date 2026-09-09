import type { Metadata } from "next";
import { Geist, Geist_Mono, Inter } from "next/font/google";
import "./globals.css";
import Header from "@/components/layout/Header";
import Footer from "@/components/layout/Footer";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

const inter = Inter({
  variable: "--font-inter",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "Politiklar",
  description: "Politiklar – Transparente Einblicke in deutsche parlamentarische Daten",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="de" className={`${geistSans.variable} ${geistMono.variable} ${inter.variable}`} suppressHydrationWarning>
      <body className="min-h-screen bg-gray-50 text-gray-900 flex flex-col antialiased" suppressHydrationWarning>
        <Header />
        <main className="flex-1 pt-[48px]">{children}</main>
        <Footer />
      </body>
    </html>
  );
}
