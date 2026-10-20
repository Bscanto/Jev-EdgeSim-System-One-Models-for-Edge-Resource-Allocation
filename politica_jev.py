import time

from langchain_typesafe import TypeSafeClassifier, Choice

class PoliticaJev:
    def __init__(self):
        self.modelo = TypeSafeClassifier()
        self.decisoes = []
        self.chamadas_api = 0
        self.tempo_total_api = 0.0

    def selecionar_servidor(self, servico, servidores):
        """Seleciona um servidor viável usando Jev."""
        
        # Filtrar servidores com CPU e RAM suficientes
        candidatos = []

        for servidor in servidores:
            cpu_livre = servidor.cpu - servidor.cpu_demand
            ram_livre = servidor.memory - servidor.memory_demand

            if (
                cpu_livre >= servico.cpu_demand 
                and ram_livre >= servico.memory_demand
            ):
                candidatos.append({
                    "id": str(servidor.id),
                    "cpu_livre": cpu_livre,
                    "ram_livre": ram_livre
                })

        if not candidatos:
            print("Nenhum servidor possui recursos suficientes.")
            return None

        # Se existe apenas um servidor, não precisa consultar o Jev
        if len(candidatos) == 1:
            escolhido = candidatos[0]["id"]
        else:
            opcoes = {
                item["id"]: (
                    f"Servidor com CPU livre "
                    f"{item['cpu_livre']} e RAM livre "
                    f"{item['ram_livre']}."
                )
                for item in candidatos
            }

            inicio = time.perf_counter()
            
            resultado = self.modelo.invoke({
                "state": {
                    "demanda_servico": {
                        "cpu": servico.cpu_demand,
                        "ram": servico.memory_demand
                    },
                    "servidores": candidatos
                },
                "questions": {
                    "servidor": Choice(
                        instructions=(
                            "Selecione o servidor mais adequado "
                            "para alocar o serviço, considerando "
                            "o equilíbrio do uso de CPU e memória."
                        ),
                        criteria = opcoes
                    )
                }
            })
            tempo = time.perf_counter() - inicio
            
            self.chamadas_api += 1
            self.tempo_total_api += tempo

            resposta = resultado.choices["servidor"]
            escolhido = resposta.choice

            print(f"\n===== DECISÃO JEV | SERVIÇO {servico.id} =====")
            print(f"Servidor escolhido: {escolhido}")
            print(f"Confiança: {resposta.confidence:.2%}")
            print(f"Tempo de API: {tempo * 1000:.2f} ms")
            print(f"Probabilidades: {resposta.probabilities}")
            escolhido = resultado.choices["servidor"].choice

       # Recuperar o servidor selecionado
        servidor_escolhido = next(
            (s for s in servidores if str(s.id) == escolhido),
            None
        )

        if servidor_escolhido is None:
            raise ValueError("Jev retornou um servidor inválido.")

        self.decisoes.append({
            "servico": servico.id,
            "servidor": escolhido
        })

        return servidor_escolhido

