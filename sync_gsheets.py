"""
sync_gsheets.py
───────────────────────────────────────────────────────────────────────────────
Lê as abas da planilha do Google Sheets (somente leitura) e gera:
  • data.json       → mesmos dados que o extract_data.py produzia
  • dashboard.html  → rebuld automático via builder3.py

Requisito: planilha compartilhada como "qualquer pessoa com o link pode ver"
Instalar: pip install requests
───────────────────────────────────────────────────────────────────────────────
"""

import csv
import io
import json
import subprocess
import sys
import os
from urllib.parse import quote
from collections import defaultdict

if sys.stdout.encoding and sys.stdout.encoding.lower() not in ('utf-8','utf8'):
    sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf-8', buffering=1)

# ── CONFIG ───────────────────────────────────────────────────────────────────
SHEET_ID   = "1SFRlXmO_xmcD1HGnMN4LmALch2tkKGNlGFoOHtu5VYM"
SHEET_TABS = [
    "MARÇO",
    "FEVEREIRO (PLANEJAMENTO)",
    "JANEIRO(PLANEJAMENTO)",
]
OUT_JSON    = os.path.join(os.path.dirname(__file__), "data.json")
BUILDER_PY  = os.path.join(os.path.dirname(__file__), "builder3.py")
# ─────────────────────────────────────────────────────────────────────────────


def fetch_gids(sheet_id: str) -> dict[str, str]:
    """Busca os GIDs de todas as abas públicas a partir do htmlview."""
    import urllib.request
    import re
    url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/htmlview"
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            html = resp.read().decode('utf-8')
        
        matches = re.findall(r'name:\s*"([^"]+)"\s*,\s*pageUrl:\s*"[^"]*gid(?:\\x3d|=)(\d+)"', html)
        if not matches:
            matches = re.findall(r'name:\s*"([^"]+)"[^}]+gid(?:\\x3d|=)(\d+)', html)
            
        gids_map = {}
        for name, gid in matches:
            try:
                decoded_name = name.encode().decode('unicode-escape')
                decoded_name = decoded_name.replace('\\/', '/')
            except Exception:
                decoded_name = name
            gids_map[decoded_name.strip()] = gid
        return gids_map
    except Exception as e:
        print(f"  ⚠ Falha ao obter GIDs dinâmicos da planilha: {e}")
        return {}


def fetch_csv(sheet_name: str, gid: str) -> list[list[str]]:
    """Baixa a aba como CSV via URL pública de exportação do Google Sheets."""
    try:
        import requests
    except ImportError:
        print("Instalando 'requests'...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "requests", "-q"])
        import requests

    url = (
        f"https://docs.google.com/spreadsheets/d/{SHEET_ID}"
        f"/export?format=csv&gid={gid}"
    )
    print(f"  ↓ Buscando aba '{sheet_name}' (GID: {gid})...")
    resp = requests.get(url, timeout=30)

    if resp.status_code == 401 or "Sign in" in resp.text[:200]:
        raise PermissionError(
            "A planilha não está pública.\n"
            "Acesse o Google Sheets → Compartilhar → "
            "'Qualquer pessoa com o link' → Visualizador."
        )
    resp.raise_for_status()
    return list(csv.reader(io.StringIO(resp.text)))


def to_float(val: str):
    """Converte string para float, retorna None se vazio."""
    v = val.strip()
    if not v or v.upper() in ("NONE", "N/A", "-", ""):
        return None
    try:
        return float(v.replace(",", "."))
    except ValueError:
        return None


def parse_alunos(val):
    if not val or not isinstance(val, str):
        return []
    val = val.strip()
    if not val or val.upper() in ("NONE", "N/A", "-", ""):
        return []
    if val.startswith('{') and val.endswith('}'):
        val = val[1:-1].strip()
    parts = val.split(';')
    return [p.replace('"', '').strip() for p in parts if p.strip()]


def parse_sheet(rows: list[list[str]]) -> list[dict]:
    """
    Estrutura das abas:
      Linha 0 → título geral (ignorar)
      Linha 1 → cabeçalhos (usar para detecção de colunas)
      Linha 2+ → dados
    """
    if len(rows) < 2:
        return []

    # Detectar se existe coluna ALUNOS nos cabeçalhos
    header = [str(h).strip().upper() for h in rows[1]]
    has_alunos = "ALUNOS" in header or "ALUNO" in header

    data = []
    for i, row in enumerate(rows):
        if i < 2:
            continue
        row = (row + [""] * 10)[:10]
        
        if has_alunos:
            unidade, setor, turno, profissional, cap_s, occ_s, curso, aluno_raw, tipo, periodo = row
        else:
            unidade, setor, turno, profissional, cap_s, occ_s, curso, tipo, periodo = row[:9]
            aluno_raw = ""

        unidade      = unidade.strip().upper()
        setor        = setor.strip()
        turno        = turno.strip().upper()
        profissional = profissional.strip().upper()
        curso        = curso.strip()
        aluno_raw    = aluno_raw.strip()
        tipo         = tipo.strip()
        periodo      = periodo.strip()

        # Pular linhas de cabeçalho repetido ou vazias
        if not unidade or unidade in ("UNIDADE", "UNNAMED: 0"):
            continue
        if not setor and not profissional:
            continue

        cap = to_float(cap_s)
        occ = to_float(occ_s)
        
        alunos_list = parse_alunos(aluno_raw)

        data.append({
            "unidade":      unidade,
            "setor":        setor,
            "turno":        turno,
            "profissional": profissional,
            "capacidade":   cap if cap is not None else 0.0,
            "ocupacao":     occ,
            "curso":        curso,
            "tipo_ocupacao": tipo if not alunos_list else "ALUNOS LISTADOS",
            "alunos":       alunos_list,
            "periodo":      periodo,
        })
    return data


def main():
    print("═" * 60)
    print(" LIGA — Sincronizando dados do Google Sheets")
    print("═" * 60)

    # Obter GIDs das abas dinamicamente ou usar fallback
    gids_map = fetch_gids(SHEET_ID)
    fallback_gids = {
        "MARÇO": "97400379",
        "FEVEREIRO (PLANEJAMENTO)": "1601275335",
        "JANEIRO(PLANEJAMENTO)": "1900166275",
    }

    all_data = {}
    for tab in SHEET_TABS:
        try:
            gid = gids_map.get(tab) or fallback_gids.get(tab)
            if not gid:
                print(f"  ⚠ GID não encontrado para a aba '{tab}'. Pulando...")
                continue
            rows   = fetch_csv(tab, gid)
            parsed = parse_sheet(rows)
            all_data[tab] = parsed
            print(f"  ✓ '{tab}': {len(parsed)} registros")
        except PermissionError as e:
            print(f"\n⛔ Erro de permissão:\n{e}")
            sys.exit(1)
        except Exception as e:
            print(f"  ⚠ Falha ao buscar '{tab}': {e}")
            all_data[tab] = []

    # ── Gravar data.json ──────────────────────────────────────────────────
    with open(OUT_JSON, "w", encoding="utf-8") as f:
        json.dump(all_data, f, ensure_ascii=False, indent=2)
    print(f"\n✅  data.json gravado  ({os.path.getsize(OUT_JSON) // 1024} KB)")

    # ── Resumo por unidade ────────────────────────────────────────────────
    marco = all_data.get("MARÇO", [])
    if marco:
        print("\n── Resumo MARÇO ──────────────────────────────────────────")
        unidades = defaultdict(set)
        for r in marco:
            unidades[r["unidade"]].add(r["setor"])
        for u, setores in sorted(unidades.items()):
            print(f"  {u}: {len(setores)} setores")

    # ── Rebuild dashboard ─────────────────────────────────────────────────
    if os.path.exists(BUILDER_PY):
        print("\n🔧 Gerando dashboard.html...")
        result = subprocess.run([sys.executable, BUILDER_PY], capture_output=True, text=True)
        if result.returncode == 0:
            out_msg = result.stdout.strip().split("\n")[-1]
            print(f"✅  {out_msg}")
        else:
            print(f"⚠  builder3.py retornou erro:\n{result.stderr}")
    else:
        print(f"\n⚠  builder3.py não encontrado — data.json atualizado, mas dashboard NÃO foi gerado.")

    print("\n✨ Sincronização concluída!\n")


if __name__ == "__main__":
    main()
