// Datos mock: representan SOLO a otras personas dentro de THERS (Momentos, Cápsulas
// ajenas, sugerencias, conversaciones, notificaciones, Descubrir). El usuario
// actualmente autenticado nunca sale de este archivo -- se lee de la sesión real
// (useAuth.getStoredUser, consumido en AppShell).
//
// Imágenes: Picsum Photos (picsum.photos/seed/<seed>) -- servicio público estable,
// cada seed devuelve siempre la misma imagen (determinista), sin necesitar API key.

const photo = (seed, size = 300) => `https://picsum.photos/seed/thers-${seed}/${size}/${size}`;
const scene = (seed, w = 900, h = 700) => `https://picsum.photos/seed/thers-${seed}/${w}/${h}`;
const portrait = (seed, w = 360, h = 540) => `https://picsum.photos/seed/thers-${seed}/${w}/${h}`;

export const MOODS = {
  inspired: { label: "Inspirado", color: "#6C4DF6" },
  motivated: { label: "Motivado", color: "#FF6B57" },
  calm: { label: "Tranquilo", color: "#4C6EF5" },
  playing: { label: "Jugando", color: "#12B886" },
  listening: { label: "Escuchando música", color: "#F783AC" },
  happy: { label: "Feliz", color: "#FA5252" },
  thinking: { label: "Pensando", color: "#845EF7" },
  studying: { label: "Estudiando", color: "#228BE6" },
};

export const mockMoments = [
  { id: 1, name: "Alex", photo: photo("alex"), image: portrait("hiking"), mood: "motivated", time: "hace 1 h" },
  { id: 2, name: "Sofia", photo: photo("sofia"), image: portrait("sunset"), mood: "inspired", time: "hace 2 h" },
  { id: 3, name: "Carlos", photo: photo("carlos"), image: portrait("gaming"), mood: "playing", time: "hace 3 h" },
  { id: 4, name: "Daniel", photo: photo("daniel"), image: portrait("citynight"), mood: "calm", time: "hace 5 h" },
  { id: 5, name: "Maria", photo: photo("maria"), image: portrait("books"), mood: "studying", time: "hace 6 h" },
  { id: 6, name: "Kevin", photo: photo("kevin"), image: portrait("beach"), mood: "happy", time: "hace 8 h" },
];

export const mockCapsules = [
  {
    id: 1,
    own: false,
    type: "photo",
    user: { name: "Sofia Reyes", username: "sofia.r", photo: photo("sofia") },
    timestamp: "Hace 2 h",
    mood: "inspired",
    image: scene("sunset-wide", 1000, 750),
    alt: "Atardecer anaranjado sobre montañas",
    text: "Primer atardecer del año que vale la pena guardar. Empezando el proyecto con toda la energía.",
    hashtags: ["thers", "atardecer", "nuevosproyectos"],
    location: "Ciudad de México",
    likes: 128,
    comments: [
      { id: 1, author: "Carlos", text: "Se ve increíble" },
      { id: 2, author: "Daniel", text: "Vamos con todo!" },
    ],
  },
  {
    id: 2,
    own: false,
    type: "thought",
    user: { name: "Carlos Medina", username: "carlosm", photo: photo("carlos") },
    timestamp: "Hace 4 h",
    mood: "thinking",
    image: null,
    text: "A veces el mejor código es el que no tuviste que escribir. Hoy aprendí a soltar una idea que no funcionaba.",
    hashtags: ["dev", "cleancode"],
    location: null,
    likes: 54,
    comments: [{ id: 1, author: "Alex", text: "Muy cierto" }],
  },
  {
    id: 3,
    own: false,
    type: "music",
    user: { name: "Alex Torres", username: "alex.t", photo: photo("alex") },
    timestamp: "Hace 6 h",
    mood: "listening",
    track: { title: "Horizonte", artist: "Nocturna" },
    text: "Esta canción va perfecta para cerrar la semana.",
    hashtags: ["musica", "finde"],
    location: null,
    likes: 212,
    comments: [
      { id: 1, author: "Maria", text: "La agrego a mi playlist!" },
      { id: 2, author: "Kevin", text: "Buenísima elección" },
    ],
  },
  {
    id: 4,
    own: false,
    type: "photo",
    user: { name: "Maria Lopez", username: "marialopez", photo: photo("maria") },
    timestamp: "Hace 8 h",
    mood: "happy",
    image: scene("art-studio", 1000, 750),
    alt: "Estudio de arte con pinturas e ilustraciones",
    text: "Nueva ilustración terminada para THERS. Todavía puliendo detalles, pero contenta con el resultado.",
    hashtags: ["diseño", "thers", "arte"],
    location: "Estudio",
    likes: 341,
    comments: [{ id: 1, author: "Kevin", text: "El color es hermoso" }],
  },
  {
    id: 5,
    own: false,
    type: "mood",
    user: { name: "Daniel Ruiz", username: "daniel.r", photo: photo("daniel") },
    timestamp: "Hace 10 h",
    mood: "calm",
    image: null,
    text: "Domingo lento, sin prisa por nada.",
    hashtags: [],
    location: null,
    likes: 76,
    comments: [],
  },
  {
    id: 6,
    own: false,
    type: "video",
    user: { name: "Kevin Santos", username: "kevin.s", photo: photo("kevin") },
    timestamp: "Hace 12 h",
    mood: "motivated",
    image: scene("sports-run", 1000, 750),
    alt: "Persona corriendo al amanecer en una pista deportiva",
    text: "5km antes del amanecer. Nueva marca personal.",
    hashtags: ["deporte", "running"],
    location: "Pista Central",
    likes: 189,
    comments: [{ id: 1, author: "Sofia", text: "Qué disciplina" }],
  },
];

export const mockSuggestions = [
  { id: 1, name: "Alex Torres", username: "alex.t", mood: "motivated", photo: photo("alex") },
  { id: 2, name: "Sofia Reyes", username: "sofia.r", mood: "inspired", photo: photo("sofia") },
  { id: 3, name: "Carlos Medina", username: "carlosm", mood: "playing", photo: photo("carlos") },
  { id: 4, name: "Daniel Ruiz", username: "daniel.r", mood: "calm", photo: photo("daniel") },
  { id: 5, name: "Kevin Santos", username: "kevin.s", mood: "happy", photo: photo("kevin") },
];

export const mockPulseEvents = [
  "Alex reaccionó a una Cápsula de música",
  "3 personas están activas en THERS ahora",
  "Sofia compartió un nuevo Momento",
  "El tema #thers está en tendencia",
  "Carlos empezó a seguir a Daniel",
  "Maria publicó una Cápsula de fotografía",
  "12 personas están en modo Estudiando",
];

export const mockTopics = [
  { id: 1, tag: "thers", capsules: 342 },
  { id: 2, tag: "musica", capsules: 218 },
  { id: 3, tag: "diseño", capsules: 156 },
  { id: 4, tag: "outdoors", capsules: 98 },
  { id: 5, tag: "cleancode", capsules: 71 },
];

export const mockDiscoverPeople = [
  { id: 1, name: "Alex Torres", username: "alex.t", mood: "motivated", photo: photo("alex") },
  { id: 2, name: "Sofia Reyes", username: "sofia.r", mood: "inspired", photo: photo("sofia") },
  { id: 3, name: "Kevin Santos", username: "kevin.s", mood: "happy", photo: photo("kevin") },
];

export const mockConversations = [
  {
    id: 1,
    name: "Sofia Reyes",
    username: "sofia.r",
    photo: photo("sofia"),
    online: true,
    lastMessage: "¿Viste la Cápsula de Alex?",
    time: "10:24",
    unread: 2,
    messages: [
      { id: 1, from: "them", text: "Hola! ¿Cómo va el proyecto?", time: "10:10" },
      { id: 2, from: "me", text: "Muy bien, casi terminando el Home", time: "10:12" },
      { id: 3, from: "them", text: "¿Viste la Cápsula de Alex?", time: "10:24" },
    ],
  },
  {
    id: 2,
    name: "Carlos Medina",
    username: "carlosm",
    photo: photo("carlos"),
    online: false,
    lastMessage: "Nos vemos en el club de senderismo",
    time: "Ayer",
    unread: 0,
    messages: [
      { id: 1, from: "them", text: "¿Te unes al club de senderismo?", time: "Ayer" },
      { id: 2, from: "me", text: "Claro, cuenta conmigo", time: "Ayer" },
      { id: 3, from: "them", text: "Nos vemos en el club de senderismo", time: "Ayer" },
    ],
  },
  {
    id: 3,
    name: "Daniel Ruiz",
    username: "daniel.r",
    photo: photo("daniel"),
    online: true,
    lastMessage: "Gracias por el follow",
    time: "Lun",
    unread: 0,
    messages: [{ id: 1, from: "them", text: "Gracias por el follow", time: "Lun" }],
  },
];

export const mockNotifications = [
  { id: 1, type: "reaction", actor: "Alex", photo: photo("alex"), detail: "reaccionó a tu Cápsula", time: "hace 5 min", important: false, read: false },
  { id: 2, type: "follow", actor: "Sofia", photo: photo("sofia"), detail: "comenzó a seguirte", time: "hace 1 h", important: true, read: false },
  { id: 3, type: "mention", actor: "Carlos", photo: photo("carlos"), detail: "te mencionó en una Cápsula", time: "hace 3 h", important: true, read: false },
  { id: 4, type: "comment", actor: "Maria", photo: photo("maria"), detail: "comentó tu Cápsula", time: "hace 5 h", important: false, read: true },
  { id: 5, type: "reaction", actor: "Kevin", photo: photo("kevin"), detail: "reaccionó a tu Momento", time: "ayer", important: false, read: true },
];
