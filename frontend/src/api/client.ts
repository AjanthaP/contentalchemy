import {
  ConversationHistoryResponse,
  GenerateRequest,
  GenerateResponse,
  ProfileResponse,
  ProfileUpdateRequest,
} from "../types";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "";

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    headers: {
      "Content-Type": "application/json",
      ...(options.headers || {}),
    },
    ...options,
  });

  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(errorText || response.statusText);
  }

  return response.json() as Promise<T>;
}

export function fetchProfile(email: string): Promise<ProfileResponse> {
  return request(`/api/profile/${encodeURIComponent(email)}`);
}

export function saveProfile(
  email: string,
  payload: ProfileUpdateRequest,
): Promise<ProfileResponse> {
  return request(`/api/profile/${encodeURIComponent(email)}`, {
    method: "PUT",
    body: JSON.stringify(payload),
  });
}

export function generateContent(
  payload: GenerateRequest,
): Promise<GenerateResponse> {
  return request("/api/generate", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function fetchHistory(
  sessionId: string,
): Promise<ConversationHistoryResponse> {
  return request(`/api/history/${encodeURIComponent(sessionId)}`);
}
