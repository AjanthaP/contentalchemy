import { useEffect, useMemo, useState } from "react";
import ReactMarkdown from "react-markdown";
import "./App.css";
import {
  fetchHistory,
  fetchProfile,
  generateContent,
  saveProfile,
} from "./api/client";
import {
  ContentType,
  GenerateRequest,
  GenerateResponse,
  Message,
  ValidationResult,
} from "./types";

type StatusState = { type: "success" | "error"; message: string } | null;

interface ContentOption {
  label: string;
  value: ContentType;
  description: string;
  actionLabel: string;
}

const contentOptions: ContentOption[] = [
  {
    label: "Research Report",
    value: "research",
    description: "Web research with structured insights and sources.",
    actionLabel: "Generate Research Report",
  },
  {
    label: "SEO Blog Post",
    value: "blog",
    description: "Long-form blog optimized for search and readability.",
    actionLabel: "Generate Blog Post",
  },
  {
    label: "LinkedIn Post",
    value: "linkedin",
    description: "Social-friendly update for professional audiences.",
    actionLabel: "Generate LinkedIn Post",
  },
  {
    label: "AI Image Prompt",
    value: "image",
    description: "Image concept + prompt for creative assets.",
    actionLabel: "Generate Image",
  },
  {
    label: "Content Strategy",
    value: "strategy",
    description: "High-level messaging plan from research findings.",
    actionLabel: "Generate Strategy",
  },
];

const toneOptions = [
  "Casual",
  "Conversational",
  "Professional",
  "Formal",
  "Technical",
];

const initialFormState = {
  contentType: contentOptions[0].value,
  tone: "Professional",
  enableSeo: true,
  includeSources: true,
  targetWords: 1500,
  query: "",
  targetAudience: "",
  keywords: "",
  additionalNotes: "",
  imageSize: "1024x1024",
  imageQuality: "standard",
};

function App() {
  const [form, setForm] = useState(initialFormState);
  const [userId, setUserId] = useState(
    () => localStorage.getItem("contentalchemy.userId") ?? "default",
  );
  const [sessionId, setSessionId] = useState(
    () => localStorage.getItem("contentalchemy.sessionId") ?? "",
  );
  const [status, setStatus] = useState<StatusState>(null);
  const [loading, setLoading] = useState(false);
  const [profileSaving, setProfileSaving] = useState(false);
  const [profileNote, setProfileNote] = useState<string | null>(null);
  const [result, setResult] = useState<GenerateResponse | null>(null);
  const [history, setHistory] = useState<Message[]>([]);
  const [activeTab, setActiveTab] = useState<"content" | "analysis" | "sources">(
    "content",
  );
  const [expandedMessages, setExpandedMessages] = useState<Set<number>>(new Set());

  const currentContent = useMemo(
    () => contentOptions.find((option) => option.value === form.contentType)!,
    [form.contentType],
  );

  const toggleMessage = (index: number) => {
    setExpandedMessages((prev) => {
      const newSet = new Set(prev);
      if (newSet.has(index)) {
        newSet.delete(index);
      } else {
        newSet.add(index);
      }
      return newSet;
    });
  };

  useEffect(() => {
    localStorage.setItem("contentalchemy.userId", userId);
    fetchProfile(userId)
      .then((profileResponse) => {
        const preferences = profileResponse.profile?.preferences as
          | Record<string, unknown>
          | undefined;
        setForm((prev) => ({
          ...prev,
          tone: (preferences?.tone as string) ?? prev.tone,
          includeSources:
            typeof preferences?.include_sources === "boolean"
              ? (preferences?.include_sources as boolean)
              : prev.includeSources,
          enableSeo:
            typeof preferences?.seo_optimization === "boolean"
              ? (preferences?.seo_optimization as boolean)
              : prev.enableSeo,
        }));
      })
      .catch(() => {
        /* profile optional */
      });
  }, [userId]);

  useEffect(() => {
    if (!sessionId) {
      setHistory([]);
      return;
    }
    localStorage.setItem("contentalchemy.sessionId", sessionId);
    fetchHistory(sessionId)
      .then((conversation) => setHistory(conversation.history))
      .catch(() => setHistory([]));
  }, [sessionId]);

  const handleProfileSave = async () => {
    setProfileSaving(true);
    setProfileNote(null);
    try {
      await saveProfile(userId, {
        preferences: {
          tone: form.tone.toLowerCase(),
          include_sources: form.includeSources,
          seo_optimization: form.enableSeo,
        },
      });
      setProfileNote("Profile saved.");
    } catch (error) {
      setProfileNote("Unable to save profile.");
    } finally {
      setProfileSaving(false);
    }
  };

  const handleGenerate = async () => {
    if (!form.query.trim()) {
      setStatus({ type: "error", message: "Enter a request to begin." });
      return;
    }

    setLoading(true);
    setStatus(null);
    try {
      const payload: GenerateRequest = {
        session_id: sessionId || undefined,
        user_id: userId,
        user_query: form.query,
        content_type: form.contentType,
        tone: form.tone.toLowerCase(),
        enable_seo: form.enableSeo,
        include_sources: form.includeSources,
        target_words:
          form.contentType === "blog" || form.contentType === "research"
            ? form.targetWords
            : undefined,
        target_audience: form.targetAudience || undefined,
        keywords: form.keywords || undefined,
        additional_notes: form.additionalNotes || undefined,
        image_size: form.contentType === "image" ? form.imageSize : undefined,
        image_quality:
          form.contentType === "image" ? form.imageQuality : undefined,
      };

      const response = await generateContent(payload);
      setResult(response);
      setSessionId(response.session_id);
      setHistory(response.conversation?.messages ?? []);
      setStatus({ type: "success", message: "Content ready." });
      setActiveTab("content");
    } catch (error) {
      const message =
        error instanceof Error ? error.message : "Unable to generate content.";
      setStatus({ type: "error", message });
    } finally {
      setLoading(false);
    }
  };

  const downloadContent = (format: "md" | "txt") => {
    if (!result?.final_content) return;
    const blob = new Blob([result.final_content], {
      type: format === "md" ? "text/markdown" : "text/plain",
    });
    const url = URL.createObjectURL(blob);
    const timestamp = new Date().toISOString().replace(/[:.]/g, "-");
    const anchor = document.createElement("a");
    anchor.href = url;
    anchor.download = `content-${timestamp}.${format}`;
    anchor.click();
    URL.revokeObjectURL(url);
  };

  const analysis: ValidationResult | null | undefined = result?.analysis;
  const isImageRequest = form.contentType === "image";
  const isImageResult = result?.content_type === "image";
  const isBlogResult = result?.content_type === "blog";

  return (
    <div className="page">
      <header className="header">
        <div>
          <p className="headline">ContentAlchemy</p>
          <p className="subhead">AI Content & Research Copilot</p>
        </div>
        <div className="session-meta">
          {sessionId && <span>Session {sessionId.slice(0, 8)}</span>}
          <span>v1.0.0</span>
        </div>
      </header>

      {status && (
        <div className={`status-banner ${status.type}`}>
          {status.message}
        </div>
      )}

      <div className="layout">
        <aside className="sidebar">
          <section className="panel">
            <h2>Configuration</h2>
            <label className="field">
              <span>User ID</span>
              <input
                value={userId}
                onChange={(event) => setUserId(event.target.value.trim() || "default")}
              />
            </label>

            <div className="options">
              {contentOptions.map((option) => (
                <button
                  key={option.value}
                  className={`option ${
                    option.value === form.contentType ? "active" : ""
                  }`}
                  onClick={() =>
                    setForm((prev) => ({ ...prev, contentType: option.value }))
                  }
                >
                  <div>
                    <strong>{option.label}</strong>
                    <p>{option.description}</p>
                  </div>
                </button>
              ))}
            </div>

            <details className="expander" open>
              <summary>Advanced Settings</summary>
              <label className="field">
                <span>Tone</span>
                <select
                  value={form.tone}
                  onChange={(event) =>
                    setForm((prev) => ({ ...prev, tone: event.target.value }))
                  }
                >
                  {toneOptions.map((tone) => (
                    <option key={tone} value={tone}>
                      {tone}
                    </option>
                  ))}
                </select>
              </label>

              <label className="checkbox">
                <input
                  type="checkbox"
                  checked={form.enableSeo}
                  onChange={(event) =>
                    setForm((prev) => ({
                      ...prev,
                      enableSeo: event.target.checked,
                    }))
                  }
                />
                Enable SEO optimization
              </label>

              <label className="checkbox">
                <input
                  type="checkbox"
                  checked={form.includeSources}
                  onChange={(event) =>
                    setForm((prev) => ({
                      ...prev,
                      includeSources: event.target.checked,
                    }))
                  }
                />
                Include sources when available
              </label>

              {(form.contentType === "blog" || form.contentType === "research") && (
                <label className="field">
                  <span>Target Word Count: {form.targetWords}</span>
                  <input
                    type="range"
                    min={800}
                    max={2500}
                    step={100}
                    value={form.targetWords}
                    onChange={(event) =>
                      setForm((prev) => ({
                        ...prev,
                        targetWords: Number(event.target.value),
                      }))
                    }
                  />
                </label>
              )}

              {isImageRequest && (
                <div className="image-settings">
                  <label className="field">
                    <span>Image Size</span>
                    <select
                      value={form.imageSize}
                      onChange={(event) =>
                        setForm((prev) => ({
                          ...prev,
                          imageSize: event.target.value,
                        }))
                      }
                    >
                      <option value="1024x1024">1024x1024</option>
                      <option value="1024x1792">1024x1792</option>
                      <option value="1792x1024">1792x1024</option>
                    </select>
                  </label>
                  <label className="field">
                    <span>Image Quality</span>
                    <select
                      value={form.imageQuality}
                      onChange={(event) =>
                        setForm((prev) => ({
                          ...prev,
                          imageQuality: event.target.value,
                        }))
                      }
                    >
                      <option value="standard">standard</option>
                      <option value="hd">hd</option>
                    </select>
                  </label>
                </div>
              )}
            </details>

            <div className="profile-actions">
              <button
                className="secondary"
                onClick={handleProfileSave}
                disabled={profileSaving}
              >
                {profileSaving ? "Saving..." : "Save Preferences"}
              </button>
              {profileNote && <p className="note">{profileNote}</p>}
            </div>
          </section>
        </aside>

        <main className="main">
          <section className="panel form-panel">
            <h2>Content Request</h2>
            <label className="field">
              <span>What should we create?</span>
              <textarea
                rows={8}
                placeholder="Describe the asset, goals, and key talking points."
                value={form.query}
                onChange={(event) =>
                  setForm((prev) => ({ ...prev, query: event.target.value }))
                }
              />
            </label>

            <details className="expander" open>
              <summary>Additional context</summary>
              <div className="grid two">
                <label className="field">
                  <span>Target audience</span>
                  <input
                    placeholder="e.g., tech founders, B2B marketers"
                    value={form.targetAudience}
                    onChange={(event) =>
                      setForm((prev) => ({
                        ...prev,
                        targetAudience: event.target.value,
                      }))
                    }
                  />
                </label>
                <label className="field">
                  <span>Keywords</span>
                  <input
                    placeholder="comma-separated keywords"
                    value={form.keywords}
                    onChange={(event) =>
                      setForm((prev) => ({
                        ...prev,
                        keywords: event.target.value,
                      }))
                    }
                  />
                </label>
              </div>
              <label className="field">
                <span>Additional notes</span>
                <textarea
                  rows={4}
                  placeholder="Must-have sections, CTA, style guardrails..."
                  value={form.additionalNotes}
                  onChange={(event) =>
                    setForm((prev) => ({
                      ...prev,
                      additionalNotes: event.target.value,
                    }))
                  }
                />
              </label>
            </details>

            <button
              className="primary large"
              onClick={handleGenerate}
              disabled={loading}
            >
              {loading ? "Working..." : currentContent.actionLabel}
            </button>
          </section>

          {result && (
            <section className="panel result-panel">
              <div className="panel-header">
                <div>
                  <h2>Generated Content</h2>
                  <p>
                    {result.content_type.replace("_", " ")} · {new Date().toLocaleTimeString()}
                  </p>
                </div>
                <div className="actions">
                  <button onClick={() => downloadContent("md")}>Download .md</button>
                  <button onClick={() => downloadContent("txt")}>Download .txt</button>
                </div>
              </div>

              <div className="tabs">
                {["content", "analysis", "sources"].map((tab) => (
                  <button
                    key={tab}
                    className={tab === activeTab ? "active" : ""}
                    onClick={() => setActiveTab(tab as typeof activeTab)}
                  >
                    {tab.charAt(0).toUpperCase() + tab.slice(1)}
                  </button>
                ))}
              </div>

              {activeTab === "content" && (
                <div className="content-view">
                  {isImageResult && result.image_url ? (
                    <div className="image-block">
                      <img src={result.image_url} alt="Generated" />
                      {result.image_prompt && (
                        <pre>{result.image_prompt}</pre>
                      )}
                    </div>
                  ) : isBlogResult ? (
                    <div className="markdown-view">
                      <ReactMarkdown>{result.final_content}</ReactMarkdown>
                    </div>
                  ) : (
                    <textarea
                      className="content-editor"
                      value={result.final_content}
                      readOnly
                    />
                  )}
                </div>
              )}

              {activeTab === "analysis" && (
                <div className="analysis-view">
                  {analysis ? (
                    <>
                      <div className="score">
                        <strong>Quality Score</strong>
                        <span>{analysis.score} / 100</span>
                      </div>
                      <div className="issue-grid">
                        <div>
                          <h4>Issues</h4>
                          {analysis.issues.length ? (
                            <ul>
                              {analysis.issues.map((issue) => (
                                <li key={issue}>{issue}</li>
                              ))}
                            </ul>
                          ) : (
                            <p>None detected.</p>
                          )}
                        </div>
                        <div>
                          <h4>Warnings</h4>
                          {analysis.warnings.length ? (
                            <ul>
                              {analysis.warnings.map((item) => (
                                <li key={item}>{item}</li>
                              ))}
                            </ul>
                          ) : (
                            <p>Clean bill of health.</p>
                          )}
                        </div>
                        <div>
                          <h4>Suggestions</h4>
                          {analysis.suggestions.length ? (
                            <ul>
                              {analysis.suggestions.map((item) => (
                                <li key={item}>{item}</li>
                              ))}
                            </ul>
                          ) : (
                            <p>No additional suggestions.</p>
                          )}
                        </div>
                      </div>
                    </>
                  ) : (
                    <p>Analysis available for blog and research assets.</p>
                  )}
                </div>
              )}

              {activeTab === "sources" && (
                <div className="sources-view">
                  {result.sources?.length ? (
                    <ul>
                      {result.sources.map((source, index) => {
                        const title =
                          typeof source.title === "string"
                            ? source.title
                            : `Source ${index + 1}`;
                        const url =
                          typeof source.url === "string" ? source.url : "";
                        const snippet =
                          typeof source.snippet === "string" ? source.snippet : "";
                        return (
                          <li key={`${title}-${index}`}>
                            <strong>{title}</strong>
                            {url && (
                              <a href={url} target="_blank" rel="noreferrer">
                                {url}
                              </a>
                            )}
                            {snippet && <p>{snippet}</p>}
                          </li>
                        );
                      })}
                    </ul>
                  ) : (
                    <p>No sources returned for this output.</p>
                  )}
                </div>
              )}
            </section>
          )}

          {history.length > 0 && (
            <section className="panel history-panel">
              <h2>Conversation History</h2>
              <ul>
                {history.map((message, index) => {
                  const isExpanded = expandedMessages.has(index);
                  const preview = message.content.slice(0, 80) + (message.content.length > 80 ? '...' : '');
                  return (
                    <li key={`${message.timestamp}-${index}`} className={isExpanded ? 'expanded' : 'collapsed'}>
                      <header onClick={() => toggleMessage(index)}>
                        <div className="message-header-content">
                          <span className="role-badge">{message.role.toUpperCase()}</span>
                          <span className="message-preview">{isExpanded ? '' : preview}</span>
                        </div>
                        <div className="message-meta">
                          <span className="timestamp">{new Date(message.timestamp).toLocaleTimeString()}</span>
                          <span className="expand-icon">{isExpanded ? '▼' : '▶'}</span>
                        </div>
                      </header>
                      {isExpanded && (
                        <div className="message-content">
                          <p>{message.content}</p>
                        </div>
                      )}
                    </li>
                  );
                })}
              </ul>
            </section>
          )}

          <section className="panel tips-panel">
            <h2>Tips & Examples</h2>
            <ul>
              <li>Be specific about the outcome, audience, and purpose.</li>
              <li>Share any required sources, tone guidance, or CTAs.</li>
              <li>Use research mode when accuracy and citations matter.</li>
              <li>Iterate often—the assistant learns from your edits.</li>
            </ul>
            <div className="examples">
              <p>Example prompts:</p>
              <code>Research the 2025 AI marketing trends for SaaS founders.</code>
              <code>Write an SEO blog about climate tech funding opportunities.</code>
              <code>Create a LinkedIn post announcing our Series B round.</code>
              <code>Design an image prompt for a futuristic workspace hero shot.</code>
            </div>
          </section>
        </main>
      </div>
    </div>
  );
}

export default App;
