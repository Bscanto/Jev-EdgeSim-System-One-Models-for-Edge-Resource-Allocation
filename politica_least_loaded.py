class PoliticaLeastLoaded:
    def __init__(self):
        self.decisoes = []
        self.chamadas_api = 0
        self.tempo_total_api = 0.0

    def selecionar_servidor(self, servico, servidores):
        """Seleciona o servidor com mais recursos livres (least-loaded)."""

        candidatos = []

        for servidor in servidores:
            cpu_livre = servidor.cpu - servidor.cpu_demand
            ram_livre = servidor.memory - servidor.memory_demand

            if (
                cpu_livre >= servico.cpu_demand
                and ram_livre >= servico.memory_demand
            ):
                candidatos.append({
                    "servidor": servidor,
                    "cpu_livre": cpu_livre,
                    "ram_livre": ram_livre
                })

        if not candidatos:
            print("Nenhum servidor possui recursos suficientes.")
            return None

        # Escolhe o servidor com maior CPU livre
        # Em caso de empate, desempata pela RAM livre
        escolhido = max(
            candidatos,
            key=lambda c: (c["cpu_livre"], c["ram_livre"])
        )["servidor"]

        self.decisoes.append({
            "servico": servico.id,
            "servidor": str(escolhido.id)
        })

        return escolhido