
const configuredBaseUrl = import.meta.env.VITE_API_BASE_URL;

export const API_BASE_URL = (
  configuredBaseUrl || "/api/v1"
).replace(/\/+$/, "");

export class ApiError extends Error {
  readonly status: number;
  readonly details: unknown;

  constructor(message: string, status: number, details: unknown) {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.details = details;
  }
}

async function readErrorBody(response: Response): Promise<unknown> {
  const contentType = response.headers.get("content-type");

  if (contentType?.includes("application/json")) {
    try {
      return await response.json();
    } catch {
      return null;
    }
  }

  try {
    return await response.text();
  } catch {
    return null;
  }
}

function getErrorMessage(
  status: number,
  details: unknown,
): string {
  if (
    typeof details === "object" &&
    details !== null &&
    "detail" in details
  ) {
    const detail = details.detail;

    if (typeof detail === "string") {
      return detail;
    }

    if (Array.isArray(detail)) {
      return detail
        .map((item) => {
          if (
            typeof item === "object" &&
            item !== null &&
            "msg" in item &&
            typeof item.msg === "string"
          ) {
            return item.msg;
          }

          return JSON.stringify(item);
        })
        .join("; ");
    }
  }

  if (typeof details === "string" && details.length > 0) {
    return details;
  }

  return `Request failed with HTTP status ${status}.`;
}

export async function apiRequest<T>(
  path: string,
  init?: RequestInit,
): Promise<T> {
  const normalizedPath = path.replace(/^\/+/, "");

  const response = await fetch(
    `${API_BASE_URL}/${normalizedPath}`,
    {
      ...init,
      headers: {
        Accept: "application/json",
        ...init?.headers,
      },
    },
  );

  if (!response.ok) {
    const details = await readErrorBody(response);

    throw new ApiError(
      getErrorMessage(response.status, details),
      response.status,
      details,
    );
  }

  if (response.status === 204) {
    return undefined as T;
  }

  return (await response.json()) as T;
}
