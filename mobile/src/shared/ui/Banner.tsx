import { StyleSheet, Text, View } from 'react-native';

import { colors, fontSize, radius, space } from '@shared/design/tokens';

type Props = { tone?: 'error' | 'info' | 'success'; children: string };

/** Aviso en línea. `error` y `success` se anuncian a lectores de pantalla. */
export function Banner({ tone = 'info', children }: Props) {
  const palette = PALETTE[tone];
  return (
    <View
      style={[styles.box, { backgroundColor: palette.bg, borderColor: palette.border }]}
      accessibilityLiveRegion={tone === 'info' ? 'none' : 'polite'}
      accessibilityRole={tone === 'error' ? 'alert' : undefined}
    >
      <Text style={[styles.text, { color: palette.fg }]}>{children}</Text>
    </View>
  );
}

const PALETTE = {
  error: { bg: colors.dangerSurface, border: colors.dangerBorder, fg: colors.dangerFg },
  info: { bg: colors.brandSoft, border: colors.brandSoftStrong, fg: colors.fgSecondary },
  success: { bg: colors.successSurface, border: colors.successAccent, fg: colors.successFg },
} as const;

const styles = StyleSheet.create({
  box: { borderWidth: 1, borderRadius: radius.sm, padding: space[3], marginBottom: space[4] },
  text: { fontSize: fontSize.bodySm, lineHeight: 18 },
});
