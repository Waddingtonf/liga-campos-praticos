import os
import time
import subprocess
import sys

# --- CONFIG ---
EXCEL_FILE = 'MAPEAMENTO DE CAMPO PRÁTICO (1).xlsx'
SYNC_SCRIPT = 'excel_to_gsheets.py'
CHECK_INTERVAL_S = 10  # Verificar a cada 10 segundos

def get_mtime(path):
    try:
        return os.path.getmtime(path)
    except FileNotFoundError:
        return None

def main():
    print(f"Monitorando arquivo: {EXCEL_FILE}")
    print(f"Pressione Ctrl+C para parar.")
    
    last_mtime = get_mtime(EXCEL_FILE)
    
    if last_mtime is None:
        print(f"ERRO: Arquivo {EXCEL_FILE} não encontrado.")
        return

    try:
        while True:
            time.sleep(CHECK_INTERVAL_S)
            current_mtime = get_mtime(EXCEL_FILE)
            
            if current_mtime is not None and current_mtime > last_mtime:
                print(f"\n[{time.strftime('%H:%M:%S')}] Mudança detectada no Excel. Sincronizando...")
                
                # Executa o script de sincronização
                try:
                    subprocess.run([sys.executable, SYNC_SCRIPT], check=True)
                    last_mtime = current_mtime
                    print(f"[{time.strftime('%H:%M:%S')}] Sincronização automática finalizada.")
                except subprocess.CalledProcessError as e:
                    print(f"ERRO ao executar sincronização: {e}")
                    # Mantém o mtime antigo para tentar novamente na próxima detecção se necessário?
                    # Ou atualiza para evitar loop de erro? Vamos atualizar para evitar loop infinito de erro.
                    last_mtime = current_mtime
                    
    except KeyboardInterrupt:
        print("\nMonitoramento encerrado pelo usuário.")

if __name__ == "__main__":
    main()
