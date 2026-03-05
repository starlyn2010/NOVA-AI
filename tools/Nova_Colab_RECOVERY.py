
# 🛠️ NOVA RECOVERY: ULTRA-STABLE CLOUD TRAINING
# Este cuaderno está diseñado para NO fallar bajo estrés.

# 1. ANTIDISCONNECT: Ejecuta esto para evitar que Colab se duerma
# (Ponlo en el inspector del navegador > Consola si puedes)
# function ClickConnect(){ console.log("Clicking Connect..."); document.querySelector("colab-connect-button").click() }
# setInterval(ClickConnect, 60000)

# 2. INSTALACIÓN (Sin ruidos, directo al grano)
!pip install --quiet "unsloth[colab-new] @ git+https://github.com/unslothai/unsloth.git"
!pip install --quiet --no-deps "xformers<0.0.27" "trl<0.9.0" peft accelerate bitsandbytes

from unsloth import FastLanguageModel
import torch
from trl import SFTTrainer
from transformers import TrainingArguments
from datasets import load_dataset
from google.colab import drive, files
import os
import shutil

# 3. SEGURIDAD DE DRIVE (FORZADO)
print("📌 Conectando Drive... Confirma el permiso en la ventana.")
drive.mount('/content/drive', force_remount=True)
SAVE_DIR = "/content/drive/MyDrive/Nova_Ultra_Result/"
os.makedirs(SAVE_DIR, exist_ok=True)

# 4. CARGA DE CEREBRO
model_name = "unsloth/llama-3.2-1b-instruct-bnb-4bit"
model, tokenizer = FastLanguageModel.from_pretrained(
    model_name = model_name,
    max_seq_length = 2048,
    load_in_4bit = True,
)

# 5. CARGA DEL DATASET
# Sube el archivo 'art_universe_500.jsonl' a la carpeta de Colab
if not os.path.exists("art_universe_500.jsonl"):
    print("❌ ERROR: No has subido 'art_universe_500.jsonl' a la izquierda.")
else:
    dataset = load_dataset("json", data_files="art_universe_500.jsonl", split="train")
    def format_p(ex):
        return {"text": [f"### Instruction:\n{i}\n\n### Response:\n{o}" for i, o in zip(ex["instruction"], ex["output"])]}
    dataset = dataset.map(format_p, batched=True)

    # 6. ENTRENAMIENTO
    model = FastLanguageModel.get_peft_model(model, r=16, lora_alpha=16, random_state=3407)
    trainer = SFTTrainer(
        model = model, tokenizer = tokenizer, train_dataset = dataset,
        dataset_text_field = "text", max_seq_length = 2048,
        args = TrainingArguments(max_steps = 100, learning_rate = 2e-4, output_dir = "outputs", logging_steps=10)
    )
    print("⏳ Entrenando... Esto tardará unos 10 mins.")
    trainer.train()

    # 7. EXPORTACIÓN BLINDADA (El punto crítico)
    FINAL_NAME = "nova_brain_v1"
    print("💾 Guardando GGUF... No cierres esta pestaña.")
    model.save_pretrained_gguf(FINAL_NAME, tokenizer, quantization_method = "q4_k_m")
    
    # BUSCAMOS EL ARCHIVO REAL GENERADO (Unsloth a veces le pone nombres largos)
    generated_files = [f for f in os.listdir(".") if f.endswith(".gguf")]
    if generated_files:
        real_file = generated_files[0]
        print(f"✅ Archivo detectado: {real_file}")
        
        # COPIA A DRIVE CON FLUSH
        print("📁 Sincronizando con Drive... Espera.")
        shutil.copy(real_file, os.path.join(SAVE_DIR, real_file))
        drive.flush_and_unmount() # FORZAMOS que se guarde de verdad antes de que se desconecte
        print(f"🔥 ¡ÉXITO! El archivo está en tu Google Drive: MyDrive/Nova_Ultra_Result/")
        
        # DESCARGA FINAL
        files.download(real_file)
    else:
        print("❌ Error: No se encontró el archivo GGUF generado.")
