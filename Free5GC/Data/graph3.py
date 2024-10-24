import os
import pandas as pd
import matplotlib.pyplot as plt
import argparse

# Função que realiza a leitura, concatenação e plotagem dos CSVs
def gerar_scatter_plot(pasta, column_names):
    # Configurações manuais do estilo
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

    colors = ['green', 'orange', 'red']
    titles = [
        'Scenario 1',
        'Scenario 2',
        'Scenario 3',
        'Scenario 4'
    ]
    arquivos_csv = [arquivo for arquivo in os.listdir(pasta) if arquivo.endswith(".csv")]
    arquivos_csv.sort()
    
    # Criar uma figura com layout 2x2
    fig, axs = plt.subplots(2, 2, figsize=(10, 8))  # Tamanho ajustado para publicação
    axs = axs.flatten()  # Achatar o array para facilitar a iteração

    for i, arquivo in enumerate(arquivos_csv):
        if i >= 4:  # Limitar a 4 subplots (layout 2x2)
            break

        base_filename = os.path.join(pasta, arquivo)
        print(f"Lendo o arquivo: {arquivo}")  # Imprime o nome do arquivo lido

        # Ler o CSV
        dados = pd.read_csv(base_filename)

        # Ordenar os dados pelo timestamp
        dados = dados.sort_values(by='timestamp')

        # Pegar o primeiro timestamp para normalizar
        timestamp_base = dados['timestamp'].iloc[0]

        # Plotar para cada coluna em column_names no subplot correspondente
        for idx, column in enumerate(column_names):
            # Normalizar os timestamps para segundos a partir do primeiro timestamp
            timestamp = (dados['timestamp'] - timestamp_base) / 1e9  
            values = dados[column]
            
            cor = colors[idx % len(colors)]  # Alternar entre as cores
            axs[i].scatter(timestamp, values, label=column, color=cor, s=5, alpha=0.7)

        # Adicionar título e labels ao subplot
        axs[i].set_title(titles[i], fontsize=12)
        
        axs[i].grid(True)  # Manter a grade para legibilidade

    # Adicionar uma legenda única para todos os subplots
    handles, labels = axs[0].get_legend_handles_labels()
    fig.legend(handles, labels, loc='upper center', fontsize=12, ncol=3, bbox_to_anchor=(0.5, 1.05))

    # Adicionar eixo X e Y gerais
    fig.text(0.5, 0.01, 'Experiment Time (s)', ha='center', fontsize=14)  # Eixo X geral ajustado
    fig.text(0.01, 0.5, 'Time to Connection (ms)', va='center', rotation='vertical', fontsize=14)  # Eixo Y geral ajustado

    # Ajustar layout para evitar sobreposição
    plt.tight_layout(rect=[0.03, 0.03, 1, 0.95])

    # Salvar a figura em alta resolução adequada para artigos NOMS
    output_filename = 'scatter_plots_NOMS.png'
    plt.savefig(output_filename, dpi=300, bbox_inches='tight')
    print(f"Gráfico salvo como: {output_filename}")
    plt.close()


# Definir o parser de argumentos
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Gerar scatter plot a partir de arquivos CSV em uma pasta.")
    parser.add_argument('pasta', type=str, help='Caminho para a pasta que contém os arquivos CSV')

    # Parse dos argumentos da linha de comando
    args = parser.parse_args()

    # Chamar a função com os argumentos
    gerar_scatter_plot(args.pasta, column_names=['MM5G_REGISTERED_INITIATED', 'MM5G_REGISTERED', 'DataPlaneReady'])
