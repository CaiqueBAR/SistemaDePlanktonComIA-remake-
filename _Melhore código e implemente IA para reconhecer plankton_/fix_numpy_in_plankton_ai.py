import sys
import os
import subprocess
import logging

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("fix_numpy_in_plankton_ai.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("fix_numpy_in_plankton_ai")

def modify_plankton_ai():
    """Modifica o arquivo plankton_ai.py para corrigir o problema do NumPy."""
    file_path = "plankton_ai.py"
    
    if not os.path.exists(file_path):
        logger.error(f"Arquivo não encontrado: {file_path}")
        return False
    
    try:
        # Ler o conteúdo do arquivo
        with open(file_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()
        
        # Modificar a importação do NumPy
        modified_lines = []
        numpy_imported = False
        
        for line in lines:
            # Substituir a importação do NumPy
            if 'import numpy as np' in line:
                modified_lines.append("# Importação do NumPy com tratamento de erro\ntry:\n    import numpy as np\nexcept ImportError:\n    print(\"Erro ao importar NumPy. Instalando versão compatível...\")\n    import sys\n    import subprocess\n    subprocess.check_call([sys.executable, \"-m\", \"pip\", \"install\", \"numpy==1.24.3\"])\n    import numpy as np\n")
                numpy_imported = True
            else:
                modified_lines.append(line)
        
        # Se não encontrou a importação do NumPy, adiciona no início
        if not numpy_imported:
            # Encontrar a posição após as importações iniciais
            insert_pos = 0
            for i, line in enumerate(modified_lines):
                if line.startswith('import ') or line.startswith('from '):
                    insert_pos = i + 1
                elif line.strip() == '' and insert_pos > 0:
                    break
            
            # Inserir a importação do NumPy com tratamento de erro
            modified_lines.insert(insert_pos, "\n# Importação do NumPy com tratamento de erro\ntry:\n    import numpy as np\nexcept ImportError:\n    print(\"Erro ao importar NumPy. Instalando versão compatível...\")\n    import sys\n    import subprocess\n    subprocess.check_call([sys.executable, \"-m\", \"pip\", \"install\", \"numpy==1.24.3\"])\n    import numpy as np\n")
        
        # Escrever o conteúdo modificado de volta ao arquivo
        with open(file_path, 'w', encoding='utf-8') as file:
            file.writelines(modified_lines)
        
        logger.info(f"Arquivo {file_path} modificado com sucesso.")
        return True
    
    except Exception as e:
        logger.error(f"Erro ao modificar o arquivo {file_path}: {str(e)}")
        return False

def modify_preprocess_image():
    """Modifica o método preprocess_image para tratar erros do NumPy."""
    file_path = "plankton_ai.py"
    
    if not os.path.exists(file_path):
        logger.error(f"Arquivo não encontrado: {file_path}")
        return False
    
    try:
        # Ler o conteúdo do arquivo
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        
        # Encontrar o método preprocess_image
        preprocess_start = content.find("def preprocess_image")
        if preprocess_start == -1:
            logger.error("Método preprocess_image não encontrado.")
            return False
        
        # Encontrar o bloco try-except dentro do método
        try_start = content.find("try:", preprocess_start)
        if try_start == -1:
            logger.error("Bloco try-except não encontrado no método preprocess_image.")
            return False
        
        # Modificar o bloco try-except para tratar erros do NumPy
        modified_content = content[:try_start] + """try:
            # Verificar se o NumPy está disponível
            try:
                import numpy as np
            except ImportError:
                error_msg = "Numpy is not available"
                logger.error(error_msg)
                return None, error_msg
                
            # Tentar abrir a imagem"""
        
        # Adicionar o restante do conteúdo
        modified_content += content[try_start + 4:]
        
        # Escrever o conteúdo modificado de volta ao arquivo
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(modified_content)
        
        logger.info("Método preprocess_image modificado com sucesso.")
        return True
    
    except Exception as e:
        logger.error(f"Erro ao modificar o método preprocess_image: {str(e)}")
        return False

def main():
    """Função principal para corrigir problemas com o NumPy no plankton_ai.py."""
    logger.info("Iniciando correção do NumPy no plankton_ai.py...")
    
    # Modificar o arquivo plankton_ai.py
    if not modify_plankton_ai():
        logger.error("Falha ao modificar o arquivo plankton_ai.py.")
        return False
    
    # Modificar o método preprocess_image
    if not modify_preprocess_image():
        logger.error("Falha ao modificar o método preprocess_image.")
        return False
    
    logger.info("Correção do NumPy no plankton_ai.py concluída com sucesso.")
    return True

if __name__ == "__main__":
    success = main()
    if success:
        print("\nArquivo plankton_ai.py modificado com sucesso para tratar erros do NumPy!")
    else:
        print("\nHouve problemas ao modificar o arquivo plankton_ai.py. Verifique o arquivo de log para mais detalhes.")