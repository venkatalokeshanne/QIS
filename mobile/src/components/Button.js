import { Pressable, Text, StyleSheet } from 'react-native'
import { colors, fonts, radii, spacing } from '../styles/tokens'

const VARIANT_STYLES = {
  primary: { bg: colors.accent, text: colors.textOnAccent, border: colors.accent },
  secondary: { bg: colors.bgPanelRaised, text: colors.textPrimary, border: colors.borderHairlineStrong },
  ghost: { bg: 'transparent', text: colors.textSecondary, border: 'transparent' },
  danger: { bg: 'transparent', text: colors.negative, border: 'transparent' },
}

// Ported from frontend/src/components/Button.jsx -- same variant/size
// vocabulary (primary/secondary/ghost/danger, sm/default), no hover
// state (not a thing on touch), Pressable's built-in opacity feedback
// stands in for it.
export default function Button({ variant = 'secondary', size, disabled, onPress, children, style }) {
  const v = VARIANT_STYLES[variant]
  return (
    <Pressable
      onPress={onPress}
      disabled={disabled}
      style={({ pressed }) => [
        styles.base,
        size === 'sm' ? styles.sm : null,
        { backgroundColor: v.bg, borderColor: v.border },
        disabled ? styles.disabled : null,
        pressed && !disabled ? styles.pressed : null,
        style,
      ]}
    >
      <Text style={[styles.text, size === 'sm' ? styles.textSm : null, { color: v.text }]}>{children}</Text>
    </Pressable>
  )
}

const styles = StyleSheet.create({
  base: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    gap: spacing[2],
    paddingVertical: 9,
    paddingHorizontal: spacing[4],
    borderRadius: radii.sm,
    borderWidth: 1,
  },
  sm: {
    paddingVertical: 6,
    paddingHorizontal: 11,
  },
  disabled: {
    opacity: 0.45,
  },
  pressed: {
    opacity: 0.75,
  },
  text: {
    fontFamily: fonts.uiSemiBold,
    fontSize: 13,
  },
  textSm: {
    fontSize: 12,
  },
})
