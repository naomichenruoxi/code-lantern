import React, { useRef, useState, useEffect } from "react";
import { uploadProjectZip } from "../services/api";
import { useNavigate } from "react-router-dom";
import GitHubConnect from "../components/GitHubConnect";
import { checkOAuthCallback, getGitHubSession } from "../services/github";
import ParticleBackground from "../components/ParticleBackground";
import TiltCard from "../components/TiltCard";
import TerminalLoader from "../components/TerminalLoader";
import TypewriterText from "../components/TypewriterText";
import CountUp from "../components/CountUp";

export default function UploadPage() {
  const fileInputRef = useRef(null);
  const [uploading, setUploading] = useState(false);
  const [activeTab, setActiveTab] = useState("upload");
  const [isDragging, setIsDragging] = useState(false);
  const navigate = useNavigate();

  // Check for OAuth callback or existing session on mount
  useEffect(() => {
    const { shouldSwitchToGitHubTab } = checkOAuthCallback();
    const existingSession = getGitHubSession();

    // Auto-switch to GitHub tab if returning from OAuth or have existing session
    if (shouldSwitchToGitHubTab || existingSession) {
      setActiveTab("github");
    }
  }, []);

  const handleFileSelect = async (event) => {
    const file = event.target.files?.[0];
    if (!file) return;
    await processFile(file);
  };

  const processFile = async (file) => {
    if (!file.name.endsWith(".zip")) {
      alert("Please upload a .zip file containing your source code.");
      return;
    }

    setUploading(true);
    try {
      // Simulate at least 2 seconds of loading for the effect
      const minLoadTime = new Promise(resolve => setTimeout(resolve, 2500));
      const uploadPromise = uploadProjectZip(file);

      const [result] = await Promise.all([uploadPromise, minLoadTime]);

      console.log('[Upload] Success:', result);
      navigate(`/project/${result.repo_id}`);
    } catch (error) {
      console.error('[Upload] Error:', error);
      alert(`Upload failed: ${error.message}`);
      setUploading(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragging(false);
    const file = e.dataTransfer.files?.[0];
    if (file) processFile(file);
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = () => setIsDragging(false);

  const handleGitHubAnalyze = (repoId) => {
    console.log('[GitHub] Repository cloned:', repoId);
    navigate(`/project/${repoId}`);
  };

  const features = [
    {
      icon: "🏗️",
      title: "Architecture Mapping",
      description: "Visualize your entire codebase structure with interactive tree diagrams and dependency graphs."
    },
    {
      icon: "📊",
      title: "Complexity Analysis",
      description: "Identify hotspots with cyclomatic complexity heatmaps and function-level metrics."
    },
    {
      icon: "🔗",
      title: "Dependency Tracking",
      description: "Understand file and function relationships with beautiful, interactive dependency graphs."
    },
    {
      icon: "🤖",
      title: "AI-Powered Insights",
      description: "Get intelligent summaries and documentation powered by advanced language models."
    },
    {
      icon: "⚡",
      title: "Deep Dive Analysis",
      description: "Explore any function in detail with source code, call graphs, and AI-generated explanations."
    },
    {
      icon: "🎨",
      title: "Visual Call Graphs",
      description: "Filter and explore function relationships with minimum complexity and connection filters."
    }
  ];

  const stats = [
    { value: "6+", label: "Languages Supported" },
    { value: "1000+", label: "Files Per Project" },
    { value: "<30s", label: "Avg Analysis Time" },
    { value: "100%", label: "Local & Private" }
  ];

  const steps = [
    {
      number: "01",
      title: <><span className="text-gradient">Upload</span> Your Code</>,
      description: "Drop a ZIP file or connect your GitHub repository"
    },
    {
      number: "02",
      title: <><span className="text-gradient">Automatic</span> Analysis</>,
      description: "AI scans functions, dependencies, and complexity metrics"
    },
    {
      number: "03",
      title: <><span className="text-gradient">Explore</span> Insights</>,
      description: "Navigate interactive visualizations and documentation"
    }
  ];

  return (
    <div className="min-h-screen bg-[var(--bg-primary)] bg-grid relative overflow-hidden">
      {/* Dynamic Particle Background */}
      <ParticleBackground />

      {/* Background gradient mesh overlay for color depth */}
      <div className="absolute inset-0 bg-gradient-mesh pointer-events-none opacity-40" />

      {/* Animated Floating Orbs */}
      <div className="absolute top-20 left-10 w-64 h-64 bg-[var(--accent-cyan)] opacity-20 rounded-full blur-[80px] animate-float pointer-events-none" />
      <div className="absolute bottom-40 right-10 w-96 h-96 bg-[var(--accent-blue)] opacity-20 rounded-full blur-[100px] animate-float pointer-events-none" style={{ animationDelay: '1s' }} />
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] bg-[var(--accent-purple)] opacity-10 rounded-full blur-[120px] animate-pulse-glow pointer-events-none" />

      {/* Hero Section */}
      <div className="relative z-10 px-8 pt-16 pb-12">
        <div className="max-w-7xl mx-auto">
          <div className="flex flex-col lg:flex-row items-center justify-between gap-16">
            {/* LEFT: Hero Text */}
            <div className="flex flex-col items-start animate-fade-in-up lg:max-w-xl">
              {/* Logo */}
              <h1 className="font-display text-5xl md:text-7xl lg:text-[5.5rem] font-extralight text-white leading-none tracking-tight">
                <span className="block">code</span>
                <span className="block text-glow">lantern<span className="text-[var(--accent-cyan)]">_</span></span>
              </h1>

              {/* Tagline */}
              <p className="mt-6 text-xl md:text-2xl font-display">
                <span className="text-gradient font-semibold">
                  <TypewriterText text="illuminate" delay={150} />
                </span>
                <span className="animate-pulse text-[var(--accent-cyan)]">_</span>
                {" "}
                <span className="text-white/90">your codebase</span>
              </p>

              {/* Beta Badge & Description */}
              <div className="mt-4 flex flex-col gap-3">
                <span className="inline-flex max-w-fit items-center gap-2 px-3 py-1 rounded-full text-xs font-medium bg-[var(--accent-blue)]/10 text-[var(--accent-blue)] border border-[var(--accent-blue)]/20">
                  <span className="relative flex h-2 w-2">
                    <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-[var(--accent-blue)] opacity-75"></span>
                    <span className="relative inline-flex rounded-full h-2 w-2 bg-[var(--accent-blue)]"></span>
                  </span>
                  Public Beta • Best for small to medium projects
                </span>

                <p className="text-[var(--text-secondary)] text-lg leading-relaxed max-w-lg">
                  Transform complex codebases into beautiful, interactive visualizations.
                  Currently optimized for repositories under 50MB with standard project structures.
                </p>

                <div className="flex gap-4 pt-4">
                  <button
                    onClick={() => navigate('/project/demo-project')}
                    className="px-6 py-2 rounded-full border border-[var(--accent-cyan)] text-[var(--accent-cyan)] hover:bg-[var(--accent-cyan)]/10 transition-colors text-sm font-medium"
                  >
                    🚀 Try Demo Project
                  </button>
                </div>
              </div>

              {/* Feature Pills */}
              <div className="mt-8 flex flex-wrap gap-3">
                {[
                  { icon: "🏗️", text: "Architecture Maps" },
                  { icon: "📊", text: "Dependency Graphs" },
                  { icon: "🤖", text: "AI Analysis" },
                ].map((feature, i) => (
                  <div
                    key={feature.text}
                    className="glass rounded-full px-4 py-2 flex items-center gap-2 animate-fade-in"
                    style={{ animationDelay: `${0.3 + i * 0.1}s` }}
                  >
                    <span>{feature.icon}</span>
                    <span className="text-sm text-white/80">{feature.text}</span>
                  </div>
                ))}
              </div>
            </div>

            {/* RIGHT: Upload Section (with 3D Tilt) */}
            <TiltCard
              className="w-full max-w-md animate-fade-in-up"
            >
              <div className="glass rounded-2xl p-8 card-glow h-full relative overflow-hidden">
                {uploading && <TerminalLoader />}

                {/* Tab Selector */}
                <div className="flex border-b border-[var(--border-default)] mb-6">
                  <button
                    onClick={() => setActiveTab("upload")}
                    className={`flex-1 pb-3 font-display text-sm transition-all ${activeTab === "upload"
                      ? "text-[var(--accent-cyan)] border-b-2 border-[var(--accent-cyan)]"
                      : "text-[var(--text-secondary)] hover:text-white"
                      }`}
                  >
                    📁 upload zip
                  </button>
                  <button
                    onClick={() => setActiveTab("github")}
                    className={`flex-1 pb-3 font-display text-sm transition-all ${activeTab === "github"
                      ? "text-[var(--accent-cyan)] border-b-2 border-[var(--accent-cyan)]"
                      : "text-[var(--text-secondary)] hover:text-white"
                      }`}
                  >
                    🔗 connect github
                  </button>
                </div>

                {/* Tab Content */}
                {activeTab === "upload" ? (
                  <div
                    onDrop={handleDrop}
                    onDragOver={handleDragOver}
                    onDragLeave={handleDragLeave}
                    className={`
                      relative group border-2 border-dashed rounded-xl p-8 text-center transition-all cursor-pointer overflow-hidden
                      ${isDragging
                        ? "border-[var(--accent-cyan)] bg-[var(--accent-cyan)]/10 scale-[1.02]"
                        : "border-[var(--border-default)] hover:border-[var(--accent-blue)] hover:bg-white/5"
                      }
                    `}
                    onClick={() => fileInputRef.current?.click()}
                  >
                    {/* Scanning Line Effect on Drag/Hover */}
                    <div className={`absolute inset-0 bg-gradient-to-b from-transparent via-[var(--accent-cyan)]/10 to-transparent w-full h-full -translate-y-full transition-transform duration-1000 ${isDragging || uploading ? 'translate-y-full duration-[2s] repeat-infinite' : 'group-hover:translate-y-full'}`} />

                    <input
                      type="file"
                      accept=".zip"
                      ref={fileInputRef}
                      onChange={handleFileSelect}
                      className="hidden"
                    />

                    <div className="mb-4 relative z-10 transition-transform group-hover:scale-110 duration-300">
                      <span className="text-5xl drop-shadow-lg">{uploading ? "⏳" : "📦"}</span>
                    </div>

                    <p className="font-display text-lg text-white mb-2 relative z-10">
                      {uploading ? "analyzing..." : <span className="group-hover:text-[var(--accent-cyan)] transition-colors">drop your project here</span>}
                    </p>

                    <p className="text-sm text-[var(--text-muted)] relative z-10">
                      or click to browse (.zip files)
                    </p>

                    {!uploading && (
                      <button className="btn-primary mt-6 w-full relative z-10 opacity-0 group-hover:opacity-100 transition-opacity translate-y-2 group-hover:translate-y-0">
                        Choose File
                      </button>
                    )}
                  </div>
                ) : (
                  <GitHubConnect onAnalyze={handleGitHubAnalyze} />
                )}
              </div>

              {/* Supported Languages */}
              {/* Supported Languages - Infinite Marquee */}
              <div className="mt-8 text-center overflow-hidden w-full max-w-2xl mx-auto mask-linear-fade relative">
                <p className="text-xs text-[var(--text-muted)] mb-4 uppercase tracking-widest font-semibold">Supported Languages</p>

                <div className="relative flex overflow-hidden group">
                  <div className="animate-marquee flex gap-4 items-center">
                    {/* Doubled list for seamless loop */}
                    {[...["Python", "JavaScript", "TypeScript", "Java", "C++", "Rust", "Go", "Ruby", "PHP", "Swift"],
                    ...["Python", "JavaScript", "TypeScript", "Java", "C++", "Rust", "Go", "Ruby", "PHP", "Swift"]].map((lang, idx) => (
                      <span
                        key={`${lang}-${idx}`}
                        className="px-4 py-2 text-sm font-display text-[var(--text-secondary)] bg-[var(--bg-elevated)] rounded-full border border-[var(--border-default)] whitespace-nowrap hover:border-[var(--accent-cyan)] hover:text-white transition-colors"
                      >
                        {lang}
                      </span>
                    ))}
                  </div>

                  {/* Fade masks for edges */}
                  <div className="absolute inset-y-0 left-0 w-12 bg-gradient-to-r from-[var(--bg-primary)] to-transparent z-10"></div>
                  <div className="absolute inset-y-0 right-0 w-12 bg-gradient-to-l from-[var(--bg-primary)] to-transparent z-10"></div>
                </div>
              </div>
            </TiltCard>
          </div>
        </div>
      </div>

      {/* Stats Section */}
      <div className="relative z-10 px-8 py-12 border-t border-[var(--border-default)]">
        <div className="max-w-5xl mx-auto">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-8">
            {stats.map((stat, i) => {
              const numeric = parseInt(stat.value.replace(/[^0-9]/g, '')) || 0;
              const suffix = stat.value.replace(/[0-9]/g, '');

              return (
                <div
                  key={stat.label}
                  className="text-center animate-fade-in"
                  style={{ animationDelay: `${0.1 * i}s` }}
                >
                  <div className="text-3xl md:text-4xl font-display font-bold text-gradient">
                    {stat.value.match(/\d/) ? (
                      <CountUp end={numeric} suffix={suffix} />
                    ) : (
                      stat.value
                    )}
                  </div>
                  <div className="mt-2 text-sm text-[var(--text-secondary)]">
                    {stat.label}
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </div>

      {/* How It Works Section */}
      <div className="relative z-10 px-8 py-16">
        <div className="max-w-5xl mx-auto">
          <h2 className="text-center font-display text-3xl md:text-4xl text-white mb-4">
            How It <span className="text-gradient">Works</span>
          </h2>
          <p className="text-center text-[var(--text-secondary)] mb-12 max-w-2xl mx-auto">
            Get insights into your codebase in three simple steps
          </p>

          <div className="grid md:grid-cols-3 gap-8">
            {steps.map((step, i) => (
              <div
                key={step.number}
                className="relative glass rounded-xl p-6 text-center animate-fade-in-up"
                style={{ animationDelay: `${0.15 * i}s` }}
              >
                {/* Step Number */}
                <div className="absolute -top-4 left-1/2 -translate-x-1/2 w-8 h-8 rounded-full bg-gradient-to-r from-[var(--accent-cyan)] to-[var(--accent-blue)] flex items-center justify-center text-sm font-bold text-white shadow-lg">
                  {step.number.slice(1)}
                </div>

                <h3 className="mt-4 font-display text-lg text-white font-medium">
                  {step.title}
                </h3>
                <p className="mt-2 text-sm text-[var(--text-secondary)]">
                  {step.description}
                </p>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Features Grid */}
      <div className="relative z-10 px-8 py-16 border-t border-[var(--border-default)]">
        <div className="max-w-6xl mx-auto">
          <h2 className="text-center font-display text-3xl md:text-4xl text-white mb-4">
            Powerful <span className="text-gradient">Features</span>
          </h2>
          <p className="text-center text-[var(--text-secondary)] mb-12 max-w-2xl mx-auto">
            Everything you need to understand and document your codebase
          </p>

          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {features.map((feature, i) => (
              <div
                key={feature.title}
                className="glass rounded-xl p-6 transition-all hover:border-[var(--accent-cyan)]/30 animate-fade-in-up group"
                style={{ animationDelay: `${0.1 * i}s` }}
              >
                <div className="text-3xl mb-4 group-hover:scale-110 transition-transform">
                  {feature.icon}
                </div>
                <h3 className="font-display text-lg text-white font-medium mb-2">
                  {feature.title}
                </h3>
                <p className="text-sm text-[var(--text-secondary)] leading-relaxed">
                  {feature.description}
                </p>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* CTA Section */}
      <div className="relative z-10 px-8 py-20">
        <div className="max-w-3xl mx-auto text-center">
          <div className="glass-accent rounded-2xl p-12">
            <h2 className="font-display text-3xl md:text-4xl text-white mb-4">
              Ready to <span className="text-gradient">illuminate</span> your code?
            </h2>
            <p className="text-[var(--text-secondary)] mb-8 max-w-xl mx-auto">
              Upload your project now and discover insights you never knew existed in your codebase.
            </p>
            <button
              onClick={() => window.scrollTo({ top: 0, behavior: 'smooth' })}
              className="btn-primary text-lg px-8 py-4"
            >
              Get Started — It's Free
            </button>
          </div>
        </div>
      </div>

      {/* Footer */}
      <div className="relative z-10 border-t border-[var(--border-default)] py-8">
        <div className="max-w-6xl mx-auto px-8">
          <div className="flex flex-col md:flex-row items-center justify-between gap-4">
            <div className="font-display text-lg text-white/80">
              code<span className="text-[var(--accent-cyan)]">lantern</span>_
            </div>
            <p className="text-sm text-[var(--text-muted)]">
              Built with ❤️ for developers who love clean code
            </p>
            <div className="flex items-center gap-6 text-sm text-[var(--text-secondary)]">
              <a
                href="https://github.com/Tjindl/code-lantern"
                target="_blank"
                rel="noreferrer"
                className="hover:text-white cursor-pointer transition-colors flex items-center gap-2"
              >
                <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 24 24"><path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z" /></svg>
                GitHub
              </a>
              <a
                href="mailto:tushar.bzp05@gmail.com"
                className="hover:text-white cursor-pointer transition-colors flex items-center gap-2"
              >
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"></path></svg>
                Collaborate
              </a>
            </div>
          </div>
        </div>
      </div>
    </div >
  );
}
