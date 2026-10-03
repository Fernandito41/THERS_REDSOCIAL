import { useRouter } from 'expo-router';
import { useMemo, useState } from 'react';
import { Alert, FlatList, Linking, Pressable, StyleSheet, Text, View } from 'react-native';

import { useAuth } from '@features/auth/context/AuthContext';
import { PostCard } from '@features/posts/PostCard';
import { usePosts } from '@features/posts/PostsContext';
import { usePostMenu } from '@features/posts/usePostMenu';
import { patchProfile } from '@features/settings/api';
import { colors, fontSize, radius, space } from '@shared/design/tokens';
import { messageOf } from '@features/posts/PostsContext';
import { Avatar } from '@shared/ui/Avatar';
import { Banner } from '@shared/ui/Banner';
import { Button } from '@shared/ui/Button';
import { EditProfileModal } from '@shared/ui/EditProfileModal';
import { Screen } from '@shared/ui/Screen';

/**
 * Perfil propio: datos reales de `GET /api/users/me` y las publicaciones propias,
 * que salen de la misma lista del feed (el servidor no tiene «publicaciones de un
 * usuario»; igual que en la web se filtra por autor). Ver perfiles AJENOS no existe
 * todavía en el servidor (no hay `GET /api/users/<id>`), así que no se inventa.
 */
export default function Profile() {
  const { user, logout, refreshUser } = useAuth();
  const router = useRouter();
  const posts = usePosts();
  const menu = usePostMenu();
  const [editing, setEditing] = useState(false);

  const mine = useMemo(
    () => posts.posts.filter((post) => post.author.id === user?.id),
    [posts.posts, user?.id],
  );

  if (!user) return null;

  async function handleLogout() {
    await logout();
    router.replace('/login');
  }

  return (
    <Screen title="Perfil" scroll={false} withBottomInset={false}>
      <FlatList
        data={mine}
        keyExtractor={(post) => post.id}
        contentContainerStyle={styles.list}
        ListHeaderComponent={
          <View>
            <View style={styles.header}>
              <Avatar name={user.name} uri={user.avatar_url} size={88} />
              <Text style={styles.name}>{user.name}</Text>
              <Text style={styles.username}>
                @{user.username}
                {user.is_private ? ' · Cuenta privada' : ''}
              </Text>
              {user.bio ? <Text style={styles.bio}>{user.bio}</Text> : null}
              {user.location ? <Text style={styles.meta}>{user.location}</Text> : null}
              {user.website ? (
                <Pressable
                  onPress={() =>
                    Linking.openURL(/^https?:\/\//i.test(user.website!) ? user.website! : `https://${user.website}`).catch(
                      () => Alert.alert('No se pudo abrir el enlace'),
                    )
                  }
                  accessibilityRole="link"
                >
                  <Text style={styles.link}>{user.website}</Text>
                </Pressable>
              ) : null}
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
              <View style={styles.statDivider} />
              <View style={styles.stat}>
                <Text style={styles.statValue}>{mine.length}</Text>
                <Text style={styles.statLabel}>Publicaciones</Text>
              </View>
            </View>

            {!user.profile_completed ? (
              <Banner tone="info">
                Faltan datos de tu perfil (teléfono y fecha de nacimiento). Complétalos desde la web
                de THERS para poder publicar.
              </Banner>
            ) : null}

            <View style={styles.buttons}>
              <Button label="Editar perfil" variant="secondary" onPress={() => setEditing(true)} style={styles.flex} />
              <Button label="Ajustes" variant="secondary" onPress={() => router.push('/settings')} style={styles.flex} />
            </View>

            <Text style={styles.sectionTitle}>Mis publicaciones</Text>
            {mine.length === 0 ? (
              <Text style={styles.empty}>
                {posts.status === 'ready'
                  ? 'Todavía no has publicado nada reciente.'
                  : 'Cargando publicaciones…'}
              </Text>
            ) : null}
          </View>
        }
        ListFooterComponent={
          <Button label="Cerrar sesión" variant="secondary" onPress={handleLogout} style={styles.logout} />
        }
        renderItem={({ item }) => (
          <PostCard
            post={item}
            myId={user.id}
            onLike={menu.like}
            onMenu={menu.openMenu}
            onFollow={menu.follow}
          />
        )}
      />
      {menu.element}
      <EditProfileModal
        visible={editing}
        user={user}
        onClose={() => setEditing(false)}
        onSave={async (patch) => {
          try {
            await patchProfile(patch);
            await refreshUser();
          } catch (e) {
            throw new Error(messageOf(e));
          }
        }}
      />
    </Screen>
  );
}

const styles = StyleSheet.create({
  list: { padding: space[4], paddingBottom: space[8] },
  header: { alignItems: 'center', marginBottom: space[4] },
  name: { fontSize: fontSize.headlineMd, fontWeight: '700', color: colors.fg, marginTop: space[3] },
  username: { fontSize: fontSize.bodyMd, color: colors.fgMuted, marginTop: space[1] },
  bio: { fontSize: fontSize.bodyMd, color: colors.fg, textAlign: 'center', marginTop: space[3], lineHeight: 21 },
  meta: { fontSize: fontSize.bodySm, color: colors.fgMuted, marginTop: space[2] },
  link: { fontSize: fontSize.bodySm, color: colors.brand, marginTop: space[1], fontWeight: '600' },
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
  buttons: { flexDirection: 'row', gap: space[2], marginBottom: space[4] },
  flex: { flex: 1, paddingHorizontal: space[2] },
  sectionTitle: { fontSize: fontSize.bodyLg, fontWeight: '700', color: colors.fg, marginBottom: space[3] },
  empty: { fontSize: fontSize.bodySm, color: colors.fgMuted, marginBottom: space[4] },
  logout: { marginTop: space[4] },
});
