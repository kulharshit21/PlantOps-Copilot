export class ApiError extends Error {
  constructor(
    message: string,
    public status?: number,
  ) {
    super(message);
  }
}

export function apiBaseUrl() {
  return process.env.NEXT_PUBLIC_API_BASE_URL?.replace(/\/$/, "") || "http://localhost:8000";
}

export async function apiFetch<T>(
  path: string,
  options: RequestInit & { accessToken?: string | null } = {},
): Promise<T> {
  const { accessToken, headers, ...rest } = options;
  const response = await fetch(`${apiBaseUrl()}${path}`, {
    ...rest,
    headers: {
      "Content-Type": "application/json",
      ...(accessToken ? { Authorization: `Bearer ${accessToken}` } : {}),
      ...headers,
    },
  });

  if (!response.ok) {
    let detail = `API request failed with HTTP ${response.status}`;
    try {
      const payload = (await response.json()) as { detail?: string; error?: string };
      detail = payload.detail || payload.error || detail;
    } catch {
      // Keep the default detail when the API returns a non-JSON error.
    }
    throw new ApiError(detail, response.status);
  }

  return (await response.json()) as T;
}
