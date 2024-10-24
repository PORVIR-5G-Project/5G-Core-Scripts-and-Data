import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from prometheus_pandas import query
from datetime import datetime
import re
import argparse
import os

# URL do Prometheus
prometheus_url = "http://localhost:37877"

# Função para converter timestamps UNIX em formato de data legível
def timestamp_to_datetime(timestamp):
    return datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S")

# Função para arredondar a data e converter para UNIX timestamp
def redefine_date(date_str):
    dt = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
    if dt.second >= 30:
        dt = dt.replace(second=30, microsecond=0)
    else:
        dt = dt.replace(second=0, microsecond=0)
    return dt.timestamp()

# Função para normalizar os resultados da consulta
def normalize_result(result):
    result_str = result.to_string()
    result_list = re.split(r'[ \n]+', result_str)
    float_values = [float(value) for value in result_list if value.replace('.', '', 1).isdigit()]
    return float_values

# Função para calcular o valor máximo de uma lista de floats
def mean_calc(float_values):
    if float_values:
        return sum(float_values)/len(float_values)
    return None

def get_receive_bytes(start_end_timestamps, output_csv):
    pastas = ['amf', 'ausf', 'bsf', 'nrf', 'nssf', 'pcf', 'smf', 'udm', 'udr', 'upf']
    prometheus = query.Prometheus(prometheus_url)
    
    # DataFrames para somar valores e contar intervalos
    combined_data_sum = pd.DataFrame(index=pastas, columns=pastas, dtype=float).fillna(0)
    count_data = pd.DataFrame(index=pastas, columns=pastas, dtype=float).fillna(0)

    for start, end in start_end_timestamps:
        start = redefine_date(timestamp_to_datetime(start))
        end = redefine_date(timestamp_to_datetime(end))
        
        data = pd.DataFrame(index=pastas, columns=pastas)

        if 'upf' in pastas:
            index = pastas.index('upf')  # Encontra o índice de 'upf'
            pastas[index] = 'upf-1'  

        for i, source_app in enumerate(pastas):
            for j, dest_app in enumerate(pastas):
                query_string = (
                    f'sum(rate(istio_requests_total{{namespace="cemenin", '
                    f'source_app="open5gs-{pastas[i]}", reporter="destination",'
                    f'response_code!~"200|201|204", destination_app="open5gs-{pastas[j]}"}}[2m0s]))'
                )
                result = prometheus.query_range(query_string, start, end, "30s")
                normalized_values = normalize_result(result)
                
                mean_value = mean_calc(normalized_values) if normalized_values else 0
                data.iloc[i, j] = mean_value

                # Acumular os somatórios
                combined_data_sum.iloc[i, j] += mean_value
                # Contar intervalos onde há dados
                if mean_value > 0:
                    count_data.iloc[i, j] += 1

    # Calcular a média dividindo os somatórios pelo número de intervalos
    combined_data = combined_data_sum.copy()
    for i in range(len(pastas)):
        for j in range(len(pastas)):
            if count_data.iloc[i, j] > 0:
                combined_data.iloc[i, j] = combined_data_sum.iloc[i, j] / count_data.iloc[i, j]
            else:
                combined_data.iloc[i, j] = 0  # Definir como 0 onde não há dados

    combined_data.to_csv(output_csv)
    return combined_data

def generate_heatmaps_for_directories(directories, output_image="Heatmap_Errors_Open5GS.png"):
    num_dirs = len(directories)
    # Configurar o gráfico para 2 linhas e 2 colunas
    fig, axs = plt.subplots(2, 2, figsize=(10, 10), squeeze=False)  # 2 linhas, 2 colunas

    # Títulos para cada subplot
    titles = [
        'Scenario 1',
        'Scenario 2',
        'Scenario 3',
        'Scenario 4'
    ]

    all_data = []  # Para armazenar todos os DataFrames
    for directory in directories:
        # Lê os dados do CSV correspondente ao diretório
        csv_file = f"{directory}/output_error.csv"  # Ajuste conforme necessário
        data = pd.read_csv(csv_file, index_col=0)

        all_data.append(data)  # Adiciona o DataFrame à lista

    # Determina os limites vmin e vmax com base em todos os dados
    combined_data = pd.concat(all_data)
    vmin = combined_data.min().min()  # Mínimo de todos os DataFrames
    vmax = combined_data.max().max()  # Máximo de todos os DataFrames

    lighter_palette = sns.light_palette("orange", as_cmap=True)

    for idx, data in enumerate(all_data):
        # Configurações do Seaborn
        sns.set_theme(style="whitegrid")
        # Acessa o eixo correto com base no índice
        row = idx // 2  # Determina a linha (0 ou 1)
        col = idx % 2   # Determina a coluna (0 ou 1)
        
        sns.heatmap(data, annot=True, cmap=lighter_palette, fmt='.2f', linewidths=.5, 
                     ax=axs[row, col], vmin=vmin, vmax=vmax, annot_kws={"size": 9, "color": "black"}, cbar=False)  # Passa vmin e vmax

        axs[row, col].set_title(f'{titles[idx]}', fontsize=14)
        axs[row, col].tick_params(axis='y', rotation=0, labelsize=12)  # Aumenta a fonte das labels do eixo Y
        axs[row, col].tick_params(axis='x', labelsize=12)

    # Adiciona uma barra de cores geral à direita de todos os subplots
    cbar_ax = fig.add_axes([0.92, 0.3, 0.02, 0.4])  # Definir a posição da barra de cores (ajustar conforme necessário)
    sm = plt.cm.ScalarMappable(cmap=lighter_palette, norm=plt.Normalize(vmin=vmin, vmax=vmax))
    sm.set_array([])  # Array vazio apenas para criar o mapeamento de cor
    fig.colorbar(sm, cax=cbar_ax)

    fig.text(0.5, 0.01, 'Destination Function', ha='center', fontsize=14)  # Eixo X geral ajustado
    fig.text(0.01, 0.5, 'Source Function', va='center', rotation='vertical', fontsize=14)  # Eixo Y geral ajustado

    # Ajustar layout para evitar sobreposição
    plt.tight_layout(rect=[0.03, 0.03, 0.9, 1.0])  # Deixar espaço para a barra de cores

    plt.savefig(output_image, dpi=300)
    plt.show()

def get_timestamps_from_file(filepath):
    start_end_timestamps = []
    with open(filepath, 'r') as f:
        for line in f:
            # Cada linha deve estar no formato "timestamp_inicial-timestamp_final"
            match = re.match(r"(\d+)-(\d+)", line.strip())
            if match:
                start_end_timestamps.append((int(match.group(1)), int(match.group(2))))
    return start_end_timestamps

def get_timestamps_from_directory(directory):
    # Caminho do arquivo timestamps.txt
    filepath = os.path.join(directory, 'timestamps.txt')
    
    # Verifica se o arquivo existe no diretório
    if os.path.exists(filepath):
        return get_timestamps_from_file(filepath)
    else:
        raise FileNotFoundError(f"O arquivo 'timestamps.txt' não foi encontrado no diretório: {directory}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Fetch and visualize metrics from Prometheus.")
    parser.add_argument("directories", nargs='+', type=str, help="List of directories containing the CSV files.")
    parser.add_argument("--output_csv", type=str, default="output_error.csv", help="Output CSV file name")
    parser.add_argument("--output_image", type=str, default="Heatmap_Errors_Open5GS.png", help="Output image file name")

    args = parser.parse_args()

    for directory in args.directories:
        start_end_timestamps = get_timestamps_from_directory(directory)
        output_csv = f"{directory}/output_error.csv"  # Salva o CSV em cada diretório
        print(output_csv)
        data = get_receive_bytes(start_end_timestamps, output_csv)
    
    # Gera os heatmaps para todos os diretórios
    generate_heatmaps_for_directories(args.directories, args.output_image)

