
from pathlib import Path
from dotenv import load_dotenv
from edge_sim_py import Simulator, Service, EdgeServer

from politica_jev import PoliticaJev



load_dotenv()

politica = PoliticaJev()

dataset = Path("dataset_jev.json")

# Política executada pelo EdgeSimPy
def algoritmo_jev(parameters):
    """Política executada a cada passo do EdgeSimPy."""

    for servico in Service.all():
        if servico.server is not None or servico.being_provisioned:
            continue

        # Evita repetir pedidos de provisionamento
        if not servico.being_provisioned:
            servidor = politica.selecionar_servidor(
                servico,
                EdgeServer.all()
            )

            if servidor is not None:
                servico.provision(target_server=servidor)
                print(
                    f"Serviço {servico.id} -> "
                    f"Servidor {servidor.id}"
                )


if not dataset.exists():
    raise FileNotFoundError(
        "Coloque um dataset do EdgeSimPy em "
        "sample_dataset.json antes de executar."
    )

simulador = Simulator(
    tick_duration=1,
    tick_unit="seconds",
    resource_management_algorithm=algoritmo_jev,
    stopping_criterion=lambda model: (
        all(s.server is not None for s in Service.all())
        or model.schedule.steps >= 100
    )
)

simulador.initialize(input_file=str(dataset))
pendentes = [
    servico for servico in Service.all()
    if servico.server is None
]

print(f"\nServiços aguardando alocação: {len(pendentes)}")

if not pendentes:
    raise RuntimeError(
        "O dataset não possui serviços pendentes."
    )

"""  
print("\n===== ESTADO INICIAL =====")

for servico in Service.all():
    servidor = servico.server.id if servico.server else "Não alocado"

    print(
        f"Serviço {servico.id} | "
        f"Servidor: {servidor} | "
        f"CPU: {servico.cpu_demand} | "
        f"RAM: {servico.memory_demand}"
    )

print("\n===== SERVIDORES =====")

for servidor in EdgeServer.all():
    print(
        f"Servidor {servidor.id} | "
        f"CPU: {servidor.cpu_demand}/{servidor.cpu} | "
        f"RAM: {servidor.memory_demand}/{servidor.memory}"
    )
"""
    
    
# Executar simulação
simulador.run_model()

# Mostrar resultados
print("\n===== RESULTADOS =====")

for servico in Service.all():
    print(
        f"Serviço {servico.id} -> "
        f"Servidor {servico.server.id if servico.server else 'Nenhum'}"
    )

print(f"Decisões realizadas: {len(politica.decisoes)}")

print("\n===== MÉTRICAS JEV =====")
print(f"Decisões registradas: {len(politica.decisoes)}")
print(f"Chamadas reais à API: {politica.chamadas_api}")

if politica.chamadas_api > 0:
    media = (
        politica.tempo_total_api
        / politica.chamadas_api
    ) * 1000

    print(f"Tempo médio da API: {media:.2f} ms")