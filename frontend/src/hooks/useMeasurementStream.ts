
import { useEffect, useState } from "react";
import { API_BASE_URL } from "../api/client";
import type {
  Measurement,
  WebSocketConnectionStatus,
} from "../api/types";

const MAX_MEASUREMENTS = 5000;

interface MeasurementStreamState {
  measurements: Measurement[];
  status: WebSocketConnectionStatus;
  lastMessageAt: string | null;
  error: string | null;
}

const initialState: MeasurementStreamState = {
  measurements: [],
  status: "connecting",
  lastMessageAt: null,
  error: null,
};

function isRecord(
  value: unknown,
): value is Record<string, unknown> {
  return (
    typeof value === "object" &&
    value !== null &&
    !Array.isArray(value)
  );
}

function extractMeasurement(message: unknown): Measurement | null {
  if (!isRecord(message)) return null;

  if ((message.type ?? message.event) !== "measurement") {
    return null;
  }

  const candidate =
    message.data ?? message.payload ?? message.measurement;

  if (!isRecord(candidate)) return null;

  const {
    timestamp,
    device_id,
    channel,
    value,
    unit,
    quality,
    metadata,
  } = candidate;

  if (
    typeof timestamp !== "string" ||
    Number.isNaN(Date.parse(timestamp)) ||
    typeof device_id !== "string" ||
    typeof channel !== "string" ||
    typeof value !== "number" ||
    !Number.isFinite(value) ||
    typeof unit !== "string" ||
    typeof quality !== "string"
  ) {
    return null;
  }

  return {
    timestamp,
    device_id,
    channel,
    value,
    unit,
    quality,
    metadata: isRecord(metadata)
      ? metadata as Measurement["metadata"]
      : {},
  };
}

function createWebSocketUrl(): string {
  const url = new URL(API_BASE_URL, window.location.origin);

  url.protocol = url.protocol === "https:" ? "wss:" : "ws:";
  url.pathname =
    `${url.pathname.replace(/\/+$/, "")}/ws/measurements`;

  return url.toString();
}

export function useMeasurementStream(): MeasurementStreamState {
  const [state, setState] =
    useState<MeasurementStreamState>(initialState);

  useEffect(() => {
    let stopped = false;
    let retryAttempt = 0;
    let reconnectTimer: ReturnType<typeof setTimeout> | undefined;
    let socket: WebSocket | undefined;

    function connect() {
      if (stopped) return;

      setState((current) => ({
        ...current,
        status: retryAttempt === 0 ? "connecting" : "reconnecting",
        error: null,
      }));

      try {
        socket = new WebSocket(createWebSocketUrl());
      } catch {
        setState((current) => ({
          ...current,
          status: "error",
          error: "No se pudo crear la conexión WebSocket.",
        }));
        scheduleReconnect();
        return;
      }

      const currentSocket = socket;

      currentSocket.onopen = () => {
        retryAttempt = 0;

        setState((current) => ({
          ...current,
          status: "connected",
          error: null,
        }));
      };

      currentSocket.onmessage = (event: MessageEvent<string>) => {
        try {
          const parsed: unknown = JSON.parse(event.data);
          const measurement = extractMeasurement(parsed);

          // Ignoramos eventos spectrum y otros mensajes.
          if (!measurement) return;

          setState((current) => ({
            ...current,
            measurements: [
              ...current.measurements,
              measurement,
            ].slice(-MAX_MEASUREMENTS),
            lastMessageAt: new Date().toISOString(),
            error: null,
          }));
        } catch {
          setState((current) => ({
            ...current,
            error: "El servidor envió un mensaje JSON no válido.",
          }));
        }
      };

      currentSocket.onerror = () => {
        setState((current) => ({
          ...current,
          error: "Error en la conexión WebSocket.",
        }));
      };

      currentSocket.onclose = () => {
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
        } else if (
          currentSocket.readyState === WebSocket.CONNECTING
        ) {
          currentSocket.onopen = () => currentSocket.close();
        } else {
          currentSocket.onopen = null;
        }
      }
    };
  }, []);

  return state;
}
