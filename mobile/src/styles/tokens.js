// Design tokens, ported from frontend/src/styles/tokens.css.
//
// Palette: near-black terminal base (#0b0d10 / #12151a give just
// enough separation between background and card layers). Accent: a
// single functional cyan (#4fd1c5) for interactive elements and the
// ranking score bar. Green/red are reserved strictly for P&L semantics,
// never used decoratively. Type: Inter for UI text, JetBrains Mono for
// every number (prices, P&L, percentages, scores) so columns of
// figures align like a real terminal tape.
export const colors = {
  bgBase: '#0b0d10',
  bgPanel: '#12151a',
  bgPanelRaised: '#171b21',
  bgHover: '#1c2129',
  borderHairline: '#232830',
  borderHairlineStrong: '#2d333d',

  textPrimary: '#e7eaee',
  textSecondary: '#9099a8',
  textTertiary: '#626b7a',
  textOnAccent: '#06181a',

  accent: '#4fd1c5',
  accentDim: '#2e6f68',
  accentWash: 'rgba(79, 209, 197, 0.1)',

  positive: '#3ddc84',
  positiveWash: 'rgba(61, 220, 132, 0.1)',
  negative: '#ff6b6b',
  negativeWash: 'rgba(255, 107, 107, 0.1)',
  neutral: '#9099a8',
}

export const fonts = {
  ui: 'Inter_400Regular',
  uiMedium: 'Inter_500Medium',
  uiSemiBold: 'Inter_600SemiBold',
  mono: 'JetBrainsMono_400Regular',
  monoMedium: 'JetBrainsMono_500Medium',
}

export const spacing = {
  1: 4,
  2: 8,
  3: 12,
  4: 16,
  5: 20,
  6: 24,
  8: 32,
  10: 40,
  12: 48,
}

export const radii = {
  sm: 6,
  md: 10,
  lg: 14,
}
