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

export type GameDetail = GameSummary & {
  storyline?: string | null;
  keywords: string[];
  developers: string[];
  publishers: string[];
  rating_band?: string | null;
  rating_reliable_flag: boolean;
  main_game_flag: boolean;
  data_caveats: string[];
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

export type ChatFilters = {
  platforms?: string[];
  release_year_min?: number | null;
  release_year_max?: number | null;
  multiplayer_mode?: string | null;
};

export type ChatHistoryMessage = {
  role: "user" | "guide";
  content: string;
};

export type ChatRequest = {
  message: string;
  conversation_id?: string | null;
  max_results?: number;
  filters?: ChatFilters | null;
  history?: ChatHistoryMessage[];
};

export type ChatRetrievedGame = GameSummary & {
  rank: number;
  retrieval_score?: number | null;
  semantic_score?: number | null;
  lexical_score?: number | null;
  evidence: string;
  match_explanation?: string | null;
  caveats: string[];
};

export type ChatResponse = {
  answer: string;
  mode: string;
  status: string;
  conversation_id?: string | null;
  retrieved_games: ChatRetrievedGame[];
  caveats: string[];
  applied_filters: Record<string, unknown>;
  follow_up_prompts: string[];
  contextual_query?: string | null;
  interpreted_preferences: Record<string, unknown>;
  chat_intent?: string | null;
  intent_confidence?: number | null;
  route_source?: string | null;
  matched_intent_example?: string | null;
};

export type ChatStatusResponse = {
  status: string;
  catalog_available: boolean;
  vector_store_available: boolean;
  collection_available: boolean;
  engine: string;
  warnings: string[];
};

export type MethodologySummary = {
  data_source: string;
  metrics: Record<string, number | string | boolean | null>;
  insight_summary: Record<string, unknown>;
  caveats: string[];
  implementation_notes: string[];
};

export type DashboardRow = Record<string, string | number | boolean | null>;

export type InsightsDashboard = {
  descriptive?: Record<string, DashboardRow[]>;
  diagnostic?: Record<string, DashboardRow[]>;
};

export type InsightsSummary = {
  dataset: Record<string, unknown>;
  descriptive: Record<string, unknown>;
  diagnostic: Record<string, unknown>;
  dashboard?: InsightsDashboard;
};

export type HealthResponse = {
  status: string;
  service: string;
  version: string;
};
