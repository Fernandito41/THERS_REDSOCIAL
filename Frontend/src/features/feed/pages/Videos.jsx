import ModulePending from "./ModulePending";

/**
 * Videos y Cortos.
 *
 * NO hay captura dedicada de este módulo entre las 24 referencias
 * (docs/THERS_REFERENCE_MANIFEST.md §4.3): el contenido de vídeo aparece
 * dentro de REF-SEARCH-01 y de los perfiles (REF-PROFILE-02/03). Cuando se
 * implemente será **diseño derivado**, no reproducción de un diseño recibido.
 */
export default function Videos() {
  return (
    <ModulePending
      title="Videos"
      reference="Sin captura dedicada — se derivará de REF-SEARCH-01 y REF-PROFILE-02/03"
      stage="Etapa D — Contenido y perfiles"
      summary="El enlace «Videos» existe en la sidebar de las 24 referencias, pero ninguna captura muestra esta pantalla completa."
      pending={[
        "Composición derivada del módulo de vídeo de REF-SEARCH-01",
        "Módulo de cortos reutilizando el de REF-PROFILE-03",
        "Sin endpoint de vídeo en el backend: requiere contrato nuevo",
        "El badge LIVE de la maqueta no se mostrará sin señal real de directo",
      ]}
    />
  );
}
