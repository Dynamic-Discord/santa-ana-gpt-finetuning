import os
import json
import docx
import tiktoken
from openai import OpenAI
from tabulate import tabulate

def read_docx(file_path):
    print(f"Leyendo el archivo: {file_path}")
    doc = docx.Document(file_path)
    full_text = []
    for para in doc.paragraphs:
        full_text.append(para.text)
    return '\n'.join(full_text)

def create_dataset_from_docs(directory_path):
    print(f"Creando dataset desde los documentos en el directorio: {directory_path}")
    examples = []
    for filename in os.listdir(directory_path):
        if filename.endswith(".docx"):
            file_path = os.path.join(directory_path, filename)
            if not os.path.isfile(file_path):
                print(f"Archivo no encontrado: {file_path}")
                continue
            try:
                content = read_docx(file_path)
                # Crear un ejemplo para el dataset
                examples.append({
                    "messages": [
                        {"role": "system", "content": "Eres un asistente útil que proporciona información sobre políticas empresariales."},
                        {"role": "user", "content": f"¿Cuál es el contenido del documento {filename}?"},
                        {"role": "assistant", "content": content}
                    ]
                })
                print(f"Ejemplo creado para el archivo: {filename}")
            except Exception as e:
                print(f"Error al leer el archivo {file_path}: {e}")
    
    print(f"Total de ejemplos creados: {len(examples)}")
    return examples

def save_dataset_to_jsonl(examples, output_dir, output_filename):
    print(f"Guardando dataset en formato .jsonl en el directorio: {output_dir}")
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, output_filename)
    with open(output_path, 'w', encoding='utf-8') as f:
        for i, example in enumerate(examples, 1):
            print("Archivo:", i, "🔄️")
            f.write(json.dumps(example, ensure_ascii=False) + '\n')
    print(f"Dataset guardado en: {output_path}")
    return output_path

def count_tokens(file_path):
    print(f"Contando tokens en el archivo: {file_path}")
    tokenizer = tiktoken.get_encoding("cl100k_base")
    total_tokens = 0
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            example = json.loads(line)
            for message in example['messages']:
                tokens = tokenizer.encode(message['content'])
                total_tokens += len(tokens)
    print(f"Total de tokens en {file_path}: {total_tokens}")
    return total_tokens

def analyze_tokens_in_directory(directory_path):
    print(f"Analizando tokens en los archivos del directorio: {directory_path}")
    token_counts = {}
    for filename in os.listdir(directory_path):
        if filename.endswith(".jsonl"):
            file_path = os.path.join(directory_path, filename)
            token_count = count_tokens(file_path)
            token_counts[filename] = token_count
    return token_counts

def calculate_costs(token_counts, epochs):
    print("Calculando costos de entrenamiento")
    costs = []
    for model in ["gpt-4o-mini-2024-07-18", "gpt-3.5-turbo"]:
        for epoch in epochs:
            for filename, tokens in token_counts.items():
                if model == "gpt-4o-mini-2024-07-18":
                    cost = tokens * epoch * 3.00 / 1e6
                elif model == "gpt-3.5-turbo":
                    cost = tokens * epoch * 8.00 / 1e6
                costs.append({
                    "model": model,
                    "epoch": epoch,
                    "filename": filename,
                    "tokens": tokens,
                    "cost": cost
                })
    return costs

# Directorio donde se encuentran los documentos .docx
directory_path = os.path.join("backend", "Data", "Gestión de calidad", "docs")
# Directorio de salida para el dataset
output_dir = os.path.join("backend", "FineTuning")
# Nombre del archivo de salida para el dataset
output_filename = "trainingFile.jsonl"

# Leer documentos y crear dataset
print("Iniciando la creación del dataset")
examples = create_dataset_from_docs(directory_path)

if examples:
    # Guardar dataset en archivo .jsonl
    output_path = save_dataset_to_jsonl(examples, output_dir, output_filename)
    print(f"Training File generado en {output_path}. ✅")

    # Analizar tokens en el archivo de entrenamiento
    token_counts = analyze_tokens_in_directory(output_dir)
    for filename, tokens in token_counts.items():
        print(f"El archivo {filename} tiene {tokens} tokens. 📈")

    # Calcular costos de entrenamiento
    epochs = [3, 4]
    costs = calculate_costs(token_counts, epochs)
    
    # Crear una tabla con los resultados
    table_data = []
    total_costs = {"gpt-4o-mini-2024-07-18": 0, "gpt-3.5-turbo": 0}
    
    for cost in costs:
        table_data.append([cost['model'], cost['epoch'], cost['filename'], cost['tokens'], f"${cost['cost']:.2f}"])
        total_costs[cost['model']] += cost['cost']
    
    headers = ["Modelo", "Épocas", "Archivo", "Tokens", "Costo"]
    table = tabulate(table_data, headers, tablefmt="grid")
    print(table)
    
    # Imprimir los costos totales por modelo
    print("\nCostos totales por modelo:")
    for model, total_cost in total_costs.items():
        print(f"{model}: ${total_cost:.2f}")

    # Subir archivo y crear un trabajo de afinación
    #training_file_id = upload_file_to_openai(output_path)
    #fine_tuning_job_id = create_fine_tuning_job(training_file_id)

    #print("Archivo de entrenamiento subido con ID:", training_file_id)
    #print("Trabajo de afinación creado con ID:", fine_tuning_job_id)
else:
    print("No se encontraron ejemplos para procesar.")
