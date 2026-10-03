import { Redirect } from 'expo-router';
import { Tabs } from 'expo-router/js-tabs';
import { ActivityIndicator, View } from 'react-native';
import { useSafeAreaInsets } from 'react-native-safe-area-context';

import { useAuth } from '@features/auth/context/AuthContext';
import { colors, fontSize } from '@shared/design/tokens';

/**
 * Navegación principal: Inicio, Buscar, Mensajes, Avisos y Perfil.
 *
 * Solo existen las pestañas de funciones que la web tiene conectadas al backend
 * (Videos, Cápsulas y Radar son marcadores «en construcción» en la web y por eso
 * no se replican aquí). Todas son pantallas de la sesión: sin sesión se vuelve al
 * inicio de sesión.
 */
export default function TabsLayout() {
  const { user, isRestoring } = useAuth();
  const insets = useSafeAreaInsets();

  if (isRestoring) {
    return (
      <View style={{ flex: 1, alignItems: 'center', justifyContent: 'center', backgroundColor: colors.bg }}>
        <ActivityIndicator size="large" color={colors.brand} />
      </View>
    );
  }
  if (!user) return <Redirect href="/login" />;

  return (
    <Tabs
      screenOptions={{
        headerShown: false,
        tabBarActiveTintColor: colors.brand,
        tabBarInactiveTintColor: colors.fgMuted,
        tabBarLabelStyle: { fontSize: fontSize.labelMd, fontWeight: '600' },
        // Sin iconos: no hay biblioteca de iconos instalada y el encargo pide no
        // sumar dependencias sin necesidad. La etiqueta sola es clara y accesible.
        tabBarIcon: () => null,
        tabBarIconStyle: { display: 'none' },
        tabBarStyle: {
          backgroundColor: colors.surface,
          borderTopColor: colors.border,
          height: 56 + insets.bottom,
          paddingBottom: insets.bottom,
        },
        tabBarLabelPosition: 'beside-icon',
      }}
    >
      <Tabs.Screen name="home" options={{ title: 'Inicio' }} />
      <Tabs.Screen name="search" options={{ title: 'Buscar' }} />
      <Tabs.Screen name="messages" options={{ title: 'Mensajes' }} />
      <Tabs.Screen name="notifications" options={{ title: 'Avisos' }} />
      <Tabs.Screen name="profile" options={{ title: 'Perfil' }} />
    </Tabs>
  );
}
