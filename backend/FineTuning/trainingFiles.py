import os
import json
import docx
import tiktoken
from openai import OpenAI

def read_docx(file_path):
    doc = docx.Document(file_path)
    full_text = []
    for para in doc.paragraphs:
        full_text.append(para.text)
    return '\n'.join(full_text)

def create_dataset_from_docs(directory_path):
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
            except Exception as e:
                print(f"Error al leer el archivo {file_path}: {e}")
    
    return examples

def save_dataset_to_jsonl(examples, output_dir, output_filename):
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, output_filename)
    with open(output_path, 'w', encoding='utf-8') as f:
        for i, example in enumerate(examples, 1):
            print("Archivo:", i,"🔄️")
            f.write(json.dumps(example, ensure_ascii=False) + '\n')
    return output_path

def count_tokens(file_path):
    tokenizer = tiktoken.get_encoding("cl100k_base")
    total_tokens = 0
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            example = json.loads(line)
            for message in example['messages']:
                tokens = tokenizer.encode(message['content'])
                total_tokens += len(tokens)
    return total_tokens

def upload_file_to_openai(file_path):
    client = OpenAI(api_key='tu_api_key')

    # Subir el archivo de entrenamiento
    response = client.files.create(
        file=open(file_path, "rb"),
        purpose="fine-tune"
    )

    return response['id']

def create_fine_tuning_job(training_file_id):
    client = OpenAI(api_key='tu_api_key')

    # Crear un trabajo de afinación
    response = client.fine_tuning.jobs.create(
        training_file=training_file_id, 
        model="gpt-3.5-turbo"
    )

    return response['id']

# Directorio donde se encuentran los documentos .docx
directory_path = os.path.join("backend", "Data", "Gestión de calidad", "docs")
# Directorio de salida para el dataset
output_dir = os.path.join("backend", "FineTuning")
# Nombre del archivo de salida para el dataset
output_filename = "trainingFile.jsonl"

# Leer documentos y crear dataset
examples = create_dataset_from_docs(directory_path)

if examples:
    # Guardar dataset en archivo .jsonl
    output_path = save_dataset_to_jsonl(examples, output_dir, output_filename)
    print(f"Training File generado en {output_path}. ✅")

    # Contar tokens en el archivo de entrenamiento
    total_tokens = count_tokens(output_path)
    print(f"El archivo de entrenamiento tiene {total_tokens} tokens. 📈")

    # Subir archivo y crear un trabajo de afinación
    #training_file_id = upload_file_to_openai(output_path)
    #fine_tuning_job_id = create_fine_tuning_job(training_file_id)

    #print("Archivo de entrenamiento subido con ID:", training_file_id)
    #print("Trabajo de afinación creado con ID:", fine_tuning_job_id)
else:
    print("No se encontraron ejemplos para procesar.")
