
import json
from copy import deepcopy
from pathlib import Path
from collections import defaultdict

ORIGEM = Path("sample_dataset.json")
DESTINO = Path("dataset_jev.json")

with ORIGEM.open("r", encoding="utf-8") as arquivo:
    dados = json.load(arquivo)

dados = deepcopy(dados)

servidores = {
    item["attributes"]["id"]: item
    for item in dados["EdgeServer"]
}

recursos_liberados = defaultdict(
    lambda: {"cpu": 0, "memory": 0}
)

print("===== PREPARANDO DATASET JEV =====")

# Remover as alocações iniciais dos serviços
for item in dados["Service"]:
    atributos = item["attributes"]
    relacionamentos = item["relationships"]

    servico_id = atributos["id"]
    servidor_atual = relacionamentos.get("server")

    if servidor_atual is None:
        print(f"Serviço {servico_id}: já está livre")
        continue

    servidor_id = servidor_atual["id"]

    if servidor_id not in servidores:
        raise ValueError(
            f"Servidor {servidor_id} não encontrado."
        )

    cpu = atributos["cpu_demand"]
    memoria = atributos["memory_demand"]

    recursos_liberados[servidor_id]["cpu"] += cpu
    recursos_liberados[servidor_id]["memory"] += memoria

    # Serviço deixa de ter servidor
    relacionamentos["server"] = None

    print(
        f"Serviço {servico_id}: "
        f"liberado do servidor {servidor_id}"
    )

# Atualizar os recursos ocupados nos servidores
for servidor_id, recursos in recursos_liberados.items():
    servidor = servidores[servidor_id]
    atributos = servidor["attributes"]

    nova_cpu = (
        atributos["cpu_demand"] - recursos["cpu"]
    )
    nova_memoria = (
        atributos["memory_demand"] - recursos["memory"]
    )

    if nova_cpu < 0 or nova_memoria < 0:
        raise ValueError(
            f"O servidor {servidor_id} apresenta "
            "contabilidade inconsistente."
        )

    atributos["cpu_demand"] = nova_cpu
    atributos["memory_demand"] = nova_memoria

# Limpar referências reversas dos serviços
ids_servicos = {
    item["attributes"]["id"]
    for item in dados["Service"]
}

for servidor in dados["EdgeServer"]:
    relacionamentos = servidor["relationships"]

    relacionamentos["services"] = [
        referencia
        for referencia in relacionamentos.get("services", [])
        if referencia["id"] not in ids_servicos
    ]

# Validar que todos os serviços estão livres
assert all(
    item["relationships"]["server"] is None
    for item in dados["Service"]
)

# Salvar dataset experimental
with DESTINO.open("w", encoding="utf-8") as arquivo:
    json.dump(
        dados,
        arquivo,
        indent=4,
        ensure_ascii=False
    )

print("\n===== DATASET PREPARADO =====")
print(f"Arquivo: {DESTINO}")
print(f"Serviços livres: {len(dados['Service'])}")

print("\n===== RECURSOS RESTANTES =====")

for servidor_id, servidor in servidores.items():
    atributos = servidor["attributes"]

    print(
        f"Servidor {servidor_id}: "
        f"CPU {atributos['cpu_demand']}/{atributos['cpu']} | "
        f"RAM {atributos['memory_demand']}/{atributos['memory']}"
    )
