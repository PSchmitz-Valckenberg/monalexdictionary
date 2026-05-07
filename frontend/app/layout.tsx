import type { Metadata } from "next";
import { Geist } from "next/font/google";
import "./globals.css";
import Nav from "@/components/nav";

const geist = Geist({ variable: "--font-geist-sans", subsets: ["latin"] });

export const metadata: Metadata = {
  title: "Monalex — Dictionnaire français-monégasque",
  description:
    "Explorez le riche patrimoine linguistique de Monaco. Dictionnaire français-monégasque avec 14 000 entrées, conjugaisons et assistant IA.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="fr" className={`${geist.variable} h-full antialiased`}>
      <body className="min-h-full flex flex-col bg-white text-gray-900">
        <Nav />
        <main className="flex-1">{children}</main>
        <footer className="border-t border-gray-100 py-6 text-center text-sm text-gray-400">
          © {new Date().getFullYear()} Monalex — Dictionnaire français-monégasque
        </footer>
      </body>
    </html>
  );
}
