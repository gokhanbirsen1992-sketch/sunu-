import { useEffect, useState } from "react";
import type { Section } from "../types";
import { layerTheme } from "../layerThemes";

type Props = {
  sections: Section[];
};

export function SideNav({ sections }: Props) {
  const [active, setActive] = useState<string | null>(null);

  useEffect(() => {
    const observer = new IntersectionObserver(
      (entries) => {
        for (const e of entries) {
          if (e.isIntersecting) {
            const id = (e.target as HTMLElement).id.replace("katman-", "");
            setActive(id);
          }
        }
      },
      { rootMargin: "-40% 0px -55% 0px", threshold: 0 },
    );
    sections.forEach((s) => {
      const el = document.getElementById(`katman-${s.id}`);
      if (el) observer.observe(el);
    });
    return () => observer.disconnect();
  }, [sections]);

  return (
    <nav className="sidenav" aria-label="Katmanlar">
      {sections.map((s) => {
        const theme = layerTheme(s.id);
        const isActive = active === s.id;
        return (
          <button
            key={s.id}
            type="button"
            data-active={isActive}
            onClick={() => {
              document
                .getElementById(`katman-${s.id}`)
                ?.scrollIntoView({ behavior: "smooth", block: "start" });
            }}
            style={{ color: isActive ? theme.accent : undefined }}
            title={`Katman ${s.id} — ${theme.label}`}
          >
            <span className="sidenav__dot" />
            <span className="sidenav__id">{s.id}</span>
            <span className="sidenav__label">{theme.label}</span>
          </button>
        );
      })}
    </nav>
  );
}
