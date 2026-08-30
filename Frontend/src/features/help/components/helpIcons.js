import {
  IoPersonCircleOutline,
  IoShieldCheckmarkOutline,
  IoLockClosedOutline,
  IoImagesOutline,
  IoHeartOutline,
  IoNotificationsOutline,
  IoFlagOutline,
  IoSettingsOutline,
  IoHelpCircleOutline,
} from "react-icons/io5";

// Mismo patrón que Footer/FooterExpandableItem: los datos guardan una clave
// de ícono (string, serializable) y los componentes la resuelven acá.
export const HELP_CATEGORY_ICONS = {
  account: IoPersonCircleOutline,
  security: IoShieldCheckmarkOutline,
  privacy: IoLockClosedOutline,
  posts: IoImagesOutline,
  interactions: IoHeartOutline,
  notifications: IoNotificationsOutline,
  reports: IoFlagOutline,
  settings: IoSettingsOutline,
};

export function getCategoryIcon(iconKey) {
  return HELP_CATEGORY_ICONS[iconKey] || IoHelpCircleOutline;
}
