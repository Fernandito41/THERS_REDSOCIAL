import { useRouter } from 'expo-router';
import { useState } from 'react';
import {
  ActivityIndicator,
  KeyboardAvoidingView,
  Platform,
  Pressable,
  ScrollView,
  StyleSheet,
  Text,
  TextInput,
  View,
} from 'react-native';
import { useSafeAreaInsets } from 'react-native-safe-area-context';

import { useAuth } from '@features/auth/context/AuthContext';
import { isValidEmail } from '@features/auth/lib/validators';
import { ApiError } from '@shared/lib/api';
import { colors, fontSize, radius, space } from '@shared/design/tokens';

export default function Login() {
  const { login } = useAuth();
  const router = useRouter();
  const insets = useSafeAreaInsets();

  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  async function handleSubmit() {
    // Guarda contra doble toque: sin esto, dos pulsaciones rápidas disparan dos
    // POST /api/login.
    if (isSubmitting) return;

    setError(null);

    if (!email.trim() || !password) {
      setError('Email y contraseña son obligatorios.');
      return;
    }
    if (!isValidEmail(email)) {
      setError('El email no es válido.');
      return;
    }

    setIsSubmitting(true);
    try {
      await login(email, password);
      // `replace`, no `push`: el login no debe quedar en la pila: el botón
      // Atrás desde el perfil no puede volver a una pantalla de credenciales.
      router.replace('/profile');
    } catch (e) {
      if (e instanceof ApiError) {
        // `403` con `email_verified: false` es un caso propio del contrato
        // (`ADR-011`): las credenciales ERAN correctas, falta verificar el
        // correo. Se distingue por el cuerpo, nunca parseando el texto.
        const body = e.body as { email_verified?: boolean } | null;
        if (e.status === 403 && body?.email_verified === false) {
          setError(
            'Tu correo todavía no fue verificado. Verificá tu cuenta desde la web de THERS ' +
              'para poder iniciar sesión.',
          );
        } else {
          setError(e.message);
        }
      } else {
        setError('Ocurrió un error inesperado. Intentá de nuevo.');
      }
    } finally {
      // En `finally`: si no, un error deja el botón cargando para siempre.
      setIsSubmitting(false);
    }
  }

  return (
    <KeyboardAvoidingView
      style={styles.flex}
      behavior={Platform.OS === 'ios' ? 'padding' : undefined}
    >
      <ScrollView
        contentContainerStyle={[
          styles.scroll,
          { paddingTop: insets.top + space[10], paddingBottom: insets.bottom + space[6] },
        ]}
        keyboardShouldPersistTaps="handled"
      >
        <Text style={styles.brand}>THERS</Text>
        <Text style={styles.subtitle}>Iniciá sesión para continuar</Text>

        <View style={styles.field}>
          <Text style={styles.label}>Email</Text>
          <TextInput
            style={styles.input}
            value={email}
            onChangeText={setEmail}
            placeholder="tu@email.com"
            placeholderTextColor={colors.fgDisabled}
            autoCapitalize="none"
            autoCorrect={false}
            keyboardType="email-address"
            textContentType="emailAddress"
            editable={!isSubmitting}
            returnKeyType="next"
          />
        </View>

        <View style={styles.field}>
          <Text style={styles.label}>Contraseña</Text>
          <TextInput
            style={styles.input}
            value={password}
            onChangeText={setPassword}
            placeholder="••••••••"
            placeholderTextColor={colors.fgDisabled}
            secureTextEntry
            autoCapitalize="none"
            autoCorrect={false}
            textContentType="password"
            editable={!isSubmitting}
            returnKeyType="go"
            onSubmitEditing={handleSubmit}
          />
        </View>

        {error ? (
          <View style={styles.errorBox} accessibilityLiveRegion="polite">
            <Text style={styles.errorText}>{error}</Text>
          </View>
        ) : null}

        <Pressable
          style={({ pressed }) => [
            styles.button,
            pressed && styles.buttonPressed,
            isSubmitting && styles.buttonDisabled,
          ]}
          onPress={handleSubmit}
          disabled={isSubmitting}
          accessibilityRole="button"
          accessibilityState={{ disabled: isSubmitting, busy: isSubmitting }}
        >
          {isSubmitting ? (
            <ActivityIndicator color={colors.onBrand} />
          ) : (
            <Text style={styles.buttonText}>Entrar</Text>
          )}
        </Pressable>

        {/*
          Registro, recuperación de contraseña y "Continuar con Google" existen
          en el backend pero NO en esta entrega (ROADMAP fase 1/2). No se pone
          un botón que no hace nada: una pantalla que aparenta una función
          inexistente es peor que su ausencia.
        */}
        <Text style={styles.note}>
          Por ahora, crear cuenta y recuperar contraseña se hacen desde la web de THERS.
        </Text>
      </ScrollView>
    </KeyboardAvoidingView>
  );
}

const styles = StyleSheet.create({
  flex: { flex: 1, backgroundColor: colors.bg },
  scroll: {
    flexGrow: 1,
    justifyContent: 'center',
    paddingHorizontal: space[6],
  },
  brand: {
    fontSize: fontSize.headlineXl,
    fontWeight: '800',
    color: colors.brand,
    textAlign: 'center',
    letterSpacing: 1,
  },
  subtitle: {
    fontSize: fontSize.bodyMd,
    color: colors.fgSecondary,
    textAlign: 'center',
    marginTop: space[2],
    marginBottom: space[8],
  },
  field: { marginBottom: space[4] },
  label: {
    fontSize: fontSize.labelLg,
    fontWeight: '600',
    color: colors.fg,
    marginBottom: space[2],
  },
  input: {
    backgroundColor: colors.surface,
    borderWidth: 1,
    borderColor: colors.border,
    borderRadius: radius.input,
    paddingHorizontal: space[4],
    // Android e iOS necesitan alturas distintas para verse igual.
    paddingVertical: Platform.OS === 'ios' ? space[4] : space[3],
    fontSize: fontSize.bodyLg,
    color: colors.fg,
  },
  errorBox: {
    backgroundColor: colors.dangerSurface,
    borderWidth: 1,
    borderColor: colors.dangerBorder,
    borderRadius: radius.sm,
    padding: space[3],
    marginBottom: space[4],
  },
  errorText: { color: colors.dangerFg, fontSize: fontSize.bodySm },
  button: {
    backgroundColor: colors.brand,
    borderRadius: radius.input,
    paddingVertical: space[4],
    alignItems: 'center',
    justifyContent: 'center',
    minHeight: 52,
  },
  buttonPressed: { backgroundColor: colors.brandHover },
  buttonDisabled: { opacity: 0.6 },
  buttonText: {
    color: colors.onBrand,
    fontSize: fontSize.bodyLg,
    fontWeight: '700',
  },
  note: {
    fontSize: fontSize.bodySm,
    color: colors.fgMuted,
    textAlign: 'center',
    marginTop: space[6],
    lineHeight: 18,
  },
});
