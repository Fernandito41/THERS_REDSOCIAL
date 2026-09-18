import ModulePending from "./ModulePending";

/**
 * Cápsulas — vista dedicada.
 *
 * Sin captura propia entre las 24 referencias (manifest §4.3): las cápsulas
 * aparecen como tarjetas dentro de Feed, Perfil y Radar. Además, «Cápsula» ya
 * es el nombre de producto que este repositorio usa para un post real
 * (ADR-004), así que antes de implementar hay que confirmar si esta vista es
 * una colección de posts o un tipo de contenido distinto (archivo maestro §6.3).
 */
export default function Capsules() {
  return (
    <ModulePending
      title="Cápsulas"
      reference="Sin captura dedicada — tarjetas presentes en REF-FEED-01 y REF-PROFILE-01"
      stage="Etapa D — Contenido y perfiles"
      summary="El enlace existe en la sidebar de las 24 referencias; ninguna captura muestra la pantalla."
      pending={[
        "Confirmar con el equipo si «Cápsulas» aquí son posts (ADR-004) u otro tipo",
        "Composición derivada de las tarjetas de cápsula ya presentes en Feed y Perfil",
        "GET /api/posts existe; falta definir el filtro/colección que alimenta esta vista",
      ]}
    />
  );
}
