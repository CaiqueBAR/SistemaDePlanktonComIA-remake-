from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
import os
import base64
import logging
import time
import traceback
import imghdr
import json
from werkzeug.utils import secure_filename
import tempfile
import uuid
from PIL import Image
import io
import sys

# Definir variável global para disponibilidade do PyTorch
pytorch_available = False

# Importar apenas o necessário do plankton_ai.py
try:
    # Adicionar o diretório atual ao path para garantir que o módulo seja encontrado
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    
    # Importar apenas a função create_plankton_classifier e a variável PYTORCH_AVAILABLE
    from plankton_ai import create_plankton_classifier, PYTORCH_AVAILABLE
    pytorch_available = PYTORCH_AVAILABLE
    print(f"PyTorch disponível: {pytorch_available}")
except ImportError as e:
    print(f"Erro ao importar do módulo plankton_ai: {e}")
    pytorch_available = False

# Importação do NumPy com tratamento de erro
try:
    import numpy as np
except ImportError:
    print("Erro ao importar NumPy. Instalando versão compatível...")
    import sys
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "numpy==1.24.3"])
    import numpy as np




# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join('logs', 'flask_server.log'), encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('flask_server')

# Criar diretório de logs se não existir
os.makedirs('logs', exist_ok=True)

app = Flask(__name__)
CORS(app)  # Permite requisições de qualquer origem

# Configurações
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'tiff', 'webp', 'heic', 'heif', 'raw', 'svg', 'psd'}
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
MIN_IMAGE_SIZE = 50  # Dimensão mínima (largura ou altura) em pixels
MAX_IMAGE_SIZE = 4000  # Dimensão máxima (largura ou altura) em pixels

# Mapeamento de extensões para formatos suportados pelo PIL
EXTENSION_FORMAT_MAP = {
    'jpg': 'JPEG',
    'jpeg': 'JPEG',
    'png': 'PNG',
    'gif': 'GIF',
    'bmp': 'BMP',
    'tiff': 'TIFF',
    'webp': 'WEBP',
    'heic': 'JPEG',  # Convertido para JPEG
    'heif': 'JPEG',  # Convertido para JPEG
    'raw': 'JPEG',   # Convertido para JPEG
    'svg': 'PNG',    # Convertido para PNG
    'psd': 'PNG'     # Convertido para PNG
}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH

# Cria a pasta de uploads se não existir
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Inicializa o classificador de plâncton
plankton_classifier = None

# Verificar se PyTorch está disponível
if not pytorch_available:
    logger.warning("PyTorch não está disponível. O servidor iniciará, mas a classificação de imagens não funcionará.")

# Tentar inicializar o classificador
try:
    # Usar a função create_plankton_classifier que já tem tratamento para PyTorch não disponível
    plankton_classifier = create_plankton_classifier()
    if plankton_classifier is not None:
        logger.info("Classificador de plâncton inicializado com sucesso")
    else:
        logger.warning("Classificador de plâncton inicializado como None (PyTorch não disponível)")
except Exception as e:
    logger.error(f"Erro ao inicializar classificador: {str(e)}")
    logger.debug(traceback.format_exc())
    plankton_classifier = None

def allowed_file(filename):
    """Verifica se o arquivo tem uma extensão permitida."""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def validate_image(file_path):
    """Valida uma imagem verificando formato, tamanho e dimensões.
    Converte formatos não suportados diretamente para formatos compatíveis.
    
    Args:
        file_path (str): Caminho para o arquivo de imagem
        
    Returns:
        tuple: (is_valid, error_message, converted_path)
            converted_path será None se não houve conversão ou o caminho do novo arquivo se houve conversão
    """
    # Verificar se o arquivo existe
    if not os.path.exists(file_path):
        return False, "Arquivo não encontrado", None
        
    # Verificar tamanho do arquivo
    file_size = os.path.getsize(file_path)
    if file_size > MAX_CONTENT_LENGTH:
        return False, f"Arquivo muito grande: {file_size/1024/1024:.1f}MB (máximo: {MAX_CONTENT_LENGTH/1024/1024:.1f}MB)", None
    if file_size < 100:  # 100 bytes é muito pequeno para uma imagem válida
        return False, f"Arquivo muito pequeno: {file_size} bytes", None
    
    # Obter extensão do arquivo
    file_ext = os.path.splitext(file_path)[1].lower().replace('.', '')
    
    # Verificar se é realmente uma imagem
    img_type = imghdr.what(file_path)
    if img_type is None and file_ext not in ['svg', 'psd', 'heic', 'heif', 'raw']:
        return False, "Arquivo não é uma imagem válida", None
        
    # Tentar abrir a imagem com PIL para validar e possivelmente converter
    try:
        # Verificar se precisamos converter o formato
        converted_path = None
        if file_ext in EXTENSION_FORMAT_MAP and file_ext not in ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'tiff']:
            # Formatos que precisam de conversão
            try:
                img = Image.open(file_path)
                # Criar um novo nome de arquivo para a versão convertida
                converted_path = os.path.join(os.path.dirname(file_path), 
                                             f"converted_{os.path.basename(file_path).split('.')[0]}.{EXTENSION_FORMAT_MAP[file_ext].lower()}")
                # Salvar no formato de destino
                img.save(converted_path, format=EXTENSION_FORMAT_MAP[file_ext])
                logger.info(f"Imagem convertida de {file_ext} para {EXTENSION_FORMAT_MAP[file_ext]}: {converted_path}")
                
                # Usar o arquivo convertido para o restante da validação
                file_path = converted_path
                img = Image.open(file_path)  # Reabrir a imagem convertida
            except Exception as e:
                logger.error(f"Erro ao converter imagem: {str(e)}")
                return False, f"Erro ao processar formato de imagem {file_ext}: {str(e)}", None
        else:
            # Formatos suportados diretamente
            img = Image.open(file_path)
            
        # Verificar dimensões
        width, height = img.size
        if width < MIN_IMAGE_SIZE or height < MIN_IMAGE_SIZE:
            return False, f"Imagem muito pequena: {width}x{height}px (mínimo: {MIN_IMAGE_SIZE}x{MIN_IMAGE_SIZE}px)", converted_path
        if width > MAX_IMAGE_SIZE or height > MAX_IMAGE_SIZE:
            return False, f"Imagem muito grande: {width}x{height}px (máximo: {MAX_IMAGE_SIZE}x{MAX_IMAGE_SIZE}px)", converted_path
            
        return True, "", converted_path
    except Exception as e:
        logger.error(f"Erro ao validar imagem: {str(e)}")
        return False, f"Erro ao processar imagem: {str(e)}", None
    
    # Verificar dimensões da imagem
    try:
        with Image.open(file_path) as img:
            width, height = img.size
            if width < MIN_IMAGE_SIZE or height < MIN_IMAGE_SIZE:
                return False, f"Imagem muito pequena: {width}x{height}px (mínimo: {MIN_IMAGE_SIZE}px)"
            if width > MAX_IMAGE_SIZE or height > MAX_IMAGE_SIZE:
                return False, f"Imagem muito grande: {width}x{height}px (máximo: {MAX_IMAGE_SIZE}px)"
    except Exception as e:
        return False, f"Erro ao processar imagem: {str(e)}"
    
    return True, ""

@app.route('/')
def index():
    """Página inicial com informações da API."""
    html_template = """
    <!DOCTYPE html>
    <html lang="pt-BR">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>API de Reconhecimento de Plâncton</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                max-width: 800px;
                margin: 0 auto;
                padding: 20px;
                background-color: #f5f5f5;
            }
            .container {
                background-color: white;
                padding: 30px;
                border-radius: 10px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }
            h1 {
                color: #2c3e50;
                text-align: center;
            }
            .endpoint {
                background-color: #ecf0f1;
                padding: 15px;
                margin: 10px 0;
                border-radius: 5px;
                border-left: 4px solid #3498db;
            }
            .method {
                font-weight: bold;
                color: #e74c3c;
            }
            .status {
                background-color: #d5f4e6;
                padding: 10px;
                border-radius: 5px;
                margin: 20px 0;
                text-align: center;
            }
            code {
                background-color: #f8f9fa;
                padding: 2px 5px;
                border-radius: 3px;
                font-family: 'Courier New', monospace;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🦠 API de Reconhecimento de Plâncton</h1>
            
            <div class="status">
                <strong>Status:</strong> ✅ Servidor ativo e funcionando
            </div>
            
            <h2>Endpoints Disponíveis:</h2>
            
            <div class="endpoint">
                <h3><span class="method">GET</span> /</h3>
                <p>Página inicial com informações da API</p>
            </div>
            
            <div class="endpoint">
                <h3><span class="method">GET</span> /status</h3>
                <p>Verifica o status do servidor e do modelo de IA</p>
            </div>
            
            <div class="endpoint">
                <h3><span class="method">POST</span> /predict</h3>
                <p>Classifica uma imagem de plâncton</p>
                <p><strong>Parâmetros:</strong></p>
                <ul>
                    <li><code>file</code>: Arquivo de imagem (PNG, JPG, JPEG, GIF, BMP, TIFF)</li>
                </ul>
                <p><strong>Resposta:</strong> JSON com a classificação e confiança</p>
            </div>
            
            <div class="endpoint">
                <h3><span class="method">POST</span> /predict_base64</h3>
                <p>Classifica uma imagem de plâncton enviada em base64</p>
                <p><strong>Parâmetros JSON:</strong></p>
                <ul>
                    <li><code>image</code>: String base64 da imagem</li>
                </ul>
                <p><strong>Resposta:</strong> JSON com a classificação e confiança</p>
            </div>
            
            <div class="endpoint">
                <h3><span class="method">GET</span> /classes</h3>
                <p>Lista todas as classes de plâncton que o modelo pode identificar</p>
            </div>
            
            <h2>Classes de Plâncton Suportadas:</h2>
            <ul>
                <li>Copepod</li>
                <li>Diatom</li>
                <li>Dinoflagellate</li>
                <li>Radiolarian</li>
                <li>Foraminifera</li>
                <li>Cyanobacteria</li>
                <li>Other</li>
            </ul>
            
            <h2>Exemplo de Uso:</h2>
            <pre><code>curl -X POST -F "file=@imagem_plancton.jpg" http://localhost:5000/predict</code></pre>
        </div>
    </body>
    </html>
    """
    return render_template_string(html_template)

@app.route('/status', methods=['GET'])
def status():
    """Retorna o status do servidor e do modelo."""
    # Adicionar informações do servidor
    server_info = {
        'server_time': time.strftime("%Y-%m-%d %H:%M:%S"),
        'upload_folder': UPLOAD_FOLDER,
        'max_file_size': f"{MAX_CONTENT_LENGTH/1024/1024:.1f}MB",
        'allowed_extensions': list(ALLOWED_EXTENSIONS),
        'image_size_limits': {
            'min': f"{MIN_IMAGE_SIZE}x{MIN_IMAGE_SIZE}px",
            'max': f"{MAX_IMAGE_SIZE}x{MAX_IMAGE_SIZE}px"
        }
    }
    
    # Verificar se o PyTorch está disponível
    if not pytorch_available:
        return jsonify({
            'status': 'limited',
            'message': 'Servidor ativo, mas PyTorch não está disponível',
            'pytorch_available': False,
            'server_info': server_info,
            'endpoints': [
                'GET /',
                'GET /status',
                'GET /classes'
            ]
        })
    
    # Verificar se o classificador está inicializado
    if plankton_classifier is None:
        return jsonify({
            'status': 'error',
            'message': 'Classificador de plâncton não inicializado',
            'model_loaded': False,
            'pytorch_available': True,
            'server_info': server_info
        }), 500
        
    try:
        model_info = plankton_classifier.get_model_info()
        
        return jsonify({
            'status': 'online',
            'message': 'Servidor de reconhecimento de plâncton ativo',
            'model_info': model_info,
            'server_info': server_info,
            'pytorch_available': True,
            'endpoints': [
                'GET /',
                'GET /status',
                'POST /predict',
                'POST /predict_base64',
                'GET /classes'
            ]
        })
    except Exception as e:
        logger.error(f"Erro ao obter status: {str(e)}")
        logger.debug(traceback.format_exc())
        return jsonify({
            'status': 'error',
            'message': f'Erro ao obter status: {str(e)}',
            'pytorch_available': True,
            'server_info': server_info
        }), 500

@app.route('/classes', methods=['GET'])
def get_classes():
    """Retorna as classes de plâncton suportadas."""
    if not pytorch_available:
        logger.warning("Tentativa de obter classes sem PyTorch disponível")
        # Retorna as classes padrão mesmo sem PyTorch
        default_classes = ["Copepod", "Diatom", "Dinoflagellate", "Radiolarian", "Foraminifera", "Cyanobacteria", "Other"]
        return jsonify({
            'classes': default_classes,
            'num_classes': len(default_classes),
            'pytorch_available': False
        })
    
    if plankton_classifier is None:
        logger.warning("Tentativa de obter classes com classificador não inicializado")
        default_classes = ["Copepod", "Diatom", "Dinoflagellate", "Radiolarian", "Foraminifera", "Cyanobacteria", "Other"]
        return jsonify({
            'classes': default_classes,
            'num_classes': len(default_classes),
            'classifier_initialized': False
        })
    
    return jsonify({
        'classes': plankton_classifier.class_names,
        'num_classes': len(plankton_classifier.class_names),
        'pytorch_available': True,
        'classifier_initialized': True
    })

@app.route('/predict', methods=['POST'])
def predict_file():
    """Classifica uma imagem de plâncton enviada como arquivo."""
    start_time = time.time()
    
    # Verificar se o PyTorch está disponível
    if not pytorch_available:
        logger.error("Tentativa de predição sem PyTorch disponível")
        return jsonify({
            'success': False,
            'error': 'PyTorch não está disponível. Reinstale o PyTorch para usar este recurso.'
        }), 503
    
    # Verificar se o classificador está inicializado
    if plankton_classifier is None:
        logger.error("Tentativa de predição com classificador não inicializado")
        return jsonify({
            'success': False,
            'error': 'Serviço de classificação indisponível'
        }), 503
    
    try:
        # Verifica se foi enviado um arquivo
        if 'file' not in request.files:
            logger.warning("Requisição sem arquivo")
            return jsonify({
                'success': False,
                'error': 'Nenhum arquivo enviado'
            }), 400
        
        file = request.files['file']
        
        # Verifica se o arquivo tem nome
        if file.filename == '':
            logger.warning("Arquivo sem nome enviado")
            return jsonify({
                'success': False,
                'error': 'Nenhum arquivo selecionado'
            }), 400
        
        # Verifica se o arquivo é permitido
        if not allowed_file(file.filename):
            logger.warning(f"Tipo de arquivo não permitido: {file.filename}")
            return jsonify({
                'success': False,
                'error': 'Tipo de arquivo não permitido',
                'allowed_types': list(ALLOWED_EXTENSIONS)
            }), 400
        
        # Salva o arquivo temporariamente
        filename = secure_filename(file.filename)
        unique_filename = f"{uuid.uuid4()}_{filename}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
        
        try:
            file.save(filepath)
            logger.info(f"Arquivo salvo temporariamente: {filepath}")
            
            # Validar a imagem
            is_valid, error_message, converted_path = validate_image(filepath)
            if not is_valid:
                logger.warning(f"Validação de imagem falhou: {error_message}")
                os.remove(filepath)
                if converted_path and os.path.exists(converted_path):
                    os.remove(converted_path)
                return jsonify({
                    'success': False,
                    'error': error_message
                }), 400
            
            # Usar o arquivo convertido se existir
            prediction_path = converted_path if converted_path else filepath
            
            # Faz a predição
            result = plankton_classifier.predict(prediction_path)
            
            # Remove os arquivos temporários
            os.remove(filepath)
            logger.info(f"Arquivo temporário removido: {filepath}")
            if converted_path and os.path.exists(converted_path):
                os.remove(converted_path)
                logger.info(f"Arquivo convertido removido: {converted_path}")
            
            if not result.get('success', False):
                logger.error(f"Erro na predição: {result.get('error', 'Erro desconhecido')}")
                return jsonify({
                    'success': False,
                    'error': result.get('error', 'Erro na predição'),
                    'details': result
                }), 500
            
            # Calcular tempo total de processamento
            total_time = time.time() - start_time
            
            response = {
                'success': True,
                'filename': filename,
                'prediction': result,
                'processing_time': round(total_time, 3)
            }
            
            logger.info(f"Predição bem-sucedida para {filename}: {result.get('class')} ({result.get('confidence', 0):.2f})")
            return jsonify(response)
            
        except Exception as e:
            # Remove o arquivo em caso de erro
            if os.path.exists(filepath):
                os.remove(filepath)
                logger.info(f"Arquivo temporário removido após erro: {filepath}")
            
            logger.error(f"Erro ao processar arquivo: {str(e)}")
            logger.debug(traceback.format_exc())
            
            return jsonify({
                'success': False,
                'error': f'Erro ao processar arquivo: {str(e)}'
            }), 500
            
    except Exception as e:
        logger.error(f"Erro interno do servidor: {str(e)}")
        logger.debug(traceback.format_exc())
        
        return jsonify({
            'success': False,
            'error': f'Erro interno do servidor: {str(e)}'
        }), 500

@app.route('/predict_base64', methods=['POST'])
def predict_base64():
    """Classifica uma imagem de plâncton enviada em base64."""
    start_time = time.time()
    
    # Verificar se o PyTorch está disponível
    if not pytorch_available:
        logger.error("Tentativa de predição sem PyTorch disponível")
        return jsonify({
            'success': False,
            'error': 'PyTorch não está disponível. Reinstale o PyTorch para usar este recurso.'
        }), 503
    
    # Verificar se o classificador está inicializado
    if plankton_classifier is None:
        logger.error("Tentativa de predição com classificador não inicializado")
        return jsonify({
            'success': False,
            'error': 'Serviço de classificação indisponível'
        }), 503
    
    try:
        # Verificar se o conteúdo é JSON
        if not request.is_json:
            logger.warning("Requisição sem conteúdo JSON")
            return jsonify({
                'success': False,
                'error': 'Conteúdo deve ser JSON'
            }), 400
            
        data = request.get_json()
        
        if not data or 'image' not in data:
            logger.warning("Dados JSON inválidos ou campo 'image' ausente")
            return jsonify({
                'success': False,
                'error': 'Dados JSON inválidos ou campo "image" ausente'
            }), 400
        
        # Verificar se a string base64 não está vazia
        if not data['image']:
            logger.warning("String base64 vazia")
            return jsonify({
                'success': False,
                'error': 'String base64 vazia'
            }), 400
        
        # Decodifica a imagem base64
        try:
            # Remover cabeçalho de data URI se presente
            base64_data = data['image']
            if ',' in base64_data:
                base64_data = base64_data.split(',', 1)[1]
                
            image_data = base64.b64decode(base64_data)
        except Exception as e:
            logger.warning(f"Erro ao decodificar base64: {str(e)}")
            return jsonify({
                'success': False,
                'error': 'Dados base64 inválidos'
            }), 400
        
        # Verificar tamanho dos dados
        if len(image_data) > MAX_CONTENT_LENGTH:
            logger.warning(f"Dados base64 muito grandes: {len(image_data)/1024/1024:.1f}MB")
            return jsonify({
                'success': False,
                'error': f'Imagem muito grande: {len(image_data)/1024/1024:.1f}MB (máximo: {MAX_CONTENT_LENGTH/1024/1024:.1f}MB)'
            }), 413
        
        # Verificar se os dados são uma imagem válida
        try:
            img = Image.open(io.BytesIO(image_data))
            width, height = img.size
            
            # Verificar dimensões
            if width < MIN_IMAGE_SIZE or height < MIN_IMAGE_SIZE:
                logger.warning(f"Imagem base64 muito pequena: {width}x{height}px")
                return jsonify({
                    'success': False,
                    'error': f'Imagem muito pequena: {width}x{height}px (mínimo: {MIN_IMAGE_SIZE}px)'
                }), 400
                
            if width > MAX_IMAGE_SIZE or height > MAX_IMAGE_SIZE:
                logger.warning(f"Imagem base64 muito grande: {width}x{height}px")
                return jsonify({
                    'success': False,
                    'error': f'Imagem muito grande: {width}x{height}px (máximo: {MAX_IMAGE_SIZE}px)'
                }), 400
                
            # Determinar formato da imagem
            img_format = img.format.lower() if img.format else 'jpeg'
            
            # Verificar se o formato precisa ser convertido
            needs_conversion = False
            target_format = 'jpeg'  # Formato padrão para conversão
            
            if img_format in EXTENSION_FORMAT_MAP:
                target_format = EXTENSION_FORMAT_MAP[img_format]
                # Se o formato original não é diretamente suportado pelo modelo, converter
                if img_format not in ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'tiff']:
                    needs_conversion = True
                    logger.info(f"Formato {img_format} será convertido para {target_format}")
            else:
                # Formato não reconhecido, usar padrão
                needs_conversion = True
                logger.info(f"Formato não reconhecido, convertendo para {target_format}")
                
            # Se precisar converter, fazer isso agora
            if needs_conversion:
                # Criar um novo buffer para a imagem convertida
                converted_buffer = io.BytesIO()
                # Salvar a imagem no formato alvo
                img.save(converted_buffer, format=target_format)
                # Atualizar os dados da imagem e o formato
                image_data = converted_buffer.getvalue()
                img_format = target_format.lower()
                logger.info(f"Imagem convertida para {target_format}")
                
            # Garantir que o formato final seja válido para o nome do arquivo
            if img_format.upper() not in [fmt.upper() for fmt in EXTENSION_FORMAT_MAP.values()]:
                img_format = 'jpeg'
                
        except Exception as e:
            logger.warning(f"Dados base64 não são uma imagem válida: {str(e)}")
            return jsonify({
                'success': False,
                'error': 'Dados base64 não são uma imagem válida'
            }), 400
        
        # Salva a imagem temporariamente
        with tempfile.NamedTemporaryFile(delete=False, suffix=f'.{img_format}') as temp_file:
            temp_file.write(image_data)
            temp_filepath = temp_file.name
            
        logger.info(f"Imagem base64 salva temporariamente: {temp_filepath}")
        
        try:
            # Validar a imagem (apenas para verificação adicional)
            is_valid, error_message, converted_path = validate_image(temp_filepath)
            if not is_valid:
                logger.warning(f"Validação de imagem base64 falhou: {error_message}")
                os.remove(temp_filepath)
                if converted_path and os.path.exists(converted_path):
                    os.remove(converted_path)
                return jsonify({
                    'success': False,
                    'error': error_message
                }), 400
                
            # Usar o arquivo convertido se existir
            prediction_path = converted_path if converted_path else temp_filepath
            
            # Faz a predição
            result = plankton_classifier.predict(prediction_path)
            
            # Remove os arquivos temporários
            os.remove(temp_filepath)
            logger.info(f"Arquivo temporário removido: {temp_filepath}")
            if converted_path and os.path.exists(converted_path):
                os.remove(converted_path)
                logger.info(f"Arquivo convertido removido: {converted_path}")
            
            if not result.get('success', False):
                logger.error(f"Erro na predição base64: {result.get('error', 'Erro desconhecido')}")
                return jsonify({
                    'success': False,
                    'error': result.get('error', 'Erro na predição'),
                    'details': result
                }), 500
            
            # Calcular tempo total de processamento
            total_time = time.time() - start_time
            
            response = {
                'success': True,
                'prediction': result,
                'processing_time': round(total_time, 3),
                'image_info': {
                    'format': img_format,
                    'width': width,
                    'height': height,
                    'size_bytes': len(image_data)
                }
            }
            
            logger.info(f"Predição base64 bem-sucedida: {result.get('class')} ({result.get('confidence', 0):.2f})")
            return jsonify(response)
            
        except Exception as e:
            # Remove o arquivo em caso de erro
            if os.path.exists(temp_filepath):
                os.remove(temp_filepath)
                logger.info(f"Arquivo temporário removido após erro: {temp_filepath}")
            
            logger.error(f"Erro ao processar imagem base64: {str(e)}")
            logger.debug(traceback.format_exc())
            
            return jsonify({
                'success': False,
                'error': f'Erro ao processar imagem: {str(e)}'
            }), 500
            
    except Exception as e:
        logger.error(f"Erro interno do servidor (base64): {str(e)}")
        logger.debug(traceback.format_exc())
        
        return jsonify({
            'success': False,
            'error': f'Erro interno do servidor: {str(e)}'
        }), 500

@app.errorhandler(413)
def too_large(e):
    """Handler para arquivos muito grandes."""
    logger.warning("Requisição com arquivo muito grande")
    return jsonify({
        'success': False,
        'error': f'Arquivo muito grande. Tamanho máximo: {MAX_CONTENT_LENGTH/1024/1024:.1f}MB'
    }), 413

@app.errorhandler(404)
def not_found(e):
    """Handler para rotas não encontradas."""
    logger.warning(f"Endpoint não encontrado: {request.path}")
    return jsonify({
        'success': False,
        'error': 'Endpoint não encontrado',
        'path': request.path,
        'available_endpoints': [
            '/',
            '/status',
            '/predict',
            '/predict_base64',
            '/classes'
        ]
    }), 404

@app.errorhandler(405)
def method_not_allowed(e):
    """Handler para métodos não permitidos."""
    logger.warning(f"Método não permitido: {request.method} {request.path}")
    return jsonify({
        'success': False,
        'error': f'Método {request.method} não permitido para este endpoint',
        'path': request.path
    }), 405

@app.errorhandler(500)
def internal_error(e):
    """Handler para erros internos."""
    logger.error(f"Erro interno do servidor: {str(e)}")
    return jsonify({
        'success': False,
        'error': 'Erro interno do servidor',
        'message': str(e)
    }), 500

if __name__ == '__main__':
    logger.info("🦠 Iniciando servidor de reconhecimento de plâncton...")
    logger.info("📡 Servidor rodando em: http://0.0.0.0:5000")
    logger.info("📋 Acesse http://localhost:5000 para ver a documentação da API")
    
    # Verifica se o modelo está carregado
    if plankton_classifier is None:
        logger.error("❌ Classificador de plâncton não inicializado!")
    else:
        model_info = plankton_classifier.get_model_info()
        if model_info.get('model_loaded', False):
            logger.info("✅ Modelo de IA carregado com sucesso!")
            logger.info(f"🔬 Classes suportadas: {', '.join(model_info.get('classes', []))}")
            
            # Informações adicionais do modelo
            if 'parameters' in model_info:
                logger.info(f"📊 Parâmetros do modelo: {model_info['parameters'].get('total', 0):,}")
            if 'device' in model_info:
                logger.info(f"💻 Dispositivo: {model_info['device'].get('type', 'cpu')}")
        else:
            logger.error("❌ Erro ao carregar o modelo de IA!")
    
    # Iniciar o servidor
    try:
        app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)
    except Exception as e:
        logger.critical(f"Erro ao iniciar o servidor: {str(e)}")
        logger.debug(traceback.format_exc())


