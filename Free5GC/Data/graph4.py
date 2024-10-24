import os
import pandas as pd
import matplotlib.pyplot as plt

folder = os.getcwd()

for file in os.listdir(folder):
    if file.endswith(".csv"):
        nome_arquivo = os.path.join(folder, file)

        data = pd.read_csv(nome_arquivo)
        timestamp_base = data.iloc[0]['timestamp']

        data['Experiment Time (s)'] = (data['timestamp'] - timestamp_base) / 1000000000
        data['Experiment Time (s)'] = data['Experiment Time (s)'].round()

        connections_per_second = data['Experiment Time (s)'].value_counts().sort_index()
        
        times = connections_per_second.index.tolist()
        num_rows = connections_per_second.values.tolist()

        plt.figure(figsize=(10, 6))

        plt.plot(times, num_rows, linewidth=2)

        # Criar o título baseado no nome do arquivo
        if "div" in nome_arquivo:
            title = f'Parallel Connection Test:\nStarting at {nome_arquivo.split("_")[4]}ms, Dividing by {nome_arquivo.split("_")[5]} Every {nome_arquivo.split("_")[6]} Connections'
            novo_nome_arquivo = f'graph_num_rows_per_second_div_{nome_arquivo.split("_")[4]}_{nome_arquivo.split("_")[5]}_{nome_arquivo.split("_")[6]}.png'
        elif "dec" in nome_arquivo:
            title = f'Parallel Connection Test:\nStarting at {nome_arquivo.split("_")[4]}ms, Decreased by {nome_arquivo.split("_")[5]} Every {nome_arquivo.split("_")[6]} Connections'
            novo_nome_arquivo = f'graph_num_rows_per_second_dec_{nome_arquivo.split("_")[4]}_{nome_arquivo.split("_")[5]}_{nome_arquivo.split("_")[6]}.png'
        else:
            title = f'Parallel Connection Test:\nInterval of {nome_arquivo.split("_")[3]}ms'
            novo_nome_arquivo = f'graph_num_rows_per_second_{nome_arquivo.split("_")[1]}_{nome_arquivo.split("_")[3]}.png'

        # Adicionar título e labels
        plt.title(title, fontsize=14)
        plt.xlabel('Experiment Time (s)', fontsize=12)
        plt.ylabel('Connection Rate', fontsize=12)
        plt.grid(True)
        plt.tight_layout()
        
        # Salvar o gráfico com o nome adequado
        plt.savefig(novo_nome_arquivo, dpi=300, bbox_inches='tight')
        plt.close()
