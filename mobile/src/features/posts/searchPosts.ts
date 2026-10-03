/**
 * Búsqueda sobre las publicaciones YA cargadas, igual que la web: el backend no
 * tiene endpoint de búsqueda (`GET /api/posts` devuelve las 50 más recientes), así
 * que se filtra en el cliente y la interfaz lo dice. Lógica pura, probada en
 * `tests/searchPosts.test.mjs`.
 */

import type { Post } from './types';

/** Minúsculas y sin tildes: «jose» encuentra «José». */
export function normalize(value: string): string {
  return value
    .normalize('NFD')
    .replace(/[̀-ͯ]/g, '')
    .toLowerCase()
    .trim();
}

export type SearchSort = 'recent' | 'likes';

/**
 * Publicaciones cuyo texto, nombre de autor o @usuario contienen TODAS las
 * palabras de la consulta (en cualquier orden). Una consulta vacía no devuelve
 * nada: «todavía no buscaste» es distinto de «sin resultados».
 */
export function searchPosts(posts: Post[], query: string, sort: SearchSort = 'recent'): Post[] {
  const words = normalize(query).split(/\s+/).filter(Boolean);
  if (words.length === 0) return [];

  const matches = posts.filter((post) => {
    const haystack = normalize(`${post.content} ${post.author.name} ${post.author.username}`);
    return words.every((word) => haystack.includes(word));
  });

  return [...matches].sort((a, b) => {
    if (sort === 'likes' && b.likes_count !== a.likes_count) return b.likes_count - a.likes_count;
    return Date.parse(b.created_at) - Date.parse(a.created_at);
  });
}
