
from dotenv import load_dotenv
from langchain_typesafe import (
    TypeSafeClassifier,
    Noul,
    Choice
)

# 1. Carregar a chave da API
load_dotenv()

# 2. Inicializar o Jev
jev = TypeSafeClassifier()

print("Jev inicializado!")
print("Analisando tráfego de rede...\n")

# 3. Tráfego fictício para o primeiro teste
trafego = {
    "protocolo": "TCP",
    "servico": "HTTP",
    "duracao": 0,
    "bytes_origem": 480,
    "bytes_destino": 0,
    "conexoes_recentes": 150,
    "erros_conexao": 120
}

# 4. Realizar classificação
try:
    resultado = jev.invoke({
        "state": trafego,
        "questions": {
            "intrusao": Noul(
                instructions=(
                    "Este fluxo de rede apresenta "
                    "características de uma possível "
                    "intrusão ou ataque cibernético?"
                )
            ),
            "categoria": Choice(
                instructions=(
                    "Qual categoria melhor descreve "
                    "esse tráfego de rede?"
                ),
                criteria={
                    "normal": "Tráfego legítimo.",
                    "dos": "Negação de serviço.",
                    "probe": "Varredura ou reconhecimento.",
                    "r2l": "Acesso remoto não autorizado.",
                    "u2r": "Escalada de privilégios."
                }
            )
        }
    })

    # 5. Exibir os resultados
    probabilidade = resultado.nouls["intrusao"].noul
    categoria = resultado.choices["categoria"].choice

    print("===== RESULTADO JEV =====")
    print(f"Probabilidade de ataque: {probabilidade:.2%}")
    print(f"Categoria prevista: {categoria}")

    if probabilidade >= 0.7:
        print("ALERTA: possível intrusão!")
    else:
        print("Sem alerta de intrusão.")

except Exception as erro:
    print(f"Erro durante a classificação: {erro}")
