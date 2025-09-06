import torch
import torch.nn as nn
import torchvision.models as models
import json
import os

# Criar diretório de modelos se não existir
os.makedirs('models', exist_ok=True)

# Definir classes de plâncton para teste
class_names = [
    "Acantharia_protist",
    "Appendicularian_s_shape",
    "Appendicularian_straight",
    "Chaetognath_non_sagitta",
    "Chaetognath_sagitta",
    "Copepod_calanoid",
    "Copepod_cyclopoid_oithona",
    "Copepod_other",
    "Crustacean_other",
    "Diatom_chain"
]

# Criar modelo MobileNetV2
model = models.mobilenet_v2(weights=models.MobileNet_V2_Weights.IMAGENET1K_V1)

# Substituir a camada classificadora final
num_ftrs = model.classifier[1].in_features
model.classifier[1] = nn.Linear(num_ftrs, len(class_names))

# Salvar o modelo
model_path = 'models/plankton_model.pth'
torch.save(model.state_dict(), model_path)
print(f"Modelo salvo em: {model_path}")

# Salvar os nomes das classes
class_names_path = 'models/plankton_model_classes.json'
with open(class_names_path, 'w', encoding='utf-8') as f:
    json.dump(class_names, f, ensure_ascii=False, indent=4)
print(f"Classes salvas em: {class_names_path}")

# Salvar informações do modelo
model_info_path = 'models/plankton_model_info.json'
model_info = {
    "num_classes": len(class_names),
    "classes": class_names,
    "input_shape": [224, 224],
    "saved_date": "2025-09-05",
    "model_type": "MobileNetV2"
}
with open(model_info_path, 'w', encoding='utf-8') as f:
    json.dump(model_info, f, ensure_ascii=False, indent=4)
print(f"Informações do modelo salvas em: {model_info_path}")

print("Modelo de teste criado com sucesso!")