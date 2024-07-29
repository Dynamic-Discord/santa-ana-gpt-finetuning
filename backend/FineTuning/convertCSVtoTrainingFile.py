import csv
import json

# Archivo CSV de entrada y archivo JSONL de salida
csv_file = 'backend/Data/Taller Automotriz/data_taller_automotrizComma.csv'
jsonl_file = 'backend/FineTuning/taller.jsonl'

with open(csv_file, 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    data = [row for row in reader]

# Función para crear un mensaje que incluya todas las columnas
def create_message(row):
    content = "\n".join([f"{key}: {value}" for key, value in row.items()])
    messages = [
        {"role": "system", "content": "Eres un asistente útil que proporciona información sobre políticas empresariales."},
        {"role": "user", "content": content},
        {"role": "assistant", "content": ""}
    ]
    return {"messages": messages}

# Crea el archivo JSONL
with open(jsonl_file, 'w', encoding='utf-8') as f:
    for row in data:
        jsonl_entry = create_message(row)
        f.write(json.dumps(jsonl_entry, ensure_ascii=False) + '\n')

print(f'Archivo JSONL creado en: {jsonl_file}')
