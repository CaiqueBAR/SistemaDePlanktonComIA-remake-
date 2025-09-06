import sys
import os
import subprocess
import logging

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("fix_numpy.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("fix_numpy")

def check_numpy():
    """Verifica se o NumPy está instalado e funcionando corretamente."""
    try:
        import numpy
        logger.info(f"NumPy está instalado. Versão: {numpy.__version__}")
        return True
    except ImportError as e:
        logger.error(f"Erro ao importar NumPy: {str(e)}")
        return False

def install_numpy():
    """Instala ou reinstala o NumPy."""
    try:
        logger.info("Tentando instalar/reinstalar NumPy...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "--force-reinstall", "numpy"])
        logger.info("NumPy reinstalado com sucesso.")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Erro ao instalar NumPy: {str(e)}")
        return False

def fix_numpy_import_in_file(file_path):
    """Corrige a importação do NumPy em um arquivo Python."""
    if not os.path.exists(file_path):
        logger.error(f"Arquivo não encontrado: {file_path}")
        return False
        
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
            
        # Verifica se já existe importação do NumPy
        if 'import numpy as np' in content:
            # Tenta mover a importação para o início do arquivo, após os imports do sistema
            lines = content.split('\n')
            numpy_import = 'import numpy as np'
            
            # Remove a importação existente
            lines = [line for line in lines if 'import numpy as np' not in line]
            
            # Encontra a posição ideal para inserir (após os imports do sistema)
            insert_pos = 0
            for i, line in enumerate(lines):
                if line.startswith('import ') or line.startswith('from '):
                    insert_pos = i + 1
                elif line.strip() == '' and insert_pos > 0:
                    break
                    
            # Insere a importação na posição correta
            lines.insert(insert_pos, numpy_import)
            
            # Reescreve o arquivo
            with open(file_path, 'w', encoding='utf-8') as file:
                file.write('\n'.join(lines))
                
            logger.info(f"Importação do NumPy reorganizada em: {file_path}")
            return True
        else:
            logger.warning(f"Importação do NumPy não encontrada em: {file_path}")
            return False
    except Exception as e:
        logger.error(f"Erro ao modificar arquivo {file_path}: {str(e)}")
        return False

def main():
    """Função principal para corrigir problemas com o NumPy."""
    logger.info("Iniciando verificação e correção do NumPy...")
    
    # Verificar se o NumPy está instalado
    if not check_numpy():
        # Tentar reinstalar
        if not install_numpy():
            logger.error("Não foi possível instalar o NumPy. Verifique sua conexão e permissões.")
            return False
    
    # Verificar novamente após a instalação
    if not check_numpy():
        logger.error("NumPy ainda não está funcionando corretamente após a reinstalação.")
        return False
    
    # Corrigir importações nos arquivos principais
    files_to_fix = [
        "plankton_ai.py",
        "flask_server.py"
    ]
    
    for file in files_to_fix:
        fix_numpy_import_in_file(file)
    
    logger.info("Processo de correção do NumPy concluído.")
    return True

if __name__ == "__main__":
    success = main()
    if success:
        print("\nNumPy verificado e corrigido com sucesso!")
    else:
        print("\nHouve problemas ao corrigir o NumPy. Verifique o arquivo de log para mais detalhes.")