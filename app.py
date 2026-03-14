"""
app.py — Servidor de produção LIGA Campos Práticos
───────────────────────────────────────────────────────────────────────────────
• GET /           → dashboard.html
• GET /api/data   → JSON com dados das 3 abas do Google Sheets (cache 5 min)

Deploy: Render (render.yaml)
Dev local: python app.py
───────────────────────────────────────────────────────────────────────────────
"""

import csv
import io
import json
import os
import time
from urllib.parse import quote

import gspread

from flask import Flask, jsonify, send_from_directory, Response

app = Flask(__name__, static_folder=None)

# ── CONFIG ────────────────────────────────────────────────────────────────────
SHEET_ID   = "1SFRlXmO_xmcD1HGnMN4LmALch2tkKGNlGFoOHtu5VYM"
SHEET_TABS = [
    "MARÇO",
    "FEVEREIRO (PLANEJAMENTO)",
    "JANEIRO(PLANEJAMENTO)",
]
CACHE_TTL  = 300   # 5 minutos
BASE_DIR   = os.path.dirname(os.path.abspath(__file__))

# ── IN-MEMORY CACHE ───────────────────────────────────────────────────────────
_cache: dict = {"data": None, "ts": 0.0}


def _to_float(val: str):
    v = val.strip()
    if not v or v.upper() in ("NONE", "N/A", "-", ""):
        return None
    try:
        return float(v.replace(",", "."))
    except ValueError:
        return None


def _parse_sheet(rows: list[list[str]]) -> list[dict]:
    """
    Linha 0 → título (ignorar)
    Linha 1 → cabeçalhos (ignorar)
    Linha 2+ → dados
    """
    data = []
    for i, row in enumerate(rows):
        if i < 2:
            continue
        row = (row + [""] * 10)[:10]
        unidade, setor, turno, prof, cap_s, occ_s, curso, aluno, tipo, periodo = row

        unidade = unidade.strip().upper()
        if not unidade or unidade in ("UNIDADE", "UNNAMED: 0"):
            continue
        setor  = setor.strip()
        turno  = turno.strip().upper()
        prof   = prof.strip().upper()
        if not setor and not prof:
            continue

        cap = _to_float(cap_s)
        occ = _to_float(occ_s)

        data.append({
            "unidade":       unidade,
            "setor":         setor,
            "turno":         turno,
            "profissional":  prof,
            "capacidade":    cap if cap is not None else 0.0,
            "ocupacao":      occ,
            "curso":         curso.strip(),
            "tipo_ocupacao": tipo.strip(),
            "periodo":       periodo.strip(),
            "aluno":         aluno.strip(),
        })
    return data


def _fetch_from_sheets() -> dict:
    """Busca dados frescos do Google Sheets usando gspread e retorna o dict completo."""
    try:
        # Autentica na Google API usando a service account fornecida
        # 1. Tenta carregar através de Variável de Ambiente (seguro para o Render)
        gcp_cred_env = os.environ.get('GCP_CREDENTIALS')
        if gcp_cred_env:
            import json
            creds_dict = json.loads(gcp_cred_env)
            gc = gspread.service_account_from_dict(creds_dict)
        else:
            # 2. Fallback para arquivo local (para desenvolvimento local)
            cred_path = os.path.join(BASE_DIR, 'gen-lang-client-0965804770-1b0674d6e028.json')
            gc = gspread.service_account(filename=cred_path)
            
        sh = gc.open_by_key(SHEET_ID)
        
        all_data = {}
        for worksheet in sh.worksheets():
            tab = worksheet.title
            rows = worksheet.get_all_values()
            all_data[tab] = _parse_sheet(rows)
            
        return all_data
    except Exception as e:
        print(f"[LIGA] Erro ao buscar dados do Google Sheets API via gspread: {e}")
        # Tentar reverter fallback em caso extremo ou retornar o que tem no momento (vazio)
        return {}


def get_data() -> dict:
    """Retorna dados do cache ou busca novos se o cache expirou."""
    now = time.monotonic()
    if _cache["data"] is not None and (now - _cache["ts"]) < CACHE_TTL:
        return _cache["data"]

    data = _fetch_from_sheets()
    _cache["data"] = data
    _cache["ts"]   = now
    return data


# ── ROUTES ────────────────────────────────────────────────────────────────────

@app.route("/")
@app.route("/index.html")
def index():
    return send_from_directory(BASE_DIR, "dashboard.html")


@app.route("/api/data")
def api_data():
    try:
        data = get_data()
    except Exception as e:
        return jsonify({"error": str(e)}), 502

    # Headers anti-cache para forçar fetch a cada visita,
    # mas o JS usa sessionStorage para cache de 5 min no lado cliente.
    resp = Response(
        json.dumps(data, ensure_ascii=False),
        mimetype="application/json;charset=utf-8",
    )
    resp.headers["Cache-Control"] = "no-store"
    return resp


@app.route("/api/refresh", methods=["POST"])
def api_refresh():
    """Limpa o cache do servidor — útil pós-edição da planilha."""
    _cache["data"] = None
    _cache["ts"]   = 0.0
    return jsonify({"ok": True, "message": "Cache limpo — próxima requisição buscará dados frescos."})


@app.route("/health")
def health():
    cached = _cache["data"] is not None
    age    = int(time.monotonic() - _cache["ts"]) if cached else -1
    return jsonify({"status": "ok", "cache_age_s": age, "cache_valid": cached})


# ── RUN LOCAL ─────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8788))
    print(f"[LIGA] Servidor local em http://localhost:{port}")
    app.run(host="0.0.0.0", port=port, debug=True)
