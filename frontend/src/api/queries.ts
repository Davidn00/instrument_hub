
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { apiRequest } from "./client";

import type {
  Device,
  DeviceCreate,
  Experiment,
  ExperimentCreate,
  HealthResponse,
  Measurement,
  ReadinessResponse,
  Spectrum,
} from "./types";

export const queryKeys = {
  health: ["health"] as const,
  readiness: ["readiness"] as const,
  devices: ["devices"] as const,
  experiments: ["experiments"] as const,
  measurements: (limit: number) =>
    ["measurements", { limit }] as const,
  spectra: (limit: number) =>
    ["spectra", { limit }] as const,
};

export function useHealthQuery() {
  return useQuery<HealthResponse, Error>({
    queryKey: queryKeys.health,
    queryFn: () => apiRequest<HealthResponse>("health"),
    staleTime: 15_000,
    refetchInterval: 30_000,
    retry: 1,
  });
}

export function useReadinessQuery() {
  return useQuery<ReadinessResponse, Error>({
    queryKey: queryKeys.readiness,
    queryFn: () => apiRequest<ReadinessResponse>("health/ready"),
    staleTime: 15_000,
    refetchInterval: 30_000,
    retry: false,
  });
}

export function useDevicesQuery() {
  return useQuery<Device[], Error>({
    queryKey: queryKeys.devices,
    queryFn: () => apiRequest<Device[]>("devices"),
    staleTime: 15_000,
    retry: 1,
  });
}

export function useExperimentsQuery() {
  return useQuery<Experiment[], Error>({
    queryKey: queryKeys.experiments,
    queryFn: () => apiRequest<Experiment[]>("experiments"),
    staleTime: 15_000,
    retry: 1,
  });
}

export function useMeasurementsQuery(limit = 10) {
  return useQuery<Measurement[], Error>({
    queryKey: queryKeys.measurements(limit),
    queryFn: () =>
      apiRequest<Measurement[]>(
        `measurements?${new URLSearchParams({
          limit: String(limit),
          offset: "0",
        }).toString()}`,
      ),
    staleTime: 5_000,
    refetchInterval: 15_000,
    retry: 1,
  });
}

export function useSpectraQuery(limit = 10) {
  return useQuery<Spectrum[], Error>({
    queryKey: queryKeys.spectra(limit),
    queryFn: () =>
      apiRequest<Spectrum[]>(
        `spectra?${new URLSearchParams({
          limit: String(limit),
          offset: "0",
        }).toString()}`,
      ),
    staleTime: 10_000,
    retry: 1,
  });
}

export function useCreateDeviceMutation() {
  const queryClient = useQueryClient();

  return useMutation<Device, Error, DeviceCreate>({
    mutationFn: (payload) =>
      apiRequest<Device>("devices", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(payload),
      }),
    onSuccess: async () => {
      await queryClient.invalidateQueries({
        queryKey: queryKeys.devices,
      });
    },
  });
}

export function useCreateExperimentMutation() {
  const queryClient = useQueryClient();

  return useMutation<Experiment, Error, ExperimentCreate>({
    mutationFn: (payload) =>
      apiRequest<Experiment>("experiments", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(payload),
      }),
    onSuccess: async () => {
      await queryClient.invalidateQueries({
        queryKey: queryKeys.experiments,
      });
    },
  });
}
