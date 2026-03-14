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
LIVE_SITE_URL = "https://liga-campos-praticos.vercel.app" # Ajuste se o domínio for diferente

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
        
        # Extrair dados do Excel (todas as linhas e colunas)
        data = []
        for row in excel_sheet.iter_rows(values_only=True):
            # Converter valores para string para evitar problemas de serialização no gspread
            data.append([str(cell) if cell is not None else "" for cell in row])
        
        # Abrir ou criar a aba no Google Sheets
        try:
            worksheet = sh.worksheet(tab_name)
        except gspread.exceptions.WorksheetNotFound:
            print(f"  + Criando aba '{tab_name}' no Google Sheets...")
            worksheet = sh.add_worksheet(title=tab_name, rows="100", cols="20")
            
        # Limpar e atualizar dados
        worksheet.clear()
        if data:
            worksheet.update('A1', data)
            print(f"  ✓ {len(data)} linhas sincronizadas.")

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
