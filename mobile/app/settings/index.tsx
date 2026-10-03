import { useRouter } from 'expo-router';
import { Pressable, StyleSheet, Text, View } from 'react-native';

import { colors, fontSize, radius, space } from '@shared/design/tokens';
import { Screen } from '@shared/ui/Screen';

type Row = { label: string; description: string; route: string; danger?: boolean };

// Solo secciones cuyo backend EXISTE y está conectado en la web. Las demás
// secciones de Configuración de la web (audio, enlaces, permisos...) son
// marcadores «pendiente» allí y no se replican.
const SECTIONS: { title: string; rows: Row[] }[] = [
  {
    title: 'Privacidad y seguridad',
    rows: [
      {
        label: 'Privacidad',
        description: 'Cuenta privada, quién puede escribirte y mencionarte, contenido sensible.',
        route: '/settings/privacy',
      },
      {
        label: 'Solicitudes de seguimiento',
        description: 'Aprueba o rechaza quién quiere seguirte (cuentas privadas).',
        route: '/settings/follow-requests',
      },
      {
        label: 'Cuentas bloqueadas',
        description: 'Revisa a quién bloqueaste y desbloquea.',
        route: '/settings/blocked',
      },
      {
        label: 'Palabras silenciadas',
        description: 'Oculta del inicio las publicaciones con ciertas palabras.',
        route: '/settings/muted',
      },
      {
        label: 'Sesiones activas',
        description: 'Dispositivos con tu cuenta abierta. Cierra los que no reconozcas.',
        route: '/settings/sessions',
      },
    ],
  },
  {
    title: 'Cuenta',
    rows: [
      {
        label: 'Eliminar cuenta',
        description: 'Elimina tu cuenta y sus datos de forma definitiva.',
        route: '/delete-account',
        danger: true,
      },
    ],
  },
];

/**
 * Ajustes. Cada fila lleva a una pantalla que lee y escribe en el SERVIDOR (no son
 * preferencias guardadas solo en el teléfono).
 */
export default function Settings() {
  const router = useRouter();

  return (
    <Screen title="Ajustes" back>
      {SECTIONS.map((section) => (
        <View key={section.title} style={styles.section}>
          <Text style={styles.sectionTitle}>{section.title}</Text>
          <View style={styles.card}>
            {section.rows.map((row, index) => (
              <Pressable
                key={row.route}
                onPress={() => router.push(row.route as never)}
                style={({ pressed }) => [
                  styles.row,
                  index > 0 && styles.rowBorder,
                  pressed && styles.rowPressed,
                ]}
                accessibilityRole="button"
                accessibilityHint={row.description}
              >
                <View style={styles.rowText}>
                  <Text style={[styles.label, row.danger && styles.danger]}>{row.label}</Text>
                  <Text style={styles.description}>{row.description}</Text>
                </View>
                <Text style={styles.chevron}>›</Text>
              </Pressable>
            ))}
          </View>
        </View>
      ))}

      <Text style={styles.footer}>
        Cambiar la contraseña, la verificación en dos pasos, descargar tus datos y la foto de perfil
        se hacen por ahora desde la web de THERS.
      </Text>
    </Screen>
  );
}

const styles = StyleSheet.create({
  section: { marginBottom: space[6] },
  sectionTitle: {
    fontSize: fontSize.labelLg,
    fontWeight: '700',
    color: colors.fgMuted,
    textTransform: 'uppercase',
    marginBottom: space[2],
    marginLeft: space[1],
  },
  card: {
    backgroundColor: colors.surface,
    borderWidth: 1,
    borderColor: colors.border,
    borderRadius: radius.card,
    overflow: 'hidden',
  },
  row: { flexDirection: 'row', alignItems: 'center', padding: space[4], minHeight: 64 },
  rowBorder: { borderTopWidth: 1, borderTopColor: colors.borderSubtle },
  rowPressed: { backgroundColor: colors.bgSubtle },
  rowText: { flex: 1 },
  label: { fontSize: fontSize.bodyLg, fontWeight: '600', color: colors.fg },
  danger: { color: colors.dangerAccent },
  description: { fontSize: fontSize.bodySm, color: colors.fgMuted, marginTop: 2, lineHeight: 18 },
  chevron: { fontSize: 26, color: colors.fgDisabled, marginLeft: space[2] },
  footer: { fontSize: fontSize.labelMd, color: colors.fgMuted, lineHeight: 17, marginTop: space[2] },
});
