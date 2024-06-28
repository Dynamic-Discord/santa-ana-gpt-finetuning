import csv
import json
import pandas as pd
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm

def calcular_estadisticas(df):
    return df.describe().to_dict()

def procesar_fila(row, index):
    estadisticas_fila = {
        'DISP': row['DISP'],
        'HORAS_JORNADA': row['HORAS_JORNADA'],
        'KMS': row['KMS'],
        'TIEMPO_VARADO': row['TIEMPO_VARADO']
    }
    data = {
        "user": f"Por favor, proporciona información sobre el caso {index + 1}.",
        "assistant": {
            "description": (f"El activo con código {row['COD_ACTIVO']} del departamento {row['NOMBRE_DEPTO']} "
                            f"en el taller {row['NOMBRE_TALLER']} tuvo una actividad de {row['NOMBRE_ACTIVIDAD']} "
                            f"durante la época {row['EPOCA']}, en el mes de {row['MonthName(MES)']} (período {row['PERIODO']}, "
                            f"semana {row['SEMANA']}). La causa del varado fue {row['CAUSA_VARADO']} y estuvo varado por "
                            f"{row['TIEMPO_VARADO']} días. La disponibilidad del activo fue del {row['Disponibilidad']} "
                            f"y su porcentaje de utilización fue del {row['Porc_utilizacion']}."),
            "statistics": estadisticas_fila
        }
    }
    return data

def csv_to_jsonl(file_path, output_path):
    df = pd.read_csv(file_path, encoding='utf-8')

    estadisticas_generales = calcular_estadisticas(df)

    with open(output_path, mode='w', encoding='utf-8') as jsonl_file:
        with ThreadPoolExecutor(max_workers=8) as executor:
            futures = {executor.submit(procesar_fila, row, index): index for index, row in df.iterrows()}
            for future in tqdm(as_completed(futures), total=len(futures), desc="Procesando filas"):
                data = future.result()
                jsonl_file.write(json.dumps(data) + '\n')

        # Agregar estadísticas generales al final
        estadisticas_data = {
            "user": "Por favor, proporciona las estadísticas generales de los datos.",
            "assistant": {
                "description": "Estadísticas generales de los datos.",
                "statistics": estadisticas_generales
            }
        }
        jsonl_file.write(json.dumps(estadisticas_data) + '\n')

# Convertir el archivo CSV a JSONL
csv_to_jsonl('data_taller_automotrizComma.csv', 'datos_convertidos.jsonl')
