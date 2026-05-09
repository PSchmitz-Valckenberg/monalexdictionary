"use client";

import { useEffect, useState } from "react";

interface BeforeInstallPromptEvent extends Event {
  prompt(): Promise<void>;
  userChoice: Promise<{ outcome: "accepted" | "dismissed" }>;
}

export default function PwaInstall() {
  const [prompt, setPrompt] = useState<BeforeInstallPromptEvent | null>(null);
  const [dismissed, setDismissed] = useState(false);

  useEffect(() => {
    if (localStorage.getItem("pwa-dismissed") === "1") {
      setDismissed(true);
      return;
    }
    function handle(e: Event) {
      e.preventDefault();
      setPrompt(e as BeforeInstallPromptEvent);
    }
    window.addEventListener("beforeinstallprompt", handle);
    return () => window.removeEventListener("beforeinstallprompt", handle);
  }, []);

  if (!prompt || dismissed) return null;

  return (
    <div className="fixed bottom-4 left-4 right-4 md:left-auto md:right-4 md:w-80 bg-white dark:bg-slate-800 border border-gray-200 dark:border-slate-700 rounded-2xl p-4 shadow-lg z-50">
      <p className="font-semibold text-gray-900 dark:text-slate-100 text-sm mb-1">
        Installer Monalex
      </p>
      <p className="text-xs text-gray-500 dark:text-slate-400 mb-3">
        Accédez au dictionnaire depuis votre écran d&apos;accueil, même sans connexion.
      </p>
      <div className="flex gap-2">
        <button
          onClick={async () => {
            await prompt.prompt();
            setPrompt(null);
          }}
          className="flex-1 px-3 py-2 bg-[#ce1126] text-white text-xs font-semibold rounded-xl hover:bg-[#a50e1f] transition-colors"
        >
          Installer
        </button>
        <button
          onClick={() => {
            localStorage.setItem("pwa-dismissed", "1");
            setDismissed(true);
          }}
          className="px-3 py-2 text-xs text-gray-500 dark:text-slate-400 hover:text-gray-700 dark:hover:text-slate-200 transition-colors"
        >
          Plus tard
        </button>
      </div>
    </div>
  );
}
