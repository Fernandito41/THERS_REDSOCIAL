import { useRouter } from 'expo-router';
import { useCallback, useState } from 'react';
import {
  ActivityIndicator,
  Pressable,
  RefreshControl,
  ScrollView,
  StyleSheet,
  Text,
  View,
} from 'react-native';
import { useSafeAreaInsets } from 'react-native-safe-area-context';

import { useAuth } from '@features/auth/context/AuthContext';
import { colors, fontSize, radius, space } from '@shared/design/tokens';

/**
 * Primera pantalla autenticada. Muestra datos REALES de `GET /api/users/me`.
 *
 * THERS_PROMPT §9: "no construyas un feed falso para aparentar que está
 * conectado". Acá no hay ni un dato inventado: todo sale del contrato.
 */
export default function Profile() {
  const { user, logout, refreshUser } = useAuth();
  const router = useRouter();
  const insets = useSafeAreaInsets();

  const [isRefreshing, setIsRefreshing] = useState(false);
  const [refreshError, setRefreshError] = useState<string | null>(null);

  const handleRefresh = useCallback(async () => {
    setIsRefreshing(true);
    setRefreshError(null);
    const ok = await refreshUser();
    if (!ok) {
      // `refreshUser` devuelve `false` por fallo de red (mantiene la sesión) o
      // porque la sesión ya no vale (la limpia). Si la limpió, el efecto de
      // abajo redirige; si fue red, se avisa sin expulsar al usuario.
      setRefreshError('No pudimos actualizar tus datos. Revisá tu conexión.');
    }
    setIsRefreshing(false);
  }, [refreshUser]);

  async function handleLogout() {
    await logout();
    router.replace('/login');
  }

  // La sesión se cayó mientras esta pantalla estaba montada (p. ej. el token de
  // 15 minutos expiró y `refreshUser` recibió 401). Se devuelve al login sin
  // dejar una pantalla vacía ni un crash por leer `user.algo` sobre `null`.
  if (!user) {
    return (
      <View style={styles.centered}>
        <ActivityIndicator size="large" color={colors.brand} />
        <Text style={styles.expiredText}>Tu sesión expiró. Volvé a iniciar sesión.</Text>
        <Pressable
          style={({ pressed }) => [styles.secondaryButton, pressed && styles.secondaryPressed]}
          onPress={() => router.replace('/login')}
          accessibilityRole="button"
        >
          <Text style={styles.secondaryButtonText}>Ir al inicio de sesión</Text>
        </Pressable>
      </View>
    );
  }

  const initial = (user.name || user.username || '?').charAt(0).toUpperCase();

  return (
    <ScrollView
      style={styles.flex}
      contentContainerStyle={[
        styles.content,
        { paddingTop: insets.top + space[6], paddingBottom: insets.bottom + space[8] },
      ]}
      refreshControl={
        <RefreshControl
          refreshing={isRefreshing}
          onRefresh={handleRefresh}
          tintColor={colors.brand}
        />
      }
    >
      <View style={styles.header}>
        <View style={styles.avatar}>
          <Text style={styles.avatarText}>{initial}</Text>
        </View>
        <Text style={styles.name}>{user.name}</Text>
        <Text style={styles.username}>@{user.username}</Text>
      </View>

      <View style={styles.statsRow}>
        <View style={styles.stat}>
          <Text style={styles.statValue}>{user.followers_count}</Text>
          <Text style={styles.statLabel}>Seguidores</Text>
        </View>
        <View style={styles.statDivider} />
        <View style={styles.stat}>
          <Text style={styles.statValue}>{user.following_count}</Text>
          <Text style={styles.statLabel}>Siguiendo</Text>
        </View>
      </View>

      <View style={styles.card}>
        <Field label="Email" value={user.email} />
        <Field label="Teléfono" value={formatPhone(user.phone, user.country_code)} />
        <Field label="Fecha de nacimiento" value={user.birth_date ?? 'No definida'} />
        <Field
          label="Correo verificado"
          value={user.email_verified ? 'Sí' : 'No'}
          valueColor={user.email_verified ? colors.successFg : colors.dangerFg}
        />
        <Field
          label="Perfil completo"
          value={user.profile_completed ? 'Sí' : 'Faltan datos'}
          valueColor={user.profile_completed ? colors.successFg : colors.dangerFg}
          isLast
        />
      </View>

      {refreshError ? (
        <View style={styles.errorBox} accessibilityLiveRegion="polite">
          <Text style={styles.errorText}>{refreshError}</Text>
        </View>
      ) : null}

      {!user.profile_completed ? (
        <Text style={styles.note}>
          Faltan datos de tu perfil. Completalos desde la web de THERS: la pantalla móvil para
          editarlos todavía no está implementada.
        </Text>
      ) : null}

      <Pressable
        style={({ pressed }) => [styles.logoutButton, pressed && styles.logoutPressed]}
        onPress={handleLogout}
        accessibilityRole="button"
      >
        <Text style={styles.logoutText}>Cerrar sesión</Text>
      </Pressable>
    </ScrollView>
  );
}

/** `phone` y `country_code` son un par atómico en el contrato (`ADR-003`). */
function formatPhone(phone: string | null, countryCode: string | null): string {
  if (!phone) return 'No definido';
  return countryCode ? `${countryCode} ${phone}` : phone;
}

function Field({
  label,
  value,
  valueColor,
  isLast,
}: {
  label: string;
  value: string;
  valueColor?: string;
  isLast?: boolean;
}) {
  return (
    <View style={[styles.field, isLast && styles.fieldLast]}>
      <Text style={styles.fieldLabel}>{label}</Text>
      <Text style={[styles.fieldValue, valueColor ? { color: valueColor } : null]}>{value}</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  flex: { flex: 1, backgroundColor: colors.bg },
  content: { paddingHorizontal: space[4] },
  centered: {
    flex: 1,
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: colors.bg,
    padding: space[6],
  },
  expiredText: {
    marginTop: space[4],
    fontSize: fontSize.bodyMd,
    color: colors.fgSecondary,
    textAlign: 'center',
  },
  header: { alignItems: 'center', marginBottom: space[6] },
  avatar: {
    width: 88,
    height: 88,
    borderRadius: radius.pill,
    backgroundColor: colors.brand,
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: space[3],
  },
  avatarText: {
    color: colors.onBrand,
    fontSize: fontSize.headlineLg,
    fontWeight: '800',
  },
  name: { fontSize: fontSize.headlineMd, fontWeight: '700', color: colors.fg },
  username: { fontSize: fontSize.bodyMd, color: colors.fgMuted, marginTop: space[1] },
  statsRow: {
    flexDirection: 'row',
    backgroundColor: colors.surface,
    borderRadius: radius.card,
    borderWidth: 1,
    borderColor: colors.border,
    paddingVertical: space[4],
    marginBottom: space[4],
  },
  stat: { flex: 1, alignItems: 'center' },
  statDivider: { width: 1, backgroundColor: colors.borderSubtle },
  statValue: { fontSize: fontSize.headlineSm, fontWeight: '700', color: colors.fg },
  statLabel: { fontSize: fontSize.labelMd, color: colors.fgMuted, marginTop: space[1] },
  card: {
    backgroundColor: colors.surface,
    borderRadius: radius.card,
    borderWidth: 1,
    borderColor: colors.border,
    paddingHorizontal: space[4],
  },
  field: {
    paddingVertical: space[3],
    borderBottomWidth: 1,
    borderBottomColor: colors.borderSubtle,
  },
  fieldLast: { borderBottomWidth: 0 },
  fieldLabel: { fontSize: fontSize.labelMd, color: colors.fgMuted, marginBottom: space[1] },
  fieldValue: { fontSize: fontSize.bodyMd, color: colors.fg },
  errorBox: {
    backgroundColor: colors.dangerSurface,
    borderWidth: 1,
    borderColor: colors.dangerBorder,
    borderRadius: radius.sm,
    padding: space[3],
    marginTop: space[4],
  },
  errorText: { color: colors.dangerFg, fontSize: fontSize.bodySm },
  note: {
    fontSize: fontSize.bodySm,
    color: colors.fgMuted,
    marginTop: space[4],
    lineHeight: 18,
  },
  logoutButton: {
    marginTop: space[8],
    borderRadius: radius.input,
    borderWidth: 1,
    borderColor: colors.dangerBorder,
    backgroundColor: colors.surface,
    paddingVertical: space[4],
    alignItems: 'center',
    minHeight: 52,
    justifyContent: 'center',
  },
  logoutPressed: { backgroundColor: colors.dangerSurface },
  logoutText: {
    color: colors.dangerAccent,
    fontSize: fontSize.bodyLg,
    fontWeight: '600',
  },
  secondaryButton: {
    marginTop: space[6],
    borderRadius: radius.input,
    backgroundColor: colors.brand,
    paddingVertical: space[3],
    paddingHorizontal: space[6],
  },
  secondaryPressed: { backgroundColor: colors.brandHover },
  secondaryButtonText: { color: colors.onBrand, fontWeight: '700', fontSize: fontSize.bodyMd },
});
