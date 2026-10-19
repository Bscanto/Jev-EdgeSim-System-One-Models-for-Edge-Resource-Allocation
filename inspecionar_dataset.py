
import json
from pathlib import Path

arquivo = Path("sample_dataset.json")

with arquivo.open(encoding="utf-8") as f:
    dados = json.load(f)

print("===== ESTRUTURA DO DATASET =====")

if isinstance(dados, dict):
    print("Chaves principais:", list(dados.keys()))
else:
    print("Tipo da estrutura:", type(dados).__name__)

def inspecionar(objeto, caminho="raiz", nivel=0):
    if nivel > 3:
        return

    if isinstance(objeto, dict):
        for chave, valor in objeto.items():
            novo_caminho = f"{caminho}.{chave}"

            if isinstance(valor, list):
                print(
                    f"{novo_caminho}: lista com "
                    f"{len(valor)} elementos"
                )

                if valor:
                    inspecionar(
                        valor[0],
                        novo_caminho + "[0]",
                        nivel + 1
                    )

            elif isinstance(valor, dict):
                print(f"{novo_caminho}: objeto")
                inspecionar(valor, novo_caminho, nivel + 1)

            else:
                print(f"{novo_caminho}: {valor}")

inspecionar(dados)
