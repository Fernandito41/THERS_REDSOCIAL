import ModulePending from "./ModulePending";

/**
 * Ubicación y Radar.
 *
 * Sí tiene referencias canónicas: REF-RADAR-01 (modo claro) y REF-RADAR-02
 * (profundidad funcional), que son complementarias — una sola ruta con
 * estados, no dos aplicaciones (manifest §3.1).
 *
 * Bloqueo conocido: no hay proveedor de cartografía contratado ni endpoints de
 * lugares. El archivo maestro §8.8 prohíbe contratar Mapbox/Google Maps o
 * presentar tráfico, precios y afluencia simulados como información real.
 */
export default function Radar() {
  return (
    <ModulePending
      title="Ubicación y Radar"
      reference="REF-RADAR-01 (canónica) + REF-RADAR-02 (profundidad funcional)"
      stage="Etapa F — Radar y servicios"
      summary="Ambas referencias están disponibles e íntegras; la implementación depende de decisiones de proveedor."
      pending={[
        "Composición completa: categorías, ficha de establecimiento, rutas, incidencias y comunidad",
        "Geolocalización solo tras permiso explícito, con búsqueda manual si se rechaza",
        "Sin proveedor de mapas contratado: el mapa se rotulará como demostración",
        "Precios de combustible, afluencia y horarios requieren fuente real o etiqueta de ejemplo",
      ]}
    />
  );
}
