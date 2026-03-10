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


def fetch_csv(sheet_name: str) -> list[list[str]]:
    """Baixa a aba como CSV via URL pública de exportação do Google Sheets."""
    try:
        import requests
    except ImportError:
        print("Instalando 'requests'...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "requests", "-q"])
        import requests

    url = (
        f"https://docs.google.com/spreadsheets/d/{SHEET_ID}"
        f"/gviz/tq?tqx=out:csv&sheet={quote(sheet_name)}"
    )
    print(f"  ↓ Buscando aba '{sheet_name}'...")
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


def parse_sheet(rows: list[list[str]]) -> list[dict]:
    """
    Estrutura das abas:
      Linha 0 → título geral (ignorar)
      Linha 1 → cabeçalhos: UNIDADE | SETOR | TURNO | PROFISSIONAL |
                             CAPACIDADE | OCUPAÇÃO | CURSO | TIPO DE OCUPAÇÃO | PERÍODO
      Linha 2+ → dados
    """
    data = []
    for i, row in enumerate(rows):
        if i < 2:
            continue
        # Garantir que a linha tenha colunas suficientes
        row = (row + [""] * 9)[:9]
        unidade, setor, turno, profissional, cap_s, occ_s, curso, tipo, periodo = row

        unidade    = unidade.strip().upper()
        setor      = setor.strip()
        turno      = turno.strip().upper()
        profissional = profissional.strip().upper()
        curso      = curso.strip()
        tipo       = tipo.strip()
        periodo    = periodo.strip()

        # Pular linhas de cabeçalho repetido ou vazias
        if not unidade or unidade in ("UNIDADE", "UNNAMED: 0"):
            continue
        if not setor and not profissional:
            continue

        cap = to_float(cap_s)
        occ = to_float(occ_s)

        data.append({
            "unidade":      unidade,
            "setor":        setor,
            "turno":        turno,
            "profissional": profissional,
            "capacidade":   cap if cap is not None else 0.0,
            "ocupacao":     occ,
            "curso":        curso,
            "tipo_ocupacao": tipo,
            "periodo":      periodo,
        })
    return data


def main():
    print("═" * 60)
    print(" LIGA — Sincronizando dados do Google Sheets")
    print("═" * 60)

    all_data = {}
    for tab in SHEET_TABS:
        try:
            rows   = fetch_csv(tab)
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
