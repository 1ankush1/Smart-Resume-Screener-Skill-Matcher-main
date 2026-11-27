/** Purpose: Provides a public resume-to-job comparison page without accounts. */

import { useState } from "react";
import { AlertCircle, ArrowRight, LoaderCircle, Sparkles } from "lucide-react";
import Navbar from "../components/Navbar";
import ResumeUpload from "../components/ResumeUpload";
import JobDescriptionForm from "../components/JobDescriptionForm";
import MatchResults from "../components/MatchResults";
import { analyzeResume } from "../services/api";

export default function Dashboard() {
  const [file, setFile] = useState(null);
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function handleAnalyze() {
    setError("");
    setResult(null);
    if (!file) return setError("Please upload a resume first.");
    if (!description.trim()) return setError("Please enter the job description.");
    if (!/\.(pdf|docx)$/i.test(file.name)) return setError("Only PDF and DOCX files are supported.");
    if (file.size > 5 * 1024 * 1024) return setError("The file is larger than 5 MB.");

    setLoading(true);
    try {
      const data = await analyzeResume(file, description, title);
      setResult(data);
      window.setTimeout(() => document.getElementById("match-results")?.scrollIntoView({ behavior: "smooth", block: "start" }), 100);
    } catch (requestError) {
      const message = requestError.response?.data?.error || requestError.message;
      setError(requestError.response
        ? `Analysis failed: ${message}`
        : `Analysis failed: ${message}. Make sure the local API is running on port 5000.`);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="app-shell">
      <Navbar />
      <main className="dashboard-main">
        <section className="welcome-row">
          <div>
            <p className="eyebrow">SMART RESUME SCREENER</p>
            <h1>Compare a resume with a role</h1>
            <p className="muted">See matching skills, gaps, and experience in a few seconds.</p>
          </div>
          <div className="welcome-icon"><Sparkles size={23} /></div>
        </section>
        <div className="workflow-label"><span>START A COMPARISON</span><span className="workflow-line" /></div>
        <div className="input-grid">
          <ResumeUpload file={file} onFileChange={setFile} />
          <JobDescriptionForm
            title={title}
            setTitle={setTitle}
            description={description}
            setDescription={setDescription}
          />
        </div>
        {error && <div className="alert-error" role="alert"><AlertCircle size={18} /><span>{error}</span></div>}
        <div className="analyze-row">
          <p>No account or credentials needed. Uploaded resumes are processed in memory.</p>
          <button className="primary-btn analyze-btn" onClick={handleAnalyze} disabled={loading}>
            {loading ? <><LoaderCircle className="spin" size={18} /> Analyzing...</> : <>Compare resume <ArrowRight size={18} /></>}
          </button>
        </div>
        {loading && <div className="loading-note">Extracting document text and comparing skills. This may take a few seconds.</div>}
        <MatchResults result={result} />
        <footer className="footer">Resume files are processed in memory and are not saved.</footer>
      </main>
    </div>
  );
}
