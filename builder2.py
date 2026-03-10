"""
Liga Campo Prático - Dashboard Builder v2
Reads data.json and generates dashboard.html with full visual campus map.
"""
import json, pathlib

BASE = pathlib.Path('C:/Users/l5857/TCC - LETICIA')
data_json_str = (BASE / 'data.json').read_text(encoding='utf-8')

CSS = r"""
:root{
  --bg:#0b1120;--surface:#111827;--card:#161f30;--border:#1e2d42;
  --text:#e8edf5;--muted:#6b7f99;--subtle:#2a3a52;
  --cecan:#a855f7;--cecan-dim:rgba(168,85,247,.12);--cecan-glow:rgba(168,85,247,.35);
  --hla:#3b82f6;--hla-dim:rgba(59,130,246,.12);--hla-glow:rgba(59,130,246,.35);
  --pol:#f59e0b;--pol-dim:rgba(245,158,11,.12);--pol-glow:rgba(245,158,11,.35);
  --full:#ef4444;--full-dim:rgba(239,68,68,.15);
  --partial:#f97316;--partial-dim:rgba(249,115,22,.15);
  --avail:#22c55e;--avail-dim:rgba(34,197,94,.15);
  --nodata:#475569;--nodata-dim:rgba(71,85,105,.15);
}
*{box-sizing:border-box;margin:0;padding:0;}
html{scroll-behavior:smooth;}
body{background:var(--bg);color:var(--text);font-family:'Segoe UI',system-ui,sans-serif;min-height:100vh;}

/* ── NAV ── */
.topnav{
  position:sticky;top:0;z-index:200;
  background:rgba(11,17,32,.93);backdrop-filter:blur(20px);
  border-bottom:1px solid var(--border);
  padding:0 28px;display:flex;align-items:center;gap:14px;height:62px;
  box-shadow:0 4px 40px rgba(0,0,0,.6);
}
.nav-logo{
  display:flex;align-items:center;gap:9px;
  font-size:1.15rem;font-weight:900;letter-spacing:.4px;white-space:nowrap;
  background:linear-gradient(135deg,#818cf8 0%,#c084fc 50%,#67e8f9 100%);
  -webkit-background-clip:text;-webkit-text-fill-color:transparent;
}
.nav-logo .ni{-webkit-text-fill-color:initial;font-size:1.5rem;}
.nav-div{width:1px;height:22px;background:var(--border);flex-shrink:0;}
.nav-sub{font-size:.72rem;color:var(--muted);white-space:nowrap;}
.nav-tabs{display:flex;gap:4px;flex-shrink:0;}
.nt{
  padding:5px 14px;border-radius:18px;border:1px solid transparent;
  background:none;color:var(--muted);cursor:pointer;font-size:.78rem;font-weight:600;
  transition:all .2s;white-space:nowrap;
}
.nt:hover{color:var(--text);border-color:var(--border);}
.nt.active{background:var(--subtle);border-color:var(--border);color:var(--text);}
.nt.active.consolidated{
  background:linear-gradient(135deg,rgba(99,102,241,.25),rgba(168,85,247,.25));
  border-color:rgba(168,85,247,.5);color:#c4b5fd;
}
.nav-sp{flex:1;}
.nav-srch{position:relative;display:flex;align-items:center;}
.nav-srch input{
  background:var(--surface);border:1px solid var(--border);border-radius:20px;
  color:var(--text);padding:6px 14px 6px 32px;font-size:.78rem;outline:none;
  width:180px;transition:width .3s,border-color .2s;
}
.nav-srch input:focus{width:260px;border-color:rgba(168,85,247,.5);}
.nav-srch input::placeholder{color:var(--muted);}
.nav-srch .si{position:absolute;left:10px;font-size:.8rem;opacity:.45;pointer-events:none;}
.live-badge{
  background:linear-gradient(135deg,rgba(34,197,94,.18),rgba(16,185,129,.18));
  border:1px solid rgba(34,197,94,.3);border-radius:20px;
  padding:4px 11px;font-size:.7rem;font-weight:700;color:#4ade80;
  display:flex;align-items:center;gap:5px;white-space:nowrap;
}
.ldot{width:6px;height:6px;border-radius:50%;background:#4ade80;animation:pulse 2s infinite;}
@keyframes pulse{0%,100%{opacity:1;}50%{opacity:.25;}}

/* ── PAGE ── */
.page{padding:22px 28px 48px;}

/* ── SUMMARY STRIP ── */
.strip{display:flex;gap:10px;flex-wrap:wrap;margin-bottom:26px;}
.sc{
  flex:1;min-width:120px;background:var(--card);border:1px solid var(--border);
  border-radius:14px;padding:14px 16px;display:flex;flex-direction:column;gap:4px;
  transition:transform .2s;
}
.sc:hover{transform:translateY(-2px);}
.sv{font-size:1.85rem;font-weight:800;line-height:1;}
.sl{font-size:.68rem;color:var(--muted);font-weight:500;margin-top:2px;}
.sc.tot .sv{color:#818cf8;}
.sc.ful .sv{color:var(--full);}
.sc.par .sv{color:var(--partial);}
.sc.ava .sv{color:var(--avail);}
.sc.cap .sv{color:#67e8f9;}
.sc.occ .sv{color:#f0abfc;}

/* ── UNIT FILTER BAR ── */
.ubar{display:flex;align-items:center;gap:8px;margin-bottom:22px;flex-wrap:wrap;}
.upill{
  padding:7px 18px;border-radius:24px;border:1.5px solid var(--border);
  background:var(--card);color:var(--muted);cursor:pointer;
  font-size:.8rem;font-weight:700;transition:all .2s;
}
.upill:hover{color:var(--text);}
.upill.all.active{background:var(--subtle);border-color:#475569;color:var(--text);}
.upill[data-u="CECAN"].active{background:var(--cecan-dim);border-color:var(--cecan);color:var(--cecan);box-shadow:0 0 16px var(--cecan-glow);}
.upill[data-u="HLA"].active{background:var(--hla-dim);border-color:var(--hla);color:var(--hla);box-shadow:0 0 16px var(--hla-glow);}
.upill[data-u="POL"].active{background:var(--pol-dim);border-color:var(--pol);color:var(--pol);box-shadow:0 0 16px var(--pol-glow);}
.lgrow{display:flex;gap:12px;align-items:center;margin-left:auto;flex-wrap:wrap;}
.lg{display:flex;align-items:center;gap:5px;font-size:.7rem;color:var(--muted);}
.lgd{width:9px;height:9px;border-radius:2px;}

/* ── CAMPUS ── */
.campus{display:flex;flex-direction:column;gap:24px;}

/* ── BUILDING ── */
.building{
  border-radius:20px;border:1.5px solid var(--border);
  overflow:hidden;transition:box-shadow .3s;
}
.building:hover{box-shadow:0 10px 50px rgba(0,0,0,.45);}
.building[data-u="CECAN"]{border-color:rgba(168,85,247,.3);}
.building[data-u="HLA"]  {border-color:rgba(59,130,246,.3);}
.building[data-u="POL"]  {border-color:rgba(245,158,11,.3);}

/* building header */
.bh{
  display:flex;align-items:center;gap:14px;
  padding:15px 22px;border-bottom:1px solid var(--border);
}
.building[data-u="CECAN"] .bh{background:linear-gradient(135deg,rgba(168,85,247,.15),rgba(139,92,246,.06));}
.building[data-u="HLA"]   .bh{background:linear-gradient(135deg,rgba(59,130,246,.15),rgba(37,99,235,.06));}
.building[data-u="POL"]   .bh{background:linear-gradient(135deg,rgba(245,158,11,.15),rgba(217,119,6,.06));}

.bico{
  width:46px;height:46px;border-radius:12px;
  display:flex;align-items:center;justify-content:center;
  font-size:1.4rem;flex-shrink:0;
}
.building[data-u="CECAN"] .bico{background:rgba(168,85,247,.18);border:1px solid rgba(168,85,247,.3);}
.building[data-u="HLA"]   .bico{background:rgba(59,130,246,.18);border:1px solid rgba(59,130,246,.3);}
.building[data-u="POL"]   .bico{background:rgba(245,158,11,.18);border:1px solid rgba(245,158,11,.3);}

.binfo{flex:1;min-width:0;}
.bname{font-size:1.1rem;font-weight:800;letter-spacing:.3px;}
.building[data-u="CECAN"] .bname{color:var(--cecan);}
.building[data-u="HLA"]   .bname{color:var(--hla);}
.building[data-u="POL"]   .bname{color:var(--pol);}
.bsub{font-size:.74rem;color:var(--muted);margin-top:2px;}

/* ring */
.bstats{display:flex;gap:8px;align-items:center;flex-shrink:0;flex-wrap:wrap;}
.bstat{
  display:flex;flex-direction:column;align-items:center;
  background:rgba(255,255,255,.04);border:1px solid var(--border);
  border-radius:10px;padding:6px 12px;
}
.bstat-v{font-size:1.15rem;font-weight:800;line-height:1;}
.bstat-l{font-size:.58rem;color:var(--muted);margin-top:2px;text-align:center;}
.ring{position:relative;width:52px;height:52px;flex-shrink:0;}
.ring svg{transform:rotate(-90deg);}
.ring .rp{position:absolute;inset:0;display:flex;align-items:center;justify-content:center;font-size:.68rem;font-weight:800;}

/* building body */
.bb{padding:16px 18px;background:var(--card);}

/* ── FLOOR SECTION (group by professional type) ── */
.floor{margin-bottom:16px;}
.floor:last-child{margin-bottom:0;}
.ftitle{
  font-size:.68rem;font-weight:700;color:var(--muted);
  letter-spacing:.8px;text-transform:uppercase;
  margin-bottom:9px;padding-bottom:6px;
  border-bottom:1px dashed var(--border);
  display:flex;align-items:center;gap:7px;
}

/* ── SECTOR GRID ── */
.sgrid{display:grid;grid-template-columns:repeat(auto-fill,minmax(200px,1fr));gap:9px;}

/* ── ROOM CARD ── */
.room{
  background:var(--surface);border:1px solid var(--border);
  border-radius:12px;overflow:hidden;
  cursor:pointer;position:relative;
  transition:transform .18s, box-shadow .18s, border-color .18s;
}
.room:hover{transform:translateY(-3px);}
/* left accent */
.room::before{content:'';position:absolute;left:0;top:0;bottom:0;width:4px;}
.room.sf::before  {background:var(--full);}
.room.sp::before  {background:var(--partial);}
.room.sa::before  {background:var(--avail);}
.room.sn::before  {background:var(--nodata);}
.room.sf{border-left-color:rgba(239,68,68,.4);}
.room.sp{border-left-color:rgba(249,115,22,.4);}
.room.sa{border-left-color:rgba(34,197,94,.4);}
.room:hover.sf{border-color:rgba(239,68,68,.5);box-shadow:0 8px 24px rgba(239,68,68,.12);}
.room:hover.sp{border-color:rgba(249,115,22,.5);box-shadow:0 8px 24px rgba(249,115,22,.12);}
.room:hover.sa{border-color:rgba(34,197,94,.5); box-shadow:0 8px 24px rgba(34,197,94,.12);}

.ri{padding:10px 11px 8px 15px;}
.rnamrow{display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:9px;gap:6px;}
.rname{font-size:.8rem;font-weight:700;line-height:1.3;flex:1;}
.rdot{width:7px;height:7px;border-radius:50%;flex-shrink:0;margin-top:3px;}
.sf .rdot{background:var(--full);}
.sp .rdot{background:var(--partial);}
.sa .rdot{background:var(--avail);}
.sn .rdot{background:var(--nodata);}

/* shift lanes */
.slanes{display:flex;flex-direction:column;gap:4px;margin-bottom:7px;}
.sl{display:flex;align-items:center;gap:5px;}
.slbl{
  font-size:.58rem;font-weight:700;color:var(--muted);
  width:26px;flex-shrink:0;text-transform:uppercase;letter-spacing:.3px;
}
.sbwrap{flex:1;height:7px;background:rgba(255,255,255,.05);border-radius:4px;overflow:hidden;}
.sbar{height:100%;border-radius:4px;transition:width .5s ease;}
.lf .sbar{background:var(--full);}
.lp .sbar{background:var(--partial);}
.la .sbar{background:var(--avail);}
.ln .sbar{background:var(--nodata);}
.socc{font-size:.58rem;font-weight:700;width:24px;text-align:right;flex-shrink:0;}
.lf .socc{color:var(--full);}
.lp .socc{color:var(--partial);}
.la .socc{color:var(--avail);}
.ln .socc{color:var(--nodata);}

/* room extras */
.rextras{display:flex;gap:5px;align-items:center;flex-wrap:wrap;margin-bottom:2px;}
.active-badge{
  display:flex;align-items:center;gap:3px;
  font-size:.58rem;font-weight:700;color:#4ade80;
  padding:1px 6px;border-radius:8px;
  background:rgba(34,197,94,.1);border:1px solid rgba(34,197,94,.25);
}
.abdt{width:4px;height:4px;border-radius:50%;background:#4ade80;animation:pulse 2s infinite;}
.rem-slots{font-size:.6rem;color:var(--avail);}

/* room footer */
.rfooter{
  display:flex;justify-content:space-between;align-items:center;
  padding:5px 11px 6px 15px;
  border-top:1px solid rgba(255,255,255,.04);
  background:rgba(0,0,0,.18);
}
.rtot{font-size:.65rem;color:var(--muted);}
.rtot strong{color:var(--text);}
.rbadge{
  font-size:.58rem;font-weight:700;padding:2px 6px;border-radius:9px;
  text-transform:uppercase;letter-spacing:.4px;
}
.sf .rbadge{background:var(--full-dim);   color:var(--full);   border:1px solid rgba(239,68,68,.3);}
.sp .rbadge{background:var(--partial-dim);color:var(--partial);border:1px solid rgba(249,115,22,.3);}
.sa .rbadge{background:var(--avail-dim);  color:var(--avail);  border:1px solid rgba(34,197,94,.3);}
.sn .rbadge{background:var(--nodata-dim); color:var(--nodata); border:1px solid rgba(71,85,105,.3);}

/* ── CHARTS ── */
.charts-row{
  display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));
  gap:14px;margin-top:26px;
}
.cbox{background:var(--card);border:1px solid var(--border);border-radius:14px;padding:18px;}
.ctitle{font-size:.82rem;font-weight:700;margin-bottom:14px;display:flex;align-items:center;gap:7px;}

/* ── TOOLTIP ── */
#tt{
  position:fixed;z-index:9999;pointer-events:none;
  background:#0c1929;border:1px solid #1e2d42;border-radius:14px;
  padding:13px 15px;max-width:340px;min-width:230px;
  box-shadow:0 24px 64px rgba(0,0,0,.75),0 0 0 1px rgba(255,255,255,.04);
  opacity:0;transition:opacity .12s;font-size:.78rem;line-height:1.5;
}
#tt.vis{opacity:1;}
.tth{display:flex;justify-content:space-between;align-items:center;margin-bottom:9px;gap:8px;}
.tts{font-size:.92rem;font-weight:800;}
.ttu{font-size:.63rem;font-weight:700;padding:2px 8px;border-radius:9px;flex-shrink:0;}
.ttdiv{border:none;border-top:1px solid var(--border);margin:7px 0;}
.ttblk{
  background:rgba(255,255,255,.025);border:1px solid var(--border);
  border-radius:9px;padding:7px 9px;margin-bottom:5px;
}
.ttblk:last-child{margin-bottom:0;}
.ttbh{display:flex;justify-content:space-between;align-items:center;margin-bottom:4px;}
.ttturno{font-size:.7rem;font-weight:800;color:#a5b4fc;}
.tttocc{font-size:.65rem;font-weight:700;}
.ttprow{display:flex;justify-content:space-between;align-items:center;font-size:.68rem;margin-top:2px;}
.ttprof{color:var(--muted);}
.ttocc{font-weight:700;}
.ttcurso{font-size:.63rem;color:#818cf8;margin-top:2px;}
.ttper{font-size:.6rem;color:var(--muted);margin-top:1px;}
.ttmb{height:3px;border-radius:2px;background:rgba(255,255,255,.07);margin-top:3px;}
.ttmf{height:100%;border-radius:2px;}

/* ── RESPONSIVE ── */
@media(max-width:640px){
  .page{padding:12px 12px 32px;}
  .topnav{padding:0 12px;gap:8px;}
  .nav-sub,.nav-div{display:none;}
  .bstats{display:none;}
  .lgrow{display:none;}
  .strip{gap:6px;}
  .sv{font-size:1.4rem;}
  .sgrid{grid-template-columns:1fr 1fr;}
}
"""

JS = r"""
const DATA   = __DATA_PLACEHOLDER__;
const TODAY  = new Date(2026,2,10);

const UNITS = ['CECAN','HLA','POL'];
const UMETA = {
  CECAN:{icon:'🔬',label:'Centro Avançado de Oncologia',color:'var(--cecan)'},
  HLA:  {icon:'🏨',label:'Hospital Luís Antônio',  color:'var(--hla)'},
  POL:  {icon:'🏥',label:'Policlínica',             color:'var(--pol)'},
};

const PGROUPS = [
  {k:'TEC_ENF', l:'Técnico de Enfermagem',    i:'🩺',  m:p=>p.includes('TÉCNICO DE ENFERMAGEM')},
  {k:'ENF',     l:'Enfermeiro / Enfermagem',   i:'👩‍⚕️', m:p=>p.includes('ENFERMEIRO')||(p.includes('ENFERMAGEM')&&!p.includes('TÉCNICO'))},
  {k:'RAD',     l:'Técnico de Radiologia',     i:'☢️',  m:p=>p.includes('RADIOLOG')},
  {k:'FARM',    l:'Farmácia / Farmacêutico',   i:'💊',  m:p=>p.includes('FARM')},
  {k:'NUTRI',   l:'Nutrição / Nutricionista',  i:'🥗',  m:p=>p.includes('NUTRI')},
  {k:'PSICO',   l:'Psicologia',                i:'🧠',  m:p=>p.includes('PSICO')},
  {k:'FISIO',   l:'Fisioterapia',              i:'🦽',  m:p=>p.includes('FISIO')},
  {k:'BIOMED',  l:'Biomedicina',               i:'🔬',  m:p=>p.includes('BIOMED')},
  {k:'SOCIAL',  l:'Assistente Social',         i:'🤝',  m:p=>p.includes('SOCIAL')},
  {k:'OUTROS',  l:'Outros',                    i:'📋',  m:()=>true},
];

const TABBR = {'MANHÃ':'MAN','TARDE':'TAR','NOITE':'NOI','INTERMEDIÁRIO':'INT'};

let sheet='MARÇO', aUnit='ALL', srch='', charts={};

/* ── STATE HELPERS ── */
function sd(){ return DATA[sheet]||[]; }

function gst(cap,occ){
  if(occ===null||occ===undefined||cap===0) return 'n';
  if(occ===0) return 'a';
  if(occ<cap)  return 'p';
  return 'f';
}
function stlbl(s){ return {f:'Lotado',p:'Parcial',a:'Disponível',n:'Sem dados'}[s]; }
function stcol(s){ return {f:'var(--full)',p:'var(--partial)',a:'var(--avail)',n:'var(--nodata)'}[s]; }
function stcls(s){ return {f:'sf',p:'sp',a:'sa',n:'sn'}[s]; }
function lcls(s){  return {f:'lf',p:'lp',a:'la',n:'ln'}[s]; }

function parseBR(str){
  if(!str) return null;
  const m=str.trim().match(/(\d{1,2})\/(\d{1,2})\/(\d{4})/);
  if(!m) return null;
  return new Date(+m[3],+m[2]-1,+m[1]);
}
function isActive(per){
  if(!per||per==='PENDENTE') return false;
  const sp = per.includes(' - ')?' - ':'-';
  const pt = per.split(sp);
  const s=parseBR(pt[0]), e=parseBR(pt[pt.length-1]);
  if(!s||!e) return false;
  return TODAY>=s && TODAY<=e;
}

function sectTotals(rows){
  const cap=rows.reduce((s,r)=>s+(r.capacidade||0),0);
  const occ=rows.reduce((s,r)=>s+(r.ocupacao||0),0);
  const hasOcc=rows.some(r=>r.ocupacao!==null);
  const st=gst(cap, hasOcc?occ:null);
  const pct=cap>0?Math.min(100,Math.round(occ/cap*100)):0;
  return {cap,occ,st,pct};
}

function bldTotals(rows){
  const sm=groupS(rows);
  let f=0,p=0,a=0,n=0,tC=0,tO=0;
  sm.forEach(sr=>{
    const t=sectTotals(sr);
    tC+=t.cap; tO+=t.occ;
    if(t.st==='f')f++; else if(t.st==='p')p++; else if(t.st==='a')a++; else n++;
  });
  return{sectors:sm.size,full:f,partial:p,avail:a,nodata:n,
    tCap:tC,tOcc:tO,pct:tC>0?Math.min(100,Math.round(tO/tC*100)):0};
}

function groupS(rows){
  const m=new Map();
  rows.forEach(r=>{
    if(!r.setor) return;
    if(!m.has(r.setor)) m.set(r.setor,[]);
    m.get(r.setor).push(r);
  });
  return m;
}

function groupU(rows){
  const m={};
  rows.forEach(r=>{ if(!r.unidade) return; if(!m[r.unidade])m[r.unidade]=[]; m[r.unidade].push(r); });
  return m;
}

function domGroup(srows){
  const cnt=new Map();
  srows.forEach(r=>{
    PGROUPS.forEach(g=>{
      if(g.k!=='OUTROS'&&g.m(r.profissional||'')){
        cnt.set(g.k,(cnt.get(g.k)||0)+(r.capacidade||1));
      }
    });
  });
  let dom='OUTROS',mx=0;
  cnt.forEach((v,k)=>{ if(v>mx){mx=v;dom=k;} });
  return dom;
}

/* ── RING SVG ── */
function ring(pct,color){
  const R=20,C=26,ci=2*Math.PI*R;
  const d=(pct/100)*ci;
  return `<div class="ring">
    <svg width="52" height="52" viewBox="0 0 52 52">
      <circle cx="${C}" cy="${C}" r="${R}" fill="none" stroke="rgba(255,255,255,.06)" stroke-width="5"/>
      <circle cx="${C}" cy="${C}" r="${R}" fill="none" stroke="${color}" stroke-width="5"
        stroke-dasharray="${d.toFixed(1)} ${ci.toFixed(1)}" stroke-linecap="round"/>
    </svg>
    <div class="rp" style="color:${color}">${pct}%</div>
  </div>`;
}

/* ── ROOM CARD ── */
function roomCard(setor, rows, unit) {
  const {cap,occ,st,pct} = sectTotals(rows);
  const cl = stcls(st);
  const hasActive = rows.some(r=>isActive(r.periodo));

  // Shift lanes
  const tmap=new Map();
  rows.forEach(r=>{ const k=r.turno||'N/A'; if(!tmap.has(k))tmap.set(k,[]); tmap.get(k).push(r); });

  let lanes='';
  tmap.forEach((tr,turno)=>{
    const tC=tr.reduce((s,r)=>s+(r.capacidade||0),0);
    const tO=tr.reduce((s,r)=>s+(r.ocupacao||0),0);
    const tH=tr.some(r=>r.ocupacao!==null);
    const tSt=gst(tC,tH?tO:null);
    const tPct=tC>0?Math.min(100,Math.round(tO/tC*100)):0;
    const ab=TABBR[turno]||turno.substring(0,3).toUpperCase();
    lanes+=`<div class="sl ${lcls(tSt)}">
      <span class="slbl">${ab}</span>
      <div class="sbwrap"><div class="sbar" style="width:${tPct}%"></div></div>
      <span class="socc">${tO.toFixed(0)}/${tC.toFixed(0)}</span>
    </div>`;
  });

  const ttt = encodeURIComponent(JSON.stringify({setor,unit,rows}));
  const actB = hasActive?`<div class="active-badge"><div class="abdt"></div>ATIVO</div>`:'';
  const rem  = Math.max(0,cap-occ);
  const remB = (st==='p'||st==='a')&&rem>0?`<span class="rem-slots">+${rem.toFixed(0)} livre${rem>1?'s':''}</span>`:'';

  return `<div class="room ${cl}" data-tt="${ttt}"
      onmouseenter="showTT(event,this)" onmouseleave="hideTT()" onmousemove="movTT(event)">
    <div class="ri">
      <div class="rnamrow">
        <div class="rname">${setor}</div>
        <div class="rdot"></div>
      </div>
      <div class="slanes">${lanes}</div>
      <div class="rextras">${actB}${remB}</div>
    </div>
    <div class="rfooter">
      <div class="rtot"><strong>${occ.toFixed(0)}</strong>/${cap.toFixed(0)} vagas</div>
      <div class="rbadge">${stlbl(st)}</div>
    </div>
  </div>`;
}

/* ── BUILDING ── */
function buildingCard(unit, rows) {
  const mt  = UMETA[unit]||{icon:'🏢',label:unit,color:'#6b7f99'};
  const bt  = bldTotals(rows);
  const sm  = groupS(rows);

  // group sectors by dominant professional category
  const byGrp = new Map();
  PGROUPS.forEach(g=>byGrp.set(g.k,[]));

  sm.forEach((srows,setor)=>{
    if(srch && !setor.toLowerCase().includes(srch)) return;
    const dom = domGroup(srows);
    byGrp.get(dom).push({setor,srows});
  });

  let floors='';
  PGROUPS.forEach(g=>{
    const items=byGrp.get(g.k)||[];
    if(!items.length) return;
    floors+=`<div class="floor">
      <div class="ftitle">
        <span>${g.i}</span>${g.l}
        <span style="font-size:.6rem;opacity:.45;">(${items.length})</span>
      </div>
      <div class="sgrid">
        ${items.map(({setor,srows})=>roomCard(setor,srows,unit)).join('')}
      </div>
    </div>`;
  });

  if(!floors) floors='<div style="color:var(--muted);font-size:.78rem;padding:10px 0">Nenhum setor encontrado.</div>';

  const statsBar=`
    <div class="bstat"><div class="bstat-v" style="color:var(--full)">${bt.full}</div><div class="bstat-l">Lotados</div></div>
    <div class="bstat"><div class="bstat-v" style="color:var(--partial)">${bt.partial}</div><div class="bstat-l">Parciais</div></div>
    <div class="bstat"><div class="bstat-v" style="color:var(--avail)">${bt.avail}</div><div class="bstat-l">Disponíveis</div></div>
    <div class="bstat"><div class="bstat-v">${bt.sectors}</div><div class="bstat-l">Setores</div></div>
    ${ring(bt.pct,mt.color)}
  `;

  return `<div class="building" data-u="${unit}">
    <div class="bh">
      <div class="bico">${mt.icon}</div>
      <div class="binfo">
        <div class="bname">${unit}</div>
        <div class="bsub">${mt.label} &bull; ${bt.sectors} setores &bull; ${bt.tOcc.toFixed(0)}/${bt.tCap.toFixed(0)} vagas</div>
      </div>
      <div class="bstats">${statsBar}</div>
    </div>
    <div class="bb">${floors}</div>
  </div>`;
}

/* ── SUMMARY ── */
function renderSum() {
  const d=sd(), fl=aUnit==='ALL'?d:d.filter(r=>r.unidade===aUnit);
  const sm=groupS(fl);
  let f=0,p=0,a=0,n=0,tC=0,tO=0;
  sm.forEach(sr=>{
    const t=sectTotals(sr);
    tC+=t.cap;tO+=t.occ;
    if(t.st==='f')f++;else if(t.st==='p')p++;else if(t.st==='a')a++;else n++;
  });
  document.getElementById('strip').innerHTML=`
    <div class="sc tot"><div class="sv">${sm.size}</div><div class="sl">🗂 Setores</div></div>
    <div class="sc ful"><div class="sv">${f}</div><div class="sl">🔴 Lotados</div></div>
    <div class="sc par"><div class="sv">${p}</div><div class="sl">🟠 Parciais</div></div>
    <div class="sc ava"><div class="sv">${a}</div><div class="sl">🟢 Disponíveis</div></div>
    <div class="sc cap"><div class="sv">${tC.toFixed(0)}</div><div class="sl">💺 Capacidade</div></div>
    <div class="sc occ"><div class="sv">${tO.toFixed(0)}</div><div class="sl">📌 Ocupadas</div></div>
  `;
}

/* ── CAMPUS ── */
function renderCampus() {
  const d=sd(), byU=groupU(d);
  let h='';
  UNITS.forEach(u=>{
    if(!byU[u]) return;
    if(aUnit!=='ALL'&&aUnit!==u) return;
    h+=buildingCard(u,byU[u]);
  });
  document.getElementById('campus').innerHTML=h||'<div style="text-align:center;color:var(--muted);padding:60px">Nenhum dado.</div>';
}

/* ── CHARTS ── */
function killCharts(){ Object.values(charts).forEach(c=>c&&c.destroy()); charts={}; }

function renderCharts() {
  killCharts();
  const d=sd(), fl=aUnit==='ALL'?d:d.filter(r=>r.unidade===aUnit);
  const sm=groupS(fl);
  let f=0,p=0,a=0,n=0;
  sm.forEach(sr=>{const t=sectTotals(sr);if(t.st==='f')f++;else if(t.st==='p')p++;else if(t.st==='a')a++;else n++;});

  // per-unit %
  const uL=[],uV=[],uC=[];
  UNITS.forEach(u=>{
    const ud=d.filter(r=>r.unidade===u);
    if(!ud.length) return;
    const bt=bldTotals(ud);
    uL.push(u); uV.push(bt.pct);
    uC.push({CECAN:'#a855f7',HLA:'#3b82f6',POL:'#f59e0b'}[u]);
  });

  // courses
  const cc=new Map();
  fl.forEach(r=>{ if(r.curso&&r.ocupacao>0) cc.set(r.curso,(cc.get(r.curso)||0)+1); });
  const sc=[...cc.entries()].sort((a,b)=>b[1]-a[1]).slice(0,8);

  document.getElementById('chartsRow').innerHTML=`
    <div class="cbox"><div class="ctitle"><span>🍩</span>Status dos Setores</div><canvas id="c1" style="max-height:210px"></canvas></div>
    <div class="cbox"><div class="ctitle"><span>📊</span>Ocupação por Unidade (%)</div><canvas id="c2" style="max-height:210px"></canvas></div>
    <div class="cbox"><div class="ctitle"><span>📚</span>Cursos com Maior Presença</div><canvas id="c3" style="max-height:210px"></canvas></div>
  `;

  const DK={color:'#6b7f99',grid:'#1e2d42'};

  charts.c1=new Chart(document.getElementById('c1'),{
    type:'doughnut',
    data:{labels:['Lotado','Parcial','Disponível','Sem dados'],
      datasets:[{data:[f,p,a,n],backgroundColor:['#ef4444','#f97316','#22c55e','#475569'],
        borderColor:'#161f30',borderWidth:3}]},
    options:{responsive:true,cutout:'68%',
      plugins:{legend:{position:'bottom',labels:{color:DK.color,padding:10,font:{size:11}}},
        tooltip:{callbacks:{label:ctx=>` ${ctx.label}: ${ctx.parsed}`}}}}
  });

  charts.c2=new Chart(document.getElementById('c2'),{
    type:'bar',
    data:{labels:uL,datasets:[{label:'%',data:uV,
      backgroundColor:uC.map(c=>c+'55'),borderColor:uC,borderWidth:2,borderRadius:10}]},
    options:{responsive:true,plugins:{legend:{display:false}},
      scales:{y:{min:0,max:100,grid:{color:DK.grid},ticks:{color:DK.color,callback:v=>v+'%'}},
        x:{grid:{display:false},ticks:{color:DK.color}}}}
  });

  charts.c3=new Chart(document.getElementById('c3'),{
    type:'bar',
    data:{labels:sc.map(([k])=>k.length>26?k.substring(0,25)+'…':k),
      datasets:[{data:sc.map(([,v])=>v),
        backgroundColor:'rgba(168,85,247,.4)',borderColor:'#a855f7',borderWidth:2,borderRadius:7}]},
    options:{indexAxis:'y',responsive:true,plugins:{legend:{display:false}},
      scales:{x:{grid:{color:DK.grid},ticks:{color:DK.color}},
        y:{grid:{display:false},ticks:{color:DK.color,font:{size:10}}}}}
  });
}

/* ── TOOLTIP ── */
const tt=document.getElementById('tt');
function showTT(e,el){
  const {setor,unit,rows}=JSON.parse(decodeURIComponent(el.dataset.tt));
  const uc={CECAN:'var(--cecan)',HLA:'var(--hla)',POL:'var(--pol)'}[unit]||'#6b7f99';
  const tmap=new Map();
  rows.forEach(r=>{ const k=r.turno||'N/A'; if(!tmap.has(k))tmap.set(k,[]); tmap.get(k).push(r); });
  let blks='';
  tmap.forEach((tr,turno)=>{
    const tC=tr.reduce((s,r)=>s+(r.capacidade||0),0);
    const tO=tr.reduce((s,r)=>s+(r.ocupacao||0),0);
    const tH=tr.some(r=>r.ocupacao!==null);
    const tSt=gst(tC,tH?tO:null);
    const tPct=tC>0?Math.min(100,Math.round(tO/tC*100)):0;
    const sc=stcol(tSt);
    const prows=tr.map(r=>{
      const o=r.ocupacao!==null?r.ocupacao:'—';
      const p2=r.capacidade>0&&r.ocupacao!==null?Math.min(100,Math.round(r.ocupacao/r.capacidade*100)):0;
      const rsc=stcol(gst(r.capacidade,r.ocupacao));
      return `<div class="ttprow"><span class="ttprof">${r.profissional}</span><span class="ttocc" style="color:${rsc}">${o}/${r.capacidade}</span></div>
        <div class="ttmb"><div class="ttmf" style="width:${p2}%;background:${rsc}"></div></div>
        ${r.curso?`<div class="ttcurso">📚 ${r.curso}</div>`:''}
        ${r.periodo?`<div class="ttper">📅 ${r.periodo}${isActive(r.periodo)?' <span style="color:#4ade80">● ativo</span>':''}</div>`:''}
        ${r.tipo_ocupacao?`<div class="ttper">🔖 ${r.tipo_ocupacao}</div>`:''}`;
    }).join('');
    blks+=`<div class="ttblk">
      <div class="ttbh">
        <span class="ttturno">⏱ ${turno}</span>
        <span class="tttocc" style="color:${sc}">${tO.toFixed(0)}/${tC.toFixed(0)} (${tPct}%)</span>
      </div>${prows}
    </div>`;
  });
  tt.innerHTML=`<div class="tth">
    <span class="tts">${setor}</span>
    <span class="ttu" style="background:${uc}22;color:${uc};border:1px solid ${uc}44">${unit}</span>
  </div><hr class="ttdiv"/>${blks}`;
  movTT(e); tt.classList.add('vis');
}
function hideTT(){ tt.classList.remove('vis'); }
function movTT(e){
  const pd=14,w=tt.offsetWidth||300,h=tt.offsetHeight||200;
  let x=e.clientX+pd, y=e.clientY+pd;
  if(x+w>window.innerWidth-pd)  x=e.clientX-w-pd;
  if(y+h>window.innerHeight-pd) y=e.clientY-h-pd;
  tt.style.left=x+'px'; tt.style.top=y+'px';
}

/* ── EVENTS ── */
document.getElementById('mTabs').addEventListener('click',e=>{
  const b=e.target.closest('.nt'); if(!b) return;
  document.querySelectorAll('.nt').forEach(x=>x.classList.remove('active'));
  b.classList.add('active'); sheet=b.dataset.s; renderAll();
});
document.getElementById('uFilter').addEventListener('click',e=>{
  const b=e.target.closest('.upill'); if(!b) return;
  document.querySelectorAll('.upill').forEach(x=>x.classList.remove('active'));
  b.classList.add('active'); aUnit=b.dataset.u; renderAll();
});
document.getElementById('srchI').addEventListener('input',e=>{
  srch=e.target.value.toLowerCase().trim(); renderCampus();
});

/* ── INIT ── */
function renderAll(){ renderSum(); renderCampus(); renderCharts(); }
renderAll();
"""

HTML = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1"/>
<title>LIGA — Mapeamento de Campos Práticos</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.3/dist/chart.umd.min.js"></script>
<style>{CSS}</style>
</head>
<body>

<nav class="topnav">
  <div class="nav-logo"><span class="ni">🏥</span>LIGA</div>
  <div class="nav-div"></div>
  <div class="nav-sub">Mapeamento de Campos Práticos</div>
  <div class="nav-div"></div>
  <div class="nav-tabs" id="mTabs">
    <button class="nt" data-s="JANEIRO(PLANEJAMENTO)">Jan · Planejamento</button>
    <button class="nt" data-s="FEVEREIRO (PLANEJAMENTO)">Fev · Planejamento</button>
    <button class="nt consolidated active" data-s="MARÇO">Mar · Consolidado ✓</button>
  </div>
  <div class="nav-sp"></div>
  <div class="nav-srch">
    <span class="si">🔍</span>
    <input type="text" id="srchI" placeholder="Buscar setor…"/>
  </div>
  <div class="live-badge"><div class="ldot"></div>10/03/2026</div>
</nav>

<div class="page">
  <div class="strip" id="strip"></div>

  <div class="ubar" id="uFilter">
    <button class="upill all active" data-u="ALL">🏢 Todas as Unidades</button>
    <button class="upill" data-u="CECAN"><span style="color:var(--cecan)">■</span> CECAN</button>
    <button class="upill" data-u="HLA"><span style="color:var(--hla)">■</span> HLA</button>
    <button class="upill" data-u="POL"><span style="color:var(--pol)">■</span> POL</button>
    <div class="lgrow">
      <div class="lg"><div class="lgd" style="background:var(--full)"></div>Lotado</div>
      <div class="lg"><div class="lgd" style="background:var(--partial)"></div>Parcial</div>
      <div class="lg"><div class="lgd" style="background:var(--avail)"></div>Disponível</div>
      <div class="lg"><div class="lgd" style="background:var(--nodata)"></div>Sem dados</div>
    </div>
  </div>

  <div class="campus" id="campus"></div>
  <div class="charts-row" id="chartsRow"></div>
</div>

<div id="tt"></div>

<script>
{JS.replace('__DATA_PLACEHOLDER__', data_json_str)}
</script>
</body>
</html>"""

out = BASE / 'dashboard.html'
out.write_text(HTML, encoding='utf-8')
print(f"✅  dashboard.html  ({len(HTML)//1024} KB)")
