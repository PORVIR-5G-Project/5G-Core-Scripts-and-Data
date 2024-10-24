import pandas as pd
import seaborn as sns
import numpy as np
import matplotlib.pyplot as plt
from prometheus_pandas import query
from datetime import datetime
import re
import argparse
import os

prometheus_url = "http://localhost:37877"
pastas = ['amf', 'ausf', 'nrf', 'nssf', 'pcf', 'smf', 'udm', 'udr', 'upf']

def timestamp_to_datetime(timestamp):
    return datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S")

def redefine_date(date_str):
    dt = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
    dt = dt.replace(second=30 if dt.second >= 30 else 0, microsecond=0)
    return dt.timestamp()

def normalize_result(result):
    normalized_result = []

    result_string = result.to_string()

    # Agora você pode usar split() na string
    separated_data = result_string.split()

    
    for i in range(3, len(separated_data), 3):
        normalized_result.append(float(separated_data[i]))
    
    return normalized_result

def mean_calc(float_values):
    return sum(float_values) / len(float_values) if float_values else 0

def calcular_media_por_componente(data):
    # Agrupa os dados pela primeira coluna (nomes dos componentes)
    media_por_componente = data.groupby(data.index).mean()
    
    # Retorna o DataFrame com as médias calculadas para cada componente
    return media_por_componente

def fetch_metrics(query_string, start, end):
    prometheus = query.Prometheus(prometheus_url)
    result = prometheus.query_range(query_string, start, end, "30s")
    return normalize_result(result)

def get_combined_metrics_data(start_end_timestamps, output_csv="output.csv"):
    data = pd.DataFrame(index=pastas, columns=["mean_cpu_usage", "mean_memory_usage", "mean_receive_bytes", "mean_transmit_bytes"])

    metrics = {
        "mean_cpu_usage": 'sum(node_namespace_pod_container:container_cpu_usage_seconds_total:sum_irate{cluster="", namespace="free5gc"} * on(namespace,pod) group_left(workload, workload_type)',
        "mean_memory_usage": 'sum(container_memory_working_set_bytes{job="kubelet", metrics_path="/metrics/cadvisor", cluster="", namespace="free5gc", container!="", image!=""} * on(namespace,pod) group_left(workload, workload_type)',
        "mean_receive_bytes": 'sum(rate(container_network_receive_bytes_total{job="kubelet", metrics_path="/metrics/cadvisor", cluster="", namespace="free5gc"}[2m0s]) * on (namespace,pod) group_left(workload,workload_type)',
        "mean_transmit_bytes": 'sum(rate(container_network_transmit_bytes_total{job="kubelet", metrics_path="/metrics/cadvisor", cluster="", namespace="free5gc"}[2m0s]) * on (namespace,pod) group_left(workload,workload_type)'
    }

    combined_data = []

    for start, end in start_end_timestamps:
        start, end = redefine_date(timestamp_to_datetime(start)), redefine_date(timestamp_to_datetime(end))
        interval_data = data.copy()

        for pasta in pastas:
            for metric_col, query_string in metrics.items():
                query_string += f' namespace_workload_pod:kube_pod_owner:relabel{{cluster="", namespace="free5gc", workload="free5gc-{pasta}"}}) by (workload)'
                mean_value = mean_calc(fetch_metrics(query_string, start, end))
                interval_data.at[pasta, metric_col] = mean_value
        #interval_data['interval'] = f"{start}-{end}"
        combined_data.append(interval_data)

    # Concatenando todos os dados coletados
    full_data = pd.concat(combined_data)
    
    # Calculando a média para cada componente
    media_por_componente = full_data.groupby(full_data.index).mean()

    # Salvando os resultados em um arquivo CSV
    media_por_componente.to_csv(output_csv)

    return media_por_componente

def generate_stacked_barplots_per_component(csv_files, output_image="stacked_barplots.png"):
    # Criar um DataFrame vazio para acumular dados de todos os CSVs
    df_combined = pd.DataFrame()
    scenarios = []
    titles = ['CPU Usage', 'Memory Usage', 'Receive Bandwidth', 'Transmit Bandwidth']
    y_axis = ['mCores', 'MB', 'Kbits/s', 'Kbits/s']

    # Dicionário de cores para os componentes
    component_colors = {
        "amf": (0.12156862745098039, 0.4666666666666667, 0.7058823529411765, 1.0),
        "ausf": (1.0, 0.4980392156862745, 0.054901960784313725, 1.0),
        "nrf": (0.17254901960784313, 0.6274509803921569, 0.17254901960784313, 1.0),
        "nssf": (0.8392156862745098, 0.15294117647058825, 0.1568627450980392, 1.0),
        "pcf": (0.5490196078431373, 0.33725490196078434, 0.29411764705882354, 1.0),
        "smf": (0.8901960784313725, 0.4666666666666667, 0.7607843137254902, 1.0),
        "udm": (0.4980392156862745, 0.4980392156862745, 0.4980392156862745, 1.0),
        "udr": (0.7372549019607844, 0.7411764705882353, 0.13333333333333333, 1.0),
        "upf": (0.09019607843137255, 0.7450980392156863, 0.8117647058823529, 1.0)
    }

    # Ler e acumular os dados de todos os arquivos CSV
    for index, csv_file in enumerate(csv_files):
        df = pd.read_csv(csv_file, index_col=0)
        # Adicionar coluna de cenário
        scenario_name = f'Scenario {index + 1}'
        df['Scenario'] = scenario_name
        df_combined = pd.concat([df_combined, df], axis=0)
        scenarios.append(scenario_name)

    # Nomes das métricas
    metrics = df_combined.columns[:-1]  # Exclui a coluna de Cenário

    # Configurar o gráfico
    fig, axes = plt.subplots(nrows=2, ncols=2, figsize=(12, 10))  # Gráficos sem compartilhamento de eixo X

    max_y3_4 = 0  # Variável para guardar o valor máximo dos gráficos 3 e 4
    handles = []  # Lista para armazenar os handles da legenda
    labels = []  # Lista para armazenar os labels da legenda (componentes)

    # Criar gráficos empilhados para cada métrica
    for i, (ax, metric) in enumerate(zip(axes.flatten(), metrics)):
        bottom = np.zeros(len(scenarios))  # Inicializa a base do empilhamento com uma barra para cada cenário

        # Conversão de unidades (MB para o gráfico 2, KB para gráficos 3 e 4)
        if i == 1:
            df_combined[metric] = df_combined[metric] / (1024 * 1024)  # Converte para MB
        elif i in [2, 3]:
            df_combined[metric] = 8 * df_combined[metric] / 1024  # Converte para Kbits

        # Empilhar as barras para cada componente e cenário
        for j, component in enumerate(component_colors.keys()):  # Iterar sobre as chaves do dicionário de cores
            # Filtrar os dados do componente e cenário atual
            values = df_combined[df_combined.index == component].groupby('Scenario')[metric].sum()
            for k, scenario in enumerate(scenarios):
                if scenario in values.index:
                    bar = ax.bar(scenario, values[scenario], bottom=bottom[k], 
                                  color=component_colors[component], label=component if k == 0 else "")
                    bottom[k] += values[scenario]  # Atualiza a base para o próximo empilhamento

            # Armazenar handles e labels apenas uma vez
            if i == 0:
                handles.append(bar)
                labels.append(component)

        # Ajuste de escala automática para garantir que os valores fiquem visíveis no eixo Y
        if i in [2, 3]:
            max_y3_4 = max(max_y3_4, bottom.max())  # Atualiza o valor máximo para os gráficos 3 e 4

        ax.set_title(f'{titles[i]}', fontsize=14)
        ax.set_ylabel(y_axis[i], fontsize=14)
        ax.tick_params(axis='both', which='major', labelsize=14)

    # Ajustar a escala dos gráficos 3 e 4 para ficarem iguais
    axes[1, 0].set_ylim(0, max_y3_4 * 1.05)
    axes[1, 1].set_ylim(0, max_y3_4 * 1.05)

    # Adicionar uma legenda única compartilhada para todos os gráficos
    fig.legend(handles, labels, loc='upper center', fontsize=12, ncol=len(component_colors), bbox_to_anchor=(0.5, 1.00))

    # Ajustar o layout
    plt.tight_layout(rect=[0, 0, 1, 0.96])  # Ajuste o layout para não sobrepor o título

    # Salvar a imagem
    plt.savefig(output_image, format='png', dpi=300)
    plt.close()  # Fecha a figura para liberar memória



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
    parser.add_argument("--output_csv", type=str, default="output.csv", help="Output CSV file name")
    parser.add_argument("--output_image", type=str, default="scientific_boxplots.png", help="Output image file name")

    args = parser.parse_args()

    outputs = []
    for directory in args.directories:
        start_end_timestamps = get_timestamps_from_directory(directory)
        output_csv = f"{directory}/output.csv"  # Salva o CSV em cada diretório
        outputs.append(output_csv)
        get_combined_metrics_data(start_end_timestamps, output_csv)
    generate_stacked_barplots_per_component(outputs, args.output_image)
