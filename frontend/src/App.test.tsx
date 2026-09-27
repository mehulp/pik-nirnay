import { fireEvent, render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import App from "./App";
import { LanguageProvider } from "./i18n";

function renderApp() {
  return render(
    <LanguageProvider>
      <App />
    </LanguageProvider>,
  );
}

describe("App", () => {
  it("defaults to Marathi", () => {
    renderApp();
    expect(screen.getByText("पीक निर्णय")).toBeInTheDocument();
  });

  it("shows the prototype disclaimer", () => {
    renderApp();
    expect(screen.getByText(/शैक्षणिक\/संशोधन प्रोटोटाइप/)).toBeInTheDocument();
  });

  it("switches to English when toggled", () => {
    renderApp();
    fireEvent.click(screen.getByRole("button", { name: "English" }));
    expect(screen.getByText("Pik Nirnay")).toBeInTheDocument();
    expect(screen.getByText(/educational\/research prototype/)).toBeInTheDocument();
  });
});
