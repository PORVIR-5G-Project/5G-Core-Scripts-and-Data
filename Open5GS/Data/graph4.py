import os
import pandas as pd
import matplotlib.pyplot as plt
import argparse

# Função para gerar gráficos a partir de arquivos CSV em uma pasta
def gerar_graficos(pasta):
    # Criar uma lista para armazenar os arquivos CSV
    arquivos_csv = [file for file in os.listdir(pasta) if file.endswith(".csv")]
    arquivos_csv.sort()
    plt.rcParams.update({
        'font.size': 10,          # Tamanho da fonte
        'axes.titlesize': 12,     # Tamanho do título do eixo
        'axes.labelsize': 12,     # Tamanho dos rótulos dos eixos
        'xtick.labelsize': 12,     # Tamanho dos rótulos do eixo x
        'ytick.labelsize': 12,     # Tamanho dos rótulos do eixo y
        'legend.fontsize': 8,     # Tamanho da fonte da legenda
        'figure.figsize': (10, 8),  # Tamanho da figura
        'lines.markersize': 5,    # Tamanho dos marcadores
        'grid.color': 'gray',      # Cor da grade
        'grid.alpha': 0.5,         # Transparência da grade
        'axes.grid': True,         # Ativar grade
    })

    titles = [
        'Scenario 1',
        'Scenario 2',
        'Scenario 3',
        'Scenario 4'
    ]

    # Criar uma figura com layout 2x2
    fig, axs = plt.subplots(2, 2, figsize=(10, 8))  # Tamanho ajustado para visualização

    for i, nome_arquivo in enumerate(arquivos_csv):
        if i >= 4:  # Limitar a 4 subplots (layout 2x2)
            break

        arquivo_path = os.path.join(pasta, nome_arquivo)

        data = pd.read_csv(arquivo_path)
        timestamp_base = data.iloc[0]['timestamp']

        data['Experiment Time (s)'] = (data['timestamp'] - timestamp_base) / 1_000_000_000
        data['Experiment Time (s)'] = data['Experiment Time (s)'].round()

        connections_per_second = data['Experiment Time (s)'].value_counts().sort_index()

        times = connections_per_second.index.tolist()
        num_rows = connections_per_second.values.tolist()

        # Plotar no subplot correspondente
        axs[i // 2, i % 2].plot(times, num_rows, linewidth=2)

        # Adicionar título e labels ao subplot
        axs[i // 2, i % 2].set_title(titles[i], fontsize=12)
        axs[i // 2, i % 2].grid(True)

    fig.text(0.5, 0.01, 'Experiment Time (s)', ha='center', fontsize=14)  # Eixo X geral ajustado
    fig.text(0.01, 0.5, 'Connection Rate', va='center', rotation='vertical', fontsize=14)  # Eixo Y geral ajustado

    # Ajustar layout para evitar sobreposição
    plt.tight_layout(rect=[0.03, 0.03, 1, 0.95])

    # Salvar o gráfico em um arquivo
    output_filename = os.path.join(pasta, 'grafico_conexoes_por_segundo.png')
    plt.savefig(output_filename, dpi=300, bbox_inches='tight')
    print(f"Gráfico salvo como: {output_filename}")

    # Fechar a figura
    plt.close()

# Definir o parser de argumentos
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Gerar gráficos a partir de arquivos CSV em uma pasta.")
    parser.add_argument('pasta', type=str, help='Caminho para a pasta que contém os arquivos CSV')

    # Parse dos argumentos da linha de comando
    args = parser.parse_args()

    # Chamar a função com os argumentos
    gerar_graficos(args.pasta)
