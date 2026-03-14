import os
import openpyxl
import gspread
from google.oauth2.service_account import Credentials

# --- CONFIG ---
EXCEL_FILE = 'MAPEAMENTO DE CAMPO PRÁTICO (1).xlsx'
SHEET_ID = "1SFRlXmO_xmcD1HGnMN4LmALch2tkKGNlGFoOHtu5VYM"
SHEET_TABS = [
    "MARÇO",
    "FEVEREIRO (PLANEJAMENTO)",
    "JANEIRO(PLANEJAMENTO)",
]
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CRED_PATH = os.path.join(BASE_DIR, 'gen-lang-client-0965804770-1b0674d6e028.json')

# URL do site deployed (Vercel/Render) para limpar o cache automaticamente
LIVE_SITE_URL = "https://liga-campos-praticos.vercel.app" 

def sync():
    print(f"Lendo Excel: {EXCEL_FILE}...")
    wb = openpyxl.load_workbook(EXCEL_FILE, data_only=True)
    
    print("Autenticando com Google Sheets...")
    scope = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
    
    if os.environ.get('GCP_CREDENTIALS'):
        import json
        creds_dict = json.loads(os.environ.get('GCP_CREDENTIALS'))
        creds = Credentials.from_service_account_info(creds_dict, scopes=scope)
    else:
        creds = Credentials.from_service_account_file(CRED_PATH, scopes=scope)
    
    client = gspread.authorize(creds)
    sh = client.open_by_key(SHEET_ID)
    
    for tab_name in SHEET_TABS:
        if tab_name not in wb.sheetnames:
            print(f"  ! Aba '{tab_name}' não encontrada no Excel. Pulando...")
            continue
            
        print(f"  -> Sincronizando aba: {tab_name}")
        excel_sheet = wb[tab_name]
        
        # 1. Tentar ler dados atuais do Google Sheets para preservar ALUNOS
        existing_students = {} # Key: (Unidade, Setor, Turno, Prof) -> Value: Alunos
        try:
            worksheet = sh.worksheet(tab_name)
            current_gs_data = worksheet.get_all_values()
            # Pular cabeçalhos (Linhas 0 e 1 no app.py)
            for i, row in enumerate(current_gs_data):
                if i < 2: continue
                # Colunas: 0:UNIT, 1:SETOR, 2:TURNO, 3:PROF, ..., 7:ALUNOS
                if len(row) > 7:
                    key = (row[0].strip().upper(), row[1].strip().upper(), row[2].strip().upper(), row[3].strip().upper())
                    students = row[7].strip()
                    if students and students not in ("None", ""):
                        existing_students[key] = students
        except gspread.exceptions.WorksheetNotFound:
            print(f"  + Aba '{tab_name}' não existe no Google Sheets. Será criada.")
            worksheet = sh.add_worksheet(title=tab_name, rows="100", cols="20")
        except Exception as e:
            print(f"  ! Aviso: Não foi possível ler dados atuais para preservar alunos: {e}")

        # 2. Extrair dados do Excel e fazer o MERGE
        final_data = []
        for row in excel_sheet.iter_rows(values_only=True):
            # No dashboard LIGA, as colunas esperadas são:
            # 0: UNIDADE | 1: SETOR | 2: TURNO | 3: PROFISSIONAL | 4: CAPACIDADE | 5: OCUPAÇÃO | 6: CURSO | 7: ALUNO (LISTA) | 8: TIPO | 9: PERÍODO
            row_list = [str(cell) if cell is not None else "" for cell in row]
            
            # Garantir 10 colunas
            if len(row_list) < 10:
                row_list += [""] * (10 - len(row_list))
            
            row_list = row_list[:10]
            
            # Se for linha de dados (não título nem cabeçalho vazios)
            if row_list[0] and row_list[0].upper() not in ("UNIDADE", "MAPEAMENTO DE CAMPO PRÁTICO"):
                # Se a célula na coluna H (índice 7) do Excel NÃO estiver no formato {"..."}, 
                # mas tivermos algo vindo do Google Sheets, preservamos o do Sheets.
                # Caso contrário, mantemos o que está no Excel (que agora suporta o formato {"..."})
                key = (row_list[0].strip().upper(), row_list[1].strip().upper(), row_list[2].strip().upper(), row_list[3].strip().upper())
                
                # Prioridade: se o Excel já tem o formato {"..."}, usamos ele.
                # Se não tem, e o Sheets tem algo salvo, usamos o do Sheets.
                excel_val = row_list[7].strip()
                if not (excel_val.startswith('{') and excel_val.endswith('}')):
                    if key in existing_students:
                        row_list[7] = existing_students[key]
            
            final_data.append(row_list)
            
        # 3. Limpar e atualizar dados
        worksheet.clear()
        if final_data:
            worksheet.update('A1', final_data)
            print(f"  ✓ {len(final_data)} linhas sincronizadas (Preservando coluna Aluno).")

    # --- REFRESH LIVE SITE CACHE ---
    if LIVE_SITE_URL:
        print(f"\nNotificando site em {LIVE_SITE_URL} para atualizar cache...")
        try:
            import requests
            refresh_url = f"{LIVE_SITE_URL.rstrip('/')}/api/refresh"
            resp = requests.post(refresh_url, timeout=10)
            if resp.status_code == 200:
                print("  ✓ Cache do site limpo com sucesso!")
            else:
                print(f"  ! Falha ao limpar cache: HTTP {resp.status_code}")
        except Exception as e:
            print(f"  ! Erro ao tentar limpar cache remoto: {e}")

if __name__ == "__main__":
    try:
        sync()
        print("\nSincronização concluída com sucesso!")
    except Exception as e:
        print(f"\nErro na sincronização: {e}")
