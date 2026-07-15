export type GameSummary = {
  game_id: number;
  name: string;
  slug?: string | null;
  release_year?: number | null;
  cover_url?: string | null;
  screenshot_url?: string | null;
  summary?: string | null;
  total_rating?: number | null;
  total_rating_count?: number | null;
  custom_interest_score?: number | null;
  custom_interest_percentile?: number | null;
  extraction_cohort?: string | null;
  platforms: string[];
  genres: string[];
  themes: string[];
  game_modes: string[];
  player_perspectives: string[];
  normal_playtime_hours?: number | null;
  hidden_gem_balanced_flag: boolean;
  rag_ready_flag: boolean;
};

export type CatalogResponse = {
  items: GameSummary[];
  page: number;
  page_size: number;
  total_items: number;
  total_pages: number;
};

export type FilterOptions = {
  release_years?: number[];
  genres?: string[];
  themes?: string[];
  platforms?: string[];
  game_modes?: string[];
  player_perspectives?: string[];
  rating_bands?: string[];
  cohorts?: string[];
};

export type RecommendationRequest = {
  platform?: string | null;
  platforms?: string[];
  genres?: string[];
  themes?: string[];
  mood_words?: string[];
  favorite_games?: string[];
  playstyle_preferences?: string[];
  discovery_preference?: string;
  rating_quality_importance?: string;
  desired_playtime?: string;
  release_year_min?: number | null;
  release_year_max?: number | null;
  max_results?: number;
};

export type RecommendationResult = GameSummary & {
  rank: number;
  match_score?: number | null;
  recommendation_score?: number | null;
  similarity_score?: number | null;
  rating_score?: number | null;
  hidden_gem_boost?: number | null;
  explanation: string;
  caveats: string[];
};

export type RecommendationResponse = {
  mode: string;
  similarity_status: string;
  request_summary: Record<string, unknown>;
  items: RecommendationResult[];
};

export type MethodologySummary = {
  data_source: string;
  metrics: Record<string, number | string | boolean | null>;
  insight_summary: Record<string, unknown>;
  caveats: string[];
  implementation_notes: string[];
};

export type HealthResponse = {
  status: string;
  service: string;
  version: string;
};
