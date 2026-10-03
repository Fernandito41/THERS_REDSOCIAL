/**
 * Notificaciones dentro de la app (`API_CONTRACT.md` §4.7). NO son notificaciones
 * push: son filas del servidor que se consultan; las push son una fase posterior
 * y no sustituyen a estas.
 */

import { request } from '@shared/lib/api';

export type NotificationType =
  | 'like'
  | 'comment'
  | 'follow'
  | 'follow_request'
  | 'follow_accepted'
  | 'mention'
  | string;

export type AppNotification = {
  id: string;
  type: NotificationType;
  actor: { id: string; username: string; name: string; avatar_url: string | null };
  post_id: string | null;
  read: boolean;
  created_at: string;
};

export async function fetchNotifications(signal?: AbortSignal): Promise<AppNotification[]> {
  const { notifications } = await request<{ notifications: AppNotification[] }>('/notifications', {
    authenticated: true,
    signal,
  });
  return notifications;
}

export function markNotificationRead(id: string): Promise<unknown> {
  return request(`/notifications/${id}/read`, { method: 'PATCH', authenticated: true });
}

/** Texto de la notificación, según su tipo. Un tipo desconocido no rompe la lista. */
export function describeNotification(type: NotificationType): string {
  switch (type) {
    case 'like':
      return 'le dio me gusta a tu publicación';
    case 'comment':
      return 'comentó tu publicación';
    case 'follow':
      return 'empezó a seguirte';
    case 'follow_request':
      return 'quiere seguirte';
    case 'follow_accepted':
      return 'aceptó tu solicitud';
    case 'mention':
      return 'te mencionó';
    default:
      return 'tiene novedades para ti';
  }
}
