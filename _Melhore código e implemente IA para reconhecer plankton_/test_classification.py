import requests
import os
import time

def test_classification():
    """Testa a classificação de imagens no servidor Flask."""
    server_url = "http://localhost:5000"
    
    # Verificar se o servidor está ativo
    try:
        response = requests.get(f"{server_url}/status", timeout=5)
        if response.status_code != 200:
            print(f"Erro: Servidor não está respondendo corretamente. Status: {response.status_code}")
            return
        print("Servidor está ativo.")
    except requests.exceptions.RequestException as e:
        print(f"Erro ao conectar ao servidor: {e}")
        return
    
    # Verificar classes suportadas
    try:
        response = requests.get(f"{server_url}/classes", timeout=5)
        if response.status_code == 200:
            classes = response.json().get('classes', [])
            print(f"Classes suportadas: {classes}")
        else:
            print(f"Erro ao obter classes: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"Erro ao obter classes: {e}")
    
    # Procurar por imagens de teste
    test_images = []
    for root, dirs, files in os.walk("."):
        for file in files:
            if file.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp')):
                test_images.append(os.path.join(root, file))
                if len(test_images) >= 3:  # Limitar a 3 imagens para teste
                    break
        if len(test_images) >= 3:
            break
    
    if not test_images:
        print("Nenhuma imagem de teste encontrada.")
        return
    
    print(f"Encontradas {len(test_images)} imagens para teste.")
    
    # Testar classificação
    for img_path in test_images:
        print(f"\nTestando classificação para: {img_path}")
        try:
            with open(img_path, 'rb') as f:
                start_time = time.time()
                response = requests.post(
                    f"{server_url}/predict", 
                    files={'file': f},
                    timeout=30
                )
                elapsed_time = time.time() - start_time
                
                if response.status_code == 200:
                    result = response.json()
                    print(f"Resposta do servidor: {result}")
                    print(f"Tempo de resposta: {elapsed_time:.2f} segundos")
                    
                    if result.get('success', False):
                        prediction = result.get('prediction', {})
                        print(f"Classe predita: {prediction.get('predicted_class', 'N/A')}")
                        print(f"Confiança: {prediction.get('confidence', 0):.2%}")
                    else:
                        print(f"Erro na classificação: {result.get('error', 'Erro desconhecido')}")
                else:
                    print(f"Erro na resposta do servidor: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"Erro ao classificar imagem: {e}")

if __name__ == "__main__":
    test_classification()