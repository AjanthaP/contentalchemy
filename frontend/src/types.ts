export type ContentType = "research" | "blog" | "linkedin" | "image" | "strategy";

export type Role = "user" | "assistant" | "system";

export interface Message {
  role: Role;
  content: string;
  timestamp: string;
  metadata?: Record<string, unknown>;
}

export interface ValidationResult {
  is_valid: boolean;
  score: number;
  issues: string[];
  warnings: string[];
  suggestions: string[];
}

export interface ConversationResponse {
  session_id: string;
  messages: Message[];
}

export interface GenerateRequest {
  session_id?: string;
  user_id: string;
  user_query: string;
  content_type: ContentType;
  tone: string;
  enable_seo: boolean;
  include_sources: boolean;
  target_words?: number;
  target_audience?: string;
  keywords?: string;
  additional_notes?: string;
  image_size?: string;
  image_quality?: string;
  override: boolean
}

export interface GenerateResponse {
  session_id: string;
  user_id: string;
  content_type: ContentType;
  final_content: string;
  metadata: Record<string, unknown>;
  analysis?: ValidationResult | null;
  image_url?: string | null;
  image_prompt?: string | null;
  sources: Record<string, unknown>[];
  raw_result: Record<string, unknown>;
  conversation?: ConversationResponse | null;
}

export interface ProfileResponse {
  user_id: string;
  profile: Record<string, unknown>;
}

export interface ProfileUpdateRequest {
  preferences?: Record<string, unknown>;
  brand_voice?: Record<string, unknown> | null;
}

export interface ConversationHistoryResponse {
  session_id: string;
  history: Message[];
}
