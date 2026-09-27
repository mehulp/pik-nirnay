import type { SupportedLanguage } from "./i18n";
import { useTranslation } from "./i18n";
import "./App.css";

// Each language's own name is shown in its own script, regardless of the
// currently active language, so a user can always recognize their target
// (e.g. an English-only reader must still be able to find "मराठी").
const LANGUAGE_OPTIONS: { code: SupportedLanguage; nativeName: string }[] = [
  { code: "mr", nativeName: "मराठी" },
  { code: "en", nativeName: "English" },
];

export default function App() {
  const { language, setLanguage, t } = useTranslation();

  return (
    <div className="app-shell">
      <header className="app-header">
        <h1>{t("app.title")}</h1>
        <div className="language-toggle" role="group" aria-label="Language">
          {LANGUAGE_OPTIONS.map((option) => (
            <button
              key={option.code}
              type="button"
              aria-pressed={language === option.code}
              className={language === option.code ? "active" : ""}
              onClick={() => setLanguage(option.code)}
            >
              {option.nativeName}
            </button>
          ))}
        </div>
      </header>

      <main>
        <p className="tagline">{t("app.tagline")}</p>
        <p className="coming-soon">{t("app.comingSoon")}</p>
      </main>

      <footer className="disclaimer">{t("app.disclaimer")}</footer>
    </div>
  );
}
