import { useFocusEffect, useRouter } from 'expo-router';
import { useCallback, useEffect, useRef, useState } from 'react';
import { AppState, FlatList, Pressable, RefreshControl, StyleSheet, Text, View } from 'react-native';

import { useAuth } from '@features/auth/context/AuthContext';
import { fetchConversations } from '@features/messages/api';
import type { ConversationSummary } from '@features/messages/api';
import { colors, fontSize, radius, space } from '@shared/design/tokens';
import { ApiError } from '@shared/lib/api';
import { formatRelativeTime } from '@shared/lib/time';
import { Avatar } from '@shared/ui/Avatar';
import { Screen } from '@shared/ui/Screen';
import { StateMessage } from '@shared/ui/StateMessage';

const REFRESH_MS = 15000;

/**
 * Lista de conversaciones (`GET /api/conversations`). Se actualiza por consulta
 * periódica, SOLO mientras esta pestaña está enfocada y la app en primer plano.
 * Una conversación se abre desde aquí o desde el menú «⋯» de una publicación
 * («Enviar mensaje»): el servidor no tiene un directorio de personas para
 * empezar una desde cero.
 */
export default function Messages() {
  const { user } = useAuth();
  const router = useRouter();

  const [items, setItems] = useState<ConversationSummary[] | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [refreshing, setRefreshing] = useState(false);
  const focused = useRef(false);

  const load = useCallback(async () => {
    try {
      setItems(await fetchConversations());
      setError(null);
    } catch (e) {
      setError(e instanceof ApiError ? e.message : 'No pudimos cargar tus mensajes.');
    }
  }, []);

  useFocusEffect(
    useCallback(() => {
      focused.current = true;
      void load();
      const timer = setInterval(() => {
        if (focused.current && AppState.currentState === 'active') void load();
      }, REFRESH_MS);
      return () => {
        focused.current = false;
        clearInterval(timer);
      };
    }, [load]),
  );

  // Al volver de segundo plano se actualiza al instante.
  useEffect(() => {
    const sub = AppState.addEventListener('change', (state) => {
      if (state === 'active' && focused.current) void load();
    });
    return () => sub.remove();
  }, [load]);

  if (!user) return null;

  return (
    <Screen title="Mensajes" scroll={false} withBottomInset={false}>
      <FlatList
        data={items ?? []}
        keyExtractor={(item) => item.user.id}
        contentContainerStyle={styles.list}
        refreshControl={
          <RefreshControl
            refreshing={refreshing}
            onRefresh={async () => {
              setRefreshing(true);
              await load();
              setRefreshing(false);
            }}
            tintColor={colors.brand}
          />
        }
        ListHeaderComponent={
          <Text style={styles.note}>
            Chat privado de texto. Los mensajes no están cifrados de extremo a extremo.
          </Text>
        }
        ListEmptyComponent={
          items === null && !error ? (
            <StateMessage kind="loading" message="Cargando conversaciones…" />
          ) : error && items === null ? (
            <StateMessage
              kind="error"
              title="No pudimos cargar tus mensajes"
              message={error}
              actionLabel="Reintentar"
              onAction={load}
            />
          ) : (
            <StateMessage
              kind="empty"
              title="Todavía no tienes conversaciones"
              message="Toca «⋯» en una publicación y elige «Enviar mensaje» para escribirle a alguien."
            />
          )
        }
        renderItem={({ item }) => (
          <Pressable
            style={({ pressed }) => [styles.row, pressed && styles.rowPressed]}
            onPress={() =>
              router.push({
                pathname: '/chat/[userId]',
                params: {
                  userId: item.user.id,
                  name: item.user.name,
                  username: item.user.username,
                  avatar: item.user.avatar_url ?? '',
                },
              })
            }
            accessibilityRole="button"
            accessibilityLabel={`Conversación con ${item.user.name}${
              item.unread_count > 0 ? `, ${item.unread_count} sin leer` : ''
            }`}
          >
            <Avatar name={item.user.name} uri={item.user.avatar_url} size={48} />
            <View style={styles.rowText}>
              <View style={styles.rowTop}>
                <Text style={styles.name} numberOfLines={1}>
                  {item.user.name}
                </Text>
                <Text style={styles.time}>{formatRelativeTime(item.last_message.created_at)}</Text>
              </View>
              <Text
                style={[styles.preview, item.unread_count > 0 && styles.previewUnread]}
                numberOfLines={1}
              >
                {item.last_message.sender_id === user.id ? 'Tú: ' : ''}
                {item.last_message.content}
              </Text>
            </View>
            {item.unread_count > 0 ? (
              <View style={styles.badge}>
                <Text style={styles.badgeText}>{item.unread_count > 99 ? '99+' : item.unread_count}</Text>
              </View>
            ) : null}
          </Pressable>
        )}
      />
    </Screen>
  );
}

const styles = StyleSheet.create({
  list: { padding: space[4], paddingBottom: space[8] },
  note: { fontSize: fontSize.labelMd, color: colors.fgMuted, marginBottom: space[3] },
  row: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: colors.surface,
    borderWidth: 1,
    borderColor: colors.border,
    borderRadius: radius.card,
    padding: space[3],
    marginBottom: space[2],
  },
  rowPressed: { backgroundColor: colors.bgSubtle },
  rowText: { flex: 1, marginHorizontal: space[3] },
  rowTop: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'baseline' },
  name: { flex: 1, fontSize: fontSize.bodyMd, fontWeight: '700', color: colors.fg },
  time: { fontSize: fontSize.labelMd, color: colors.fgMuted, marginLeft: space[2] },
  preview: { fontSize: fontSize.bodySm, color: colors.fgMuted, marginTop: 2 },
  previewUnread: { color: colors.fg, fontWeight: '600' },
  badge: {
    minWidth: 24,
    height: 24,
    borderRadius: 12,
    backgroundColor: colors.brand,
    alignItems: 'center',
    justifyContent: 'center',
    paddingHorizontal: 6,
  },
  badgeText: { color: colors.onBrand, fontSize: fontSize.labelMd, fontWeight: '700' },
});
