import type {
  CatalogResponse,
  FilterOptions,
  GameDetail,
  HealthResponse,
  InsightsSummary,
  MethodologySummary,
  RecommendationRequest,
  RecommendationResponse,
} from "@/types/api";

export const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

async function apiFetch<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    cache: "no-store",
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...(init?.headers ?? {}),
    },
  });

  if (!response.ok) {
    throw new Error(`API request failed: ${response.status} ${response.statusText}`);
  }

  return response.json() as Promise<T>;
}

export async function getHealth(): Promise<HealthResponse | null> {
  try {
    return await apiFetch<HealthResponse>("/health");
  } catch {
    return null;
  }
}

export async function getFilterOptions(): Promise<FilterOptions> {
  return apiFetch<FilterOptions>("/catalog/filter-options");
}

export async function getCatalogGames(query = ""): Promise<CatalogResponse> {
  const path = query ? `/catalog/games?${query}` : "/catalog/games";
  return apiFetch<CatalogResponse>(path);
}

export async function getCatalogGame(gameId: number | string): Promise<GameDetail> {
  return apiFetch<GameDetail>(`/catalog/games/${gameId}`);
}

export async function getMethodologySummary(): Promise<MethodologySummary> {
  return apiFetch<MethodologySummary>("/methodology/summary");
}

export async function getInsightsSummary(): Promise<InsightsSummary> {
  return apiFetch<InsightsSummary>("/insights/summary");
}

export async function postRecommendations(
  payload: RecommendationRequest,
): Promise<RecommendationResponse> {
  return apiFetch<RecommendationResponse>("/recommendations", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}
