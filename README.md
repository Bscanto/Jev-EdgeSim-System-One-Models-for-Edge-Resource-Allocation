# JEV + EdgeSimPy — Alocação de recursos na borda

Projeto experimental que integra o modelo de inteligência artificial JEV (System One Model), por meio de `TypeSafeClassifier`, ao simulador EdgeSimPy para investigar a alocação de serviços em servidores de borda. Inclui uma política Least Loaded como alternativa para comparação.

## Estrutura

| Arquivo ou diretório | Responsabilidade |
| --- | --- |
| `sample_dataset.json` | Cenário original do EdgeSimPy, com serviços inicialmente alocados. |
| `preparar_dataset.py` | Libera os serviços e ajusta a contabilidade de CPU e memória dos servidores. |
| `dataset_jev.json` | Cenário preparado para executar o experimento. |
| `politica_jev.py` | Escolha de servidores usando JEV e registro de decisões e métricas da API. |
| `politica_least_loaded.py` | Escolha local pelo maior volume de recursos livres. |
| `simulacao.py` | Configuração do simulador, provisionamento e apresentação dos resultados. |
| `logs/` | Registros da simulação em formato `.msgpack`. |

Os datasets descrevem componentes por meio de `attributes` (propriedades, capacidades e demandas) e `relationships` (referências entre serviços, servidores e demais componentes).

## Fluxo de funcionamento

```text
sample_dataset.json
        ↓ preparar_dataset.py
dataset_jev.json
        ↓ simulacao.py
Serviço pendente → política selecionada → servidor escolhido
        ↓ EdgeSimPy
Provisionamento → resultados e métricas
```

1. A preparação remove a associação dos serviços aos servidores, desconta os recursos correspondentes e limpa as referências reversas. Outros consumos existentes são preservados. O resultado sobrescreve `dataset_jev.json`, mantendo o arquivo original.
2. A simulação carrega o cenário preparado e identifica os serviços pendentes.
3. A cada passo, percorre os serviços que ainda não possuem servidor e não estão sendo provisionados.
4. A política filtra os servidores com CPU e memória livres suficientes e escolhe um candidato.
5. O script solicita o provisionamento com `servico.provision(target_server=servidor)`.
6. A execução termina quando todos os serviços possuem servidor ou quando alcança 100 passos. Cada passo representa 1 segundo de tempo simulado.

Se não houver servidor viável, a política retorna `None`. O serviço pode ser reconsiderado nos próximos passos e ainda estar pendente quando o limite for atingido.

## Políticas disponíveis

### JEV — padrão

A classe `PoliticaJev` calcula os recursos livres de cada servidor:

```python
cpu_livre = servidor.cpu - servidor.cpu_demand
ram_livre = servidor.memory - servidor.memory_demand
```

Com apenas um candidato viável, a escolha é direta. Com vários candidatos, envia suas disponibilidades e a demanda do serviço ao `TypeSafeClassifier`, pedindo uma escolha que considere o equilíbrio de CPU e memória.

A política imprime o servidor escolhido, a confiança, as probabilidades e a duração da consulta. Não há treinamento de modelo no repositório.

### Least Loaded

A classe `PoliticaLeastLoaded` aplica o mesmo filtro de viabilidade e escolhe o servidor com **maior CPU livre**. Em caso de empate, escolhe o de **maior memória livre**. Persistindo o empate, prevalece o primeiro candidato na ordem recebida.

Essa política não faz chamadas à API. O critério usa recursos livres absolutos, sem normalizar pela capacidade total dos servidores.

## Preparação do ambiente

Utilize um ambiente Python com as dependências correspondentes aos módulos importados pelos scripts:

| Módulo | Uso |
| --- | --- |
| `edge_sim_py` | Simulador e componentes da infraestrutura. |
| `dotenv` (pacote `python-dotenv`) | Carregamento de variáveis de ambiente a partir de `.env`. |
| `langchain_typesafe` | `TypeSafeClassifier` e `Choice`, utilizados pela política JEV. |

O repositório não possui um manifesto de dependências com versões fixadas. Instale as dependências conforme a configuração das bibliotecas utilizadas no seu ambiente.

Para usar JEV, configure as credenciais exigidas pela sua instalação de `langchain_typesafe` no ambiente ou em um arquivo `.env`. O script chama `load_dotenv()` antes de instanciar a política; os nomes das variáveis e a configuração do provedor não estão definidos nos scripts deste projeto. Não versione credenciais.

## Execução

Execute os comandos na raiz do projeto, pois os caminhos dos datasets são relativos ao diretório de execução.

### 1. Preparar os dados

Garanta que `sample_dataset.json` contém um cenário válido do EdgeSimPy e execute:

```bash
python preparar_dataset.py
```

O script gera `dataset_jev.json` com todos os serviços sem servidor associado. Ele interrompe a preparação se encontrar um servidor referenciado inexistente ou se a liberação resultar em consumo negativo de CPU ou memória.

### 2. Escolher a política

A seleção é feita diretamente em `simulacao.py`; não há argumento de linha de comando para alterná-la.

Para JEV, mantenha o import e a instanciação ativos:

```python
from politica_jev import PoliticaJev

politica = PoliticaJev()
```

Para Least Loaded, comente ou remova tanto o import quanto a instanciação de JEV e ative:

```python
from politica_least_loaded import PoliticaLeastLoaded

politica = PoliticaLeastLoaded()
```

Deixe apenas uma instanciação ativa. Remover o import de JEV permite executar Least Loaded sem importar `langchain_typesafe`; as dependências `edge_sim_py` e `dotenv` continuam necessárias.

### 3. Executar a simulação

```bash
python simulacao.py
```

Para comparar as políticas, execute cada uma separadamente usando o mesmo dataset preparado e guarde os resultados de cada execução.

## Resultados e métricas

O terminal apresenta:

- Quantidade inicial de serviços aguardando alocação.
- Solicitações de provisionamento e associação final entre serviços e servidores.
- Total de decisões registradas.
- Total de chamadas à API.
- Tempo médio das consultas em milissegundos, quando existem chamadas.

A lista `decisoes` mantém os identificadores do serviço e do servidor escolhido. Uma decisão registrada representa uma seleção, não uma confirmação de provisionamento concluído. Confiança e probabilidades de JEV são impressas, mas não são armazenadas nessa lista.

O tempo de API é medido em tempo real com `time.perf_counter()`, separadamente do tempo simulado. Para Least Loaded, os contadores de chamadas e tempo de API permanecem em zero. O cabeçalho de saída ainda aparece como `MÉTRICAS JEV`, independentemente da política selecionada.

## Limitações e diagnóstico

- As políticas consideram CPU e memória; latência, localização dos usuários, disco, energia e largura de banda não participam da escolha.
- A instrução de balanceamento enviada a JEV não define uma função matemática de otimização nem garante uma distribuição ótima.
- As chamadas ao classificador não possuem tratamento de exceções ou tentativas adicionais no código da política.
- Atingir 100 passos não garante que todos os serviços tenham sido alocados; confira a associação final apresentada no terminal.
- Se aparecer `O dataset não possui serviços pendentes`, prepare novamente o cenário e confirme que a simulação lê o arquivo esperado.
- A simulação lê `dataset_jev.json`, embora sua mensagem de arquivo ausente mencione `sample_dataset.json`. Execute a preparação para gerar o arquivo efetivamente utilizado.
