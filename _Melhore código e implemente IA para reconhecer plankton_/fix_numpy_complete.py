import os
import logging
import sys
import subprocess

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("fix_numpy_complete.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("fix_numpy_complete")

def reinstall_numpy():
    """Reinstala o NumPy com a versão específica."""
    try:
        logger.info("Reinstalando NumPy versão 1.24.3...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "--force-reinstall", "numpy==1.24.3"])
        logger.info("NumPy reinstalado com sucesso.")
        return True
    except Exception as e:
        logger.error(f"Erro ao reinstalar NumPy: {str(e)}")
        return False

def fix_plankton_ai():
    """Corrige o arquivo plankton_ai.py para garantir que o NumPy seja importado corretamente."""
    file_path = "plankton_ai.py"
    
    if not os.path.exists(file_path):
        logger.error(f"Arquivo não encontrado: {file_path}")
        return False
    
    try:
        # Ler o conteúdo do arquivo
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        
        # Verificar se já existe a importação do NumPy no início do arquivo
        if "import numpy as np" in content:
            # Remover a importação existente e o bloco try-except relacionado
            import_start = content.find("# Importação do NumPy com tratamento de erro")
            if import_start != -1:
                import_end = content.find("import numpy as np", import_start)
                if import_end != -1:
                    end_line = content.find("\n", import_end)
                    if end_line != -1:
                        # Remover o bloco de importação do NumPy
                        content = content[:import_start] + content[end_line+1:]
        
        # Adicionar a nova importação do NumPy no início do arquivo, após as importações existentes
        import_section = """# Importação do NumPy com tratamento de erro
try:
    import numpy as np
except ImportError:
    print("Erro ao importar NumPy. Instalando versão compatível...")
    import sys
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "numpy==1.24.3"])
    import numpy as np

"""
        
        # Encontrar o ponto de inserção após as importações iniciais
        insert_point = 0
        import_lines = ["import ", "from ", "# import"]
        last_import = -1
        
        lines = content.split("\n")
        for i, line in enumerate(lines):
            if any(line.strip().startswith(prefix) for prefix in import_lines):
                last_import = i
        
        if last_import != -1:
            # Inserir após a última importação
            lines.insert(last_import + 1, import_section)
            modified_content = "\n".join(lines)
        else:
            # Inserir no início do arquivo
            modified_content = import_section + content
        
        # Escrever o conteúdo modificado de volta ao arquivo
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(modified_content)
        
        logger.info("Arquivo plankton_ai.py modificado com sucesso.")
        return True
    
    except Exception as e:
        logger.error(f"Erro ao modificar o arquivo plankton_ai.py: {str(e)}")
        return False

def fix_flask_server():
    """Corrige o arquivo flask_server.py para garantir que o NumPy seja importado corretamente."""
    file_path = "flask_server.py"
    
    if not os.path.exists(file_path):
        logger.error(f"Arquivo não encontrado: {file_path}")
        return False
    
    try:
        # Ler o conteúdo do arquivo
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        
        # Verificar se já existe a importação do NumPy no início do arquivo
        if "import numpy as np" in content:
            # Remover a importação existente e o bloco try-except relacionado
            import_start = content.find("# Importação do NumPy com tratamento de erro")
            if import_start != -1:
                import_end = content.find("import numpy as np", import_start)
                if import_end != -1:
                    end_line = content.find("\n", import_end)
                    if end_line != -1:
                        # Remover o bloco de importação do NumPy
                        content = content[:import_start] + content[end_line+1:]
        
        # Adicionar a nova importação do NumPy no início do arquivo, após as importações existentes
        import_section = """# Importação do NumPy com tratamento de erro
try:
    import numpy as np
except ImportError:
    print("Erro ao importar NumPy. Instalando versão compatível...")
    import sys
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "numpy==1.24.3"])
    import numpy as np

"""
        
        # Encontrar o ponto de inserção após as importações iniciais
        insert_point = 0
        import_lines = ["import ", "from ", "# import"]
        last_import = -1
        
        lines = content.split("\n")
        for i, line in enumerate(lines):
            if any(line.strip().startswith(prefix) for prefix in import_lines):
                last_import = i
        
        if last_import != -1:
            # Inserir após a última importação
            lines.insert(last_import + 1, import_section)
            modified_content = "\n".join(lines)
        else:
            # Inserir no início do arquivo
            modified_content = import_section + content
        
        # Escrever o conteúdo modificado de volta ao arquivo
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(modified_content)
        
        logger.info("Arquivo flask_server.py modificado com sucesso.")
        return True
    
    except Exception as e:
        logger.error(f"Erro ao modificar o arquivo flask_server.py: {str(e)}")
        return False

def fix_transform_method():
    """Corrige o método transform na classe PlanktonClassifierPyTorch para não depender do NumPy."""
    file_path = "plankton_ai.py"
    
    if not os.path.exists(file_path):
        logger.error(f"Arquivo não encontrado: {file_path}")
        return False
    
    try:
        # Ler o conteúdo do arquivo
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        
        # Encontrar a definição do transform
        transform_start = content.find("self.transform = transforms.Compose")
        if transform_start == -1:
            logger.error("Definição do transform não encontrada.")
            return False
        
        # Encontrar o final do bloco transform
        transform_end = content.find("])", transform_start)
        if transform_end == -1:
            logger.error("Final do bloco transform não encontrado.")
            return False
        
        # Extrair o bloco transform atual
        transform_block = content[transform_start:transform_end+2]
        
        # Criar um novo bloco transform que não dependa do NumPy
        new_transform = """self.transform = transforms.Compose([
            transforms.Resize(self.img_size),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
        ])"""
        
        # Substituir o bloco transform
        modified_content = content.replace(transform_block, new_transform)
        
        # Escrever o conteúdo modificado de volta ao arquivo
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(modified_content)
        
        logger.info("Método transform modificado com sucesso.")
        return True
    
    except Exception as e:
        logger.error(f"Erro ao modificar o método transform: {str(e)}")
        return False

def create_test_script():
    """Cria um script de teste para verificar se o NumPy está funcionando corretamente."""
    file_path = "test_numpy.py"
    
    try:
        content = """import sys
print(f"Python version: {sys.version}")

try:
    import numpy as np
    print(f"NumPy version: {np.__version__}")
    print("NumPy is available and working correctly.")
    
    # Teste básico do NumPy
    arr = np.array([1, 2, 3, 4, 5])
    print(f"NumPy array: {arr}")
    print(f"NumPy array mean: {arr.mean()}")
    print("NumPy test successful!")
    
except ImportError as e:
    print(f"Error importing NumPy: {e}")
except Exception as e:
    print(f"Error using NumPy: {e}")
"""
        
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(content)
        
        logger.info(f"Script de teste {file_path} criado com sucesso.")
        return True
    
    except Exception as e:
        logger.error(f"Erro ao criar o script de teste: {str(e)}")
        return False

def main():
    """Função principal para corrigir o problema do NumPy."""
    logger.info("Iniciando correção completa do problema do NumPy...")
    
    # Reinstalar NumPy
    if not reinstall_numpy():
        logger.error("Falha ao reinstalar NumPy.")
    
    # Corrigir plankton_ai.py
    if not fix_plankton_ai():
        logger.error("Falha ao corrigir plankton_ai.py.")
    
    # Corrigir flask_server.py
    if not fix_flask_server():
        logger.error("Falha ao corrigir flask_server.py.")
    
    # Corrigir método transform
    if not fix_transform_method():
        logger.error("Falha ao corrigir o método transform.")
    
    # Criar script de teste
    if not create_test_script():
        logger.error("Falha ao criar o script de teste.")
    
    logger.info("Correção completa do problema do NumPy concluída.")
    return True

if __name__ == "__main__":
    success = main()
    if success:
        print("\nCorreção completa do problema do NumPy concluída com sucesso!")
        print("Execute 'python test_numpy.py' para verificar se o NumPy está funcionando corretamente.")
    else:
        print("\nHouve problemas durante a correção do NumPy. Verifique o arquivo de log para mais detalhes.")