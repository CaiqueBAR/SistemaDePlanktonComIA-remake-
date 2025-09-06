import subprocess
import sys
import os
import time
import platform
import signal
import logging

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("flask_launcher.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("flask_launcher")

FLASK_SCRIPT_PATH = os.path.abspath("flask_server.py")

def start_flask_server():
    logger.info("Iniciando o servidor Flask...")
    try:
        # Criar diretório de logs se não existir
        logs_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logs")
        os.makedirs(logs_dir, exist_ok=True)
        
        # Arquivos de log com caminho absoluto
        stdout_path = os.path.join(logs_dir, "flask_server_stdout.log")
        stderr_path = os.path.join(logs_dir, "flask_server_stderr.log")
        
        # Abrir arquivos de log
        stdout_file = open(stdout_path, "w", encoding="utf-8")
        stderr_file = open(stderr_path, "w", encoding="utf-8")
        
        # Configurações específicas para cada sistema operacional
        kwargs = {
            "stdout": stdout_file,
            "stderr": stderr_file,
        }
        
        # Adicionar flags específicas do sistema operacional
        if platform.system() == "Windows":
            # No Windows, usamos DETACHED_PROCESS para desacoplar o processo
            kwargs["creationflags"] = subprocess.CREATE_NEW_PROCESS_GROUP
        else:
            # No Unix/Linux, usamos setsid
            kwargs["preexec_fn"] = os.setsid
            
        # Determinar o caminho do executável Python no ambiente virtual
        if platform.system() == "Windows":
            venv_python = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".venv", "Scripts", "python.exe")
        else:
            venv_python = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".venv", "bin", "python")
            
        # Usar o Python do ambiente virtual se existir, caso contrário usar o Python do sistema
        python_executable = venv_python if os.path.exists(venv_python) else sys.executable
        
        # Configurar o ambiente para incluir o site-packages do ambiente virtual
        env = os.environ.copy()
        if platform.system() == "Windows":
            site_packages = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".venv", "Lib", "site-packages")
        else:
            site_packages = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".venv", "lib", "python" + sys.version[:3], "site-packages")
            
        # Adicionar ao PYTHONPATH se o diretório existir
        if os.path.exists(site_packages):
            if "PYTHONPATH" in env:
                env["PYTHONPATH"] = site_packages + os.pathsep + env["PYTHONPATH"]
            else:
                env["PYTHONPATH"] = site_packages
        
        # Adicionar env ao kwargs
        kwargs["env"] = env
        
        process = subprocess.Popen(
            [python_executable, FLASK_SCRIPT_PATH],
            **kwargs
        )
        logger.info(f"Servidor Flask iniciado com PID: {process.pid}")
        logger.info(f"Logs disponíveis em: {logs_dir}")
        
        # Verificar se o servidor iniciou corretamente (esperar um pouco)
        time.sleep(2)
        if process.poll() is not None:
            # Se o processo já terminou, algo deu errado
            return_code = process.returncode
            logger.error(f"Servidor Flask falhou ao iniciar. Código de retorno: {return_code}")
            return None
            
        return process
    except Exception as e:
        logger.error(f"Erro ao iniciar o servidor Flask: {str(e)}", exc_info=True)
        return None

def stop_flask_server(process):
    """Para o servidor Flask se estiver rodando."""
    if process is None:
        logger.warning("Nenhum servidor Flask em execução para parar.")
        return False
        
    logger.info(f"Parando o servidor Flask (PID: {process.pid})...")
    try:
        if platform.system() == "Windows":
            # No Windows, enviamos CTRL+C para o grupo de processos
            process.send_signal(signal.CTRL_C_EVENT)
        else:
            # No Unix/Linux, enviamos SIGTERM para o grupo de processos
            os.killpg(os.getpgid(process.pid), signal.SIGTERM)
            
        # Esperar o processo terminar (com timeout)
        for _ in range(5):  # Esperar até 5 segundos
            if process.poll() is not None:
                logger.info("Servidor Flask parado com sucesso.")
                return True
            time.sleep(1)
            
        # Se ainda não terminou, força o encerramento
        if platform.system() == "Windows":
            process.send_signal(signal.CTRL_BREAK_EVENT)
        else:
            os.killpg(os.getpgid(process.pid), signal.SIGKILL)
            
        logger.warning("Servidor Flask forçado a parar.")
        return True
    except Exception as e:
        logger.error(f"Erro ao parar o servidor Flask: {str(e)}", exc_info=True)
        return False

def check_server_status(process):
    """Verifica se o servidor Flask está rodando."""
    if process is None:
        return False
        
    # Verifica se o processo ainda está em execução
    return process.poll() is None

if __name__ == "__main__":
    # Este script pode ser executado diretamente para iniciar o servidor.
    # Ele não vai esperar o servidor terminar.
    server_process = start_flask_server()
    
    if server_process:
        logger.info("Servidor Flask iniciado com sucesso.")
        logger.info("Script de inicialização do servidor Flask finalizado. O servidor está rodando em segundo plano.")
        
        # Verificar URL do servidor
        server_url = "http://localhost:5000"
        logger.info(f"Acesse {server_url} para usar a API de reconhecimento de plâncton.")
    else:
        logger.error("Falha ao iniciar o servidor Flask.")


