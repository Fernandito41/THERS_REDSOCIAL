import { useCallback, useEffect, useState } from "react";
import Icon from "@shared/components/Icon";
import Spinner from "@shared/components/Spinner";
import { api, getErrorMessage } from "@shared/lib/api";
import { getStoredToken } from "@features/auth";
import { useToast } from "@shared/components/Toast";
import { useLanguage } from "@shared/i18n";
import { formatRelativeTime } from "../../lib/formatRelativeTime";

// Exportación de datos (POST/GET /api/data-exports y
// GET /api/data-exports/<id>/download -- ADR-024-data-export.md).
//
// Antes de ese ADR estos controles eran `pending` ("No existe el trabajo de
// exportación en el servidor"). Ahora el servidor genera un ZIP real con los
// datos de la cuenta; esta fila solo pide el archivo, lista el historial y
// descarga.
//
// Un único componente sirve a los dos grupos de la pantalla (`mode="request"`
// y `mode="history"`): ambos comparten la misma lista de solicitudes, y
// cargarla dos veces sería una petición duplicada. El estado vive en
// `useDataExports`, que SettingsSectionPage llama una sola vez.

function authHeaders() {
  return { Authorization: `Bearer ${getStoredToken()}` };
}

function formatSize(bytes) {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

function formatDate(isoString) {
  return new Date(isoString).toLocaleDateString("es", {
    day: "numeric",
    month: "short",
    year: "numeric",
  });
}

export function useDataExports({ enabled = true } = {}) {
  const toast = useToast();
  const { t } = useLanguage();

  const [exports, setExports] = useState(null);
  const [ttlDays, setTtlDays] = useState(7);
  const [loading, setLoading] = useState(enabled);
  const [requesting, setRequesting] = useState(false);
  const [downloadingId, setDownloadingId] = useState(null);

  const load = useCallback(async () => {
    try {
      const res = await api.get("/data-exports", { headers: authHeaders() });
      setExports(res.data.exports);
      setTtlDays(res.data.ttl_days);
    } catch (error) {
      toast.error(getErrorMessage(error, t));
    } finally {
      setLoading(false);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // Solo se pide el historial cuando se está mirando esta sección: el hook
  // se llama siempre (reglas de hooks), pero no tiene por qué costar una
  // petición en las otras once secciones de Configuración.
  useEffect(() => {
    if (enabled) load();
  }, [enabled, load]);

  const download = useCallback(
    async (item) => {
      setDownloadingId(item.id);
      try {
        const res = await api.get(`/data-exports/${item.id}/download`, {
          headers: authHeaders(),
          responseType: "blob",
        });
        const url = URL.createObjectURL(res.data);
        const link = document.createElement("a");
        link.href = url;
        link.download = item.file_name;
        document.body.appendChild(link);
        link.click();
        link.remove();
        URL.revokeObjectURL(url);
        await load();
      } catch (error) {
        // Con `responseType: "blob"` el cuerpo del error llega como Blob, no
        // como JSON: `getErrorMessage` no puede leer `data.msg`, así que los
        // dos casos esperables se resuelven por estado.
        const status = error.response?.status;
        if (status === 410) {
          toast.error("Este archivo caducó. Pedí uno nuevo.");
          await load();
        } else if (status === 404) {
          toast.error("No encontramos ese archivo.");
        } else {
          toast.error(getErrorMessage(error, t));
        }
      } finally {
        setDownloadingId(null);
      }
    },
    [load, toast, t]
  );

  const request = useCallback(async () => {
    setRequesting(true);
    try {
      const res = await api.post("/data-exports", null, { headers: authHeaders() });
      toast.success("Tu archivo está listo. Ya puedes descargarlo.");
      await load();
      await download(res.data.export);
    } catch (error) {
      toast.error(getErrorMessage(error, t));
    } finally {
      setRequesting(false);
    }
  }, [load, download, toast, t]);

  return { exports, ttlDays, loading, requesting, downloadingId, request, download };
}

/** Grupo "Solicitar descarga de información". */
export function DataExportRequestRow({ state }) {
  const { requesting, request } = state;

  return (
    <div className="flex flex-wrap items-start justify-between gap-4 py-4 first:pt-0 last:pb-0">
      <div className="flex min-w-0 flex-1 flex-col gap-1">
        <span className="text-label-lg font-semibold text-th-fg-strong">Solicitar mi archivo</span>
        <p className="text-body-sm text-th-fg-muted">
          Un ZIP con tu perfil, publicaciones, comentarios, likes, seguidores, mensajes,
          notificaciones y dispositivos. Se genera al momento y se descarga automáticamente.
        </p>
        <p className="text-body-sm text-th-fg-subtle">Se aplica en el servidor.</p>
      </div>
      <button
        type="button"
        onClick={request}
        disabled={requesting}
        className="inline-flex min-h-[44px] shrink-0 items-center gap-2 rounded-th-input bg-th-brand px-4 py-2.5 text-label-lg font-bold text-th-on-brand transition-colors th-focus-ring hover:bg-th-brand-hover disabled:opacity-60"
      >
        {requesting && <Spinner size={16} />}
        {requesting ? "Generando..." : "Solicitar"}
      </button>
    </div>
  );
}

/** Grupo "Archivos listos para descargar (Historial)". */
export function DataExportHistoryRow({ state }) {
  const { exports, loading, downloadingId, download } = state;

  if (loading) {
    return (
      <div className="flex items-center gap-2 py-4 text-th-fg-muted" role="status">
        <Spinner size={16} />
        <span className="text-body-sm">Cargando historial...</span>
      </div>
    );
  }

  if (!exports || exports.length === 0) {
    return (
      <div className="flex flex-col gap-1 py-4 first:pt-0 last:pb-0">
        <span className="text-label-lg font-semibold text-th-fg-strong">
          Historial de solicitudes
        </span>
        <p className="text-body-sm text-th-fg-muted">
          Todavía no pediste ningún archivo. Cuando lo hagas, aparecerá acá.
        </p>
      </div>
    );
  }

  return (
    <ul className="flex flex-col gap-2 py-4 first:pt-0 last:pb-0">
      {exports.map((item) => {
        const ready = item.status === "ready";
        return (
          <li
            key={item.id}
            className="flex flex-wrap items-center gap-3 rounded-th-card bg-th-surface-subtle px-3 py-2.5"
          >
            <Icon
              name={ready ? "folder_zip" : "history"}
              size={20}
              className="shrink-0 text-th-fg-muted"
            />
            <div className="min-w-0 flex-1">
              <p className="truncate text-label-md font-bold text-th-fg-strong">{item.file_name}</p>
              <p className="truncate text-body-sm text-th-fg-muted">
                Pedido {formatRelativeTime(item.created_at)} · {formatSize(item.size_bytes)} ·{" "}
                {ready ? `caduca el ${formatDate(item.expires_at)}` : "caducado"}
                {item.download_count > 0 &&
                  ` · descargado ${item.download_count} ${item.download_count === 1 ? "vez" : "veces"}`}
              </p>
            </div>
            {ready ? (
              <button
                type="button"
                onClick={() => download(item)}
                disabled={downloadingId === item.id}
                aria-label={`Descargar ${item.file_name}`}
                className="flex h-9 shrink-0 items-center gap-1.5 rounded-th-pill border border-th-border px-3 text-label-md font-bold text-th-fg transition-colors th-focus-ring hover:bg-th-surface disabled:opacity-40"
              >
                {downloadingId === item.id ? <Spinner size={14} /> : "Descargar"}
              </button>
            ) : (
              <span className="shrink-0 text-label-md font-bold text-th-fg-subtle">Caducado</span>
            )}
          </li>
        );
      })}
    </ul>
  );
}
