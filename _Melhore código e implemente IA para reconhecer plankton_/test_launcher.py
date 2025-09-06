import os
import sys
import platform
import time
import argparse
from flask_server_launcher import start_flask_server, stop_flask_server, check_server_status

def test_launcher():
    """Testa o lançador do servidor Flask em diferentes sistemas operacionais."""
    print(f"\n{'='*50}")
    print(f"Teste de Compatibilidade do Lançador Flask")
    print(f"{'='*50}")
    print(f"Sistema Operacional: {platform.system()} {platform.release()}")
    print(f"Python: {sys.version}")
    print(f"Diretório atual: {os.getcwd()}")
    print(f"{'='*50}\n")
    
    # Iniciar o servidor
    print("Iniciando o servidor Flask...")
    server_process = start_flask_server()
    
    if server_process is None:
        print("❌ FALHA: Não foi possível iniciar o servidor Flask.")
        return False
    
    print(f"✅ SUCESSO: Servidor iniciado com PID {server_process.pid}")
    
    # Verificar status
    time.sleep(3)  # Esperar um pouco para o servidor inicializar completamente
    
    if check_server_status(server_process):
        print("✅ SUCESSO: Servidor está rodando corretamente.")
    else:
        print("❌ FALHA: Servidor não está rodando.")
        return False
    
    # Testar conexão com o servidor
    try:
        import requests
        response = requests.get("http://localhost:5000/status", timeout=5)
        if response.status_code == 200:
            print("✅ SUCESSO: API respondeu corretamente.")
            print(f"Informações do modelo: {response.json().get('model_info', {})}")
        else:
            print(f"❌ FALHA: API retornou código {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ FALHA: Não foi possível conectar à API: {str(e)}")
        return False
    
    # Parar o servidor
    print("\nParando o servidor Flask...")
    if stop_flask_server(server_process):
        print("✅ SUCESSO: Servidor parado corretamente.")
    else:
        print("❌ FALHA: Não foi possível parar o servidor.")
        return False
    
    # Verificar se realmente parou
    time.sleep(2)
    if not check_server_status(server_process):
        print("✅ SUCESSO: Servidor está completamente parado.")
    else:
        print("❌ FALHA: Servidor ainda está rodando após tentativa de parada.")
        return False
    
    print(f"\n{'='*50}")
    print("✅ TODOS OS TESTES PASSARAM COM SUCESSO!")
    print(f"{'='*50}\n")
    return True

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Teste de compatibilidade do lançador Flask")
    parser.add_argument("--auto-exit", action="store_true", help="Sair automaticamente após os testes")
    args = parser.parse_args()
    
    success = test_launcher()
    
    if args.auto_exit:
        sys.exit(0 if success else 1)
    else:
        input("Pressione Enter para sair...")