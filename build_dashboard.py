"""
Generates dashboard.html that loads data.json via fetch()
Clean separation: HTML is static, data is dynamic JSON.
"""
import os

HTML = r"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1"/>
<title>Liga – Mapeamento de Campos Práticos</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.3/dist/chart.umd.min.js"></script>
<style>
/* ══════════════════════════════════════════════════════
   TOKENS & RESET
══════════════════════════════════════════════════════ */
:root{
  --cecan:#8b5cf6; --cecan-dim:hsl(265,40%,14%); --cecan-glow:rgba(139,92,246,.3);
  --hla:  #3b82f6; --hla-dim:  hsl(213,50%,12%); --hla-glow:  rgba(59,130,246,.3);
  --pol:  #f59e0b; --pol-dim:  hsl(38,50%,12%);  --pol-glow:  rgba(245,158,11,.3);
  --s-full:#ef4444; --s-partial:#f97316; --s-avail:#22c55e; --s-nodata:#475569;
  --bg:#07101f; --bg2:#0b1628; --card:#0f1e33;
  --border:#1a2d46; --text:#e2e8f0; --muted:#4d6a8a; --subtle:#121f35;
}
*{box-sizing:border-box;margin:0;padding:0}
body{background:var(--bg);color:var(--text);font-family:'Segoe UI',system-ui,sans-serif;min-height:100vh;overflow-x:hidden}

/* ══════════════════════════════════════════════════════
   TOP BAR
══════════════════════════════════════════════════════ */
.topbar{
  position:sticky;top:0;z-index:200;
  background:rgba(7,16,31,.95);
  backdrop-filter:blur(12px);
  border-bottom:1px solid var(--border);
  padding:0 24px;height:58px;
  display:flex;align-items:center;justify-content:space-between;
  box-shadow:0 4px 24px rgba(0,0,0,.5);
}
.tb-left{display:flex;align-items:center;gap:16px}
.liga-brand{display:flex;align-items:center;gap:10px}
.liga-icon{
  width:36px;height:36px;border-radius:9px;
  background:linear-gradient(135deg,#4338ca,#7c3aed);
  display:flex;align-items:center;justify-content:center;
  font-size:17px;box-shadow:0 0 14px rgba(99,102,241,.4);flex-shrink:0;
}
.liga-text strong{font-size:.9rem;font-weight:800;letter-spacing:.3px;display:block}
.liga-text small{font-size:.65rem;color:var(--muted);display:block}
.tb-sep{width:1px;height:26px;background:var(--border)}
.month-tabs{display:flex;gap:3px;background:var(--subtle);border:1px solid var(--border);border-radius:9px;padding:3px}
.month-tab{
  padding:4px 13px;border-radius:6px;border:none;
  background:transparent;color:var(--muted);
  font-size:.75rem;font-weight:600;cursor:pointer;transition:all .18s;
}
.month-tab:hover{color:var(--text)}
.month-tab.active{background:linear-gradient(135deg,#4338ca,#6d28d9);color:#fff;box-shadow:0 2px 10px rgba(99,102,241,.35)}

.tb-right{display:flex;align-items:center;gap:10px}
.search-box{position:relative;display:flex;align-items:center}
.search-box input{
  background:var(--subtle);border:1px solid var(--border);
  border-radius:8px;padding:5px 12px 5px 28px;
  color:var(--text);font-size:.77rem;width:175px;outline:none;
  transition:border-color .18s,width .2s;
}
.search-box input:focus{border-color:#4f46e5;width:210px}
.search-box input::placeholder{color:var(--muted)}
.search-box .si{position:absolute;left:9px;font-size:.78rem;opacity:.45;pointer-events:none}
.live-badge{
  padding:4px 11px;border-radius:8px;font-size:.68rem;font-weight:700;
  background:rgba(16,185,129,.1);border:1px solid rgba(16,185,129,.22);color:#34d399;
  display:flex;align-items:center;gap:5px;
}
.live-dot{width:6px;height:6px;border-radius:50%;background:#34d399;animation:pls 1.6s infinite}
@keyframes pls{0%,100%{opacity:1}50%{opacity:.25}}

/* ══════════════════════════════════════════════════════
   APP SHELL  –  sidebar + main
══════════════════════════════════════════════════════ */
.shell{display:grid;grid-template-columns:210px 1fr;min-height:calc(100vh - 58px)}

/* ── SIDEBAR ── */
.sidebar{
  background:var(--bg2);border-right:1px solid var(--border);
  padding:18px 12px;display:flex;flex-direction:column;gap:22px;overflow-y:auto;
}
.sb-label{font-size:.62rem;font-weight:700;letter-spacing:1px;color:var(--muted);text-transform:uppercase;margin-bottom:7px}

/* unit filter buttons */
.unit-btns{display:flex;flex-direction:column;gap:5px}
.ubtn{
  display:flex;align-items:center;gap:9px;
  padding:9px 11px;border-radius:9px;border:1px solid transparent;
  background:transparent;color:var(--text);cursor:pointer;
  font-size:.8rem;font-weight:600;transition:all .18s;text-align:left;width:100%;
}
.ubtn .udot{width:9px;height:9px;border-radius:50%;flex-shrink:0}
.ubtn .ucnt{
  margin-left:auto;font-size:.68rem;padding:1px 7px;
  border-radius:8px;font-weight:700;
}
.ubtn:hover{background:var(--subtle)}
.ubtn.active-ALL  {background:var(--subtle);border-color:#334155}
.ubtn.active-CECAN{background:var(--cecan-dim);border-color:rgba(139,92,246,.45);box-shadow:0 0 10px var(--cecan-glow)}
.ubtn.active-HLA  {background:var(--hla-dim);  border-color:rgba(59,130,246,.45); box-shadow:0 0 10px var(--hla-glow)}
.ubtn.active-POL  {background:var(--pol-dim);  border-color:rgba(245,158,11,.45); box-shadow:0 0 10px var(--pol-glow)}

/* kpi minis */
.kpi-col{display:flex;flex-direction:column;gap:7px}
.kmi{
  background:var(--card);border:1px solid var(--border);
  border-radius:9px;padding:9px 12px;
  display:flex;align-items:center;justify-content:space-between;
}
.kmi-v{font-size:1.25rem;font-weight:800;line-height:1}
.kmi-l{font-size:.68rem;color:var(--muted);margin-top:1px}
.kmi.km-t .kmi-v{color:#a5b4fc}
.kmi.km-f .kmi-v{color:var(--s-full)}
.kmi.km-p .kmi-v{color:var(--s-partial)}
.kmi.km-a .kmi-v{color:var(--s-avail)}

/* donut chart */
.donut-wrap{position:relative;height:155px}

/* legend */
.leg{display:flex;flex-direction:column;gap:6px}
.leg-item{display:flex;align-items:center;gap:7px;font-size:.72rem;color:var(--muted)}
.leg-sw{width:11px;height:11px;border-radius:3px;flex-shrink:0}

/* ══════════════════════════════════════════════════════
   MAIN CANVAS  –  THE LIGA MAP
══════════════════════════════════════════════════════ */
.map-canvas{
  padding:22px 26px;overflow-y:auto;
  display:flex;flex-direction:column;gap:28px;
}

/* ── UNIT BUILDING ── */
.building{
  border-radius:16px;border:1.5px solid var(--border);
  overflow:hidden;transition:box-shadow .25s;
}
.building:hover{box-shadow:0 12px 48px rgba(0,0,0,.4)}
.building[data-u="CECAN"]{border-color:rgba(139,92,246,.25)}
.building[data-u="HLA"]  {border-color:rgba(59,130,246,.25)}
.building[data-u="POL"]  {border-color:rgba(245,158,11,.25)}

/* facade / header banner */
.bfacade{
  padding:15px 20px;
  display:flex;align-items:center;justify-content:space-between;
  border-bottom:1px solid rgba(255,255,255,.05);
}
.building[data-u="CECAN"] .bfacade{background:linear-gradient(130deg,hsl(265,35%,13%),hsl(265,25%,9%))}
.building[data-u="HLA"]   .bfacade{background:linear-gradient(130deg,hsl(213,35%,13%),hsl(213,25%,9%))}
.building[data-u="POL"]   .bfacade{background:linear-gradient(130deg,hsl(38,35%,12%),hsl(38,25%,8%))}

.bf-left{display:flex;align-items:center;gap:13px}
.b-icon{
  width:42px;height:42px;border-radius:11px;
  display:flex;align-items:center;justify-content:center;font-size:19px;flex-shrink:0;
}
.building[data-u="CECAN"] .b-icon{background:rgba(139,92,246,.18);border:1px solid rgba(139,92,246,.28)}
.building[data-u="HLA"]   .b-icon{background:rgba(59,130,246,.18); border:1px solid rgba(59,130,246,.28)}
.building[data-u="POL"]   .b-icon{background:rgba(245,158,11,.18); border:1px solid rgba(245,158,11,.28)}

.b-name strong{font-size:1.1rem;font-weight:800;letter-spacing:.4px}
.b-name span{font-size:.72rem;color:var(--muted);display:block;margin-top:1px}
.building[data-u="CECAN"] .b-name strong{color:var(--cecan)}
.building[data-u="HLA"]   .b-name strong{color:var(--hla)}
.building[data-u="POL"]   .b-name strong{color:var(--pol)}

.bf-right{display:flex;align-items:center;gap:8px;flex-wrap:wrap;justify-content:flex-end}
.b-stat{
  display:flex;flex-direction:column;align-items:center;
  padding:5px 12px;border-radius:9px;
  background:rgba(0,0,0,.3);border:1px solid rgba(255,255,255,.05);
  min-width:56px;
}
.b-stat .bsv{font-size:1.15rem;font-weight:800;line-height:1.1}
.b-stat .bsl{font-size:.6rem;color:var(--muted);margin-top:2px;white-space:nowrap}
.b-occ{display:flex;flex-direction:column;gap:4px;flex:0 0 150px}
.b-occ-head{display:flex;justify-content:space-between;font-size:.67rem}
.b-occ-track{height:7px;background:rgba(255,255,255,.07);border-radius:4px;overflow:hidden}
.b-occ-fill{height:100%;border-radius:4px;transition:width .5s}
.b-occ-foot{font-size:.62rem;color:var(--muted)}

/* ── FLOOR (inside building) ── */
.bfloor{background:var(--bg2);padding:16px 18px}

/* profession section divider */
.pg-head{
  font-size:.63rem;font-weight:700;letter-spacing:.9px;
  color:var(--muted);text-transform:uppercase;
  padding:8px 0 7px;
  display:flex;align-items:center;gap:8px;
  border-top:1px solid var(--border);margin-top:4px;
}
.pg-head:first-child{border-top:none;margin-top:0}
.pg-head::after{content:'';flex:1;height:1px;background:var(--border)}
.pg-head .pgp{
  padding:1px 7px;border-radius:6px;font-size:.6rem;
  background:rgba(255,255,255,.05);border:1px solid var(--border);color:var(--text);
}

/* ── SECTOR GRID ── */
.sgrid{display:grid;grid-template-columns:repeat(auto-fill,minmax(162px,1fr));gap:9px;margin-bottom:6px}

/* ── SECTOR CELL (the room in the map) ── */
.scell{
  border-radius:11px;border:1.5px solid var(--border);
  padding:11px 12px;cursor:pointer;
  position:relative;overflow:hidden;
  display:flex;flex-direction:column;gap:6px;
  transition:transform .16s,box-shadow .16s,border-color .16s;
}
/* top status stripe */
.scell::after{
  content:'';position:absolute;top:0;left:0;right:0;height:3px;
  border-radius:11px 11px 0 0;
}
.scell.sf::after{background:var(--s-full)}
.scell.sp::after{background:var(--s-partial)}
.scell.sa::after{background:var(--s-avail)}
.scell.sn::after{background:var(--s-nodata)}

/* unit-tint backgrounds */
.building[data-u="CECAN"] .scell{background:hsl(265,20%,10%)}
.building[data-u="HLA"]   .scell{background:hsl(213,20%,10%)}
.building[data-u="POL"]   .scell{background:hsl(38,20%,10%)}

.scell:hover{transform:translateY(-3px) scale(1.015);z-index:5}
.scell.sf:hover{border-color:var(--s-full);   box-shadow:0 8px 24px rgba(239,68,68,.2)}
.scell.sp:hover{border-color:var(--s-partial);box-shadow:0 8px 24px rgba(249,115,22,.2)}
.scell.sa:hover{border-color:var(--s-avail);  box-shadow:0 8px 24px rgba(34,197,94,.18)}
.scell.sn:hover{border-color:#334155;         box-shadow:0 8px 24px rgba(0,0,0,.3)}

/* cell interior */
.sc-top{display:flex;align-items:flex-start;justify-content:space-between;gap:5px}
.sc-name{font-size:.78rem;font-weight:700;line-height:1.25;flex:1}
.sc-dot{width:7px;height:7px;border-radius:50%;flex-shrink:0;margin-top:3px}
.sf .sc-dot{background:var(--s-full);  box-shadow:0 0 6px var(--s-full)}
.sp .sc-dot{background:var(--s-partial);box-shadow:0 0 6px var(--s-partial)}
.sa .sc-dot{background:var(--s-avail); box-shadow:0 0 6px var(--s-avail)}
.sn .sc-dot{background:var(--s-nodata)}

.sc-bar{height:4px;background:rgba(255,255,255,.07);border-radius:2px;overflow:hidden}
.sc-bar-f{height:100%;border-radius:2px;transition:width .4s}
.sf .sc-bar-f{background:var(--s-full)}
.sp .sc-bar-f{background:var(--s-partial)}
.sa .sc-bar-f{background:var(--s-avail)}
.sn .sc-bar-f{background:var(--s-nodata)}

.sc-row{display:flex;align-items:center;justify-content:space-between}
.sc-nums{font-size:.8rem;font-weight:800}
.sc-cap-txt{font-size:.68rem;color:var(--muted)}
.sc-badge{
  font-size:.58rem;font-weight:700;padding:2px 6px;
  border-radius:7px;text-transform:uppercase;letter-spacing:.3px;
}
.sf .sc-badge{background:rgba(239,68,68,.14);  color:var(--s-full);   border:1px solid rgba(239,68,68,.22)}
.sp .sc-badge{background:rgba(249,115,22,.14); color:var(--s-partial);border:1px solid rgba(249,115,22,.22)}
.sa .sc-badge{background:rgba(34,197,94,.12);  color:var(--s-avail);  border:1px solid rgba(34,197,94,.18)}
.sn .sc-badge{background:rgba(71,85,105,.14);  color:var(--s-nodata); border:1px solid rgba(71,85,105,.22)}

/* turno pips */
.sc-turnos{display:flex;gap:3px;flex-wrap:wrap}
.tpip{
  font-size:.58rem;padding:1px 5px;border-radius:5px;
  background:rgba(255,255,255,.05);border:1px solid rgba(255,255,255,.08);
  color:var(--muted);white-space:nowrap;
}
.tpip.occ{background:rgba(255,255,255,.09);color:var(--text)}

/* active badge */
.sc-active{
  display:inline-flex;align-items:center;gap:3px;
  font-size:.58rem;font-weight:700;padding:2px 5px;border-radius:5px;
  background:rgba(34,197,94,.1);color:#4ade80;
  border:1px solid rgba(34,197,94,.18);width:fit-content;
}
.sc-active .ap{width:4px;height:4px;border-radius:50%;background:#4ade80;animation:pls 1.6s infinite}

/* ══════════════════════════════════════════════════════
   TOOLTIP
══════════════════════════════════════════════════════ */
#tt{
  position:fixed;z-index:9999;pointer-events:none;
  background:#060f1e;border:1px solid var(--border);
  border-radius:14px;overflow:hidden;
  max-width:350px;min-width:250px;
  box-shadow:0 24px 60px rgba(0,0,0,.75);
  opacity:0;transition:opacity .14s;
}
#tt.vis{opacity:1}
.tt-head{padding:12px 15px 10px;border-bottom:1px solid var(--border)}
.tt-htop{display:flex;align-items:center;justify-content:space-between;gap:8px;margin-bottom:2px}
.tt-setor{font-size:.95rem;font-weight:800}
.tt-uchip{font-size:.62rem;font-weight:700;padding:2px 7px;border-radius:7px}
.tt-body{padding:10px 14px;display:flex;flex-direction:column;gap:8px;max-height:360px;overflow-y:auto}
.tt-tblock{border-radius:9px;border:1px solid var(--border);overflow:hidden}
.tt-tlabel{
  padding:5px 10px;font-size:.68rem;font-weight:700;letter-spacing:.4px;
  display:flex;align-items:center;justify-content:space-between;
  background:rgba(255,255,255,.04);
}
.tt-trows{padding:7px 10px;display:flex;flex-direction:column;gap:7px}
.tt-prow{}
.tt-pname{font-size:.73rem;font-weight:700;margin-bottom:2px}
.tt-pmeta{font-size:.65rem;color:var(--muted)}
.tt-pbar{height:3px;background:rgba(255,255,255,.07);border-radius:2px;margin-top:3px;overflow:hidden}
.tt-pbarf{height:100%;border-radius:2px}
.tt-pnum{display:flex;justify-content:space-between;font-size:.65rem;margin-top:2px}
.tt-pnum .tn{font-weight:700}
.tt-pnum .tp{color:var(--muted)}
.tt-curso{
  margin-top:3px;font-size:.65rem;display:inline-block;
  padding:2px 6px;border-radius:5px;
  background:rgba(99,102,241,.1);color:#a5b4fc;border:1px solid rgba(99,102,241,.18);
}
.tt-periodo{font-size:.62rem;color:var(--muted);margin-top:2px}

/* ══════════════════════════════════════════════════════
   BOTTOM CHARTS
══════════════════════════════════════════════════════ */
.charts-bar{
  background:var(--bg2);border-top:1px solid var(--border);
  padding:20px 26px;
  display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:16px;
}
.cbox{background:var(--card);border:1px solid var(--border);border-radius:13px;padding:16px 18px}
.cbox-t{font-size:.8rem;font-weight:700;margin-bottom:12px;display:flex;align-items:center;gap:5px}
.cbox-t .ci{opacity:.65}
.cbox-w{position:relative;height:175px}

/* ══════════════════════════════════════════════════════
   SCROLLBAR
══════════════════════════════════════════════════════ */
::-webkit-scrollbar{width:5px;height:5px}
::-webkit-scrollbar-track{background:transparent}
::-webkit-scrollbar-thumb{background:#1a2d46;border-radius:3px}
::-webkit-scrollbar-thumb:hover{background:#263f5a}

/* ══════════════════════════════════════════════════════
   RESPONSIVE
══════════════════════════════════════════════════════ */
@media(max-width:820px){
  .shell{grid-template-columns:1fr}
  .sidebar{display:none}
}
@media(max-width:560px){
  .topbar{padding:0 12px}
  .map-canvas{padding:12px}
  .liga-text small{display:none}
}
</style>
</head>
<body>

<!-- ─── TOP BAR ─── -->
<div class="topbar">
  <div class="tb-left">
    <div class="liga-brand">
      <div class="liga-icon">🏥</div>
      <div class="liga-text">
        <strong>LIGA NORTE-RIOGRANDENSE</strong>
        <small>Mapeamento de Campos Práticos</small>
      </div>
    </div>
    <div class="tb-sep"></div>
    <div class="month-tabs" id="monthTabs">
      <button class="month-tab" data-sheet="JANEIRO(PLANEJAMENTO)">Jan</button>
      <button class="month-tab" data-sheet="FEVEREIRO (PLANEJAMENTO)">Fev</button>
      <button class="month-tab active" data-sheet="MARÇO">Mar ✓</button>
    </div>
  </div>
  <div class="tb-right">
    <div class="search-box">
      <span class="si">🔍</span>
      <input id="srch" type="text" placeholder="Buscar setor…"/>
    </div>
    <div class="live-badge"><div class="live-dot"></div>Consolidado Mar/26</div>
  </div>
</div>

<!-- ─── SHELL ─── -->
<div class="shell">

  <!-- ─── SIDEBAR ─── -->
  <aside class="sidebar">

    <div>
      <div class="sb-label">Unidades</div>
      <div class="unit-btns" id="unitBtns">
        <button class="ubtn active-ALL" data-u="ALL">
          <span class="udot" style="background:#6366f1"></span>Todas
          <span class="ucnt" id="cnt-ALL" style="background:rgba(99,102,241,.14);color:#818cf8"></span>
        </button>
        <button class="ubtn" data-u="CECAN">
          <span class="udot" style="background:var(--cecan)"></span>CECAN
          <span class="ucnt" id="cnt-CECAN" style="background:rgba(139,92,246,.14);color:var(--cecan)"></span>
        </button>
        <button class="ubtn" data-u="HLA">
          <span class="udot" style="background:var(--hla)"></span>HLA
          <span class="ucnt" id="cnt-HLA" style="background:rgba(59,130,246,.14);color:var(--hla)"></span>
        </button>
        <button class="ubtn" data-u="POL">
          <span class="udot" style="background:var(--pol)"></span>POL
          <span class="ucnt" id="cnt-POL" style="background:rgba(245,158,11,.14);color:var(--pol)"></span>
        </button>
      </div>
    </div>

    <div>
      <div class="sb-label">Vagas</div>
      <div class="kpi-col">
        <div class="kmi km-t"><div><div class="kmi-v" id="kv-t">—</div><div class="kmi-l">Total Setores</div></div><span style="font-size:1.3rem;opacity:.45">🗂️</span></div>
        <div class="kmi km-f"><div><div class="kmi-v" id="kv-f">—</div><div class="kmi-l">Lotados</div></div><span style="font-size:1.3rem;opacity:.55">🔴</span></div>
        <div class="kmi km-p"><div><div class="kmi-v" id="kv-p">—</div><div class="kmi-l">Parciais</div></div><span style="font-size:1.3rem;opacity:.55">🟠</span></div>
        <div class="kmi km-a"><div><div class="kmi-v" id="kv-a">—</div><div class="kmi-l">Disponíveis</div></div><span style="font-size:1.3rem;opacity:.55">🟢</span></div>
      </div>
    </div>

    <div>
      <div class="sb-label">Distribuição</div>
      <div class="donut-wrap"><canvas id="chartD"></canvas></div>
    </div>

    <div>
      <div class="sb-label">Legenda</div>
      <div class="leg">
        <div class="leg-item"><div class="leg-sw" style="background:var(--s-full)"></div>Lotado (100%)</div>
        <div class="leg-item"><div class="leg-sw" style="background:var(--s-partial)"></div>Parcial (&gt;0 &lt;100%)</div>
        <div class="leg-item"><div class="leg-sw" style="background:var(--s-avail)"></div>Disponível (0%)</div>
        <div class="leg-item"><div class="leg-sw" style="background:var(--s-nodata)"></div>Sem dados</div>
      </div>
    </div>

  </aside>

  <!-- ─── MAIN MAP ─── -->
  <main class="map-canvas" id="mapCanvas">
    <div style="text-align:center;padding:60px 20px;color:var(--muted)">
      <div style="font-size:2rem;margin-bottom:12px">⏳</div>
      Carregando mapeamento…
    </div>
  </main>

</div>

<!-- ─── BOTTOM CHARTS ─── -->
<div class="charts-bar" id="chartsBar">
  <div class="cbox">
    <div class="cbox-t"><span class="ci">📊</span> Ocupação por Unidade</div>
    <div class="cbox-w"><canvas id="chartBar"></canvas></div>
  </div>
  <div class="cbox">
    <div class="cbox-t"><span class="ci">👥</span> Top Profissionais</div>
    <div class="cbox-w"><canvas id="chartProf"></canvas></div>
  </div>
  <div class="cbox">
    <div class="cbox-t"><span class="ci">📅</span> Setores Ativos em Março</div>
    <div class="cbox-w"><canvas id="chartAct"></canvas></div>
  </div>
</div>

<!-- TOOLTIP -->
<div id="tt"></div>

<!-- ══════════════════════════════════════════════════════════
     APP SCRIPT
══════════════════════════════════════════════════════════ -->
<script>
/* ── CONFIG ─────────────────────────────────────────── */
const TODAY = new Date(2026, 2, 9);
const UNIT_META = {
  CECAN:{icon:'🔬',label:'CECAN',sub:'Centro Avançado de Oncologia'},
  HLA:  {icon:'🏨',label:'HLA',  sub:'Hospital Luís Antônio'},
  POL:  {icon:'🩺',label:'POL',  sub:'Policlínica / Unidade Ambulatorial'},
};
const UNIT_COLORS = {CECAN:'#8b5cf6',HLA:'#3b82f6',POL:'#f59e0b'};
const UNIT_ORDER  = ['CECAN','HLA','POL'];
const STATUS_LABEL = {sf:'Lotado',sp:'Parcial',sa:'Disponível',sn:'S/dados'};

/* ── STATE ───────────────────────────────────────────── */
let DB = {};
let curSheet = 'MARÇO';
let curUnit  = 'ALL';
let srch     = '';
let charts   = {};

/* ── LOAD DATA ───────────────────────────────────────── */
async function loadData(){
  const url = 'data.json?t=' + Date.now();
  try {
    const r = await fetch(url);
    DB = await r.json();
  } catch(e) {
    // If fetch fails (e.g. file:// protocol), try inline fallback
    console.warn('fetch failed, using embedded data:', e);
  }
  renderAll();
}

/* ── HELPERS ─────────────────────────────────────────── */
function rows()  { return DB[curSheet] || []; }
function ucolor(u){ return UNIT_COLORS[u] || '#6b7280'; }
function profAbbr(p){
  const m={'TÉCNICO DE ENFERMAGEM':'TEC.ENF','TÉCNICO DE RADIOLOGIA':'TEC.RAD',
           'ENFERMEIRO':'ENF','ENFERMAGEM':'ENF','FARMACÊUTICO':'FARM','FARMÁCIA':'FARM',
           'BIOMEDICINA':'BIOMED','NUTRICIONISTA':'NUTRI','NUTRIÇÃO':'NUTRI',
           'FISIOTERAPEUTA':'FISIO','ASSISTENTE SOCIAL':'ASS.SOC',
           'PSICOLOGIA':'PSICO','DENTISTA':'DENT'};
  return m[p] || (p && p.length>9 ? p.slice(0,8)+'…' : p||'');
}

function parseBrDate(s){
  if(!s) return null;
  const m = s.trim().match(/(\d{1,2})\/(\d{1,2})\/(\d{4})/);
  return m ? new Date(+m[3],+m[2]-1,+m[1]) : null;
}
function isPeriodActive(p){
  if(!p||p==='PENDENTE') return false;
  const sep = p.includes(' - ')?' - ':'-';
  const pts = p.split(sep).map(x=>x.trim());
  if(pts.length<2) return false;
  const s=parseBrDate(pts[0]), e=parseBrDate(pts[pts.length-1]);
  return s&&e&&TODAY>=s&&TODAY<=e;
}

function groupSectors(data){
  const m = new Map();
  data.forEach(r=>{
    if(!r.setor) return;
    const k = r.unidade+'|'+r.setor;
    if(!m.has(k)) m.set(k,{setor:r.setor,unidade:r.unidade,rows:[]});
    m.get(k).rows.push(r);
  });
  return [...m.values()];
}

function sectorStatus(rs){
  const v = rs.filter(r=>r.capacidade>0);
  if(!v.length) return 'sn';
  const wo = v.filter(r=>r.ocupacao!==null&&r.ocupacao!==undefined);
  if(!wo.length) return 'sn';
  const cap = v.reduce((s,r)=>s+r.capacidade,0);
  const occ = wo.reduce((s,r)=>s+(r.ocupacao||0),0);
  if(occ===0) return 'sa';
  if(occ<cap) return 'sp';
  return 'sf';
}

function sectorTotals(rs){
  const cap=rs.reduce((s,r)=>s+(r.capacidade||0),0);
  const occ=rs.reduce((s,r)=>s+(r.ocupacao||0),0);
  return {cap,occ,pct:cap>0?Math.min(100,Math.round(occ/cap*100)):0};
}

/* ── KPI ─────────────────────────────────────────────── */
function updateKPI(){
  const data = rows();
  const filtered = curUnit==='ALL' ? data : data.filter(r=>r.unidade===curUnit);
  const secs = groupSectors(filtered);
  const c = {sf:0,sp:0,sa:0,sn:0};
  secs.forEach(s=>c[sectorStatus(s.rows)]++);
  document.getElementById('kv-t').textContent = secs.length;
  document.getElementById('kv-f').textContent = c.sf;
  document.getElementById('kv-p').textContent = c.sp;
  document.getElementById('kv-a').textContent = c.sa;

  // unit counts
  const all = rows();
  document.getElementById('cnt-ALL').textContent   = groupSectors(all).length;
  UNIT_ORDER.forEach(u=>{
    const el = document.getElementById('cnt-'+u);
    if(el) el.textContent = groupSectors(all.filter(r=>r.unidade===u)).length;
  });
}

/* ── BUILD MAP ───────────────────────────────────────── */
function buildMap(){
  const data = rows();
  const term = srch.toLowerCase();
  const activeUnits = curUnit==='ALL' ? UNIT_ORDER : [curUnit];
  const canvas = document.getElementById('mapCanvas');
  canvas.innerHTML = '';

  activeUnits.forEach(uk=>{
    const meta = UNIT_META[uk];
    const urows  = data.filter(r=>r.unidade===uk);
    let sectors  = groupSectors(urows);
    if(term) sectors = sectors.filter(s=>s.setor.toLowerCase().includes(term));
    if(!sectors.length) return;

    // building-level stats
    const {cap:uCap,occ:uOcc,pct:uPct} = sectorTotals(urows);
    const c = {sf:0,sp:0,sa:0,sn:0};
    sectors.forEach(s=>c[sectorStatus(s.rows)]++);
    const fillC = uPct>=90?'var(--s-full)':uPct>=30?'var(--s-partial)':'var(--s-avail)';

    // Group sectors by main profissional for sub-floors
    const pgMap = new Map();
    sectors.forEach(s=>{
      const profs=[...new Set(s.rows.map(r=>r.profissional).filter(Boolean))];
      const mainP = profs[0]||'OUTROS';
      if(!pgMap.has(mainP)) pgMap.set(mainP,[]);
      pgMap.get(mainP).push(s);
    });

    let floorsHTML = '';
    pgMap.forEach((secs,profKey)=>{
      const cells = secs.map(s=>buildCell(s)).join('');
      floorsHTML += `
        <div class="pg-head">${profAbbr(profKey)}<span class="pgp">${secs.length} setor${secs.length>1?'es':''}</span></div>
        <div class="sgrid">${cells}</div>`;
    });

    const uc = ucolor(uk);
    const bld = document.createElement('div');
    bld.className='building';
    bld.dataset.u=uk;
    bld.innerHTML=`
      <div class="bfacade">
        <div class="bf-left">
          <div class="b-icon">${meta.icon}</div>
          <div class="b-name"><strong>${meta.label}</strong><span>${meta.sub}</span></div>
        </div>
        <div class="bf-right">
          <div class="b-stat"><span class="bsv" style="color:${uc}">${sectors.length}</span><span class="bsl">Setores</span></div>
          <div class="b-stat"><span class="bsv" style="color:var(--s-full)">${c.sf}</span><span class="bsl">Lotados</span></div>
          <div class="b-stat"><span class="bsv" style="color:var(--s-partial)">${c.sp}</span><span class="bsl">Parciais</span></div>
          <div class="b-stat"><span class="bsv" style="color:var(--s-avail)">${c.sa}</span><span class="bsl">Livres</span></div>
          <div class="b-occ">
            <div class="b-occ-head">
              <span style="color:var(--muted)">Ocupação total</span>
              <span style="font-weight:700;color:${fillC}">${uPct}%</span>
            </div>
            <div class="b-occ-track"><div class="b-occ-fill" style="width:${uPct}%;background:${fillC}"></div></div>
            <div class="b-occ-foot">${uOcc.toFixed(0)} / ${uCap.toFixed(0)} vagas</div>
          </div>
        </div>
      </div>
      <div class="bfloor">${floorsHTML}</div>
    `;
    canvas.appendChild(bld);
  });

  if(!canvas.children.length){
    canvas.innerHTML=`<div style="text-align:center;padding:60px;color:var(--muted)">🔍 Nenhum setor encontrado${srch?' para "'+srch+'"':''}</div>`;
  }
}

function buildCell(s){
  const st = sectorStatus(s.rows);
  const {cap,occ,pct} = sectorTotals(s.rows);
  const barW = st==='sn'?0:pct;

  const turnos = [...new Set(s.rows.map(r=>r.turno).filter(Boolean))];
  const pips = turnos.map(t=>{
    const hasO = s.rows.filter(r=>r.turno===t).some(r=>(r.ocupacao||0)>0);
    return `<span class="tpip${hasO?' occ':''}">${t.substring(0,4)}</span>`;
  }).join('');

  const isActive = s.rows.some(r=>isPeriodActive(r.periodo));
  const activeBadge = (isActive&&st!=='sn')
    ?`<div class="sc-active"><div class="ap"></div>ATIVO</div>`:'';

  const td = encodeURIComponent(JSON.stringify({setor:s.setor,unidade:s.unidade,rows:s.rows}));
  return `<div class="scell ${st}" data-td="${td}"
               onmouseenter="showTT(event,this)"
               onmouseleave="hideTT()"
               onmousemove="moveTT(event)">
    <div class="sc-top"><div class="sc-name">${s.setor}</div><div class="sc-dot"></div></div>
    <div class="sc-bar"><div class="sc-bar-f" style="width:${barW}%"></div></div>
    <div class="sc-row">
      <div><span class="sc-nums">${occ.toFixed(0)}</span><span class="sc-cap-txt"> / ${cap.toFixed(0)}</span></div>
      <span class="sc-badge">${STATUS_LABEL[st]}</span>
    </div>
    ${activeBadge}
    <div class="sc-turnos">${pips}</div>
  </div>`;
}

/* ── TOOLTIP ─────────────────────────────────────────── */
const ttEl = document.getElementById('tt');
function showTT(e,el){
  const d = JSON.parse(decodeURIComponent(el.dataset.td));
  const uc = ucolor(d.unidade);
  const byTurno = new Map();
  d.rows.forEach(r=>{
    if(!byTurno.has(r.turno)) byTurno.set(r.turno,[]);
    byTurno.get(r.turno).push(r);
  });

  let blocks='';
  byTurno.forEach((rs,turno)=>{
    const rowsH = rs.map(r=>{
      const cap=r.capacidade||0;
      const occ=r.ocupacao!==null&&r.ocupacao!==undefined?r.ocupacao:null;
      const pct=cap>0&&occ!==null?Math.min(100,Math.round(occ/cap*100)):0;
      const rc=occ===null?'#475569':occ>=cap?'#ef4444':occ>0?'#f97316':'#22c55e';
      const occStr=occ!==null?occ.toFixed(0):'—';
      return `<div class="tt-prow">
        <div class="tt-pname">${r.profissional||'—'}</div>
        <div class="tt-pnum">
          <span class="tn" style="color:${rc}">${occStr} / ${cap.toFixed(0)} vagas</span>
          <span class="tp">${cap>0?pct+'%':''}</span>
        </div>
        <div class="tt-pbar"><div class="tt-pbarf" style="width:${pct}%;background:${rc}"></div></div>
        ${r.curso?`<span class="tt-curso">📚 ${r.curso}</span>`:''}
        ${r.periodo?`<div class="tt-periodo">📅 ${r.periodo}${isPeriodActive(r.periodo)?' <span style="color:#4ade80">● ativo</span>':''}</div>`:''}
      </div>`;
    }).join('');
    blocks+=`<div class="tt-tblock">
      <div class="tt-tlabel">
        <span>⏰ ${turno||'N/D'}</span>
        <span style="color:var(--muted);font-size:.62rem">${rs.length} linha(s)</span>
      </div>
      <div class="tt-trows">${rowsH}</div>
    </div>`;
  });

  ttEl.innerHTML=`
    <div class="tt-head">
      <div class="tt-htop">
        <span class="tt-setor">${d.setor}</span>
        <span class="tt-uchip" style="background:${uc}22;color:${uc};border:1px solid ${uc}44">${d.unidade}</span>
      </div>
    </div>
    <div class="tt-body">${blocks}</div>`;
  moveTT(e);
  ttEl.classList.add('vis');
}
function hideTT(){ttEl.classList.remove('vis')}
function moveTT(e){
  const pad=16,tw=ttEl.offsetWidth||310,th=ttEl.offsetHeight||180;
  let x=e.clientX+pad,y=e.clientY+pad;
  if(x+tw>window.innerWidth-pad)  x=e.clientX-tw-pad;
  if(y+th>window.innerHeight-pad) y=e.clientY-th-pad;
  ttEl.style.left=x+'px'; ttEl.style.top=y+'px';
}

/* ── CHARTS ──────────────────────────────────────────── */
function destroyCharts(){ Object.values(charts).forEach(c=>c?.destroy()); charts={}; }

function buildCharts(){
  destroyCharts();
  const all = rows();
  const filt= curUnit==='ALL'?all:all.filter(r=>r.unidade===curUnit);

  // 1. Donut
  const secs = groupSectors(filt);
  const c={sf:0,sp:0,sa:0,sn:0};
  secs.forEach(s=>c[sectorStatus(s.rows)]++);
  charts.d = new Chart(document.getElementById('chartD'),{
    type:'doughnut',
    data:{labels:['Lotado','Parcial','Disponível','S/dados'],
      datasets:[{data:[c.sf,c.sp,c.sa,c.sn],
        backgroundColor:['#ef4444','#f97316','#22c55e','#475569'],
        borderColor:'#0f1e33',borderWidth:3}]},
    options:{responsive:true,maintainAspectRatio:false,cutout:'66%',
      plugins:{legend:{position:'bottom',labels:{color:'#4d6a8a',padding:7,font:{size:10}}},
               tooltip:{callbacks:{label:ctx=>` ${ctx.label}: ${ctx.parsed}`}}}}
  });

  // 2. Bar – occ% per unit
  const bL=[],bD=[],bC=[];
  UNIT_ORDER.forEach(u=>{
    const ud=all.filter(r=>r.unidade===u);
    if(!ud.length) return;
    const cap=ud.reduce((s,r)=>s+(r.capacidade||0),0);
    const occ=ud.reduce((s,r)=>s+(r.ocupacao||0),0);
    bL.push(u); bD.push(cap>0?Math.round(occ/cap*100):0); bC.push(UNIT_COLORS[u]);
  });
  charts.bar = new Chart(document.getElementById('chartBar'),{
    type:'bar',data:{labels:bL,
      datasets:[{data:bD,backgroundColor:bC.map(c=>c+'99'),borderColor:bC,borderWidth:2,borderRadius:8}]},
    options:{responsive:true,maintainAspectRatio:false,
      plugins:{legend:{display:false},tooltip:{callbacks:{label:ctx=>ctx.parsed.y+'%'}}},
      scales:{y:{min:0,max:100,grid:{color:'#1a2d46'},ticks:{color:'#4d6a8a',callback:v=>v+'%'}},
              x:{grid:{display:false},ticks:{color:'#94a3b8'}}}}
  });

  // 3. Horizontal – top profissionais
  const pc=new Map();
  filt.forEach(r=>{ if(r.profissional) pc.set(r.profissional,(pc.get(r.profissional)||0)+1); });
  const top=[...pc.entries()].sort((a,b)=>b[1]-a[1]).slice(0,7);
  const pal=['#8b5cf6','#3b82f6','#f59e0b','#22c55e','#ef4444','#ec4899','#14b8a6'];
  charts.prof= new Chart(document.getElementById('chartProf'),{
    type:'bar',
    data:{labels:top.map(([p])=>profAbbr(p)),
      datasets:[{data:top.map(([,v])=>v),backgroundColor:pal.map(c=>c+'99'),borderColor:pal,borderWidth:2,borderRadius:6}]},
    options:{indexAxis:'y',responsive:true,maintainAspectRatio:false,
      plugins:{legend:{display:false}},
      scales:{x:{grid:{color:'#1a2d46'},ticks:{color:'#4d6a8a'}},
              y:{grid:{display:false},ticks:{color:'#94a3b8',font:{size:10}}}}}
  });

  // 4. Active periods per unit
  const acMap={CECAN:0,HLA:0,POL:0};
  groupSectors(all).forEach(s=>{
    if(acMap[s.unidade]!==undefined && s.rows.some(r=>isPeriodActive(r.periodo))) acMap[s.unidade]++;
  });
  const ac=Object.entries(acMap);
  charts.act= new Chart(document.getElementById('chartAct'),{
    type:'bar',
    data:{labels:ac.map(([u])=>u),
      datasets:[{data:ac.map(([,v])=>v),
        backgroundColor:ac.map(([u])=>UNIT_COLORS[u]+'99'),
        borderColor:ac.map(([u])=>UNIT_COLORS[u]),
        borderWidth:2,borderRadius:8}]},
    options:{responsive:true,maintainAspectRatio:false,
      plugins:{legend:{display:false}},
      scales:{y:{grid:{color:'#1a2d46'},ticks:{color:'#4d6a8a',precision:0}},
              x:{grid:{display:false},ticks:{color:'#94a3b8'}}}}
  });
}

/* ── RENDER ALL ──────────────────────────────────────── */
function renderAll(){ updateKPI(); buildMap(); buildCharts(); }

/* ── EVENTS ──────────────────────────────────────────── */
document.getElementById('monthTabs').addEventListener('click',e=>{
  const b=e.target.closest('.month-tab');
  if(!b) return;
  document.querySelectorAll('.month-tab').forEach(x=>x.classList.remove('active'));
  b.classList.add('active');
  curSheet=b.dataset.sheet;
  renderAll();
});
document.getElementById('unitBtns').addEventListener('click',e=>{
  const b=e.target.closest('.ubtn');
  if(!b) return;
  document.querySelectorAll('.ubtn').forEach(x=>{x.className='ubtn'});
  const u=b.dataset.u;
  b.classList.add('active-'+u);
  curUnit=u;
  renderAll();
});
document.getElementById('srch').addEventListener('input',e=>{
  srch=e.target.value;
  buildMap();
  updateKPI();
});

/* ── INIT ────────────────────────────────────────────── */
loadData();
</script>
</body>
</html>"""

with open('C:/Users/l5857/TCC - LETICIA/dashboard.html', 'w', encoding='utf-8') as f:
    f.write(HTML)

print(f"dashboard.html generated — {len(HTML)/1024:.1f} KB")
print("Uses data.json via fetch() — clean separation")
