# 📋 Instruções de Uso - Sistema de Reconhecimento de Plâncton

## 🚀 Início Rápido

### 1. Preparação do Ambiente
```bash
# Instalar dependências
pip install -r requirements.txt

# Verificar instalação
python test_system.py
```

### 2. Executar o Sistema

**IMPORTANTE:** O servidor Flask precisa estar rodando em segundo plano para que a interface gráfica funcione corretamente.

```bash
# PASSO 1: Iniciar o Servidor Flask em segundo plano
python flask_server_launcher.py

# PASSO 2: Iniciar a Interface Gráfica
python plankton_gui.py
```

## 🖥️ Usando a Interface Gráfica

### Passo 1: Iniciar o Servidor Flask (em segundo plano)
1. Abra um terminal e execute:
   ```bash
   python flask_server_launcher.py
   ```
2. Você verá uma mensagem confirmando que o servidor foi iniciado e o PID do processo. Este terminal pode ser fechado ou minimizado, pois o servidor rodará em segundo plano.

### Passo 2: Iniciar a Interface Gráfica
1. Abra **outro** terminal e execute:
   ```bash
   python plankton_gui.py
   ```
2. A janela principal será aberta com o título "Sistema de Reconhecimento de Plâncton com IA"

### Passo 3: Verificar o Status do Servidor na GUI
1. Na seção "Controle do Servidor Flask", o status deve aparecer como **"Servidor ativo"** (cor verde).
2. Se não estiver ativo, clique em **"🔍 Verificar Status"**.

### Passo 4: Selecionar uma Imagem
1. Na seção "Reconhecimento de Plâncton com IA", clique em **"📁 Selecionar Imagem"**
2. Navegue até uma imagem de plâncton (formatos suportados: PNG, JPG, JPEG, GIF, BMP, TIFF)
3. A imagem será exibida no canvas à esquerda

### Passo 5: Classificar o Plâncton
1. Com a imagem selecionada e o servidor ativo, clique em **"🔬 Classificar Plâncton"**
2. Aguarde o processamento (alguns segundos)
3. Os resultados aparecerão na área de resultados à direita

### Passo 6: Interpretar os Resultados
Os resultados mostram:
- **Classe Predita**: O tipo de plâncton identificado
- **Confiança**: Percentual de certeza da classificação
- **Todas as Probabilidades**: Ranking completo com barras visuais
- **Interpretação**: Avaliação da qualidade do resultado

## 🌐 Usando a API REST

### Iniciar o Servidor (Standalone)
```bash
python flask_server.py
```

### Acessar a Documentação
Abra no navegador: `http://localhost:5000`

### Exemplos de Uso da API

#### 1. Verificar Status
```bash
curl http://localhost:5000/status
```

#### 2. Listar Classes Suportadas
```bash
curl http://localhost:5000/classes
```

#### 3. Classificar Imagem (Upload)
```bash
curl -X POST -F "file=@minha_imagem.jpg" http://localhost:5000/predict
```

#### 4. Classificar Imagem (Base64)
```python
import requests
import base64

# Ler e codificar imagem
with open("imagem.jpg", "rb") as f:
    image_data = base64.b64encode(f.read()).decode()

# Enviar para API
response = requests.post(
    "http://localhost:5000/predict_base64",
    json={"image": image_data}
)

result = response.json()
print(f"Classe: {result["prediction"]["predicted_class"]}")
print(f"Confiança: {result["prediction"]["confidence"]:.2%}")
```

## 🔬 Interpretando os Resultados

### Níveis de Confiança
- **> 80%**: Alta confiança - Resultado muito provável
- **60-80%**: Confiança moderada - Resultado provável  
- **40-60%**: Baixa confiança - Resultado incerto
- **< 40%**: Confiança muito baixa - Resultado duvidoso

### Classes de Plâncton
1. **Copepod**: Pequenos crustáceos, muito comuns no zooplâncton
2. **Diatom**: Algas unicelulares com carapaça de sílica
3. **Dinoflagellate**: Protistas flagelados, alguns bioluminescentes
4. **Radiolarian**: Protozoários com esqueleto mineral complexo
5. **Foraminifera**: Protistas com carapaça calcária
6. **Cyanobacteria**: Bactérias fotossintéticas (fitoplâncton)
7. **Other**: Outras formas de plâncton não classificadas

## 🛠️ Solução de Problemas Comuns

### Problema: Interface não abre
**Solução:**
```bash
# Verificar se tkinter está instalado
python -c "import tkinter; print(\'OK\')"

# Se der erro, instalar tkinter (Ubuntu/Debian)
sudo apt-get install python3-tk
```

### Problema: Servidor não inicia
**Solução:**
```bash
# Verificar se a porta 5000 está livre
netstat -tlnp | grep 5000

# Se estiver ocupada, matar o processo
sudo lsof -ti:5000 | xargs kill -9
```

### Problema: Erro ao carregar modelo
**Solução:**
- Verifique se o arquivo `plankton_model.h5` existe. Se não, execute `python plankton_ai.py` para recriar o modelo.

### Problema: Erro de memória
**Solução:**
- Redimensionar imagens grandes antes do upload
- Fechar outros programas que consomem muita RAM
- Usar imagens com resolução máxima de 2048x2048

### Problema: Classificação incorreta
**Possíveis causas:**
- Imagem de baixa qualidade
- Organismo não está nas classes suportadas
- Iluminação inadequada na imagem
- Múltiplos organismos na mesma imagem

**Dicas para melhores resultados:**
- Use imagens com boa iluminação
- Centralize o organismo na imagem
- Evite fundos muito complexos
- Use zoom adequado (organismo visível mas não pixelizado)

## 📊 Monitoramento e Logs

### Logs da Interface Gráfica
- **[INFO]**: Informações gerais do sistema
- **[SUCCESS]**: Operações bem-sucedidas
- **[WARNING]**: Avisos que não impedem o funcionamento
- **[ERROR]**: Erros que precisam de atenção

### Logs do Servidor Flask
Os logs aparecem na área inferior da interface e incluem:
- Requisições HTTP recebidas
- Tempo de processamento
- Erros de classificação
- Status de inicialização

## 🔧 Configurações Avançadas

### Alterar Porta do Servidor
No arquivo `flask_server.py`, linha final:
```python
app.run(host=\'0.0.0.0\', port=5000, debug=True)  # Altere 5000 para outra porta
```

### Ajustar Tamanho Máximo de Arquivo
No arquivo `flask_server.py`:
```python
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB - altere conforme necessário
```

### Adicionar Novos Formatos de Imagem
No arquivo `flask_server.py`:
```python
ALLOWED_EXTENSIONS = {\'png\', \'jpg\', \'jpeg\', \'gif\', \'bmp\', \'tiff\', \'webp\'}  # Adicione novos formatos
```

## 📱 Uso em Diferentes Sistemas

### Windows
```cmd
# Instalar Python 3.8+ do site oficial
# Abrir Command Prompt ou PowerShell
pip install -r requirements.txt
python plankton_gui.py
```

### macOS
```bash
# Instalar Python via Homebrew
brew install python
pip3 install -r requirements.txt
python3 plankton_gui.py
```

### Linux (Ubuntu/Debian)
```bash
# Instalar dependências do sistema
sudo apt-get update
sudo apt-get install python3 python3-pip python3-tk

# Instalar dependências Python
pip3 install -r requirements.txt
python3 plankton_gui.py
```

## 🎯 Casos de Uso Recomendados

### Pesquisa Científica
- Classificação rápida de amostras de plâncton
- Análise preliminar antes de identificação manual
- Documentação de biodiversidade marinha

### Educação
- Ensino de biologia marinha
- Demonstrações de IA aplicada
- Projetos estudantis de ciência

### Monitoramento Ambiental
- Avaliação da qualidade da água
- Estudos de impacto ambiental
- Monitoramento de ecossistemas aquáticos

---

**💡 Dica**: Mantenha sempre imagens de teste na pasta `test_images/` para verificar se o sistema está funcionando corretamente!

