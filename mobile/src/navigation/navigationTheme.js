import { DarkTheme } from '@react-navigation/native'
import { colors, fonts } from '../styles/tokens'

// Shared React Navigation theme + screen-option defaults so every
// stack/tab navigator in the app renders the same near-black surfaces
// and cyan accent as the web app, instead of RN's default blue/white.
export const navigationTheme = {
  ...DarkTheme,
  colors: {
    ...DarkTheme.colors,
    background: colors.bgBase,
    card: colors.bgPanel,
    text: colors.textPrimary,
    border: colors.borderHairline,
    primary: colors.accent,
  },
}

export const stackScreenOptions = {
  headerStyle: { backgroundColor: colors.bgPanel },
  headerTintColor: colors.textPrimary,
  headerTitleStyle: { fontFamily: fonts.uiSemiBold },
  contentStyle: { backgroundColor: colors.bgBase },
  // Just the chevron, not the previous screen's title -- native-stack's
  // default back button otherwise falls back to the route name (e.g.
  // "RunBacktests") when a screen doesn't set its own back title.
  headerBackButtonDisplayMode: 'minimal',
}

export const bottomTabScreenOptions = {
  tabBarStyle: {
    backgroundColor: colors.bgPanel,
    borderTopColor: colors.borderHairline,
  },
  tabBarActiveTintColor: colors.accent,
  tabBarInactiveTintColor: colors.textSecondary,
  tabBarLabelStyle: { fontFamily: fonts.ui, fontSize: 11 },
  headerStyle: { backgroundColor: colors.bgPanel },
  headerTintColor: colors.textPrimary,
  headerTitleStyle: { fontFamily: fonts.uiSemiBold },
}

export const topTabScreenOptions = {
  tabBarStyle: { backgroundColor: colors.bgPanel },
  tabBarIndicatorStyle: { backgroundColor: colors.accent },
  tabBarActiveTintColor: colors.accent,
  tabBarInactiveTintColor: colors.textSecondary,
  tabBarLabelStyle: { fontFamily: fonts.ui, fontSize: 12, textTransform: 'none' },
}
