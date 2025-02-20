import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, Trainer, TrainingArguments
from peft import LoraConfig, get_peft_model, PeftModel
from datasets import Dataset
import pandas as pd

# 1. Define the dataset (example data)
data = [
    {"input_text": "The new policy will drastically cut emissions by 2030!", "normalized_claim": "Policy reduces emissions"},
    {"input_text": "Taxes are outrageously high this year.", "normalized_claim": "Taxes are elevated"},
    {"input_text": "Vaccines might save lives, say experts.", "normalized_claim": "Vaccines save lives"},
]
df = pd.DataFrame(data)
dataset = Dataset.from_pandas(df)

# 2. Load the base model and tokenizer
model_name = "meta-llama/Llama-2-7b-hf"  # Replace with your model (e.g., Mistral-7B)
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(model_name, device_map="auto", torch_dtype=torch.float16)

# Set padding token if not already set (common for some models)
if tokenizer.pad_token is None:
    tokenizer.pad_token = tokenizer.eos_token

# 3. Configure LoRA
lora_config = LoraConfig(
    r=16,              # Rank of the LoRA matrices
    lora_alpha=32,     # Scaling factor
    target_modules=["q_proj", "v_proj"],  # Target attention layers
    lora_dropout=0.05, # Dropout for regularization
    bias="none",       # No bias in LoRA
    task_type="CAUSAL_LM"  # For causal language modeling
)

# Apply LoRA to the model
model = get_peft_model(model, lora_config)
model.print_trainable_parameters()  # Check how many parameters are trainable

# 4. Preprocess the dataset
def preprocess_function(examples):
    # Format input with a prompt and append the target
    inputs = [f"Extract normalized claim: {text}" for text in examples["input_text"]]
    targets = examples["normalized_claim"]
    
    # Tokenize inputs
    model_inputs = tokenizer(inputs, max_length=128, truncation=True, padding="max_length")
    
    # Tokenize targets (shifted for causal LM)
    with tokenizer.as_target_tokenizer():
        labels = tokenizer(targets, max_length=32, truncation=True, padding="max_length")
    
    # Replace padding token IDs in labels with -100 (ignored by cross-entropy)
    labels["input_ids"] = [
        [(l if l != tokenizer.pad_token_id else -100) for l in label] 
        for label in labels["input_ids"]
    ]
    
    model_inputs["labels"] = labels["input_ids"]
    return model_inputs

# Apply preprocessing
tokenized_dataset = dataset.map(preprocess_function, batched=True)

# 5. Define training arguments
training_args = TrainingArguments(
    output_dir="./lora_retrained_model",
    per_device_train_batch_size=4,
    gradient_accumulation_steps=4,  # Effective batch size = 16
    num_train_epochs=3,
    learning_rate=2e-4,
    fp16=True,  # Mixed precision for efficiency
    logging_steps=10,
    save_steps=50,
    save_total_limit=2,
    remove_unused_columns=True,
)

# 6. Initialize Trainer
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=tokenized_dataset,
)

# 7. Train the model
trainer.train()

# 8. Save the retrained LoRA adapters
model.save_pretrained("./lora_retrained_model/final_adapters")
tokenizer.save_pretrained("./lora_retrained_model")

# 9. Inference example
def generate_normalized_claim(input_text, model, tokenizer):
    prompt = f"Extract normalized claim: {input_text}"
    inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
    outputs = model.generate(**inputs, max_new_tokens=20, num_beams=5, early_stopping=True)
    return tokenizer.decode(outputs[0], skip_special_tokens=True).split("Extract normalized claim: ")[-1]

# Test it
test_input = "The CEO says profits will soar next quarter!"
print(generate_normalized_claim(test_input, model, tokenizer))
# Expected output: Something like "Profits increase"