
import { useEffect, useState } from "react";
import { API_BASE_URL } from "../api/client";
import type {
  Spectrum,
  WebSocketConnectionStatus,
} from "../api/types";

interface SpectrumStreamState {
  spectrum: Spectrum | null;
  status: WebSocketConnectionStatus;
  lastMessageAt: string | null;
  error: string | null;
}

const initialState: SpectrumStreamState = {
  spectrum: null,
  status: "connecting",
  lastMessageAt: null,
  error: null,
};

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}

function isJsonValue(value: unknown): boolean {
  if (
    value === null ||
    typeof value === "string" ||
    typeof value === "boolean" ||
    (typeof value === "number" && Number.isFinite(value))
  ) {
    return true;
  }

  if (Array.isArray(value)) {
    return value.every(isJsonValue);
  }

  return isRecord(value) && Object.values(value).every(isJsonValue);
}

function isJsonObject(value: unknown): value is Spectrum["metadata"] {
  return isRecord(value) && Object.values(value).every(isJsonValue);
}

function isNumberArray(value: unknown): value is number[] {
  return (
    Array.isArray(value) &&
    value.every(
      (item) => typeof item === "number" && Number.isFinite(item),
    )
  );
}

function extractSpectrum(message: unknown): Spectrum | null {
  if (!isRecord(message)) return null;

  const eventType = message.type ?? message.event;

  if (eventType !== "spectrum") return null;

  // El backend puede envolver el espectro en data, payload o spectrum.
  const candidate =
    message.data ?? message.payload ?? message.spectrum ?? message;

  if (!isRecord(candidate)) return null;

  // También admite una envoltura del tipo { data: { spectrum: {...} } }.
  const nested =
    candidate.spectrum && isRecord(candidate.spectrum)
      ? candidate.spectrum
      : candidate;

  if (
    !isNumberArray(nested.wavelength) ||
    !isNumberArray(nested.intensity)
  ) {
    return null;
  }

  if (nested.wavelength.length !== nested.intensity.length) {
    return null;
  }

  if (nested.wavelength.length === 0) {
    return null;
  }

  const timestamp =
    typeof nested.timestamp === "string"
      ? nested.timestamp
      : new Date().toISOString();

  const deviceId =
    typeof nested.device_id === "string" ? nested.device_id : "unknown";

  const wavelengthUnit =
    typeof nested.wavelength_unit === "string"
      ? nested.wavelength_unit
      : "nm";

  const intensityUnit =
    typeof nested.intensity_unit === "string"
      ? nested.intensity_unit
      : "a.u.";

  const metadata = isJsonObject(nested.metadata)
    ? nested.metadata
    : {};

  const id =
    typeof nested.id === "string" ? nested.id : null;

  return {
    id,
    timestamp,
    device_id: deviceId,
    wavelength: nested.wavelength,
    intensity: nested.intensity,
    wavelength_unit: wavelengthUnit,
    intensity_unit: intensityUnit,
    metadata,
  };
}

function createWebSocketUrl(): string {
  const baseUrl = new URL(API_BASE_URL, window.location.origin);

  baseUrl.protocol =
    baseUrl.protocol === "https:" ? "wss:" : "ws:";

  baseUrl.pathname =
    `${baseUrl.pathname.replace(/\/+$/, "")}/ws/measurements`;

  baseUrl.search = "";
  baseUrl.hash = "";

  return baseUrl.toString();
}

export function useSpectrumStream() {
  const [state, setState] =
    useState<SpectrumStreamState>(initialState);

  useEffect(() => {
    let socket: WebSocket | null = null;
    let reconnectTimer: ReturnType<typeof setTimeout> | undefined;
    let stopped = false;
    let retryAttempt = 0;

    function connect() {
      if (stopped) return;

      setState((current) => ({
        ...current,
        status: retryAttempt === 0 ? "connecting" : "reconnecting",
        error: null,
      }));

      try {
        socket = new WebSocket(createWebSocketUrl());
      } catch (error) {
        setState((current) => ({
          ...current,
          status: "error",
          error:
            error instanceof Error
              ? error.message
              : "No se pudo crear la conexión WebSocket.",
        }));

        scheduleReconnect();
        return;
      }

      socket.onopen = () => {
        retryAttempt = 0;

        setState((current) => ({
          ...current,
          status: "connected",
          error: null,
        }));
      };

      socket.onmessage = (event: MessageEvent<string>) => {
        try {
          const parsed: unknown = JSON.parse(event.data);
          const spectrum = extractSpectrum(parsed);

          // Los eventos de tipo measurement no actualizan el gráfico
          // espectral; se podrán utilizar en la Parte 31.
          if (spectrum) {
            setState((current) => ({
              ...current,
              spectrum,
              lastMessageAt: new Date().toISOString(),
              error: null,
            }));
          }
        } catch {
          setState((current) => ({
            ...current,
            error: "El servidor envió un mensaje JSON no válido.",
          }));
        }
      };

      socket.onerror = () => {
        setState((current) => ({
          ...current,
          error: "Se produjo un error en la conexión WebSocket.",
        }));
      };

      socket.onclose = () => {
        if (stopped) return;

        setState((current) => ({
          ...current,
          status: "disconnected",
        }));

        scheduleReconnect();
      };
    }

    function scheduleReconnect() {
      if (stopped || reconnectTimer !== undefined) return;

      retryAttempt += 1;

      // Espera progresiva: 1, 2, 4, 8... hasta un máximo de 15 segundos.
      const delay = Math.min(
        1000 * 2 ** Math.min(retryAttempt - 1, 4),
        15000,
      );

      reconnectTimer = setTimeout(() => {
        reconnectTimer = undefined;
        connect();
      }, delay);
    }

    connect();

    return () => {
      stopped = true;

      if (reconnectTimer !== undefined) {
        clearTimeout(reconnectTimer);
      }
      if (socket) {
        const currentSocket = socket;

        currentSocket.onmessage = null;
        currentSocket.onerror = null;
        currentSocket.onclose = null;

        if (currentSocket.readyState === WebSocket.OPEN) {
          currentSocket.close();
        } else if (currentSocket.readyState === WebSocket.CONNECTING) {
          // No cerrar mientras conecta: se cierra apenas se abra.
          currentSocket.onopen = () => currentSocket.close();
        } else {
          currentSocket.onopen = null;
        }
      }
    };
  }, []);

  return state;
}
