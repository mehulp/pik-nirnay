import { createContext, useContext, useMemo, useState, type ReactNode } from "react";

import en from "./locales/en.json";
import mr from "./locales/mr.json";

export type SupportedLanguage = "mr" | "en";

export const DEFAULT_LANGUAGE: SupportedLanguage = "mr";

const catalogues: Record<SupportedLanguage, Record<string, string>> = { mr, en };

interface LanguageContextValue {
  language: SupportedLanguage;
  setLanguage: (language: SupportedLanguage) => void;
  t: (key: string) => string;
}

const LanguageContext = createContext<LanguageContextValue | undefined>(undefined);

export function LanguageProvider({ children }: { children: ReactNode }) {
  const [language, setLanguage] = useState<SupportedLanguage>(DEFAULT_LANGUAGE);

  const value = useMemo<LanguageContextValue>(() => {
    const t = (key: string): string =>
      catalogues[language][key] ?? catalogues[DEFAULT_LANGUAGE][key] ?? key;
    return { language, setLanguage, t };
  }, [language]);

  return <LanguageContext.Provider value={value}>{children}</LanguageContext.Provider>;
}

export function useTranslation(): LanguageContextValue {
  const context = useContext(LanguageContext);
  if (!context) {
    throw new Error("useTranslation must be used within a LanguageProvider");
  }
  return context;
}
