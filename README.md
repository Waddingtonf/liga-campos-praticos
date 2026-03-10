# LIGA — Mapeamento de Campos Práticos

Dashboard interativo para visualização e acompanhamento da ocupação dos campos práticos nas unidades da LIGA Acadêmica: **CECAN**, **HLA** e **Policlínica**.

## Funcionalidades

- **Mapa de unidades** com anéis de ocupação, zoom e pan
- **Visão por setores** agrupados por área profissional (Enfermagem, Radiologia, Farmácia, etc.)
- **Painel de vagas (cinema seats)** — cada assento representa uma vaga, por turno
- **Filtros** por status (Lotado / Parcial / Disponível), turno e situação (ativos)
- **Abas de mês** — Janeiro, Fevereiro e Março
- **Botão Voltar** e breadcrumb para navegação entre níveis
- **Tutorial interativo** (How-to wizard) com 5 passos
- **Barra de vagas** resumida na visão da unidade

## Estrutura

```
builder3.py          ← gerador principal (Python → HTML único)
dashboard.html       ← dashboard gerado (abrir no navegador)
data.json            ← dados extraídos do Excel
MAPEAMENTO DE CAMPO PRÁTICO (1).xlsx  ← fonte de dados original
extract_data.py      ← extração dos dados do Excel para data.json
```

## Como gerar

```bash
# 1. Criar ambiente virtual (uma vez)
python -m venv .venv
.venv\Scripts\activate

# 2. Instalar dependências
pip install openpyxl

# 3. Gerar o dashboard
python builder3.py

# 4. Servir localmente
python -m http.server 8788
# Abrir: http://localhost:8788/dashboard.html
```

## Tecnologias

- **Python 3** — geração do HTML
- **HTML / CSS / JavaScript** puro — sem dependências externas
- CSS Grid, CSS Custom Properties, glassmorphism, animações GPU
- Acessibilidade: ARIA labels, skip link, navegação por teclado (ESC)

---

Trabalho de Conclusão de Curso — Leticia Waddington
