import json

with open("/working_dir/c_15be93eeb8dee532/ai_orbit_pipeline/data/processed/entities.json", "r") as f:
    entities_json_str = f.read()

with open("/working_dir/c_15be93eeb8dee532/ai_orbit_pipeline/data/processed/relationships.json", "r") as f:
    relationships_json_str = f.read()

with open("/working_dir/c_15be93eeb8dee532/ai_orbit_pipeline/data/processed/pipeline_summary.json", "r") as f:
    summary_json_str = f.read()

with open("/working_dir/c_15be93eeb8dee532/ai_orbit_pipeline/data/processed/graph_metrics.json", "r") as f:
    graph_metrics_json_str = f.read()

template = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>AI Orbit — Ecosystem Ingestion & Relationship Explorer</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet">
  <style>
    :root {
      --bg-primary: #0a0e17;
      --bg-secondary: #111827;
      --bg-card: rgba(17, 24, 39, 0.75);
      --bg-card-hover: rgba(31, 41, 55, 0.9);
      --border-color: rgba(255, 255, 255, 0.08);
      --border-focus: rgba(99, 102, 241, 0.5);
      --text-primary: #f8fafc;
      --text-secondary: #94a3b8;
      --text-muted: #64748b;
      --accent-primary: #6366f1;
      --accent-secondary: #8b5cf6;
      --accent-cyan: #06b6d4;
      --accent-emerald: #10b981;
      --accent-amber: #f59e0b;
      --accent-rose: #f43f5e;
      --gradient-brand: linear-gradient(135deg, #6366f1 0%, #a855f7 50%, #ec4899 100%);
      --gradient-card: linear-gradient(180deg, rgba(255, 255, 255, 0.04) 0%, rgba(255, 255, 255, 0.01) 100%);
      --shadow-sm: 0 2px 8px rgba(0, 0, 0, 0.25);
      --shadow-md: 0 8px 24px rgba(0, 0, 0, 0.35);
      --shadow-lg: 0 16px 40px rgba(0, 0, 0, 0.5);
      --radius-sm: 8px;
      --radius-md: 14px;
      --radius-lg: 20px;
      --font-main: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
      --font-mono: 'JetBrains Mono', monospace;
    }

    * {
      box-sizing: border-box;
      margin: 0;
      padding: 0;
    }

    body {
      background-color: var(--bg-primary);
      color: var(--text-primary);
      font-family: var(--font-main);
      line-height: 1.5;
      min-height: 100vh;
      overflow-x: hidden;
      background-image: 
        radial-gradient(circle at 15% 15%, rgba(99, 102, 241, 0.12) 0%, transparent 40%),
        radial-gradient(circle at 85% 25%, rgba(236, 72, 153, 0.08) 0%, transparent 40%),
        radial-gradient(circle at 50% 85%, rgba(6, 182, 212, 0.08) 0%, transparent 50%);
      background-attachment: fixed;
    }

    header {
      position: sticky;
      top: 0;
      z-index: 50;
      backdrop-filter: blur(16px);
      background: rgba(10, 14, 23, 0.85);
      border-bottom: 1px solid var(--border-color);
      padding: 1rem 2rem;
    }

    .header-container {
      max-width: 1440px;
      margin: 0 auto;
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 1.5rem;
    }

    .logo-group {
      display: flex;
      align-items: center;
      gap: 0.85rem;
      text-decoration: none;
      color: var(--text-primary);
    }

    .logo-icon {
      width: 40px;
      height: 40px;
      border-radius: 10px;
      background: var(--gradient-brand);
      display: flex;
      align-items: center;
      justify-content: center;
      font-weight: 800;
      font-size: 1.25rem;
      color: white;
      box-shadow: 0 0 20px rgba(99, 102, 241, 0.4);
    }

    .logo-title {
      font-size: 1.35rem;
      font-weight: 800;
      letter-spacing: -0.03em;
      background: linear-gradient(180deg, #ffffff 0%, #cbd5e1 100%);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
    }

    .logo-badge {
      font-size: 0.7rem;
      font-weight: 700;
      text-transform: uppercase;
      padding: 0.2rem 0.5rem;
      border-radius: 6px;
      background: rgba(99, 102, 241, 0.15);
      color: #818cf8;
      border: 1px solid rgba(99, 102, 241, 0.3);
      margin-left: 0.5rem;
    }

    .nav-tabs {
      display: flex;
      background: rgba(255, 255, 255, 0.04);
      padding: 0.25rem;
      border-radius: 12px;
      border: 1px solid var(--border-color);
    }

    .nav-tab {
      padding: 0.55rem 1.15rem;
      border-radius: 8px;
      border: none;
      background: transparent;
      color: var(--text-secondary);
      font-family: var(--font-main);
      font-size: 0.88rem;
      font-weight: 600;
      cursor: pointer;
      transition: all 0.2s ease;
      display: flex;
      align-items: center;
      gap: 0.5rem;
    }

    .nav-tab:hover {
      color: var(--text-primary);
      background: rgba(255, 255, 255, 0.05);
    }

    .nav-tab.active {
      background: var(--accent-primary);
      color: white;
      box-shadow: 0 4px 12px rgba(99, 102, 241, 0.35);
    }

    .hero-section {
      max-width: 1440px;
      margin: 2rem auto 1.5rem;
      padding: 0 2rem;
    }

    .hero-title-area {
      text-align: center;
      margin-bottom: 2rem;
    }

    .hero-headline {
      font-size: 2.75rem;
      font-weight: 800;
      letter-spacing: -0.04em;
      margin-bottom: 0.75rem;
      line-height: 1.15;
    }

    .gradient-text {
      background: var(--gradient-brand);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
    }

    .hero-sub {
      color: var(--text-secondary);
      font-size: 1.1rem;
      max-width: 760px;
      margin: 0 auto;
    }

    .stats-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
      gap: 1.25rem;
      margin-bottom: 2rem;
    }

    .stat-card {
      background: var(--bg-card);
      border: 1px solid var(--border-color);
      border-radius: var(--radius-md);
      padding: 1.25rem 1.5rem;
      backdrop-filter: blur(12px);
      box-shadow: var(--shadow-sm);
      display: flex;
      flex-direction: column;
      position: relative;
      overflow: hidden;
      transition: transform 0.2s ease, border-color 0.2s ease;
    }

    .stat-card:hover {
      transform: translateY(-2px);
      border-color: rgba(99, 102, 241, 0.4);
    }

    .stat-card::before {
      content: '';
      position: absolute;
      top: 0;
      left: 0;
      width: 100%;
      height: 3px;
      background: var(--gradient-brand);
      opacity: 0.8;
    }

    .stat-label {
      font-size: 0.8rem;
      font-weight: 600;
      color: var(--text-muted);
      text-transform: uppercase;
      letter-spacing: 0.05em;
      margin-bottom: 0.35rem;
    }

    .stat-value {
      font-size: 1.85rem;
      font-weight: 800;
      color: var(--text-primary);
      letter-spacing: -0.02em;
    }

    .stat-meta {
      font-size: 0.78rem;
      color: var(--accent-emerald);
      margin-top: 0.25rem;
      display: flex;
      align-items: center;
      gap: 0.35rem;
    }

    .controls-container {
      max-width: 1440px;
      margin: 0 auto 1.5rem;
      padding: 0 2rem;
      display: flex;
      flex-direction: column;
      gap: 1rem;
    }

    .search-box-row {
      display: flex;
      gap: 1rem;
      align-items: center;
    }

    .search-input-wrapper {
      position: relative;
      flex: 1;
    }

    .search-input {
      width: 100%;
      background: rgba(17, 24, 39, 0.8);
      border: 1px solid var(--border-color);
      border-radius: var(--radius-sm);
      padding: 0.85rem 1.25rem 0.85rem 2.85rem;
      color: var(--text-primary);
      font-family: var(--font-main);
      font-size: 0.95rem;
      transition: all 0.2s ease;
      outline: none;
    }

    .search-input:focus {
      border-color: var(--accent-primary);
      box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.2);
      background: rgba(17, 24, 39, 1);
    }

    .search-icon {
      position: absolute;
      left: 1rem;
      top: 50%;
      transform: translateY(-50%);
      color: var(--text-muted);
      pointer-events: none;
    }

    .category-pills {
      display: flex;
      flex-wrap: wrap;
      gap: 0.5rem;
      padding-bottom: 0.5rem;
    }

    .pill {
      padding: 0.45rem 0.95rem;
      border-radius: 20px;
      font-size: 0.82rem;
      font-weight: 600;
      border: 1px solid var(--border-color);
      background: rgba(255, 255, 255, 0.03);
      color: var(--text-secondary);
      cursor: pointer;
      transition: all 0.2s ease;
      display: flex;
      align-items: center;
      gap: 0.4rem;
    }

    .pill:hover {
      background: rgba(255, 255, 255, 0.08);
      color: var(--text-primary);
    }

    .pill.active {
      background: rgba(99, 102, 241, 0.2);
      border-color: var(--accent-primary);
      color: #a5b4fc;
      box-shadow: 0 2px 8px rgba(99, 102, 241, 0.2);
    }

    .pill-count {
      background: rgba(255, 255, 255, 0.1);
      padding: 0.1rem 0.45rem;
      border-radius: 10px;
      font-size: 0.72rem;
    }

    main {
      max-width: 1440px;
      margin: 0 auto 4rem;
      padding: 0 2rem;
    }

    .view-panel {
      display: none;
    }

    .view-panel.active {
      display: block;
    }

    .entity-grid {
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
      gap: 1.5rem;
    }

    .entity-card {
      background: var(--bg-card);
      border: 1px solid var(--border-color);
      border-radius: var(--radius-md);
      padding: 1.5rem;
      backdrop-filter: blur(12px);
      box-shadow: var(--shadow-sm);
      display: flex;
      flex-direction: column;
      justify-content: space-between;
      transition: all 0.2s ease;
      cursor: pointer;
      position: relative;
    }

    .entity-card:hover {
      transform: translateY(-3px);
      border-color: rgba(99, 102, 241, 0.4);
      box-shadow: var(--shadow-md);
      background: var(--bg-card-hover);
    }

    .card-top {
      display: flex;
      justify-content: space-between;
      align-items: flex-start;
      margin-bottom: 0.85rem;
      gap: 0.75rem;
    }

    .entity-name {
      font-size: 1.2rem;
      font-weight: 700;
      color: var(--text-primary);
      line-height: 1.3;
    }

    .type-badge {
      font-size: 0.72rem;
      font-weight: 700;
      text-transform: uppercase;
      padding: 0.25rem 0.6rem;
      border-radius: 6px;
      letter-spacing: 0.04em;
      white-space: nowrap;
    }

    .badge-Model { background: rgba(99, 102, 241, 0.18); color: #818cf8; border: 1px solid rgba(99, 102, 241, 0.3); }
    .badge-Tool { background: rgba(6, 182, 212, 0.18); color: #22d3ee; border: 1px solid rgba(6, 182, 212, 0.3); }
    .badge-Company { background: rgba(16, 185, 129, 0.18); color: #34d399; border: 1px solid rgba(16, 185, 129, 0.3); }
    .badge-Robot { background: rgba(245, 158, 11, 0.18); color: #fbbf24; border: 1px solid rgba(245, 158, 11, 0.3); }
    .badge-Device { background: rgba(236, 72, 153, 0.18); color: #f472b6; border: 1px solid rgba(236, 72, 153, 0.3); }
    .badge-MCP { background: rgba(168, 85, 247, 0.18); color: #c084fc; border: 1px solid rgba(168, 85, 247, 0.3); }
    .badge-Repository { background: rgba(148, 163, 184, 0.18); color: #cbd5e1; border: 1px solid rgba(148, 163, 184, 0.3); }
    .badge-Task { background: rgba(59, 130, 246, 0.18); color: #60a5fa; border: 1px solid rgba(59, 130, 246, 0.3); }
    .badge-News { background: rgba(239, 68, 68, 0.18); color: #f87171; border: 1px solid rgba(239, 68, 68, 0.3); }
    .badge-Video { background: rgba(244, 63, 94, 0.18); color: #fb7185; border: 1px solid rgba(244, 63, 94, 0.3); }
    .badge-Creative { background: rgba(217, 70, 239, 0.18); color: #e879f9; border: 1px solid rgba(217, 70, 239, 0.3); }
    .badge-Personal { background: rgba(20, 184, 166, 0.18); color: #2dd4bf; border: 1px solid rgba(20, 184, 166, 0.3); }
    .badge-Collection { background: rgba(234, 179, 8, 0.18); color: #facc15; border: 1px solid rgba(234, 179, 8, 0.3); }

    .entity-desc {
      font-size: 0.88rem;
      color: var(--text-secondary);
      margin-bottom: 1rem;
      line-height: 1.5;
      display: -webkit-box;
      -webkit-line-clamp: 3;
      -webkit-box-orient: vertical;
      overflow: hidden;
    }

    .entity-tags {
      display: flex;
      flex-wrap: wrap;
      gap: 0.35rem;
      margin-bottom: 1.25rem;
    }

    .tag {
      font-size: 0.72rem;
      background: rgba(255, 255, 255, 0.05);
      color: var(--text-muted);
      padding: 0.2rem 0.5rem;
      border-radius: 4px;
    }

    .card-footer {
      display: flex;
      justify-content: space-between;
      align-items: center;
      border-top: 1px solid rgba(255, 255, 255, 0.05);
      padding-top: 0.85rem;
      font-size: 0.8rem;
    }

    .source-link {
      color: var(--text-muted);
      text-decoration: none;
      display: flex;
      align-items: center;
      gap: 0.35rem;
      transition: color 0.2s ease;
    }

    .source-link:hover {
      color: var(--accent-cyan);
    }

    .view-rel-btn {
      background: transparent;
      border: 1px solid rgba(99, 102, 241, 0.3);
      color: #a5b4fc;
      padding: 0.35rem 0.75rem;
      border-radius: 6px;
      font-size: 0.78rem;
      font-weight: 600;
      cursor: pointer;
      transition: all 0.2s ease;
    }

    .view-rel-btn:hover {
      background: var(--accent-primary);
      color: white;
    }

    .graph-panel {
      background: var(--bg-card);
      border: 1px solid var(--border-color);
      border-radius: var(--radius-lg);
      padding: 1.5rem;
      box-shadow: var(--shadow-md);
    }

    .graph-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 1rem;
    }

    .graph-instructions {
      font-size: 0.85rem;
      color: var(--text-secondary);
    }

    #graphCanvas {
      width: 100%;
      height: 620px;
      background: #080c14;
      border-radius: var(--radius-md);
      border: 1px solid rgba(255, 255, 255, 0.05);
      cursor: grab;
    }

    #graphCanvas:active {
      cursor: grabbing;
    }

    .graph-legend {
      display: flex;
      flex-wrap: wrap;
      gap: 1rem;
      margin-top: 1rem;
      padding: 0.75rem;
      background: rgba(0, 0, 0, 0.2);
      border-radius: var(--radius-sm);
    }

    .legend-item {
      display: flex;
      align-items: center;
      gap: 0.4rem;
      font-size: 0.78rem;
      color: var(--text-secondary);
    }

    .legend-color {
      width: 10px;
      height: 10px;
      border-radius: 50%;
    }

    .modal-overlay {
      position: fixed;
      inset: 0;
      background: rgba(0, 0, 0, 0.8);
      backdrop-filter: blur(8px);
      z-index: 100;
      display: none;
      align-items: center;
      justify-content: center;
      padding: 1.5rem;
    }

    .modal-overlay.open {
      display: flex;
    }

    .modal-card {
      background: #0f172a;
      border: 1px solid rgba(255, 255, 255, 0.12);
      border-radius: var(--radius-lg);
      max-width: 800px;
      width: 100%;
      max-height: 85vh;
      overflow-y: auto;
      box-shadow: var(--shadow-lg);
      padding: 2rem;
      position: relative;
    }

    .modal-close {
      position: absolute;
      top: 1.5rem;
      right: 1.5rem;
      background: rgba(255, 255, 255, 0.08);
      border: none;
      color: var(--text-secondary);
      width: 32px;
      height: 32px;
      border-radius: 50%;
      cursor: pointer;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 1.2rem;
      transition: all 0.2s ease;
    }

    .modal-close:hover {
      background: rgba(255, 255, 255, 0.15);
      color: white;
    }

    .modal-section-title {
      font-size: 0.85rem;
      text-transform: uppercase;
      letter-spacing: 0.05em;
      color: var(--text-muted);
      font-weight: 700;
      margin: 1.5rem 0 0.75rem;
      border-bottom: 1px solid rgba(255, 255, 255, 0.06);
      padding-bottom: 0.4rem;
    }

    .rel-list {
      display: flex;
      flex-direction: column;
      gap: 0.6rem;
    }

    .rel-item {
      background: rgba(255, 255, 255, 0.03);
      border: 1px solid rgba(255, 255, 255, 0.06);
      border-radius: var(--radius-sm);
      padding: 0.75rem 1rem;
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 1rem;
      font-size: 0.85rem;
    }

    .rel-pred {
      font-family: var(--font-mono);
      font-size: 0.75rem;
      font-weight: 600;
      padding: 0.2rem 0.5rem;
      border-radius: 4px;
      background: rgba(99, 102, 241, 0.2);
      color: #a5b4fc;
    }

    .meta-table {
      width: 100%;
      border-collapse: collapse;
      font-size: 0.85rem;
    }

    .meta-table td {
      padding: 0.5rem 0;
      border-bottom: 1px solid rgba(255, 255, 255, 0.04);
    }

    .meta-key {
      color: var(--text-muted);
      width: 35%;
      font-weight: 600;
    }

    .meta-val {
      color: var(--text-primary);
      font-family: var(--font-mono);
      word-break: break-all;
    }

    .analytics-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
      gap: 1.5rem;
    }

    .chart-box {
      background: var(--bg-card);
      border: 1px solid var(--border-color);
      border-radius: var(--radius-md);
      padding: 1.5rem;
    }

    .bar-row {
      display: flex;
      align-items: center;
      gap: 1rem;
      margin-bottom: 0.75rem;
      font-size: 0.85rem;
    }

    .bar-label {
      width: 160px;
      color: var(--text-secondary);
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }

    .bar-track {
      flex: 1;
      height: 8px;
      background: rgba(255, 255, 255, 0.05);
      border-radius: 4px;
      overflow: hidden;
    }

    .bar-fill {
      height: 100%;
      border-radius: 4px;
      background: var(--accent-primary);
      transition: width 0.5s ease;
    }

    .bar-num {
      width: 35px;
      text-align: right;
      font-weight: 700;
      font-family: var(--font-mono);
    }

    footer {
      border-top: 1px solid var(--border-color);
      padding: 2.5rem 2rem;
      text-align: center;
      color: var(--text-muted);
      font-size: 0.85rem;
    }

    .footer-links {
      display: flex;
      justify-content: center;
      gap: 1.5rem;
      margin-top: 0.75rem;
    }

    .footer-links a {
      color: var(--text-secondary);
      text-decoration: none;
    }

    .footer-links a:hover {
      color: var(--accent-primary);
    }
  </style>
</head>
<body>

  <header>
    <div class="header-container">
      <a href="#" class="logo-group">
        <div class="logo-icon">🪐</div>
        <div>
          <span class="logo-title">AI Orbit</span>
          <span class="logo-badge">Ecosystem Pipeline</span>
        </div>
      </a>

      <nav class="nav-tabs">
        <button class="nav-tab active" onclick="switchTab('directory')">📂 Directory</button>
        <button class="nav-tab" onclick="switchTab('graph')">🕸️ Graph Explorer</button>
        <button class="nav-tab" onclick="switchTab('recent')">⚡ Recently Added</button>
        <button class="nav-tab" onclick="switchTab('analytics')">📊 Analytics</button>
      </nav>
    </div>
  </header>

  <section class="hero-section">
    <div class="hero-title-area">
      <h1 class="hero-headline">The Global <span class="gradient-text">AI Ecosystem</span> Ingestion Engine</h1>
      <p class="hero-sub">Production-grade pipeline aggregating, deduplicating, and mapping relationships across models, tools, robots, devices, companies, and MCP servers.</p>
    </div>

    <div class="stats-grid">
      <div class="stat-card">
        <span class="stat-label">Total Canonical Entities</span>
        <span class="stat-value" id="statEntities">269</span>
        <span class="stat-meta">✓ Target 250-300 records met</span>
      </div>
      <div class="stat-card">
        <span class="stat-label">Graph Relationships</span>
        <span class="stat-value" id="statRelations">324</span>
        <span class="stat-meta">✓ 1.20 edges / entity density</span>
      </div>
      <div class="stat-card">
        <span class="stat-label">Ecosystem Domains</span>
        <span class="stat-value">14</span>
        <span class="stat-meta">✓ Complete domain coverage</span>
      </div>
      <div class="stat-card">
        <span class="stat-label">Data Quality Score</span>
        <span class="stat-value" style="color: var(--accent-emerald);">100.0%</span>
        <span class="stat-meta">✓ 0 schema or referential errors</span>
      </div>
    </div>
  </section>

  <div class="controls-container" id="controlsSection">
    <div class="search-box-row">
      <div class="search-input-wrapper">
        <span class="search-icon">🔍</span>
        <input type="text" id="searchInput" class="search-input" placeholder="Search entities by name, description, tags, provider, or architecture..." oninput="handleSearch()">
      </div>
    </div>

    <div class="category-pills" id="categoryPills"></div>
  </div>

  <main>
    <div id="panelDirectory" class="view-panel active">
      <div class="entity-grid" id="entityGrid"></div>
    </div>

    <div id="panelGraph" class="view-panel">
      <div class="graph-panel">
        <div class="graph-header">
          <div>
            <h2 style="font-size: 1.3rem; font-weight: 700; margin-bottom: 0.25rem;">Interactive Ecosystem Network Graph</h2>
            <p class="graph-instructions">Click and drag nodes. Hover to inspect entity relationships across Companies, Models, Tools, Tasks, and Devices.</p>
          </div>
          <button class="view-rel-btn" onclick="resetGraphView()">Reset View</button>
        </div>
        <canvas id="graphCanvas"></canvas>
        <div class="graph-legend">
          <div class="legend-item"><span class="legend-color" style="background: #818cf8;"></span> Model</div>
          <div class="legend-item"><span class="legend-color" style="background: #22d3ee;"></span> Tool</div>
          <div class="legend-item"><span class="legend-color" style="background: #34d399;"></span> Company</div>
          <div class="legend-item"><span class="legend-color" style="background: #fbbf24;"></span> Robot</div>
          <div class="legend-item"><span class="legend-color" style="background: #f472b6;"></span> Device</div>
          <div class="legend-item"><span class="legend-color" style="background: #c084fc;"></span> MCP</div>
          <div class="legend-item"><span class="legend-color" style="background: #60a5fa;"></span> Task</div>
        </div>
      </div>
    </div>

    <div id="panelRecent" class="view-panel">
      <h2 style="font-size: 1.4rem; font-weight: 700; margin-bottom: 1.25rem;">⚡ Cutting-Edge Ingested Additions</h2>
      <div class="entity-grid" id="recentGrid"></div>
    </div>

    <div id="panelAnalytics" class="view-panel">
      <div class="analytics-grid">
        <div class="chart-box">
          <h3 style="font-size: 1.1rem; font-weight: 700; margin-bottom: 1.25rem;">Entities by Domain Category</h3>
          <div id="categoryBarChart"></div>
        </div>
        <div class="chart-box">
          <h3 style="font-size: 1.1rem; font-weight: 700; margin-bottom: 1.25rem;">Top Relationship Predicates</h3>
          <div id="relationBarChart"></div>
        </div>
        <div class="chart-box" style="grid-column: 1 / -1;">
          <h3 style="font-size: 1.1rem; font-weight: 700; margin-bottom: 1.25rem;">Top Connected Ecosystem Hubs</h3>
          <div id="hubsTable"></div>
        </div>
      </div>
    </div>
  </main>

  <div class="modal-overlay" id="detailModal" onclick="closeModal(event)">
    <div class="modal-card" onclick="event.stopPropagation()">
      <button class="modal-close" onclick="closeModalDirect()">&times;</button>
      <div id="modalContent"></div>
    </div>
  </div>

  <footer>
    <div>AI Orbit Ecosystem Data Ingestion Pipeline & Graph Engine</div>
    <div class="footer-links">
      <a href="https://github.com" target="_blank">GitHub</a>
      <a href="https://huggingface.co" target="_blank">Hugging Face</a>
      <a href="https://modelcontextprotocol.io" target="_blank">Model Context Protocol</a>
      <a href="https://openai.com" target="_blank">OpenAI</a>
      <a href="https://anthropic.com" target="_blank">Anthropic</a>
    </div>
  </footer>

  <script>
    const ENTITIES_DATA = __ENTITIES__;
    const RELATIONSHIPS_DATA = __RELATIONSHIPS__;
    const SUMMARY_DATA = __SUMMARY__;
    const GRAPH_METRICS = __METRICS__;

    let selectedCategory = "ALL";
    let searchQuery = "";

    const entityById = new Map();
    ENTITIES_DATA.forEach(e => entityById.set(e.id, e));

    const outgoingRels = new Map();
    const incomingRels = new Map();
    RELATIONSHIPS_DATA.forEach(r => {
      if (!outgoingRels.has(r.source_id)) outgoingRels.set(r.source_id, []);
      outgoingRels.get(r.source_id).push(r);

      if (!incomingRels.has(r.target_id)) incomingRels.set(r.target_id, []);
      incomingRels.get(r.target_id).push(r);
    });

    function initCategoryPills() {
      const catCounts = {};
      ENTITIES_DATA.forEach(e => {
        catCounts[e.entity_type] = (catCounts[e.entity_type] || 0) + 1;
      });

      const container = document.getElementById('categoryPills');
      container.innerHTML = `
        <button class="pill active" onclick="setCategory('ALL', this)">
          All <span class="pill-count">${ENTITIES_DATA.length}</span>
        </button>
      `;

      Object.keys(catCounts).sort().forEach(cat => {
        const btn = document.createElement('button');
        btn.className = 'pill';
        btn.innerHTML = `${cat} <span class="pill-count">${catCounts[cat]}</span>`;
        btn.onclick = () => setCategory(cat, btn);
        container.appendChild(btn);
      });
    }

    function setCategory(cat, element) {
      selectedCategory = cat;
      document.querySelectorAll('.category-pills .pill').forEach(p => p.classList.remove('active'));
      if (element) element.classList.add('active');
      renderEntityGrid();
    }

    function handleSearch() {
      searchQuery = document.getElementById('searchInput').value.trim().toLowerCase();
      renderEntityGrid();
    }

    function renderEntityGrid() {
      const grid = document.getElementById('entityGrid');
      const filtered = ENTITIES_DATA.filter(e => {
        const matchesCat = (selectedCategory === "ALL" || e.entity_type === selectedCategory);
        if (!matchesCat) return false;
        if (!searchQuery) return true;

        const textCorpus = `${e.name} ${e.description} ${e.categories.join(' ')} ${e.source.name} ${JSON.stringify(e.metadata || {})}`.toLowerCase();
        return textCorpus.includes(searchQuery);
      });

      if (filtered.length === 0) {
        grid.innerHTML = `<div style="grid-column: 1/-1; text-align: center; padding: 4rem; color: var(--text-muted);">
          <h3>No matching entities found</h3>
          <p>Try adjusting your search keywords or category filters.</p>
        </div>`;
        return;
      }

      grid.innerHTML = filtered.map(e => `
        <div class="entity-card" onclick="openDetailsModal('${e.id}')">
          <div>
            <div class="card-top">
              <h3 class="entity-name">${e.name}</h3>
              <span class="type-badge badge-${e.entity_type}">${e.entity_type}</span>
            </div>
            <p class="entity-desc">${e.description}</p>
            <div class="entity-tags">
              ${e.categories.slice(0, 3).map(c => `<span class="tag">${c}</span>`).join('')}
            </div>
          </div>
          <div class="card-footer">
            <a href="${e.url}" target="_blank" class="source-link" onclick="event.stopPropagation()">
              🔗 ${e.source.name}
            </a>
            <button class="view-rel-btn">Explore Graph &rarr;</button>
          </div>
        </div>
      `).join('');
    }

    function renderRecentGrid() {
      const grid = document.getElementById('recentGrid');
      const recent = ENTITIES_DATA.slice(0, 24);
      grid.innerHTML = recent.map(e => `
        <div class="entity-card" onclick="openDetailsModal('${e.id}')">
          <div>
            <div class="card-top">
              <h3 class="entity-name">${e.name}</h3>
              <span class="type-badge badge-${e.entity_type}">${e.entity_type}</span>
            </div>
            <p class="entity-desc">${e.description}</p>
            <div class="entity-tags">
              ${e.categories.slice(0, 3).map(c => `<span class="tag">${c}</span>`).join('')}
            </div>
          </div>
          <div class="card-footer">
            <span style="color: var(--accent-cyan); font-weight: 600; font-size: 0.75rem;">⚡ Ingested</span>
            <button class="view-rel-btn">Details</button>
          </div>
        </div>
      `).join('');
    }

    function openDetailsModal(entityId) {
      const entity = entityById.get(entityId);
      if (!entity) return;

      const out = outgoingRels.get(entityId) || [];
      const inc = incomingRels.get(entityId) || [];

      const content = document.getElementById('modalContent');
      content.innerHTML = `
        <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 1rem;">
          <div>
            <span class="type-badge badge-${entity.entity_type}" style="margin-bottom: 0.5rem; display: inline-block;">${entity.entity_type}</span>
            <h2 style="font-size: 1.8rem; font-weight: 800;">${entity.name}</h2>
          </div>
        </div>

        <p style="color: var(--text-secondary); font-size: 1rem; line-height: 1.6; margin-bottom: 1.5rem;">${entity.description}</p>

        <div style="display: flex; gap: 1rem; margin-bottom: 1.5rem; flex-wrap: wrap;">
          <a href="${entity.url}" target="_blank" style="color: var(--accent-cyan); text-decoration: none; font-size: 0.9rem; font-weight: 600;">
            🔗 Official URL: ${entity.url}
          </a>
        </div>

        <div class="modal-section-title">Ecosystem Relationships (${out.length + inc.length} Connections)</div>
        <div class="rel-list">
          ${out.map(r => `
            <div class="rel-item">
              <div>
                <strong>${entity.name}</strong>
                <span class="rel-pred">${r.relationship_type}</span>
                <span style="color: var(--accent-cyan); cursor: pointer; text-decoration: underline;" onclick="openDetailsModal('${r.target_id}')">
                  ${r.target_name} (${r.target_type})
                </span>
              </div>
              <span style="color: var(--text-muted); font-size: 0.78rem;">${r.description}</span>
            </div>
          `).join('')}
          ${inc.map(r => `
            <div class="rel-item">
              <div>
                <span style="color: var(--accent-cyan); cursor: pointer; text-decoration: underline;" onclick="openDetailsModal('${r.source_id}')">
                  ${r.source_name} (${r.source_type})
                </span>
                <span class="rel-pred">${r.relationship_type}</span>
                <strong>${entity.name}</strong>
              </div>
              <span style="color: var(--text-muted); font-size: 0.78rem;">${r.description}</span>
            </div>
          `).join('')}
          ${out.length === 0 && inc.length === 0 ? '<p style="color: var(--text-muted); font-size: 0.85rem;">No direct edges mapped.</p>' : ''}
        </div>

        <div class="modal-section-title">Entity Metadata & Identification</div>
        <table class="meta-table">
          <tr><td class="meta-key">Entity ID (UUIDv5)</td><td class="meta-val">${entity.id}</td></tr>
          <tr><td class="meta-key">Source Provider</td><td class="meta-val">${entity.source.name} (${entity.source.url})</td></tr>
          <tr><td class="meta-key">Taxonomy Categories</td><td class="meta-val">${entity.categories.join(', ')}</td></tr>
          ${Object.entries(entity.metadata || {}).map(([k, v]) => `
            <tr><td class="meta-key">${k}</td><td class="meta-val">${typeof v === 'object' ? JSON.stringify(v) : v}</td></tr>
          `).join('')}
        </table>
      `;

      document.getElementById('detailModal').classList.add('open');
    }

    function closeModal(e) {
      if (e.target.id === 'detailModal') {
        document.getElementById('detailModal').classList.remove('open');
      }
    }

    function closeModalDirect() {
      document.getElementById('detailModal').classList.remove('open');
    }

    function switchTab(tabId) {
      document.querySelectorAll('.nav-tab').forEach(t => t.classList.remove('active'));
      document.querySelectorAll('.view-panel').forEach(p => p.classList.remove('active'));

      const controls = document.getElementById('controlsSection');

      if (tabId === 'directory') {
        document.querySelector('.nav-tab:nth-child(1)').classList.add('active');
        document.getElementById('panelDirectory').classList.add('active');
        controls.style.display = 'flex';
      } else if (tabId === 'graph') {
        document.querySelector('.nav-tab:nth-child(2)').classList.add('active');
        document.getElementById('panelGraph').classList.add('active');
        controls.style.display = 'none';
        initGraphSimulation();
      } else if (tabId === 'recent') {
        document.querySelector('.nav-tab:nth-child(3)').classList.add('active');
        document.getElementById('panelRecent').classList.add('active');
        controls.style.display = 'none';
        renderRecentGrid();
      } else if (tabId === 'analytics') {
        document.querySelector('.nav-tab:nth-child(4)').classList.add('active');
        document.getElementById('panelAnalytics').classList.add('active');
        controls.style.display = 'none';
        renderAnalytics();
      }
    }

    function renderAnalytics() {
      const catChart = document.getElementById('categoryBarChart');
      const counts = SUMMARY_DATA.entities_by_category || {};
      const maxCount = Math.max(...Object.values(counts));

      catChart.innerHTML = Object.entries(counts).map(([cat, count]) => `
        <div class="bar-row">
          <span class="bar-label">${cat}</span>
          <div class="bar-track"><div class="bar-fill" style="width: ${(count/maxCount)*100}%;"></div></div>
          <span class="bar-num">${count}</span>
        </div>
      `).join('');

      const relChart = document.getElementById('relationBarChart');
      const relCounts = SUMMARY_DATA.relationships_by_type || {};
      const maxRel = Math.max(...Object.values(relCounts));

      relChart.innerHTML = Object.entries(relCounts).filter(([_, c]) => c > 0).map(([pred, count]) => `
        <div class="bar-row">
          <span class="bar-label">${pred}</span>
          <div class="bar-track"><div class="bar-fill" style="width: ${(count/maxRel)*100}%; background: var(--accent-secondary);"></div></div>
          <span class="bar-num">${count}</span>
        </div>
      `).join('');

      const hubsTable = document.getElementById('hubsTable');
      const hubs = GRAPH_METRICS.top_connected_hubs || [];
      hubsTable.innerHTML = `
        <table class="meta-table">
          <thead>
            <tr style="color: var(--text-muted); font-size: 0.75rem; text-transform: uppercase;">
              <th style="text-align: left; padding: 0.5rem 0;">Entity Hub</th>
              <th style="text-align: left;">Domain Type</th>
              <th style="text-align: right;">In-Degree</th>
              <th style="text-align: right;">Out-Degree</th>
              <th style="text-align: right;">Total Degree</th>
            </tr>
          </thead>
          <tbody>
            ${hubs.map(h => `
              <tr>
                <td style="font-weight: 700; color: var(--text-primary); padding: 0.6rem 0;">${h.name}</td>
                <td><span class="type-badge badge-${h.type}">${h.type}</span></td>
                <td style="text-align: right; font-family: var(--font-mono);">${h.in_degree}</td>
                <td style="text-align: right; font-family: var(--font-mono);">${h.out_degree}</td>
                <td style="text-align: right; font-family: var(--font-mono); font-weight: 700; color: var(--accent-cyan);">${h.total_degree}</td>
              </tr>
            `).join('')}
          </tbody>
        </table>
      `;
    }

    let canvas, ctx, nodes = [], links = [], animId;
    let isDragging = false, dragNode = null;

    const typeColors = {
      Model: "#818cf8", Tool: "#22d3ee", Company: "#34d399", Robot: "#fbbf24",
      Device: "#f472b6", MCP: "#c084fc", Repository: "#cbd5e1", Task: "#60a5fa",
      News: "#f87171", Video: "#fb7185", Creative: "#e879f9", Personal: "#2dd4bf", Collection: "#facc15"
    };

    function initGraphSimulation() {
      canvas = document.getElementById('graphCanvas');
      ctx = canvas.getContext('2d');
      canvas.width = canvas.parentElement.clientWidth;
      canvas.height = 620;

      const topEntities = ENTITIES_DATA.slice(0, 75);
      const topIds = new Set(topEntities.map(e => e.id));

      nodes = topEntities.map((e, idx) => ({
        id: e.id,
        name: e.name,
        type: e.entity_type,
        x: (canvas.width / 2) + (Math.cos(idx) * 220 * Math.random()),
        y: (canvas.height / 2) + (Math.sin(idx) * 180 * Math.random()),
        vx: 0,
        vy: 0,
        radius: 6 + Math.min(10, ((incomingRels.get(e.id)||[]).length + (outgoingRels.get(e.id)||[]).length)),
        color: typeColors[e.entity_type] || "#94a3b8"
      }));

      const nodeMap = new Map();
      nodes.forEach(n => nodeMap.set(n.id, n));

      links = RELATIONSHIPS_DATA
        .filter(r => topIds.has(r.source_id) && topIds.has(r.target_id))
        .map(r => ({
          source: nodeMap.get(r.source_id),
          target: nodeMap.get(r.target_id),
          predicate: r.relationship_type
        })).filter(l => l.source && l.target);

      if (animId) cancelAnimationFrame(animId);
      animateGraph();
    }

    function animateGraph() {
      ctx.clearRect(0, 0, canvas.width, canvas.height);

      nodes.forEach(n1 => {
        nodes.forEach(n2 => {
          if (n1 === n2) return;
          const dx = n2.x - n1.x;
          const dy = n2.y - n1.y;
          const dist = Math.sqrt(dx*dx + dy*dy) || 1;
          if (dist < 120) {
            const force = (120 - dist) / 120;
            n1.vx -= (dx / dist) * force * 0.4;
            n1.vy -= (dy / dist) * force * 0.4;
          }
        });
      });

      links.forEach(l => {
        const dx = l.target.x - l.source.x;
        const dy = l.target.y - l.source.y;
        const dist = Math.sqrt(dx*dx + dy*dy) || 1;
        const force = (dist - 80) * 0.03;
        l.source.vx += (dx / dist) * force;
        l.source.vy += (dy / dist) * force;
        l.target.vx -= (dx / dist) * force;
        l.target.vy -= (dy / dist) * force;
      });

      ctx.strokeStyle = "rgba(255, 255, 255, 0.12)";
      ctx.lineWidth = 1;
      links.forEach(l => {
        ctx.beginPath();
        ctx.moveTo(l.source.x, l.source.y);
        ctx.lineTo(l.target.x, l.target.y);
        ctx.stroke();
      });

      nodes.forEach(n => {
        if (n !== dragNode) {
          n.x += n.vx;
          n.y += n.vy;
          n.vx *= 0.85;
          n.vy *= 0.85;

          if (n.x < 30) n.x = 30;
          if (n.x > canvas.width - 30) n.x = canvas.width - 30;
          if (n.y < 30) n.y = 30;
          if (n.y > canvas.height - 30) n.y = canvas.height - 30;
        }

        ctx.fillStyle = n.color;
        ctx.beginPath();
        ctx.arc(n.x, n.y, n.radius, 0, Math.PI * 2);
        ctx.fill();

        ctx.fillStyle = "#cbd5e1";
        ctx.font = "10px sans-serif";
        ctx.fillText(n.name, n.x + n.radius + 4, n.y + 3);
      });

      animId = requestAnimationFrame(animateGraph);
    }

    function resetGraphView() {
      initGraphSimulation();
    }

    window.addEventListener('DOMContentLoaded', () => {
      initCategoryPills();
      renderEntityGrid();
    });
  </script>
</body>
</html>
"""

html_final = template.replace("__ENTITIES__", entities_json_str)\
                     .replace("__RELATIONSHIPS__", relationships_json_str)\
                     .replace("__SUMMARY__", summary_json_str)\
                     .replace("__METRICS__", graph_metrics_json_str)

with open("/working_dir/c_15be93eeb8dee532/ai_orbit_pipeline/web/index.html", "w", encoding="utf-8") as f:
    f.write(html_final)

print(f"Successfully created /working_dir/c_15be93eeb8dee532/ai_orbit_pipeline/web/index.html ({len(html_final)} chars)")
