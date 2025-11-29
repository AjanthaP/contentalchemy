import { useEffect, useState } from "react";
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
  imageProvider: "dalle3",
};

function App() {
    // Handler to post LinkedIn content
    const [posting, setPosting] = useState(false);
    const [postStatus, setPostStatus] = useState<string | null>(null);

    const handlePostToLinkedIn = async () => {
      if (!result?.final_content || !linkedinToken) {
        setPostStatus("Missing LinkedIn token or content.");
        return;
      }
      setPosting(true);
      setPostStatus(null);
      try {
        const res = await fetch("/api/linkedin/post", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${linkedinToken}`,
          },
          body: JSON.stringify({ content: result.final_content }),
        });
        if (res.ok) {
          setPostStatus("Successfully posted to LinkedIn.");
        } else {
          const data = await res.json().catch(() => ({}));
          setPostStatus(data?.error || "Failed to post to LinkedIn.");
        }
      } catch (err) {
        setPostStatus("Error posting to LinkedIn.");
      } finally {
        setPosting(false);
      }
    };
  const [form, setForm] = useState(initialFormState);
  const [overrideEnabled, setOverrideEnabled] = useState(false);
  // userEmail is derived from LinkedIn profile or fallback
  const [userEmail, setUserEmail] = useState<string>("default_guest");
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
  // LinkedIn OAuth token state
  const [linkedinToken, setLinkedinToken] = useState(() => localStorage.getItem("contentalchemy.linkedinToken") || "");
  interface LinkedinProfile {
    given_name?: string;
    family_name?: string;
    email?: string;
    [key: string]: unknown;
  }
  const [linkedinProfile, setLinkedinProfile] = useState<LinkedinProfile | null>(null);

    // LinkedIn logout handler
    const handleLinkedinLogout = () => {
      setLinkedinToken("");
      setLinkedinProfile(null);
      localStorage.removeItem("contentalchemy.linkedinToken");
       // Debug: verify it's actually gone
      localStorage.removeItem("contentalchemy.linkedinProfile"); // Also clear profile if stored
          
      console.log("Token after logout:", localStorage.getItem("contentalchemy.linkedinToken")); // Should be null
      console.log("Profile after logout:", localStorage.getItem("contentalchemy.linkedinProfile")); // Should be null
      // Optionally reload page to clear query params/state
      // window.location.reload();
      window.location.href = "/login";
    };

  // const currentContent = useMemo(
  //   () => contentOptions.find((option) => option.value === form.contentType)!,
  //   [form.contentType],
  // );

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

  // Set userEmail from LinkedIn profile or fallback, replacing '@' and '.' with '_'
  useEffect(() => {
    let email = "default_guest";
    if (linkedinProfile && linkedinProfile.email) {
      email = linkedinProfile.email.replace(/[@.]/g, "_");
    }
    setUserEmail(email);
    if (email) {
      fetchProfile(email)
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
    }
  }, [linkedinProfile]);

    // LinkedIn OAuth token handling: detect token in callback URL, store, and fetch profile
    useEffect(() => {
      const params = new URLSearchParams(window.location.search);
      const token = params.get("linkedin_token");
      if (token) {
        setLinkedinToken(token);
        localStorage.setItem("contentalchemy.linkedinToken", token);
        // Remove token from URL for cleanliness
        window.history.replaceState({}, document.title, window.location.pathname);
      }
    }, []);

    // Optionally fetch LinkedIn profile if token is present
    useEffect(() => {
      if (linkedinToken) {
        console.log("LinkedIn token used for profile fetch:", linkedinToken); // Add this line
        fetch("/api/linkedin/profile", {
          headers: { Authorization: `Bearer ${linkedinToken}` },
        })
          .then((res) => res.ok ? res.json() : null)
          .then((data) => {
            console.log("Fetched LinkedIn profile data:", data); // Add this line
            if (data && data.profile) setLinkedinProfile(data.profile);
          })
          .catch(() => {
            // intentionally ignore LinkedIn profile fetch errors
          });
      }
    }, [linkedinToken]);

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
      await saveProfile(userEmail, {
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
      const selectedContentType = form.contentType;
      // Always send user_profile with all UI fields and override
      const user_profile = {
        override: overrideEnabled,
        ui_tone: form.tone,
        ui_keywords: form.keywords,
        ui_target_words: form.targetWords,
        ui_target_audience: form.targetAudience,
        ui_topic: form.query,
        ui_key_findings: undefined,
        ui_research_summary: undefined,
        ui_sources: form.includeSources,
        ui_user_query: form.query,
        ui_image_size: form.imageSize,
        ui_image_quality: form.imageQuality,
        ui_image_provider: form.imageProvider,
        ui_max_results: undefined,
        ui_key_points: undefined,
        ui_enable_seo: form.enableSeo,
      };
      const payload: GenerateRequest = {
        session_id: sessionId || undefined,
        user_id: userEmail,
        user_query: form.query,
        content_type: selectedContentType,
        tone: form.tone.toLowerCase(),
        enable_seo: form.enableSeo,
        include_sources: form.includeSources,
        target_words:
          selectedContentType === "blog" || selectedContentType === "research"
            ? form.targetWords
            : undefined,
        target_audience: form.targetAudience || undefined,
        keywords: form.keywords || undefined,
        additional_notes: form.additionalNotes || undefined,
        image_size: selectedContentType === "image" ? form.imageSize : undefined,
        image_quality:
          selectedContentType === "image" ? form.imageQuality : undefined,
        image_provider: form.imageProvider || "dalle3",
        override: overrideEnabled,
        user_profile: user_profile,
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
            {/* Email input removed. Email is now set from LinkedIn profile or defaults to 'default_guest'. */}

            <div style={{ marginBottom: 16 }}>
              {/* LinkedIn OAuth Button */}
              {!linkedinToken ? (
                <a
                  href="/api/linkedin/login"
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    background: '#0077b5',
                    color: '#fff',
                    borderRadius: 6,
                    padding: '8px 16px',
                    margin: '12px 0',
                    fontWeight: 600,
                    textDecoration: 'none',
                    boxShadow: '0 2px 8px rgba(0,119,181,0.08)',
                    transition: 'background 0.2s',
                  }}
                  title="Sign in with LinkedIn"
                >
                  <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" style={{ marginRight: 8 }}>
                    <rect width="24" height="24" rx="4" fill="#0077b5"/>
                    <path d="M7.1 19H4.6V9H7.1V19ZM5.85 7.8C5.01 7.8 4.35 7.13 4.35 6.3C4.35 5.47 5.01 4.8 5.85 4.8C6.69 4.8 7.35 5.47 7.35 6.3C7.35 7.13 6.69 7.8 5.85 7.8ZM19.1 19H16.6V14.2C16.6 13.07 16.57 11.61 15.07 11.61C13.56 11.61 13.34 12.85 13.34 14.12V19H10.84V9H13.22V10.34H13.25C13.59 9.72 14.37 9.07 15.47 9.07C18.13 9.07 19.1 10.77 19.1 13.13V19Z" fill="white"/>
                  </svg>
                  Sign in with LinkedIn
                </a>
              ) : (
                <div style={{
                  display: 'flex',
                  background: '#eaf6fb',
                  color: '#0077b5',
                  borderRadius: 6,
                  padding: '8px 16px',
                  margin: '12px 0',
                  fontWeight: 600,
                  boxShadow: '0 2px 8px rgba(0,119,181,0.08)',
                  flexDirection: 'column',
                  alignItems: 'flex-start',
                }}>
                  <div style={{ display: 'flex', alignItems: 'center', width: '100%' }}>
                    <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" style={{ marginRight: 8 }}>
                      <rect width="24" height="24" rx="4" fill="#0077b5"/>
                      <path d="M7.1 19H4.6V9H7.1V19ZM5.85 7.8C5.01 7.8 4.35 7.13 4.35 6.3C4.35 5.47 5.01 4.8 5.85 4.8C6.69 4.8 7.35 5.47 7.35 6.3C7.35 7.13 6.69 7.8 5.85 7.8ZM19.1 19H16.6V14.2C16.6 13.07 16.57 11.61 15.07 11.61C13.56 11.61 13.34 12.85 13.34 14.12V19H10.84V9H13.22V10.34H13.25C13.59 9.72 14.37 9.07 15.47 9.07C18.13 9.07 19.1 10.77 19.1 13.13V19Z" fill="white"/>
                    </svg>
                    <span>LinkedIn Connected</span>
                    <button
                      onClick={handleLinkedinLogout}
                      style={{
                        marginLeft: 12,
                        background: '#fff',
                        color: '#0077b5',
                        border: '1px solid #0077b5',
                        borderRadius: 4,
                        padding: '4px 12px',
                        fontWeight: 500,
                        cursor: 'pointer',
                        boxShadow: '0 1px 4px rgba(0,119,181,0.08)',
                        transition: 'background 0.2s',
                      }}
                      title="Logout from LinkedIn"
                    >
                      Logout
                    </button>
                  </div>
                  {/* Profile Section */}
                  {linkedinProfile && (
                    <div style={{ marginTop: 12, width: '100%', background: '#fff', borderRadius: 4, padding: 12, boxShadow: '0 1px 4px rgba(0,119,181,0.08)' }}>
                      <h4 style={{ margin: '0 0 8px 0', color: '#0077b5' }}>Profile</h4>
                      <div style={{ fontSize: 15, fontWeight: 500 }}>
                        {linkedinProfile.given_name} {linkedinProfile.family_name}
                      </div>
                      {linkedinProfile.email && (
                        <div style={{ fontSize: 13, color: '#555' }}>Email: {linkedinProfile.email}</div>
                      )}
                      {/* Add more profile fields as needed */}
                    </div>
                  )}
                </div>
              )}
            </div>
              
              <label className="field" style={{ display: 'flex', alignItems: 'center', marginBottom: 0 }}>
                <span style={{ marginRight: 8 }}>Override Routing</span>
                <span
                  style={{
                    display: 'inline-block',
                    width: 48,
                    height: 24,
                    borderRadius: 12,
                    background: overrideEnabled ? 'linear-gradient(90deg, #4caf50 60%, #388e3c 100%)' : 'linear-gradient(90deg, #ccc 60%, #888 100%)',
                    cursor: 'pointer',
                    boxShadow: overrideEnabled ? '0 0 4px #4caf50' : '0 0 2px #888',
                    position: 'relative',
                    transition: 'background 0.2s',
                    marginBottom: 8,
                  }}
                  onClick={() => setOverrideEnabled(!overrideEnabled)}
                >
                  <span
                    style={{
                      position: 'absolute',
                      left: overrideEnabled ? 24 : 4,
                      top: 4,
                      width: 16,
                      height: 16,
                      borderRadius: '50%',
                      background: '#fff',
                      boxShadow: '0 1px 4px rgba(0,0,0,0.08)',
                      transition: 'left 0.2s',
                    }}
                  />
                </span>
              </label>

                {/* Move Content Type dropdown below override toggle */}
                <label className="field">
                  <span>Content Type</span>
                  <select
                    value={form.contentType}
                    onChange={(event) =>
                      setForm((prev) => ({ ...prev, contentType: event.target.value as ContentType }))
                    }
                    style={{ marginBottom: 12 }}
                  >
                    {contentOptions.map((option) => (
                      <option key={option.value} value={option.value}>
                        {option.label}
                      </option>
                    ))}
                  </select>
                </label>

            <details style={{ marginBottom: 16 }} className="expander" open>
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
              <div className="grid two">
                <label className="checkbox" style={{ display: 'flex', alignItems: 'flex-start', marginTop: 8, marginBottom: 0 }}>
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
                  SEO optimization
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
                  Include sources
                </label>
              </div>
              {(form.contentType === "blog" || form.contentType === "research") && (
                <label className="field">
                  <span>Target Word Count: {form.targetWords}</span>
                  <input
                    type="range"
                    min={600}
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
                  <label className="field">
                    <span>Image Provider</span>
                    <select
                      value={form.imageProvider}
                      onChange={(event) =>
                        setForm((prev) => ({
                          ...prev,
                          imageProvider: event.target.value,
                        }))
                      }
                    >
                      <option value="dalle3">DALL·E 3</option>
                      <option value="stable-diffusion">Stable Diffusion</option>
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
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
              <h2>Content Request</h2>
              {/* Always show Post to LinkedIn button */}
              {postStatus && (
                <span style={{ marginLeft: 12, color: postStatus.includes("Success") ? "#388e3c" : "#d32f2f" }}>
                  {postStatus}
                </span>
              )}
              <button
                className="primary"
                style={{ marginLeft: 8 }}
                onClick={handlePostToLinkedIn}
                disabled={posting}
              >
                {posting ? "Posting..." : "Post to LinkedIn"}
              </button>
            </div>
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

            {/* ...existing code... */}

            <details className="expander" style={{marginBottom: 8}} open>
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
              {loading ? "Working..." : "Generate Content"}
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
                  {isImageResult && (result.image_url || result.image_base64 || result.image_object) ? (
                    <div className="image-block">
                      <img src={result.image_url || (result.image_object ? `data:image/png;base64,${result.image_object}` : "")}
                        alt="Generated" />
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

              {/* Metadata Section */}
              <div className="metadata-panel" style={{ marginTop: 24, padding: 16, background: "#f9f9f9", borderRadius: 8 }}>
                <h3>Metadata</h3>
                <ul style={{ listStyle: "none", padding: 0 }}>
                  <li><strong>Content Type:</strong> {result.content_type}</li>
                  <li><strong>Tone:</strong> {typeof result.metadata?.tone === 'string' ? result.metadata.tone : form.tone}</li>
                  <li><strong>Word Length:</strong> {typeof result.metadata?.word_count === 'number' ? result.metadata.word_count : (typeof result.metadata?.char_count === 'number' ? result.metadata.char_count : (typeof result.final_content === 'string' ? result.final_content.length : "N/A"))}</li>
                  <li><strong>Target Audience:</strong> {typeof result.metadata?.target_audience === 'string' ? result.metadata.target_audience : (form.targetAudience || "N/A")}</li>
                  <li><strong>Keywords:</strong> {Array.isArray(result.metadata?.keywords) ? result.metadata.keywords.join(", ") : (typeof result.metadata?.keywords === 'string' ? result.metadata.keywords : (form.keywords || "N/A"))}</li>
                  {/* Add more fields as needed */}
                </ul>
              </div>
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
