import sys
import os
import subprocess
import logging

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("fix_torchvision_numpy.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("fix_torchvision_numpy")

def fix_torchvision_numpy_issue():
    """Corrige o problema de compatibilidade entre TorchVision e NumPy."""
    try:
        # Reinstalar NumPy com versão compatível
        logger.info("Reinstalando NumPy com versão compatível (1.24.3)...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "numpy==1.24.3", "--force-reinstall"])
        
        # Reinstalar TorchVision para garantir compatibilidade
        logger.info("Reinstalando TorchVision...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "torchvision", "--force-reinstall"])
        
        # Verificar se o NumPy está funcionando
        logger.info("Verificando se o NumPy está funcionando...")
        try:
            import numpy as np
            logger.info(f"NumPy importado com sucesso. Versão: {np.__version__}")
        except ImportError as e:
            logger.error(f"Erro ao importar NumPy: {str(e)}")
            return False
        
        # Verificar se o TorchVision está funcionando
        logger.info("Verificando se o TorchVision está funcionando...")
        try:
            import torchvision
            logger.info(f"TorchVision importado com sucesso. Versão: {torchvision.__version__}")
        except ImportError as e:
            logger.error(f"Erro ao importar TorchVision: {str(e)}")
            return False
        
        # Verificar se o NumPy está disponível no TorchVision
        logger.info("Verificando se o NumPy está disponível no TorchVision...")
        try:
            import torchvision.transforms as transforms
            transform = transforms.ToTensor()
            logger.info("TorchVision transforms importado com sucesso.")
        except Exception as e:
            logger.error(f"Erro ao usar TorchVision transforms: {str(e)}")
            return False
        
        logger.info("Correção do problema de compatibilidade entre TorchVision e NumPy concluída com sucesso.")
        return True
    
    except Exception as e:
        logger.error(f"Erro ao corrigir problema de compatibilidade: {str(e)}")
        return False

def modify_plankton_ai_imports():
    """Modifica a ordem de importação no plankton_ai.py para evitar conflitos."""
    file_path = "plankton_ai.py"
    
    if not os.path.exists(file_path):
        logger.error(f"Arquivo não encontrado: {file_path}")
        return False
    
    try:
        # Ler o conteúdo do arquivo
        with open(file_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()
        
        # Reorganizar as importações
        modified_lines = []
        numpy_import = None
        torch_imports = []
        other_imports = []
        non_imports = []
        
        # Separar as importações
        for line in lines:
            if line.strip().startswith('import numpy as np') or 'import numpy as np' in line:
                numpy_import = line
            elif line.strip().startswith('import torch') or line.strip().startswith('from torch'):
                torch_imports.append(line)
            elif line.strip().startswith('import ') or line.strip().startswith('from '):
                other_imports.append(line)
            else:
                non_imports.append(line)
        
        # Adicionar as importações na ordem correta
        if numpy_import:
            modified_lines.append("# Importação do NumPy primeiro para evitar conflitos\n")
            modified_lines.append(numpy_import)
        else:
            modified_lines.append("# Importação do NumPy primeiro para evitar conflitos\n")
            modified_lines.append("import numpy as np\n")
        
        modified_lines.append("\n# Importações do PyTorch\n")
        modified_lines.extend(torch_imports)
        
        modified_lines.append("\n# Outras importações\n")
        modified_lines.extend(other_imports)
        
        # Adicionar o restante do código
        modified_lines.append("\n")
        modified_lines.extend(non_imports)
        
        # Escrever o conteúdo modificado de volta ao arquivo
        with open(file_path, 'w', encoding='utf-8') as file:
            file.writelines(modified_lines)
        
        logger.info(f"Arquivo {file_path} modificado com sucesso.")
        return True
    
    except Exception as e:
        logger.error(f"Erro ao modificar o arquivo {file_path}: {str(e)}")
        return False

def create_test_numpy_script():
    """Cria um script para testar se o NumPy está funcionando corretamente."""
    file_path = "test_numpy.py"
    
    try:
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write("""import sys
import numpy as np
import torch
import torchvision

print(f"Python version: {sys.version}")
print(f"NumPy version: {np.__version__}")
print(f"PyTorch version: {torch.__version__}")
print(f"TorchVision version: {torchvision.__version__}")

# Testar NumPy
try:
    arr = np.array([1, 2, 3])
    print(f"NumPy array: {arr}")
    print("NumPy está funcionando corretamente.")
except Exception as e:
    print(f"Erro ao usar NumPy: {str(e)}")

# Testar TorchVision com NumPy
try:
    import torchvision.transforms as transforms
    transform = transforms.ToTensor()
    print("TorchVision transforms importado com sucesso.")
except Exception as e:
    print(f"Erro ao usar TorchVision transforms: {str(e)}")
""")
        
        logger.info(f"Arquivo {file_path} criado com sucesso.")
        return True
    
    except Exception as e:
        logger.error(f"Erro ao criar o arquivo {file_path}: {str(e)}")
        return False

def main():
    """Função principal para corrigir problemas com o NumPy e TorchVision."""
    logger.info("Iniciando correção do problema de compatibilidade entre TorchVision e NumPy...")
    
    # Corrigir problema de compatibilidade
    if not fix_torchvision_numpy_issue():
        logger.error("Falha ao corrigir problema de compatibilidade.")
        return False
    
    # Modificar a ordem de importação no plankton_ai.py
    if not modify_plankton_ai_imports():
        logger.error("Falha ao modificar a ordem de importação no plankton_ai.py.")
        return False
    
    # Criar script de teste
    if not create_test_numpy_script():
        logger.error("Falha ao criar script de teste.")
        return False
    
    logger.info("Correção do problema de compatibilidade entre TorchVision e NumPy concluída com sucesso.")
    return True

if __name__ == "__main__":
    success = main()
    if success:
        print("\nProblema de compatibilidade entre TorchVision e NumPy corrigido com sucesso!")
        print("Execute 'python test_numpy.py' para verificar se o NumPy está funcionando corretamente.")
    else:
        print("\nHouve problemas ao corrigir o problema de compatibilidade. Verifique o arquivo de log para mais detalhes.")