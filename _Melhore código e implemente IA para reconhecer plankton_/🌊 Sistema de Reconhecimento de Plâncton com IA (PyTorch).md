# 🌊 Sistema de Reconhecimento de Plâncton com IA (PyTorch)

Este projeto implementa um sistema completo para reconhecimento de diferentes tipos de plâncton utilizando Inteligência Artificial, agora com **PyTorch** como framework de deep learning.

## ✨ Funcionalidades

*   **Reconhecimento de Plâncton**: Classifica imagens de plâncton em 7 categorias distintas.
*   **Interface Gráfica (GUI)**: Aplicação desktop intuitiva construída com Tkinter para interação fácil.
*   **API RESTful**: Servidor Flask que expõe endpoints para classificação de imagens, permitindo integração com outras aplicações.
*   **Modelo Otimizado**: Utiliza uma arquitetura de rede neural eficiente (MobileNetV2) para inferência rápida.

## 🔬 Classes de Plâncton Suportadas

O modelo é treinado para identificar as seguintes classes de plâncton:

1.  **Copepod**
2.  **Diatom**
3.  **Dinoflagellate**
4.  **Radiolarian**
5.  **Foraminifera**
6.  **Cyanobacteria**
7.  **Other**

## 🚀 Como Usar

Para instruções detalhadas sobre como configurar e executar o sistema, por favor, consulte o arquivo `INSTRUCOES_USO.md`.

## 🛠️ Estrutura do Projeto

*   `plankton_ai.py`: Contém a implementação do modelo de IA (PyTorch) para classificação de plâncton.
*   `flask_server.py`: Implementa o servidor Flask que expõe a API RESTful para o modelo de IA.
*   `flask_server_launcher.py`: Script auxiliar para iniciar o servidor Flask em segundo plano.
*   `plankton_gui.py`: Contém o código da interface gráfica do usuário (GUI) construída com Tkinter.
*   `plankton_model.pth`: O modelo de IA pré-treinado (formato PyTorch).
*   `plankton_model_classes.json`: Arquivo JSON com os nomes das classes que o modelo pode identificar.
*   `requirements.txt`: Lista de todas as dependências Python necessárias.
*   `test_system.py`: Script para testar a funcionalidade completa do sistema.
*   `INSTRUCOES_USO.md`: Documentação detalhada sobre a instalação, execução e uso do sistema.
*   `README.md`: Este arquivo.

## 📦 Instalação

1.  **Clone o repositório (se aplicável) ou baixe os arquivos.**
2.  **Instale as dependências Python** usando o `requirements.txt`:
    ```bash
    pip install -r requirements.txt
    ```

## ▶️ Execução

Para executar o sistema, siga as instruções no `INSTRUCOES_USO.md`.

## 🧪 Testes

Você pode executar o script de testes para verificar a funcionalidade do sistema:

```bash
python test_system.py
```

## 🤝 Contribuição

Sinta-se à vontade para contribuir com melhorias, correções de bugs ou novas funcionalidades. Por favor, abra uma issue ou envie um pull request.

## 📄 Licença

Este projeto está licenciado sob a [SUA LICENÇA AQUI, ex: MIT License].

---

