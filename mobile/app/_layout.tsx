import { Stack } from 'expo-router';
import { StatusBar } from 'expo-status-bar';
import { SafeAreaProvider } from 'react-native-safe-area-context';

import { AuthProvider } from '@features/auth/context/AuthContext';
import { colors } from '@shared/design/tokens';

/**
 * Layout raíz. Monta los proveedores una sola vez para toda la app.
 *
 * `headerShown: false`: las pantallas de esta entrega dibujan su propia
 * cabecera con los tokens de THERS, para no mezclar el estilo nativo por
 * defecto con la identidad del producto.
 */
export default function RootLayout() {
  return (
    <SafeAreaProvider>
      <AuthProvider>
        <StatusBar style="dark" />
        <Stack
          screenOptions={{
            headerShown: false,
            contentStyle: { backgroundColor: colors.bg },
          }}
        />
      </AuthProvider>
    </SafeAreaProvider>
  );
}
