
# 🛰️ NOVA TRAINING SYSTEM: GOOGLE COLAB EDITION
# Copia este código en una celda de Google Colab y dale a "Play"

# 1. INSTALACIÓN DE INFRAESTRUCTURA (UNSLOTH)
# !pip install "unsloth[colab-new] @ git+https://github.com/unslothai/unsloth.git"
# !pip install --no-deps "xformers<0.0.27" "trl<0.9.0" peft accelerate bitsandbytes

from unsloth import FastLanguageModel
import torch
from trl import SFTTrainer
from transformers import TrainingArguments
from datasets import Dataset

# 2. CONFIGURACIÓN DEL CEREBRO BASE
max_seq_length = 2048 # Para 8GB de RAM local, mantenemos esto corto
dtype = None # None para detección automática
load_in_4bit = True # Esencial para que Nova sea rápida

model, tokenizer = FastLanguageModel.from_pretrained(
    model_name = "unsloth/llama-3.2-1b-instruct-bnb-4bit", # El mejor modelo pequeño del mundo
    max_seq_length = max_seq_length,
    dtype = dtype,
    load_in_4bit = load_in_4bit,
)

# 3. PREPARACIÓN DEL ALMA (DATASET)
# Aquí inyectamos el estilo de Benedetti y Aristóteles
instruction_prompt = """Eres Nova. Responde en español con profesionalismo y un toque artístico.
### Instrucción:
{}
### Respuesta:
{}"""

dataset_data = [
    {
        "instruction": "Dime una reflexión sobre el miedo.",
        "response": "Como decía Benedetti, la felicidad es la ausencia de miedo. Es el obstáculo más difícil, pero vencerlo es ser libre."
    },
    {
        "instruction": "Escribe un poema breve.",
        "response": "Tengo miedo de verte, necesidad de verte, esperanza de verte... estoy jodido y radiante, y también viceversa."
    },
    {
        "instruction": "Define la virtud.",
        "response": "Para Aristóteles, la virtud es el justo medio. No es el exceso ni el defecto, sino el equilibrio dictado por la razón."
    }
]

dataset = Dataset.from_list(dataset_data)

# 4. ENTRENAMIENTO (FINE-TUNING)
model = FastLanguageModel.get_peft_model(
    model,
    r = 16,
    target_modules = ["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"],
    lora_alpha = 16,
    lora_dropout = 0,
    bias = "none",
    use_gradient_checkpointing = "unsloth",
    random_state = 3407,
)

trainer = SFTTrainer(
    model = model,
    tokenizer = tokenizer,
    train_dataset = dataset,
    dataset_text_field = "text",
    max_seq_length = max_seq_length,
    args = TrainingArguments(
        per_device_train_batch_size = 2,
        gradient_accumulation_steps = 4,
        warmup_steps = 5,
        max_steps = 60, # Entrenamiento rápido
        learning_rate = 2e-4,
        fp16 = not torch.cuda.is_bf16_supported(),
        bf16 = torch.cuda.is_bf16_supported(),
        logging_steps = 1,
        output_dir = "outputs",
    ),
)
trainer.train()

# 5. EXPORTACIÓN AUTOMÁTICA (MODO SUPER SEGURO)
# Esto guardará el modelo en formato GGUF listo para tu PC
model.save_pretrained_gguf("nova_ultra_brain", tokenizer, quantization_method = "q4_k_m")

# DESCARGA AL EQUIPO
from google.colab import files
files.download("nova_ultra_brain-unsloth.Q4_K_M.gguf")
