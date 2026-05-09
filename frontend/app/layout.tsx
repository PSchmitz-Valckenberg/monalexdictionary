import type { Metadata } from "next";
import { Geist } from "next/font/google";
import { Lora } from "next/font/google";
import "./globals.css";
import Nav from "@/components/nav";
import { ThemeProvider } from "@/components/theme-provider";
import SwRegister from "@/components/sw-register";
import PwaInstall from "@/components/pwa-install";

const geist = Geist({ variable: "--font-geist-sans", subsets: ["latin"] });
const lora = Lora({
  variable: "--font-lora",
  subsets: ["latin"],
  display: "swap",
});

export const metadata: Metadata = {
  title: "Monalex — Dictionnaire français-monégasque",
  description:
    "Explorez le riche patrimoine linguistique de Monaco. Dictionnaire français-monégasque avec 14 000 entrées, conjugaisons et assistant IA.",
  manifest: "/manifest.json",
  appleWebApp: {
    capable: true,
    statusBarStyle: "default",
    title: "Monalex",
  },
  // TODO: replace with a real 180×180 PNG (SVG is ignored by iOS for home screen icons)
  icons: { icon: "/icons/icon.svg" },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="fr" className={`${geist.variable} ${lora.variable} h-full antialiased`}>
      <head>
        <meta name="theme-color" content="#ce1126" />
        <meta name="mobile-web-app-capable" content="yes" />
        {/* Prevent flash of wrong theme before React hydrates */}
        <script
          dangerouslySetInnerHTML={{
            __html: `(function(){try{var s=localStorage.getItem('theme');var p=window.matchMedia('(prefers-color-scheme: dark)').matches;if(s==='dark'||(s===null&&p))document.documentElement.classList.add('dark');}catch(e){}})();`,
          }}
        />
      </head>
      <body className="min-h-full flex flex-col bg-white dark:bg-slate-900 text-gray-900 dark:text-slate-100 transition-colors">
        <ThemeProvider>
          <Nav />
          <main className="flex-1">{children}</main>
          <footer className="border-t border-gray-100 dark:border-slate-800 py-6 text-center text-sm text-gray-400 dark:text-slate-500">
            © {new Date().getFullYear()} Monalex — Dictionnaire français-monégasque
          </footer>
          <PwaInstall />
        </ThemeProvider>
        <SwRegister />
      </body>
    </html>
  );
}
