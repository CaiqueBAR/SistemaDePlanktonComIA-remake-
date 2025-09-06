import sys
import os
import subprocess
import logging

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("fix_numpy_system_wide.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("fix_numpy_system_wide")

def install_numpy_compatible():
    """Instala a versão compatível do NumPy."""
    try:
        logger.info("Instalando NumPy versão compatível (1.24.3)...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "numpy==1.24.3", "--force-reinstall"])
        logger.info("NumPy 1.24.3 instalado com sucesso.")
        return True
    except Exception as e:
        logger.error(f"Erro ao instalar NumPy: {str(e)}")
        return False

def modify_flask_server():
    """Modifica o arquivo flask_server.py para importar NumPy corretamente."""
    file_path = "flask_server.py"
    
    if not os.path.exists(file_path):
        logger.error(f"Arquivo não encontrado: {file_path}")
        return False
    
    try:
        # Ler o conteúdo do arquivo
        with open(file_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()
        
        # Adicionar importação do NumPy após as importações existentes
        modified_lines = []
        import_section_end = 0
        numpy_imported = False
        
        for i, line in enumerate(lines):
            if line.strip().startswith('import ') or line.strip().startswith('from '):
                import_section_end = i
                if 'import numpy as np' in line:
                    numpy_imported = True
            modified_lines.append(line)
        
        # Se NumPy não foi importado, adicionar após a última importação
        if not numpy_imported:
            # Adicionar uma linha em branco se não houver
            if not modified_lines[import_section_end].strip() == '':
                import_section_end += 1
                modified_lines.insert(import_section_end, '\n')
            
            # Adicionar importação do NumPy com tratamento de erro
            modified_lines.insert(import_section_end + 1, "# Importação do NumPy com tratamento de erro\ntry:\n    import numpy as np\nexcept ImportError:\n    print(\"Erro ao importar NumPy. Instalando versão compatível...\")\n    import sys\n    import subprocess\n    subprocess.check_call([sys.executable, \"-m\", \"pip\", \"install\", \"numpy==1.24.3\"])\n    import numpy as np\n\n")
        
        # Escrever o conteúdo modificado de volta ao arquivo
        with open(file_path, 'w', encoding='utf-8') as file:
            file.writelines(modified_lines)
        
        logger.info(f"Arquivo {file_path} modificado com sucesso.")
        return True
    
    except Exception as e:
        logger.error(f"Erro ao modificar o arquivo {file_path}: {str(e)}")
        return False

def modify_plankton_ai():
    """Verifica se o arquivo plankton_ai.py já foi modificado corretamente."""
    file_path = "plankton_ai.py"
    
    if not os.path.exists(file_path):
        logger.error(f"Arquivo não encontrado: {file_path}")
        return False
    
    try:
        # Ler o conteúdo do arquivo
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        
        # Verificar se o tratamento de erro do NumPy já está presente
        if "try:\n    import numpy as np\nexcept ImportError:" in content:
            logger.info(f"Arquivo {file_path} já está corretamente modificado.")
            return True
        
        # Se não estiver, modificar o arquivo
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
    """Verifica se o método preprocess_image já foi modificado corretamente."""
    file_path = "plankton_ai.py"
    
    if not os.path.exists(file_path):
        logger.error(f"Arquivo não encontrado: {file_path}")
        return False
    
    try:
        # Ler o conteúdo do arquivo
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        
        # Verificar se o tratamento de erro do NumPy já está presente no método preprocess_image
        if "# Verificar se o NumPy está disponível\n            try:\n                import numpy as np" in content:
            logger.info("Método preprocess_image já está corretamente modificado.")
            return True
        
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
    """Função principal para corrigir problemas com o NumPy em todo o sistema."""
    logger.info("Iniciando correção do NumPy em todo o sistema...")
    
    # Instalar NumPy compatível
    if not install_numpy_compatible():
        logger.error("Falha ao instalar NumPy compatível.")
        return False
    
    # Modificar o arquivo flask_server.py
    if not modify_flask_server():
        logger.error("Falha ao modificar o arquivo flask_server.py.")
        return False
    
    # Modificar o arquivo plankton_ai.py
    if not modify_plankton_ai():
        logger.error("Falha ao modificar o arquivo plankton_ai.py.")
        return False
    
    # Modificar o método preprocess_image
    if not modify_preprocess_image():
        logger.error("Falha ao modificar o método preprocess_image.")
        return False
    
    logger.info("Correção do NumPy em todo o sistema concluída com sucesso.")
    return True

if __name__ == "__main__":
    success = main()
    if success:
        print("\nSistema modificado com sucesso para tratar erros do NumPy!")
    else:
        print("\nHouve problemas ao modificar o sistema. Verifique o arquivo de log para mais detalhes.")