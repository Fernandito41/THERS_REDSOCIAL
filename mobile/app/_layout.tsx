import { Stack } from 'expo-router';
import { StatusBar } from 'expo-status-bar';
import { SafeAreaProvider } from 'react-native-safe-area-context';

import { AuthProvider } from '@features/auth/context/AuthContext';
import { PostsProvider } from '@features/posts/PostsContext';
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
        {/* Las publicaciones se cargan al iniciar sesión y se vacían al cerrarla. */}
        <PostsProvider>
          <StatusBar style="dark" />
          <Stack
            screenOptions={{
              headerShown: false,
              contentStyle: { backgroundColor: colors.bg },
            }}
          />
        </PostsProvider>
      </AuthProvider>
    </SafeAreaProvider>
  );
}
