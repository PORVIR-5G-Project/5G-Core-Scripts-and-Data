import pymongo
from bson import ObjectId
from bson import Int64

# Conexão com o servidor do MongoDB. Alterar a porta específica do serviço do MongoDB
client = pymongo.MongoClient("mongodb://localhost:63145/")

# Acessa a base de dados e seleciona a coleção
db = client["free5gc"]
collection = db["subscriptionData.provisionedData.amData"]

# Define uma lista de documentos a ser passada para a base de dados posteriormente
documentos = []

# Define o valor inicial para o imsi
valor_inicial = "208930000000000"

# Define a quantidade de UEs que queira cadastrar
qtd_UE = 5000

# Cria os documentos 
for num_UE in range(qtd_UE):
    documento = {
        "ueId": "imsi-"+str(int(valor_inicial) + num_UE),
        "servingPlmnId": "20893",
        "tenantId": "9e16cabd-eb53-46f0-99d4-0f58396630ef",
        "gpsis": ["msisdn-"],
        "subscribedUeAmbr": {
        "uplink": "1 Gbps",
        "downlink": "2 Gbps"
        },
        "nssai": {
        "defaultSingleNssais": [
            {
            "sst": 1,
            "sd": "010203"
            },
        ]
        }
}
    documentos.append(documento)

# Insere todos os documentos na coleção
resultado = collection.insert_many(documentos)
