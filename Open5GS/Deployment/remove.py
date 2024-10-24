import os
import subprocess
import time

def deletar_manifesto(caminho_do_arquivo):
    comando = f'kubectl delete -f {caminho_do_arquivo}'
    processo = subprocess.Popen(comando, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    saida, erro = processo.communicate()
    
    if processo.returncode == 0:
        print(f'Sucesso! O comando foi executado:\n{saida.decode("utf-8")}')
    else:
        print(f'Erro ao executar o comando:\n{erro.decode("utf-8")}')
    
def deletar_manifestos_na_pasta(pasta):
    for arquivo in os.listdir(pasta):
        if arquivo.endswith(".yaml"):
            caminho_completo = os.path.join(pasta, arquivo)
            deletar_manifesto(caminho_completo)
    time.sleep(5)

pastas = ['mongodb','webui', 'nrf', 'ausf', 'udr', 'udm', 'pcf', 'bsf', 'nssf', 'smf', 'upf', 'amf']

for pasta in pastas:
    deletar_manifestos_na_pasta(pasta)
