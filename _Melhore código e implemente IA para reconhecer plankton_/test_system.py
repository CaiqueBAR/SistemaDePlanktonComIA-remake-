#!/usr/bin/env python3
"""
Script de teste para o sistema de reconhecimento de plâncton.
Testa a integração entre o modelo de IA (PyTorch) e o servidor Flask.
"""

import requests
import json
import os
import time
import subprocess
import sys
from plankton_ai import PlanktonClassifierPyTorch # Importa a classe PyTorch

def test_plankton_classifier():
    """Testa o classificador de plâncton diretamente (PyTorch)."""
    print("=== Testando Classificador de Plâncton (PyTorch) ===")
    
    try:
        # Cria o classificador
        classifier = PlanktonClassifierPyTorch()
        
        # Testa informações do modelo
        info = classifier.get_model_info()
        print(f"✅ Modelo carregado: {info['model_loaded']}")
        print(f"✅ Classes suportadas: {len(info['classes'])}")
        print(f"✅ Classes: {', '.join(info['classes'])}")
        
        # Testa com uma imagem de teste (se existir)
        test_image = "test_images/copepod_test.jpg"
        if os.path.exists(test_image):
            print(f"\n🔬 Testando classificação com: {test_image}")
            result = classifier.predict(test_image)
            
            if "error" not in result:
                print(f"✅ Classe predita: {result['predicted_class']}")
                print(f"✅ Confiança: {result['confidence']:.2%}")
            else:
                print(f"❌ Erro na predição: {result['error']}")
        else:
            print(f"⚠️ Imagem de teste não encontrada: {test_image}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro no teste do classificador: {e}")
        return False

def test_flask_server():
    """Testa o servidor Flask."""
    print("\n=== Testando Servidor Flask ===")
    
    server_url = "http://localhost:5000"
    
    try:
        # Testa endpoint de status
        print("🔍 Testando endpoint /status...")
        response = requests.get(f"{server_url}/status", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Status: {data.get('status')}")
            print(f"✅ Mensagem: {data.get('message')}")
            
            # Testa endpoint de classes
            print("\n🔍 Testando endpoint /classes...")
            response = requests.get(f"{server_url}/classes", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Classes disponíveis: {len(data['classes'])}")
                print(f"✅ Classes: {', '.join(data['classes'])}")
            else:
                print(f"❌ Erro no endpoint /classes: {response.status_code}")
                return False
            
            # Testa endpoint de predição (se houver imagem)
            test_image = "test_images/copepod_test.jpg"
            if os.path.exists(test_image):
                print(f"\n🔬 Testando predição com: {test_image}")
                
                with open(test_image, "rb") as f:
                    files = {"file": f}
                    response = requests.post(f"{server_url}/predict", files=files, timeout=30)
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get("success"):
                        prediction = data["prediction"]
                        print(f"✅ Predição bem-sucedida!")
                        print(f"✅ Classe: {prediction['predicted_class']}")
                        print(f"✅ Confiança: {prediction['confidence']:.2%}")
                    else:
                        print(f"❌ Erro na predição: {data}")
                        return False
                else:
                    print(f"❌ Erro HTTP na predição: {response.status_code}")
                    return False
            else:
                print(f"⚠️ Imagem de teste não encontrada: {test_image}")
            
            return True
            
        else:
            print(f"❌ Servidor não respondeu corretamente: {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Não foi possível conectar ao servidor Flask")
        print("💡 Certifique-se de que o servidor está rodando em localhost:5000")
        return False
        
    except Exception as e:
        print(f"❌ Erro no teste do servidor: {e}")
        return False

def test_integration():
    """Testa a integração completa do sistema."""
    print("\n=== Teste de Integração Completa ===")
    
    # Verifica se os arquivos necessários existem
    required_files = [
        "plankton_ai.py",
        "flask_server.py",
        "plankton_gui.py",
        "plankton_model.pth" # Alterado para .pth
    ]
    
    missing_files = []
    for file in required_files:
        if not os.path.exists(file):
            missing_files.append(file)
    
    if missing_files:
        print(f"❌ Arquivos necessários não encontrados: {', '.join(missing_files)}")
        return False
    else:
        print("✅ Todos os arquivos necessários estão presentes")
    
    # Verifica se as dependências estão instaladas
    try:
        import torch
        import torchvision
        import flask
        import flask_cors
        import PIL
        import cv2
        import numpy
        print("✅ Todas as dependências estão instaladas")
    except ImportError as e:
        print(f"❌ Dependência não encontrada: {e}")
        return False
    
    return True

def main():
    """Função principal do teste."""
    print("🧪 SISTEMA DE TESTE - RECONHECIMENTO DE PLÂNCTON")
    print("=" * 60)
    
    # Executa os testes
    tests = [
        ("Classificador de IA", test_plankton_classifier),
        ("Integração do Sistema", test_integration),
        ("Servidor Flask", test_flask_server)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        print(f"\n🔬 Executando: {test_name}")
        print("-" * 40)
        
        try:
            result = test_func()
            results[test_name] = result
            
            if result:
                print(f"✅ {test_name}: PASSOU")
            else:
                print(f"❌ {test_name}: FALHOU")
                
        except Exception as e:
            print(f"❌ {test_name}: ERRO - {e}")
            results[test_name] = False
    
    # Resumo dos resultados
    print("\n" + "=" * 60)
    print("📊 RESUMO DOS TESTES")
    print("=" * 60)
    
    passed = sum(1 for result in results.values() if result)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASSOU" if result else "❌ FALHOU"
        print(f"{test_name:<25} {status}")
    
    print(f"\n📈 Resultado Final: {passed}/{total} testes passaram")
    
    if passed == total:
        print("🎉 Todos os testes passaram! Sistema funcionando corretamente.")
        return True
    else:
        print("⚠️ Alguns testes falharam. Verifique os erros acima.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)


