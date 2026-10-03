import { useNavigate } from "react-router-dom";
import { ActionRow } from "./SettingsPrimitives";

// Fila de Seguridad que lleva al flujo de eliminación de cuenta
// (ADR-031-account-deletion.md). No repite el flujo aquí: la página pública
// `/eliminar-cuenta` es la misma que se declara en Play Console, así que web,
// app y navegador sin sesión recorren exactamente los mismos pasos.
export default function DeleteAccountRow() {
  const navigate = useNavigate();

  return (
    <ActionRow
      label="Eliminar mi cuenta"
      description="Es definitiva. Antes puedes descargar tus datos desde Configuración › Datos."
      action="Continuar"
      onAction={() => navigate("/eliminar-cuenta")}
    />
  );
}
