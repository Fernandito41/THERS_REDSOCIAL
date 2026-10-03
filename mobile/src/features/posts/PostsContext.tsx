/**
 * Estado de las publicaciones, compartido por Inicio, Buscar, Perfil y el detalle
 * de una publicación.
 *
 * Hay UNA sola lista porque el backend solo expone `GET /api/posts` (feed
 * global, 50 publicaciones, sin paginación ni endpoint por id, `API_CONTRACT.md`
 * §4.3). Buscar y el perfil filtran esa misma lista, igual que la web: no se
 * finge un buscador de servidor que no existe.
 *
 * Me gusta y seguir son **optimistas**: la interfaz responde al instante y, si el
 * servidor rechaza, se revierte. Reintentar una escritura de forma ciega crearía
 * duplicados, así que ninguna se reintenta sola.
 */

import { createContext, useCallback, useContext, useEffect, useMemo, useRef, useState } from 'react';
import type { ReactNode } from 'react';

import { useAuth } from '@features/auth/context/AuthContext';
import { ApiError } from '@shared/lib/api';

import * as api from './api';
import type { Post } from './types';

type Status = 'idle' | 'loading' | 'ready' | 'error';

type PostsState = {
  posts: Post[];
  status: Status;
  /** Mensaje del último fallo de carga; `null` si la última carga salió bien. */
  error: string | null;
  refreshing: boolean;
  reload: (options?: { pullToRefresh?: boolean }) => Promise<void>;
  getPost: (postId: string) => Post | undefined;
  create: (content: string, isSensitive: boolean) => Promise<void>;
  edit: (postId: string, content: string) => Promise<void>;
  remove: (postId: string) => Promise<void>;
  toggleLike: (postId: string) => Promise<void>;
  toggleFollow: (authorId: string) => Promise<void>;
  /** Ajusta el contador de comentarios sin volver a pedir toda la lista. */
  bumpCommentCount: (postId: string, delta: number) => void;
  /** Quita de la lista las publicaciones de una cuenta (p. ej. tras bloquearla). */
  dropAuthor: (authorId: string) => void;
};

const PostsContext = createContext<PostsState | null>(null);

export function messageOf(error: unknown): string {
  return error instanceof ApiError
    ? error.message
    : 'Ocurrió un error inesperado. Inténtalo de nuevo.';
}

export function PostsProvider({ children }: { children: ReactNode }) {
  const { user } = useAuth();
  const userId = user?.id ?? null;

  const [posts, setPosts] = useState<Post[]>([]);
  const [status, setStatus] = useState<Status>('idle');
  const [error, setError] = useState<string | null>(null);
  const [refreshing, setRefreshing] = useState(false);

  // Evita que una respuesta lenta de una sesión anterior pise la de la actual.
  const loadSeq = useRef(0);

  const reload = useCallback(
    async (options?: { pullToRefresh?: boolean }) => {
      const seq = ++loadSeq.current;
      if (options?.pullToRefresh) setRefreshing(true);
      else setStatus((current) => (current === 'ready' ? current : 'loading'));

      try {
        const next = await api.fetchPosts();
        if (seq !== loadSeq.current) return;
        setPosts(next);
        setError(null);
        setStatus('ready');
      } catch (e) {
        if (seq !== loadSeq.current) return;
        setError(messageOf(e));
        // Si ya había datos se conservan: perder señal no vacía la pantalla.
        setStatus((current) => (current === 'ready' ? 'ready' : 'error'));
      } finally {
        if (seq === loadSeq.current) setRefreshing(false);
      }
    },
    [],
  );

  // Al iniciar o cambiar de sesión se carga; al cerrarla se vacía todo.
  useEffect(() => {
    if (!userId) {
      loadSeq.current++;
      setPosts([]);
      setStatus('idle');
      setError(null);
      return;
    }
    void reload();
  }, [userId, reload]);

  const replacePost = useCallback((next: Post) => {
    setPosts((current) => current.map((p) => (p.id === next.id ? next : p)));
  }, []);

  const create = useCallback(async (content: string, isSensitive: boolean) => {
    const created = await api.createPost(content, isSensitive);
    setPosts((current) => [created, ...current]);
  }, []);

  const edit = useCallback(
    async (postId: string, content: string) => {
      replacePost(await api.updatePost(postId, content));
    },
    [replacePost],
  );

  const remove = useCallback(async (postId: string) => {
    await api.deletePost(postId);
    setPosts((current) => current.filter((p) => p.id !== postId));
  }, []);

  const toggleLike = useCallback(
    async (postId: string) => {
      const before = posts.find((p) => p.id === postId);
      if (!before) return;

      const optimistic: Post = {
        ...before,
        liked_by_me: !before.liked_by_me,
        likes_count: Math.max(0, before.likes_count + (before.liked_by_me ? -1 : 1)),
      };
      replacePost(optimistic);

      try {
        const result = before.liked_by_me
          ? await api.unlikePost(postId)
          : await api.likePost(postId);
        // El servidor manda el contador real: se usa en vez de seguir adivinando.
        setPosts((current) =>
          current.map((p) =>
            p.id === postId
              ? { ...p, liked_by_me: result.liked_by_me, likes_count: result.likes_count }
              : p,
          ),
        );
      } catch (e) {
        replacePost(before);
        throw e;
      }
    },
    [posts, replacePost],
  );

  const toggleFollow = useCallback(
    async (authorId: string) => {
      const sample = posts.find((p) => p.author.id === authorId);
      if (!sample) return;
      const previous = { follow: sample.author.follow_status, followed: sample.author.is_followed_by_me };
      const wasFollowing = previous.follow !== null;

      const apply = (follow: Post['author']['follow_status']) =>
        setPosts((current) =>
          current.map((p) =>
            p.author.id === authorId
              ? {
                  ...p,
                  author: {
                    ...p.author,
                    follow_status: follow,
                    is_followed_by_me: follow === 'accepted',
                  },
                }
              : p,
          ),
        );

      // Optimista: una cuenta privada queda "pendiente", no "siguiendo".
      apply(wasFollowing ? null : sample.author.is_private ? 'pending' : 'accepted');

      try {
        const result = wasFollowing
          ? await api.unfollowUser(authorId)
          : await api.followUser(authorId);
        apply(result.follow_status);
      } catch (e) {
        apply(previous.follow);
        throw e;
      }
    },
    [posts],
  );

  const bumpCommentCount = useCallback((postId: string, delta: number) => {
    setPosts((current) =>
      current.map((p) =>
        p.id === postId ? { ...p, comments_count: Math.max(0, p.comments_count + delta) } : p,
      ),
    );
  }, []);

  const dropAuthor = useCallback((authorId: string) => {
    setPosts((current) => current.filter((p) => p.author.id !== authorId));
  }, []);

  const getPost = useCallback(
    (postId: string) => posts.find((p) => p.id === postId),
    [posts],
  );

  const value = useMemo<PostsState>(
    () => ({
      posts,
      status,
      error,
      refreshing,
      reload,
      getPost,
      create,
      edit,
      remove,
      toggleLike,
      toggleFollow,
      bumpCommentCount,
      dropAuthor,
    }),
    [
      posts,
      status,
      error,
      refreshing,
      reload,
      getPost,
      create,
      edit,
      remove,
      toggleLike,
      toggleFollow,
      bumpCommentCount,
      dropAuthor,
    ],
  );

  return <PostsContext.Provider value={value}>{children}</PostsContext.Provider>;
}

export function usePosts(): PostsState {
  const context = useContext(PostsContext);
  if (!context) throw new Error('usePosts debe usarse dentro de <PostsProvider>');
  return context;
}
