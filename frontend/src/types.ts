export type Section = {
  id: string;
  title: string;
  paragraphs: string[];
};

export type Story = {
  title: string;
  subtitle: string;
  sections: Section[];
};

export type LayerTheme = {
  /** Short label shown in nav */
  label: string;
  /** Emoji-free single glyph or 1-2 char marker for the side rail */
  glyph: string;
  /** Accent color (hex) used for the section heading + nav dot */
  accent: string;
  /** Optional brief tagline displayed above the title */
  tagline: string;
};
