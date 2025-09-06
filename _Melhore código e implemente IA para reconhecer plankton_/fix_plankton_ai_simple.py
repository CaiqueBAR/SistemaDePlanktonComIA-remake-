import os
import logging

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("fix_plankton_ai_simple.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("fix_plankton_ai_simple")

def modify_preprocess_image():
    """Modifica o método preprocess_image para contornar o erro do NumPy."""
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
        
        # Substituir completamente o método preprocess_image por uma versão simplificada
        # que não depende do NumPy para o processamento básico
        method_end = content.find("def ", preprocess_start + 1)
        if method_end == -1:
            method_end = len(content)
        
        # Nova implementação do método preprocess_image
        new_method = '''    def preprocess_image(self, image_path):
        """Pré-processa a imagem para classificação."""
        try:
            # Verificar tamanho do arquivo
            file_size = os.path.getsize(image_path)
            if file_size == 0:
                logger.error(f"Arquivo vazio: {image_path}")
                return None, "Arquivo de imagem vazio"
                
            # Tentar abrir a imagem
            try:
                from PIL import Image, UnidentifiedImageError
                img = Image.open(image_path)
            except UnidentifiedImageError:
                logger.error(f"Formato de imagem não reconhecido: {image_path}")
                return None, "Formato de imagem não reconhecido"
                
            # Converter para RGB (lidar com imagens em escala de cinza, RGBA, etc)
            if img.mode != "RGB":
                logger.info(f"Convertendo imagem de {img.mode} para RGB")
                img = img.convert("RGB")
                
            # Verificar dimensões mínimas
            if img.width < 10 or img.height < 10:
                logger.warning(f"Imagem muito pequena: {img.width}x{img.height}")
                
            # Aplicar transformações
            img_tensor = self.transform(img)
            img_tensor = img_tensor.unsqueeze(0)  # Adiciona dimensão do batch
            return img_tensor.to(self.device), None
            
        except Exception as e:
            error_msg = f"Erro no pré-processamento da imagem: {str(e)}"
            logger.error(error_msg)
            import traceback
            logger.debug(traceback.format_exc())
            return None, error_msg
'''
        
        # Substituir o método antigo pelo novo
        modified_content = content[:preprocess_start] + new_method + content[method_end:]
        
        # Escrever o conteúdo modificado de volta ao arquivo
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(modified_content)
        
        logger.info("Método preprocess_image modificado com sucesso.")
        return True
    
    except Exception as e:
        logger.error(f"Erro ao modificar o método preprocess_image: {str(e)}")
        return False

def main():
    """Função principal para corrigir o problema do NumPy no plankton_ai.py."""
    logger.info("Iniciando correção simplificada do plankton_ai.py...")
    
    # Modificar o método preprocess_image
    if not modify_preprocess_image():
        logger.error("Falha ao modificar o método preprocess_image.")
        return False
    
    logger.info("Correção simplificada do plankton_ai.py concluída com sucesso.")
    return True

if __name__ == "__main__":
    success = main()
    if success:
        print("\nMétodo preprocess_image modificado com sucesso para contornar o erro do NumPy!")
    else:
        print("\nHouve problemas ao modificar o método preprocess_image. Verifique o arquivo de log para mais detalhes.")