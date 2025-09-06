# Definir variável global para disponibilidade do PyTorch
PYTORCH_AVAILABLE = False

# Importações que não dependem do PyTorch
import os
import json
import logging
import time
import traceback
from functools import lru_cache
from PIL import Image, UnidentifiedImageError

# Importação do NumPy com tratamento de erro
try:
    import numpy as np
except ImportError:
    print("Erro ao importar NumPy. Instalando versão compatível...")
    import sys
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "numpy==1.24.3"])
    import numpy as np

# Tentativa de importação do PyTorch
try:
    import torch
    import torch.nn as nn
    import torchvision.transforms as transforms
    import torchvision.models as models
    PYTORCH_AVAILABLE = True
except ImportError as e:
    print(f"Erro ao importar PyTorch: {e}")
    # Criar mocks para evitar quebra do código
    class DummyModule:
        def __init__(self, *args, **kwargs):
            pass
    
    class DummyTransforms:
        def Compose(self, *args, **kwargs):
            return lambda x: x
    
    class DummyModels:
        def mobilenet_v2(self, *args, **kwargs):
            return None
        class MobileNet_V2_Weights:
            IMAGENET1K_V1 = None
    
    torch = DummyModule()
    torch.nn = DummyModule()
    torch.nn.functional = DummyModule()
    torch.nn.Linear = lambda *args, **kwargs: None
    torch.device = lambda x: None
    torch.cuda = DummyModule()
    torch.cuda.is_available = lambda: False
    torch.cuda.get_device_name = lambda x: "N/A"
    torch.load = lambda *args, **kwargs: {}
    torch.no_grad = lambda: DummyModule()
    torch.max = lambda *args, **kwargs: (0, 0)
    torch.save = lambda *args, **kwargs: None

    transforms = DummyTransforms()
    models = DummyModels()

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("plankton_ai.log"), logging.StreamHandler()]
)
logger = logging.getLogger("plankton_ai")


class PlanktonClassifierPyTorch:
    def __init__(self, model_path=None):
        if not PYTORCH_AVAILABLE:
            logger.error("PyTorch não está disponível. O classificador não funcionará corretamente.")
            self.model = None
            self.device = None
        else:
            self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
            self.model = None

        self.class_names = [
            "Copepod",
            "Diatom",
            "Dinoflagellate",
            "Radiolarian",
            "Foraminifera",
            "Cyanobacteria",
            "Other"
        ]
        self.img_size = (224, 224)

        self.transform = transforms.Compose([
            transforms.Resize(self.img_size),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406],
                                 std=[0.229, 0.224, 0.225]),
        ])

        if model_path and os.path.exists(model_path):
            self.load_model(model_path)
        else:
            self.create_model()

    def create_model(self):
        if not PYTORCH_AVAILABLE:
            logger.error("Não é possível criar o modelo: PyTorch não está disponível")
            self.model = None
            return

        try:
            self.model = models.mobilenet_v2(weights=models.MobileNet_V2_Weights.IMAGENET1K_V1)
            for param in self.model.parameters():
                param.requires_grad = False
            num_ftrs = self.model.classifier[1].in_features
            self.model.classifier[1] = nn.Linear(num_ftrs, len(self.class_names))
            self.model = self.model.to(self.device)
            logger.info("Modelo PyTorch criado com sucesso!")
        except Exception as e:
            logger.error(f"Erro ao criar modelo: {str(e)}")
            self.model = None

    def preprocess_image(self, image_path):
        try:
            if os.path.getsize(image_path) == 0:
                return None, "Arquivo de imagem vazio"

            try:
                img = Image.open(image_path)
            except UnidentifiedImageError:
                return None, "Formato de imagem não reconhecido"

            if img.mode != "RGB":
                img = img.convert("RGB")

            img_tensor = self.transform(img).unsqueeze(0)
            return img_tensor.to(self.device), None
        except Exception as e:
            return None, f"Erro no pré-processamento da imagem: {str(e)}"

    def predict(self, image_path):
        start_time = time.time()
        if not PYTORCH_AVAILABLE:
            return {"error": "PyTorch não disponível", "success": False}

        if self.model is None:
            return {"error": "Modelo não carregado", "success": False}

        processed_img, error_msg = self.preprocess_image(image_path)
        if processed_img is None:
            return {"error": error_msg, "success": False}

        try:
            self.model.eval()
            with torch.no_grad():
                outputs = self.model(processed_img)
                probabilities = torch.nn.functional.softmax(outputs, dim=1)[0]
                confidence, predicted_class_idx = torch.max(probabilities, 0)

            result = {
                "predicted_class": self.class_names[predicted_class_idx.item()],
                "confidence": float(confidence.item()),
                "all_predictions": {c: float(probabilities[i].item()) for i, c in enumerate(self.class_names)},
                "success": True,
                "processing_time": round(time.time() - start_time, 3)
            }
            return result
        except Exception as e:
            return {"error": f"Erro durante a predição: {str(e)}", "success": False}

    def save_model(self, save_path):
        if self.model is None:
            return {"success": False, "message": "Nenhum modelo para salvar"}
        try:
            os.makedirs(os.path.dirname(os.path.abspath(save_path)), exist_ok=True)
            torch.save(self.model.state_dict(), save_path)
            with open(save_path.replace(".pth", "_classes.json"), "w", encoding="utf-8") as f:
                json.dump(self.class_names, f, ensure_ascii=False, indent=4)
            return {"success": True, "message": f"Modelo salvo em {save_path}"}
        except Exception as e:
            return {"success": False, "message": str(e)}

    def load_model(self, model_path):
        if not PYTORCH_AVAILABLE:
            return {"success": False, "message": "PyTorch não disponível"}
        if not os.path.exists(model_path):
            return {"success": False, "message": f"Arquivo não encontrado: {model_path}"}

        try:
            self.create_model()
            self.model.load_state_dict(torch.load(model_path, map_location=self.device))
            self.model.eval()
            return {"success": True, "message": f"Modelo carregado: {model_path}"}
        except Exception as e:
            return {"success": False, "message": str(e)}

    def get_model_info(self):
        if not PYTORCH_AVAILABLE:
            return {"success": False, "message": "PyTorch não disponível"}
        if self.model is None:
            return {"success": False, "message": "Modelo não carregado"}
        return {
            "classes": self.class_names,
            "num_classes": len(self.class_names),
            "input_shape": self.img_size,
            "device": str(self.device),
            "success": True
        }


def create_plankton_classifier():
    return PlanktonClassifierPyTorch()


if __name__ == "__main__":
    classifier = PlanktonClassifierPyTorch()
    info = classifier.get_model_info()
    print(f"Info: {info}")
    classifier.save_model("plankton_model.pth")
