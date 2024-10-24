import os
import subprocess
import time

def aplicar_manifesto(caminho_do_arquivo):
    comando = f'kubectl delete -f {caminho_do_arquivo}'
    processo = subprocess.Popen(comando, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    saida, erro = processo.communicate()
    
    if processo.returncode == 0:
        print(f'Sucesso! O comando foi executado:\n{saida.decode("utf-8")}')
    else:
        print(f'Erro ao executar o comando:\n{erro.decode("utf-8")}')
    
def aplicar_manifestos_na_pasta(pasta):
    for arquivo in os.listdir(pasta):
        if arquivo.endswith(".yaml"):
            caminho_completo = os.path.join(pasta, arquivo)
            aplicar_manifesto(caminho_completo)
    time.sleep(5)

pastas = ['upf', 'mongo', 'nrf', 'amf', 'ausf', 'nssf', 'pcf', 'smf', 'udm', 'udr', 'webui']

for pasta in pastas:
    aplicar_manifestos_na_pasta("Deployment/"+pasta)