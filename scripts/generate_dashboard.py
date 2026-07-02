#!/usr/bin/env python3
"""
Dashboard Generator — Futuristic Edition
==========================================
Generates a premium sci-fi themed HTML dashboard from dataset statistics.

Usage:
    python scripts/generate_dashboard.py
"""

import json
import math
from pathlib import Path


def generate_dashboard():
    project_root = Path(__file__).parent.parent
    stats_file = project_root / "data" / "processed" / "dataset_statistics.json"
    output_file = project_root / "results" / "dashboard.html"

    if not stats_file.exists():
        print(f"Error: {stats_file} not found. Run preprocess.py first.")
        return

    with open(stats_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    # ── aggregate ────────────────────────────────────────────────────────
    total_pairs = 0
    total_clones = 0
    total_non_clones = 0
    type_dist = {}
    splits_order = []

    for split_name, stats in data.items():
        splits_order.append(split_name)
        total_pairs += stats.get("total_pairs", 0)
        total_clones += stats.get("clone_pairs", 0)
        total_non_clones += stats.get("non_clone_pairs", 0)
        for t, count in stats.get("type_distribution", {}).items():
            type_dist[t] = type_dist.get(t, 0) + count

    clone_ratio = (total_clones / total_pairs * 100) if total_pairs else 0
    num_splits = len(splits_order)

    mapped_type_dist = {}
    for k, v in type_dist.items():
        if str(k) == "0":
            mapped_type_dist["Non-Clone"] = v
        elif str(k) == "1":
            mapped_type_dist["Type I (Exact)"] = v
        elif str(k) == "2":
            mapped_type_dist["Type II (Renamed)"] = v
        elif str(k) == "3":
            mapped_type_dist["Type III (Near-Miss)"] = v
        elif str(k) == "4":
            mapped_type_dist["Type IV (Semantic)"] = v
        else:
            mapped_type_dist[f"Type {k}"] = v

    # per-split table rows
    split_rows_html = ""
    for s in splits_order:
        st = data[s]
        avg_tok = st.get("token_stats", {}).get("code1_mean", 0)
        med_tok = st.get("token_stats", {}).get("code1_median", 0)
        max_tok = st.get("token_stats", {}).get("code1_max", 0)
        ratio = st.get("clone_ratio", 0) * 100
        split_rows_html += f"""
                <tr>
                    <td><span class="badge badge-{s}">{s.upper()}</span></td>
                    <td>{st.get('total_pairs', 0):,}</td>
                    <td>{st.get('clone_pairs', 0):,}</td>
                    <td>{st.get('non_clone_pairs', 0):,}</td>
                    <td>{ratio:.1f}%</td>
                    <td>{avg_tok:.0f}</td>
                    <td>{med_tok:.0f}</td>
                    <td>{max_tok:,}</td>
                </tr>"""

    split_labels_js = json.dumps([s.capitalize() for s in splits_order])
    clone_counts_js = json.dumps([data[s].get("clone_pairs", 0) for s in splits_order])
    non_clone_counts_js = json.dumps([data[s].get("non_clone_pairs", 0) for s in splits_order])
    type_dist_js = json.dumps(mapped_type_dist)

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Dataset Statistics — Semantic Clone Detection</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Orbitron:wght@400;500;600;700;800;900&family=Inter:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
<style>
/* ═══════════════════════════════════════════════════════════════
   FUTURISTIC DARK THEME
   ═══════════════════════════════════════════════════════════════ */
*,*::before,*::after{{box-sizing:border-box;margin:0;padding:0}}
:root{{
  --bg:#030712;
  --surface:rgba(15,23,42,.65);
  --surface2:rgba(20,30,55,.55);
  --border:rgba(100,200,255,.08);
  --border-glow:rgba(0,200,255,.25);
  --text:#c8d6e5;
  --text-dim:#4a5e7a;
  --text-bright:#e8f4ff;
  --cyan:#00e5ff;
  --cyan2:#00b8d4;
  --magenta:#e040fb;
  --magenta2:#d500f9;
  --electric:#536dfe;
  --neon-green:#00e676;
  --amber:#ffab00;
  --radius:16px;
}}
html{{scroll-behavior:smooth}}

/* ── Custom Scrollbar ──────────────────────────────── */
::-webkit-scrollbar{{width:6px}}
::-webkit-scrollbar-track{{background:var(--bg)}}
::-webkit-scrollbar-thumb{{background:rgba(0,229,255,.25);border-radius:3px}}
::-webkit-scrollbar-thumb:hover{{background:rgba(0,229,255,.45)}}

body{{
  font-family:'Inter',system-ui,sans-serif;
  background:var(--bg);
  color:var(--text);
  min-height:100vh;
  overflow-x:hidden;
  position:relative;
}}

/* ── Animated Background ───────────────────────────── */
#particles-canvas{{
  position:fixed;top:0;left:0;width:100%;height:100%;
  z-index:0;pointer-events:none;
}}
.bg-orb{{
  position:fixed;border-radius:50%;filter:blur(80px);
  pointer-events:none;z-index:0;opacity:.35;
  animation:orbFloat 20s ease-in-out infinite;
}}
.bg-orb.orb1{{width:500px;height:500px;background:radial-gradient(circle,rgba(0,229,255,.25),transparent 70%);top:-10%;left:-5%;animation-delay:0s}}
.bg-orb.orb2{{width:400px;height:400px;background:radial-gradient(circle,rgba(224,64,251,.2),transparent 70%);bottom:-5%;right:-5%;animation-delay:-7s}}
.bg-orb.orb3{{width:350px;height:350px;background:radial-gradient(circle,rgba(83,109,254,.2),transparent 70%);top:40%;left:50%;animation-delay:-14s}}
@keyframes orbFloat{{
  0%,100%{{transform:translate(0,0) scale(1)}}
  25%{{transform:translate(30px,-40px) scale(1.08)}}
  50%{{transform:translate(-20px,30px) scale(.95)}}
  75%{{transform:translate(40px,20px) scale(1.05)}}
}}

/* ── Scan Line Effect ──────────────────────────────── */
body::after{{
  content:'';position:fixed;top:0;left:0;width:100%;height:100%;
  pointer-events:none;z-index:9999;
  background:repeating-linear-gradient(0deg,transparent,transparent 2px,rgba(0,0,0,.03) 2px,rgba(0,0,0,.03) 4px);
}}

/* ── Grid Overlay ──────────────────────────────────── */
.grid-bg{{
  position:fixed;top:0;left:0;width:100%;height:100%;
  z-index:0;pointer-events:none;
  background-image:
    linear-gradient(rgba(0,229,255,.03) 1px, transparent 1px),
    linear-gradient(90deg, rgba(0,229,255,.03) 1px, transparent 1px);
  background-size:60px 60px;
  mask-image:radial-gradient(ellipse 70% 50% at 50% 50%,black,transparent);
}}

.wrap{{max-width:1380px;margin:0 auto;padding:2.5rem 1.5rem 4rem;position:relative;z-index:1}}

/* ── Header ────────────────────────────────────────── */
.header{{text-align:center;margin-bottom:3rem;animation:fadeDown .8s ease-out}}
.header .tag{{
  display:inline-block;
  padding:.35rem 1rem;border-radius:100px;
  font-size:.7rem;font-weight:600;letter-spacing:2px;text-transform:uppercase;
  background:rgba(0,229,255,.08);border:1px solid rgba(0,229,255,.2);
  color:var(--cyan);margin-bottom:1rem;
}}
.header h1{{
  font-family:'Orbitron',sans-serif;
  font-size:2.8rem;font-weight:900;letter-spacing:.04em;
  background:linear-gradient(135deg,var(--cyan),var(--magenta),var(--electric));
  background-size:200% 200%;
  -webkit-background-clip:text;-webkit-text-fill-color:transparent;
  background-clip:text;
  animation:gradientShift 6s ease infinite;
}}
.header p{{color:var(--text-dim);font-size:1rem;margin-top:.5rem;font-weight:400;letter-spacing:.5px}}
@keyframes gradientShift{{
  0%,100%{{background-position:0% 50%}}
  50%{{background-position:100% 50%}}
}}

/* ── Stat Cards ────────────────────────────────────── */
.stats-row{{
  display:grid;grid-template-columns:repeat(5,1fr);
  gap:1.1rem;margin-bottom:2rem;
}}
.stat-card{{
  position:relative;
  background:var(--surface);
  border:1px solid var(--border);
  border-radius:var(--radius);
  padding:1.5rem 1.3rem;
  overflow:hidden;
  backdrop-filter:blur(20px);-webkit-backdrop-filter:blur(20px);
  transition:all .35s cubic-bezier(.4,0,.2,1);
  animation:fadeUp .6s ease-out backwards;
}}
.stat-card:hover{{
  transform:translateY(-6px);
  border-color:var(--border-glow);
  box-shadow:0 0 30px rgba(0,229,255,.08),0 20px 40px rgba(0,0,0,.3);
}}
/* Animated glow border on hover */
.stat-card::before{{
  content:'';position:absolute;inset:-1px;border-radius:var(--radius);
  background:conic-gradient(from 0deg,var(--cyan),var(--magenta),var(--electric),var(--neon-green),var(--cyan));
  opacity:0;transition:opacity .4s;z-index:-1;
  animation:borderSpin 4s linear infinite;
}}
.stat-card:hover::before{{opacity:1}}
@keyframes borderSpin{{0%{{filter:hue-rotate(0deg)}}100%{{filter:hue-rotate(360deg)}}}}

.stat-card:nth-child(1){{animation-delay:.05s}}
.stat-card:nth-child(2){{animation-delay:.1s}}
.stat-card:nth-child(3){{animation-delay:.15s}}
.stat-card:nth-child(4){{animation-delay:.2s}}
.stat-card:nth-child(5){{animation-delay:.25s}}

.stat-card .sc-icon{{
  width:44px;height:44px;border-radius:12px;
  display:flex;align-items:center;justify-content:center;
  font-size:1.2rem;margin-bottom:.8rem;
  position:relative;
}}
.stat-card:nth-child(1) .sc-icon{{background:rgba(0,229,255,.1);box-shadow:0 0 15px rgba(0,229,255,.1)}}
.stat-card:nth-child(2) .sc-icon{{background:rgba(224,64,251,.1);box-shadow:0 0 15px rgba(224,64,251,.1)}}
.stat-card:nth-child(3) .sc-icon{{background:rgba(83,109,254,.1);box-shadow:0 0 15px rgba(83,109,254,.1)}}
.stat-card:nth-child(4) .sc-icon{{background:rgba(0,230,118,.1);box-shadow:0 0 15px rgba(0,230,118,.1)}}
.stat-card:nth-child(5) .sc-icon{{background:rgba(255,171,0,.1);box-shadow:0 0 15px rgba(255,171,0,.1)}}

.stat-card .sc-label{{
  font-size:.68rem;font-weight:700;color:var(--text-dim);
  text-transform:uppercase;letter-spacing:1.8px;margin-bottom:.3rem;
}}
.stat-card .sc-val{{
  font-family:'Orbitron',sans-serif;
  font-size:2rem;font-weight:800;line-height:1.15;
}}
.stat-card:nth-child(1) .sc-val{{color:var(--cyan)}}
.stat-card:nth-child(2) .sc-val{{color:var(--magenta)}}
.stat-card:nth-child(3) .sc-val{{color:var(--electric)}}
.stat-card:nth-child(4) .sc-val{{color:var(--neon-green)}}
.stat-card:nth-child(5) .sc-val{{color:var(--amber)}}

.stat-card .sc-sub{{font-size:.72rem;color:var(--text-dim);margin-top:.3rem}}

/* glow lines inside cards */
.stat-card .glow-line{{
  position:absolute;bottom:0;left:0;right:0;height:2px;
  opacity:.5;
}}
.stat-card:nth-child(1) .glow-line{{background:linear-gradient(90deg,transparent,var(--cyan),transparent)}}
.stat-card:nth-child(2) .glow-line{{background:linear-gradient(90deg,transparent,var(--magenta),transparent)}}
.stat-card:nth-child(3) .glow-line{{background:linear-gradient(90deg,transparent,var(--electric),transparent)}}
.stat-card:nth-child(4) .glow-line{{background:linear-gradient(90deg,transparent,var(--neon-green),transparent)}}
.stat-card:nth-child(5) .glow-line{{background:linear-gradient(90deg,transparent,var(--amber),transparent)}}

/* ── Panel ─────────────────────────────────────────── */
.panel{{
  position:relative;
  background:var(--surface);
  border:1px solid var(--border);
  border-radius:var(--radius);
  padding:2rem;
  backdrop-filter:blur(20px);-webkit-backdrop-filter:blur(20px);
  transition:border-color .35s;
  animation:fadeUp .7s ease-out .3s backwards;
  overflow:hidden;
}}
.panel:hover{{border-color:rgba(100,200,255,.15)}}
.panel::after{{
  content:'';position:absolute;top:0;left:0;right:0;height:1px;
  background:linear-gradient(90deg,transparent,rgba(0,229,255,.3),transparent);
}}
.panel-title{{
  font-family:'Orbitron',sans-serif;
  font-size:1rem;font-weight:700;color:var(--text-bright);
  margin-bottom:1.2rem;display:flex;align-items:center;gap:.6rem;
  letter-spacing:.5px;
}}
.panel-title .dot{{width:8px;height:8px;border-radius:50%;display:inline-block;box-shadow:0 0 8px currentColor}}

/* ── Charts Grid ───────────────────────────────────── */
.charts-grid{{display:grid;grid-template-columns:1fr 1fr;gap:1.25rem;margin-bottom:1.5rem}}
.chart-wrap{{position:relative;height:340px}}

/* ── Data Table ────────────────────────────────────── */
.tbl-wrap{{overflow-x:auto;margin-bottom:0}}
.data-table{{width:100%;border-collapse:separate;border-spacing:0;font-size:.85rem}}
.data-table thead th{{
  text-align:left;padding:.75rem 1rem;
  font-family:'Orbitron',sans-serif;
  font-weight:600;font-size:.65rem;text-transform:uppercase;letter-spacing:1.2px;
  color:var(--text-dim);
  border-bottom:1px solid rgba(0,229,255,.1);
  background:rgba(0,229,255,.03);
}}
.data-table thead th:first-child{{border-radius:10px 0 0 0}}
.data-table thead th:last-child{{border-radius:0 10px 0 0}}
.data-table tbody td{{
  padding:.75rem 1rem;border-bottom:1px solid rgba(255,255,255,.03);
  color:var(--text);font-variant-numeric:tabular-nums;
  transition:background .2s;
}}
.data-table tbody tr:hover td{{background:rgba(0,229,255,.03)}}
.data-table tbody tr:last-child td{{border-bottom:none}}
.badge{{
  display:inline-block;padding:.22rem .65rem;border-radius:6px;
  font-family:'Orbitron',sans-serif;
  font-weight:700;font-size:.6rem;letter-spacing:1px;
}}
.badge-train{{background:rgba(0,229,255,.12);color:var(--cyan);border:1px solid rgba(0,229,255,.2)}}
.badge-val{{background:rgba(224,64,251,.12);color:var(--magenta);border:1px solid rgba(224,64,251,.2)}}
.badge-test{{background:rgba(0,230,118,.12);color:var(--neon-green);border:1px solid rgba(0,230,118,.2)}}
.badge-total{{background:rgba(255,171,0,.12);color:var(--amber);border:1px solid rgba(255,171,0,.2)}}

/* ── Characteristics ───────────────────────────────── */
.chars-row{{
  display:grid;grid-template-columns:repeat(5,1fr);
  gap:1rem;margin-top:1.8rem;
  animation:fadeUp .7s ease-out .5s backwards;
}}
.char-card{{
  background:var(--surface);
  border:1px solid var(--border);
  border-radius:var(--radius);
  padding:1.3rem 1rem;text-align:center;
  backdrop-filter:blur(16px);
  transition:all .3s;
  position:relative;overflow:hidden;
}}
.char-card:hover{{
  transform:translateY(-4px);
  border-color:var(--border-glow);
  box-shadow:0 0 20px rgba(0,229,255,.06);
}}
.char-card::after{{
  content:'';position:absolute;bottom:0;left:0;right:0;height:1px;
  background:linear-gradient(90deg,transparent,rgba(0,229,255,.2),transparent);
}}
.char-card .c-icon{{font-size:1.5rem;margin-bottom:.5rem;filter:drop-shadow(0 0 6px rgba(0,229,255,.3))}}
.char-card .c-title{{font-family:'Orbitron',sans-serif;font-size:.7rem;font-weight:700;color:var(--text-bright);margin-bottom:.2rem;letter-spacing:.5px}}
.char-card .c-desc{{font-size:.68rem;color:var(--text-dim)}}

/* ── Footer ────────────────────────────────────────── */
.footer{{
  text-align:center;margin-top:2.5rem;padding-top:1.5rem;
  border-top:1px solid rgba(0,229,255,.06);
  color:var(--text-dim);font-size:.72rem;letter-spacing:.3px;
}}
.footer code{{color:var(--cyan);font-size:.7rem}}

/* ── Animations ────────────────────────────────────── */
@keyframes fadeDown{{from{{opacity:0;transform:translateY(-20px)}}to{{opacity:1;transform:translateY(0)}}}}
@keyframes fadeUp{{from{{opacity:0;transform:translateY(24px)}}to{{opacity:1;transform:translateY(0)}}}}
@keyframes pulse{{0%,100%{{opacity:.6}}50%{{opacity:1}}}}

/* ── Responsive ────────────────────────────────────── */
@media(max-width:1100px){{
  .stats-row{{grid-template-columns:repeat(3,1fr)}}
  .chars-row{{grid-template-columns:repeat(3,1fr)}}
}}
@media(max-width:900px){{
  .charts-grid{{grid-template-columns:1fr}}
  .stats-row{{grid-template-columns:repeat(2,1fr)}}
  .chars-row{{grid-template-columns:repeat(2,1fr)}}
}}
@media(max-width:500px){{
  .stats-row,.chars-row{{grid-template-columns:1fr}}
  .header h1{{font-size:1.6rem}}
}}
</style>
</head>
<body>

<!-- Background effects -->
<canvas id="particles-canvas"></canvas>
<div class="grid-bg"></div>
<div class="bg-orb orb1"></div>
<div class="bg-orb orb2"></div>
<div class="bg-orb orb3"></div>

<div class="wrap">

  <!-- Header -->
  <div class="header">
    <div class="tag">&#9889; Data Intelligence</div>
    <h1>DATASET STATISTICS</h1>
    <p>Semantic Clone Detection &mdash; Neural Analysis Dashboard</p>
  </div>

  <!-- Stat Cards -->
  <div class="stats-row">
    <div class="stat-card">
      <div class="sc-icon">&#128202;</div>
      <div class="sc-label">Total Pairs</div>
      <div class="sc-val" data-count="{total_pairs}">0</div>
      <div class="sc-sub">Across all splits</div>
      <div class="glow-line"></div>
    </div>
    <div class="stat-card">
      <div class="sc-icon">&#128279;</div>
      <div class="sc-label">Clone Pairs</div>
      <div class="sc-val" data-count="{total_clones}">0</div>
      <div class="sc-sub">Semantically similar</div>
      <div class="glow-line"></div>
    </div>
    <div class="stat-card">
      <div class="sc-icon">&#128306;</div>
      <div class="sc-label">Non-Clone Pairs</div>
      <div class="sc-val" data-count="{total_non_clones}">0</div>
      <div class="sc-sub">Dissimilar code</div>
      <div class="glow-line"></div>
    </div>
    <div class="stat-card">
      <div class="sc-icon">&#9878;&#65039;</div>
      <div class="sc-label">Clone Ratio</div>
      <div class="sc-val" data-count-float="{clone_ratio:.1f}">0%</div>
      <div class="sc-sub">Dataset balance</div>
      <div class="glow-line"></div>
    </div>
    <div class="stat-card">
      <div class="sc-icon">&#128230;</div>
      <div class="sc-label">Data Splits</div>
      <div class="sc-val" data-count="{num_splits}">0</div>
      <div class="sc-sub">{' / '.join(s.capitalize() for s in splits_order)}</div>
      <div class="glow-line"></div>
    </div>
  </div>

  <!-- Charts -->
  <div class="charts-grid">
    <div class="panel">
      <div class="panel-title"><span class="dot" style="color:var(--cyan)"></span>Clone Distribution by Type</div>
      <div class="chart-wrap"><canvas id="typeChart"></canvas></div>
    </div>
    <div class="panel">
      <div class="panel-title"><span class="dot" style="color:var(--magenta)"></span>Split Composition</div>
      <div class="chart-wrap"><canvas id="splitChart"></canvas></div>
    </div>
  </div>

  <!-- Detailed Table -->
  <div class="panel" style="margin-bottom:0">
    <div class="panel-title"><span class="dot" style="color:var(--neon-green)"></span>Per-Split Breakdown</div>
    <div class="tbl-wrap">
      <table class="data-table">
        <thead>
          <tr>
            <th>Split</th><th>Total Pairs</th><th>Clones</th><th>Non-Clones</th>
            <th>Ratio</th><th>Avg Tokens</th><th>Med Tokens</th><th>Max Tokens</th>
          </tr>
        </thead>
        <tbody>{split_rows_html}
          <tr style="font-weight:700;background:rgba(255,171,0,.03)">
            <td><span class="badge badge-total">TOTAL</span></td>
            <td>{total_pairs:,}</td>
            <td>{total_clones:,}</td>
            <td>{total_non_clones:,}</td>
            <td>{clone_ratio:.1f}%</td>
            <td colspan="3" style="color:var(--text-dim);font-weight:400;font-style:italic">&mdash;</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>

  <!-- Characteristics -->
  <div class="chars-row">
    <div class="char-card">
      <div class="c-icon">&#9889;</div>
      <div class="c-title">BALANCED</div>
      <div class="c-desc">{clone_ratio:.0f}% clone ratio</div>
    </div>
    <div class="char-card">
      <div class="c-icon">&#128200;</div>
      <div class="c-title">STRATIFIED</div>
      <div class="c-desc">{num_splits} reproducible splits</div>
    </div>
    <div class="char-card">
      <div class="c-icon">&#127981;</div>
      <div class="c-title">DIVERSE</div>
      <div class="c-desc">{len(mapped_type_dist)} clone categories</div>
    </div>
    <div class="char-card">
      <div class="c-icon">&#128296;</div>
      <div class="c-title">PROCESSED</div>
      <div class="c-desc">Normalized &amp; tokenized</div>
    </div>
    <div class="char-card">
      <div class="c-icon">&#128274;</div>
      <div class="c-title">REPRODUCIBLE</div>
      <div class="c-desc">Seeded &amp; deterministic</div>
    </div>
  </div>

  <div class="footer">
    Generated from <code>dataset_statistics.json</code> &middot;
    Semantic Clone Detection &middot; Neural Analysis Engine
  </div>
</div>

<script>
/* ═══════════════════════════════════════════════════════════════
   PARTICLES
   ═══════════════════════════════════════════════════════════════ */
(function(){{
  const canvas=document.getElementById('particles-canvas');
  const ctx=canvas.getContext('2d');
  let W,H;
  const particles=[];
  const PARTICLE_COUNT=90;

  function resize(){{W=canvas.width=window.innerWidth;H=canvas.height=window.innerHeight}}
  window.addEventListener('resize',resize);resize();

  for(let i=0;i<PARTICLE_COUNT;i++){{
    particles.push({{
      x:Math.random()*W,y:Math.random()*H,
      vx:(Math.random()-.5)*.25,vy:(Math.random()-.5)*.25,
      r:Math.random()*1.5+.5,
      a:Math.random()*.4+.1,
      color:['0,229,255','224,64,251','83,109,254','0,230,118'][Math.floor(Math.random()*4)]
    }});
  }}

  function draw(){{
    ctx.clearRect(0,0,W,H);
    for(const p of particles){{
      p.x+=p.vx;p.y+=p.vy;
      if(p.x<0)p.x=W;if(p.x>W)p.x=0;
      if(p.y<0)p.y=H;if(p.y>H)p.y=0;
      ctx.beginPath();
      ctx.arc(p.x,p.y,p.r,0,Math.PI*2);
      ctx.fillStyle=`rgba(${{p.color}},${{p.a}})`;
      ctx.fill();
    }}
    // draw connections
    for(let i=0;i<particles.length;i++){{
      for(let j=i+1;j<particles.length;j++){{
        const dx=particles[i].x-particles[j].x;
        const dy=particles[i].y-particles[j].y;
        const dist=Math.sqrt(dx*dx+dy*dy);
        if(dist<120){{
          ctx.beginPath();
          ctx.moveTo(particles[i].x,particles[i].y);
          ctx.lineTo(particles[j].x,particles[j].y);
          ctx.strokeStyle=`rgba(0,229,255,${{.06*(1-dist/120)}})`;
          ctx.lineWidth=.5;
          ctx.stroke();
        }}
      }}
    }}
    requestAnimationFrame(draw);
  }}
  draw();
}})();

/* ═══════════════════════════════════════════════════════════════
   COUNT-UP ANIMATION
   ═══════════════════════════════════════════════════════════════ */
function easeOutExpo(t){{return t===1?1:1-Math.pow(2,-10*t)}}

document.querySelectorAll('.sc-val[data-count]').forEach(el=>{{
  const target=parseInt(el.dataset.count,10);
  if(isNaN(target))return;
  const duration=1500;
  const start=performance.now();
  function tick(now){{
    const elapsed=now-start;
    const progress=Math.min(elapsed/duration,1);
    const value=Math.floor(easeOutExpo(progress)*target);
    el.textContent=value.toLocaleString();
    if(progress<1)requestAnimationFrame(tick);
    else el.textContent=target.toLocaleString();
  }}
  requestAnimationFrame(tick);
}});

document.querySelectorAll('.sc-val[data-count-float]').forEach(el=>{{
  const target=parseFloat(el.dataset.countFloat);
  if(isNaN(target))return;
  const duration=1500;
  const start=performance.now();
  function tick(now){{
    const elapsed=now-start;
    const progress=Math.min(elapsed/duration,1);
    const value=(easeOutExpo(progress)*target).toFixed(1);
    el.textContent=value+'%';
    if(progress<1)requestAnimationFrame(tick);
    else el.textContent=target.toFixed(1)+'%';
  }}
  requestAnimationFrame(tick);
}});

/* ═══════════════════════════════════════════════════════════════
   CHARTS
   ═══════════════════════════════════════════════════════════════ */
Chart.defaults.color='#4a5e7a';
Chart.defaults.font.family="'Inter',system-ui,sans-serif";
Chart.defaults.font.size=12;

const tooltipStyle={{
  backgroundColor:'rgba(10,15,30,.95)',
  titleColor:'#e8f4ff',bodyColor:'#94a3b8',
  borderColor:'rgba(0,229,255,.15)',borderWidth:1,
  cornerRadius:12,padding:14,
  bodyFont:{{size:13}},titleFont:{{size:13,weight:700}},
  boxPadding:6
}};

// ── Doughnut ──
const typeData={type_dist_js};
new Chart(document.getElementById('typeChart'),{{
  type:'doughnut',
  data:{{
    labels:Object.keys(typeData),
    datasets:[{{
      data:Object.values(typeData),
      backgroundColor:[
        'rgba(0,229,255,.8)',
        'rgba(0,230,118,.8)',
        'rgba(224,64,251,.8)',
        'rgba(255,171,0,.8)',
        'rgba(83,109,254,.8)'
      ],
      borderWidth:0,hoverOffset:16,borderRadius:6,
      hoverBorderColor:'rgba(255,255,255,.15)',hoverBorderWidth:2
    }}]
  }},
  options:{{
    responsive:true,maintainAspectRatio:false,
    cutout:'72%',
    plugins:{{
      legend:{{
        position:'bottom',
        labels:{{
          padding:18,usePointStyle:true,pointStyle:'circle',
          font:{{size:12,weight:500}},color:'#94a3b8'
        }}
      }},
      tooltip:tooltipStyle
    }},
    animation:{{animateRotate:true,animateScale:true,duration:1200,easing:'easeOutQuart'}}
  }}
}});

// ── Bar ──
const barGradient1=(function(){{
  const c=document.getElementById('splitChart');
  const ctx2=c.getContext('2d');
  const g=ctx2.createLinearGradient(0,0,0,340);
  g.addColorStop(0,'rgba(0,229,255,.85)');
  g.addColorStop(1,'rgba(83,109,254,.6)');
  return g;
}})();
const barGradient2=(function(){{
  const c=document.getElementById('splitChart');
  const ctx2=c.getContext('2d');
  const g=ctx2.createLinearGradient(0,0,0,340);
  g.addColorStop(0,'rgba(224,64,251,.75)');
  g.addColorStop(1,'rgba(0,230,118,.5)');
  return g;
}})();

new Chart(document.getElementById('splitChart'),{{
  type:'bar',
  data:{{
    labels:{split_labels_js},
    datasets:[
      {{label:'Clone Pairs',data:{clone_counts_js},backgroundColor:barGradient1,borderRadius:8,borderSkipped:false}},
      {{label:'Non-Clone Pairs',data:{non_clone_counts_js},backgroundColor:barGradient2,borderRadius:8,borderSkipped:false}}
    ]
  }},
  options:{{
    responsive:true,maintainAspectRatio:false,
    plugins:{{
      legend:{{
        position:'bottom',
        labels:{{padding:18,usePointStyle:true,pointStyle:'circle',font:{{size:12,weight:500}},color:'#94a3b8'}}
      }},
      tooltip:tooltipStyle
    }},
    scales:{{
      y:{{
        beginAtZero:true,
        grid:{{color:'rgba(0,229,255,.04)',drawBorder:false}},
        ticks:{{font:{{size:11}},color:'#4a5e7a'}}
      }},
      x:{{
        grid:{{display:false}},
        ticks:{{font:{{size:12,weight:600}},color:'#94a3b8'}}
      }}
    }},
    animation:{{duration:1200,easing:'easeOutQuart'}}
  }}
}});
</script>
</body>
</html>"""

    output_file.parent.mkdir(parents=True, exist_ok=True)
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"Dashboard generated at: {output_file}")


if __name__ == "__main__":
    generate_dashboard()
