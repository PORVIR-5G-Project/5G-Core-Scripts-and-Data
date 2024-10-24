import pymongo
from bson import ObjectId
from bson import Int64

# Conexão com o servidor do MongoDB. Alterar a porta específica do serviço do MongoDB
client = pymongo.MongoClient("mongodb://localhost:63145/")

# Acessa a base de dados e seleciona a coleção
db = client["free5gc"]
collection = db["subscriptionData.provisionedData.smData"]

# Define uma lista de documentos a ser passada para a base de dados posteriormente
documentos = []

# Define o valor inicial para o imsi
valor_inicial = "208930000000000"

# Define a quantidade de UEs que queira cadastrar
qtd_UE = 5000

# Cria os documentos 
for num_UE in range(qtd_UE):

    documento = {
        "singleNssai": {
        "sd": "010203",
        "sst": 1
        },
        "dnnConfigurations": {
        "internet": {
            "pduSessionTypes": {
            "allowedSessionTypes": ["IPV4"],
            "defaultSessionType": "IPV4"
            },
            "sscModes": {
            "allowedSscModes": ["SSC_MODE_2", "SSC_MODE_3"],
            "defaultSscMode": "SSC_MODE_1"
            },
            "5gQosProfile": {
            "5qi": 9,
            "arp": {
                "priorityLevel": 8,
                "preemptCap": "",
                "preemptVuln": ""
            },
            "priorityLevel": 8
            },
            "sessionAmbr": {
            "uplink": "200 Mbps",
            "downlink": "100 Mbps"
            }
        }
        },
        "ueId": "imsi-"+str(int(valor_inicial) + num_UE),
        "servingPlmnId": "20893"
    }
    documentos.append(documento)

# Insere todos os documentos na coleção
resultado = collection.insert_many(documentos)
