import { useEffect, useMemo, useState } from "react";

const apiBase = import.meta.env.VITE_API_BASE || "";
const api = (path) => `${apiBase}${path}`;

const formatCount = (count) => `${count} candidate${count !== 1 ? "s" : ""}`;

function App() {
  const [jobTitle, setJobTitle] = useState("");
  const [jobDescription, setJobDescription] = useState("");
  const [files, setFiles] = useState([]);
  const [history, setHistory] = useState([]);
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    loadHistory();
  }, []);

  const selectedFiles = useMemo(
    () => Array.from(files).filter((file) => file),
    [files]
  );

  const reset = () => {
    setJobTitle("");
    setJobDescription("");
    setFiles([]);
    setResults(null);
    setError("");
  };

  const loadHistory = async () => {
    try {
      const response = await fetch(api("/api/history"));
      const data = await response.json();
      setHistory(Array.isArray(data) ? data : []);
    } catch (err) {
      console.warn("Unable to load history", err);
    }
  };

  const handleFileChange = (event) => {
    setFiles([...selectedFiles, ...Array.from(event.target.files)]);
  };

  const removeFile = (name) => {
    setFiles(selectedFiles.filter((file) => file.name !== name));
  };

  const handleSubmit = async () => {
    setError("");

    if (!jobDescription.trim()) {
      setError("Please provide a job description.");
      return;
    }
    if (!selectedFiles.length) {
      setError("Please upload at least one resume.");
      return;
    }

    setLoading(true);
    const formData = new FormData();
    formData.append("job_title", jobTitle.trim() || "Untitled Role");
    formData.append("job_description", jobDescription.trim());
    selectedFiles.forEach((file) => formData.append("resumes", file));

    try {
      const response = await fetch(api("/api/screen"), {
        method: "POST",
        body: formData,
      });
      const data = await response.json();
      if (!response.ok) {
        setError(data.error || "Screening failed.");
        setResults(null);
        return;
      }
      setResults(data);
      await loadHistory();
    } catch (err) {
      setError("Unable to connect to the API. Confirm the backend is running.");
      setResults(null);
    } finally {
      setLoading(false);
    }
  };

  const loadScreening = async (screeningId) => {
    setError("");
    setLoading(true);
    try {
      const response = await fetch(api(`/api/screening/${screeningId}`));
      const data = await response.json();
      if (!response.ok) {
        setError(data.error || "Failed to load screening details.");
        return;
      }
      setResults(data);
    } catch (err) {
      setError("Unable to load screening details.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="app-shell">
      <header className="topbar">
        <div>
          <h1>ResumeIQ</h1>
          <p>AI screening for resumes with a dedicated React frontend and API backend.</p>
        </div>
      </header>

      <main>
        <section className="screen-card">
          <div className="panel">
            <h2>New screening</h2>
            <label>
              Job title
              <input value={jobTitle} onChange={(event) => setJobTitle(event.target.value)} placeholder="e.g. Data Engineer" />
            </label>
            <label>
              Job description
              <textarea value={jobDescription} onChange={(event) => setJobDescription(event.target.value)} rows={8} placeholder="Paste the full job description here" />
            </label>
            <label className="file-input-label">
              Upload resumes
              <input type="file" multiple accept=".pdf,.docx,.txt" onChange={handleFileChange} />
            </label>
            <div className="file-list">
              {selectedFiles.map((file) => (
                <div key={file.name} className="file-chip">
                  {file.name}
                  <button type="button" onClick={() => removeFile(file.name)}>
                    Remove
                  </button>
                </div>
              ))}
            </div>
            <div className="button-row">
              <button className="primary" onClick={handleSubmit} disabled={loading}>
                {loading ? "Screening…" : "Screen Candidates"}
              </button>
              <button className="secondary" onClick={reset} type="button">
                Clear
              </button>
            </div>
            {error && <div className="error-banner">{error}</div>}
          </div>

          <div className="panel summary-panel">
            <h2>Recent screenings</h2>
            {history.length ? (
              <ul className="history-list">
                {history.map((item) => (
                  <li key={item.id} onClick={() => loadScreening(item.id)}>
                    <span>{item.job_title}</span>
                    <span>{item.created_at}</span>
                    <span>{formatCount(item.total)}</span>
                    <strong>{item.top_score}%</strong>
                  </li>
                ))}
              </ul>
            ) : (
              <p className="muted">No history yet. Run a screening to see results.</p>
            )}
          </div>
        </section>

        {results && (
          <section className="result-panel">
            <div className="result-header">
              <div>
                <h2>Results</h2>
                <p>{results.job_title || "Screening results"}</p>
              </div>
              <button className="secondary" type="button" onClick={reset}>
                New session
              </button>
            </div>
            <div className="candidate-grid">
              {results.results.map((candidate) => (
                <div key={candidate.filename} className="candidate-card">
                  <div className="candidate-card__header">
                    <h3>{candidate.filename}</h3>
                    <span className="score-badge">{candidate.score}%</span>
                  </div>
                  <div className="candidate-card__meta">
                    <span>{candidate.word_count} words</span>
                    <span>{candidate.experience_level}</span>
                  </div>
                  <div className="tag-row">
                    {candidate.matched_skills.slice(0, 6).map((skill) => (
                      <span key={skill} className="tag matched">
                        {skill}
                      </span>
                    ))}
                  </div>
                  <div className="tag-row missing">
                    {candidate.missing_skills.slice(0, 6).map((skill) => (
                      <span key={skill} className="tag missing">{skill}</span>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          </section>
        )}
      </main>
      <footer className="app-footer">
        ResumeIQ — React frontend with Flask API backend.
      </footer>
    </div>
  );
}

export default App;
