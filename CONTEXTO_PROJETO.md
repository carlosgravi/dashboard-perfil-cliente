# Contexto do Projeto: Dashboard Perfil de Cliente

## Visao Geral

Este projeto e um **dashboard de analise de perfil de clientes** para a rede de shoppings **Almeida Junior**. O dashboard e desenvolvido em **Streamlit** e hospedado no Streamlit Cloud.

**URL do Dashboard:** https://dashboard-perfil-cliente.streamlit.app
**Repositorio GitHub:** https://github.com/carlosgravi/dashboard-perfil-cliente

---

## Estrutura de Diretorios

```
C:\util\Docker_Airflow\
├── Estudo_Perfil_Cliente\           # Pasta principal do projeto
│   ├── analise_perfil_cliente.py    # Script de analise demografica
│   ├── gerar_rfv_por_periodo.py     # Script de geracao RFV por periodo
│   ├── gerar_top_consumidores_rfv.py # Script de top consumidores (exclui colaboradores)
│   ├── atualizar_dashboard.py       # Script de automacao completa
│   ├── atualizar_dashboard.bat      # Versao batch do script
│   ├── CONTEXTO_PROJETO.md          # Este documento (manter atualizado!)
│   ├── Resultados\                  # CSVs gerados pela analise
│   │   ├── indice_periodos.csv      # Indice de todos os periodos
│   │   ├── top_consumidores_rfv.csv # Top 150 consumidores por shopping
│   │   ├── Completo\                # Dados do periodo completo
│   │   │   └── RFV\                 # Dados RFV do periodo
│   │   ├── Por_Ano\                 # Dados por ano (2023, 2024, 2025, 2026)
│   │   ├── Por_Trimestre\           # Dados por trimestre
│   │   └── Por_Mes\                 # Dados por mes
│   │
│   └── deploy_streamlit\            # Codigo do dashboard (repo GitHub separado)
│       ├── .git\                    # Repositorio: carlosgravi/dashboard-perfil-cliente
│       ├── dashboard_perfil_cliente.py  # Dashboard principal
│       ├── Resultados\              # Copia dos dados para deploy
│       │   └── top_consumidores_rfv.csv # Deve ser igual ao da pasta pai
│       ├── requirements.txt
│       └── .streamlit\              # Configuracoes Streamlit
│
├── MySQL_Extrator\                  # Scripts de extracao do MySQL
│   ├── extrair_dados_mysql.py
│   └── query_base_cupons.sql        # Query SQL de extracao
│
├── clientes_vs_colaboradores.xlsx   # Lista de colaboradores por shopping
└── base_cupons_completa_v3.csv      # Base de dados principal
```

---

## Base de Dados

**Arquivo:** `base_cupons_completa_v3.csv`

Contem registros de cupons fiscais dos shoppings Almeida Junior com as colunas principais:
- `id` - ID do cupom
- `cliente_id` - ID do cliente
- `data_envio` - Data da transacao
- `valor` - Valor da compra
- `shopping_id` - ID do shopping (1-6)
- `loja_nome` - Nome da loja
- `segmento_loja` - Segmento da loja
- `genero` - Genero do cliente
- `data_nascimento` - Data de nascimento
- `status` - Status do cupom (filtrado por 'Validado')
- **Dados de Endereco:** `logradouro`, `numero`, `complemento`, `bairro`, `cidade_moradia`, `estado_moradia`, `cep`

**Shoppings (IDs):**
| ID | Nome |
|----|------|
| 1 | Continente |
| 2 | Balneario |
| 3 | Neumarkt |
| 4 | Norte |
| 5 | Garten |
| 6 | Nacoes |

---

## Fluxo de Atualizacao dos Dados

```
1. extrair_dados_mysql.py     -> Extrai dados do MySQL -> base_cupons_completa_v3.csv
2. analise_perfil_cliente.py  -> Analisa perfil demografico -> Resultados/*.csv
3. gerar_rfv_por_periodo.py   -> Gera dados RFV por periodo -> Resultados/{periodo}/RFV/*.csv
4. Copia para deploy_streamlit/Resultados/
5. Git push para GitHub
6. Streamlit Cloud atualiza automaticamente
```

**Script de automacao:** `python atualizar_dashboard.py [--skip-mysql] [--skip-git]`

---

## Implementacao Recente: Sistema de Quintis RFV

### O que foi implementado

Evoluimos a classificacao RFV de um sistema baseado apenas em **thresholds fixos de valor (R$)** para um sistema completo de **scoring por quintis** nas 3 dimensoes: Recencia (R), Frequencia (F) e Valor (V).

### Arquivos Modificados

1. **`gerar_rfv_por_periodo.py`** - Adicionadas funcoes:
   - `classificar_por_score()` - Mapeia soma R+F+V para perfil
   - `calcular_quintis_rfv()` - Calcula scores 1-5 por dimensao
   - `salvar_thresholds_quintis()` - Salva valores de corte
   - `gerar_metricas_perfil_quintis()` - Metricas agregadas por perfil
   - `gerar_metricas_shopping_quintis()` - Metricas por shopping

2. **`dashboard_perfil_cliente.py`** - Adicionados:
   - Toggle de metodo: "Por Valor (R$)" vs "Por Quintis (R+F+V)"
   - Toggle de escopo: "Global" vs "Por Shopping"
   - Nova aba "Scores R/F/V" com histogramas e radar chart
   - Carregamento dos novos arquivos de quintis
   - Exportacao de dados de quintis
   - Metodologia atualizada com documentacao completa

### Metodos de Classificacao

#### Metodo 1: Por Valor (R$) - Existente
Thresholds fixos baseados apenas no valor gasto:

| Perfil | Historico | Por Periodo |
|--------|-----------|-------------|
| VIP | >= R$ 5.000 | >= R$ 2.000 |
| Premium | R$ 2.500 - R$ 4.999 | R$ 1.000 - R$ 1.999 |
| Potencial | R$ 1.000 - R$ 2.499 | R$ 500 - R$ 999 |
| Pontual | < R$ 1.000 | < R$ 500 |

#### Metodo 2: Por Quintis (R+F+V) - Novo
Scoring dinamico baseado na distribuicao dos dados:

**Scores por dimensao (1-5):**
- **Recencia (R):** Score 5 = comprou recentemente, Score 1 = ha muito tempo
- **Frequencia (F):** Score 5 = muitas compras, Score 1 = poucas compras
- **Valor (V):** Score 5 = alto valor, Score 1 = baixo valor

**Classificacao por soma (3-15):**
| Score Total | Perfil |
|-------------|--------|
| 13-15 | VIP |
| 10-12 | Premium |
| 7-9 | Potencial |
| 3-6 | Pontual |

**Escopos:**
- **Global:** Quintis sobre todos os clientes (comparacao justa entre shoppings)
- **Por Shopping:** Quintis dentro de cada shopping (cada um tem seus "melhores")

### Top Consumidores por Shopping

**Script:** `gerar_top_consumidores_rfv.py`

Gera lista dos top N consumidores de cada shopping com classificacao RFV.

**Caracteristicas:**
- Exclui colaboradores dos shoppings (baseado em `clientes_vs_colaboradores.xlsx`)
- Usa dados de quintis para classificacao (escopo global ou por shopping)
- Inclui dados completos de contato e endereco

**Colunas do arquivo `top_consumidores_rfv.csv`:**
| Grupo | Colunas |
|-------|---------|
| Identificacao | Ranking, Shopping, Cliente_ID, Nome, CPF |
| Contato | Email, Celular |
| Endereco | Logradouro, Numero, Complemento, Bairro, Cidade, Estado, CEP |
| Metricas | Genero, Valor_Total, Frequencia_Compras, Recencia_Dias |
| Datas | Data_Primeira_Compra, Data_Ultima_Compra |
| Comportamento | Segmento_Principal, Valor_Segmento_Principal, Loja_Favorita, Valor_Loja_Favorita |
| RFV | Score_Recencia, Score_Frequencia, Score_Valor, Score_Total_RFV, Perfil_Cliente |

**Uso:**
```bash
python gerar_top_consumidores_rfv.py --top 150 --periodo Completo --escopo global
```

### Arquivos CSV Gerados (por periodo)

```
Resultados/{periodo}/RFV/
├── [METODO POR VALOR - existentes]
│   ├── metricas_perfil_historico.csv
│   ├── metricas_perfil_periodo.csv
│   ├── metricas_shopping_rfv.csv
│   ├── TOP10_SEGMENTOS_POR_PERFIL_SHOPPING.csv
│   ├── TOP10_LOJAS_POR_GENERO_SHOPPING_PERFIL.csv
│   └── resumo_rfv.csv
│
├── [METODO POR QUINTIS - novos]
│   ├── rfv_quintis_global.csv           # Clientes com scores (escopo global)
│   ├── rfv_quintis_por_shopping.csv     # Clientes com scores (escopo por shopping)
│   ├── metricas_perfil_quintis_global.csv
│   ├── metricas_perfil_quintis_shopping.csv
│   ├── metricas_shopping_quintis_global.csv
│   ├── metricas_shopping_quintis_shopping.csv
│   ├── quintile_thresholds_global.csv   # Valores de corte para auditoria
│   └── quintile_thresholds_shopping.csv
```

---

## Dashboard Streamlit

### Paginas Disponiveis

1. **Visao Geral** - Panorama consolidado de todos os shoppings
2. **Personas** - 14 perfis comportamentais de clientes
3. **Por Shopping** - Analise detalhada por shopping
4. **Perfil Demografico** - Analise por genero, faixa etaria
5. **High Spenders** - Top 10% de clientes por shopping
6. **Top Consumidores** - Top 150 consumidores por shopping com dados de contato e endereco
7. **Segmentos** - Analise por categoria de produto
8. **RFV** - Classificacao de clientes (com toggles de metodo/escopo)
9. **Comportamento** - Analise por periodo do dia e dia da semana
10. **Comparativo** - Comparacao entre shoppings
11. **Exportar Dados** - Download de CSVs e Excel
12. **Assistente** - Chat para duvidas e sugestoes
13. **Documentacao** - Documentacao completa do dashboard

### Autenticacao

O dashboard possui autenticacao simples com dois perfis:
- **admin** - Acesso completo
- **viewer** - Apenas visualizacao

Configurado em `.streamlit/secrets.toml` (no Streamlit Cloud)

---

## Estatisticas da Base Atual

- **Periodo:** 01/01/2022 a 30/01/2026
- **Transacoes:** ~1,651,043
- **Clientes:** ~254,000
- **Valor Total:** ~R$ 551 milhoes
- **Shoppings:** 6
- **Periodos processados:** 42 (completo + anos + trimestres + meses)
- **Top Consumidores:** 900 (150 por shopping, excluindo colaboradores)

---

## Comandos Uteis

```bash
# Atualizar tudo (MySQL + analise + RFV + deploy + git)
python atualizar_dashboard.py

# Pular extracao MySQL (usar dados existentes)
python atualizar_dashboard.py --skip-mysql

# Pular git push (apenas processar localmente)
python atualizar_dashboard.py --skip-mysql --skip-git

# Apenas gerar dados RFV
python gerar_rfv_por_periodo.py

# Apenas analise demografica
python analise_perfil_cliente.py

# Gerar lista top consumidores (150 por shopping, exclui colaboradores)
python gerar_top_consumidores_rfv.py --top 150

# Testar dashboard localmente
cd deploy_streamlit
streamlit run dashboard_perfil_cliente.py
```

---

## Commits Recentes (repositorio deploy_streamlit)

1. `0850a6f` - fix: corrigir API do Hasher para streamlit_authenticator v0.3+
2. `eec3d35` - docs: adicionar documento de contexto do projeto
3. `829aa39` - feat: adicionar campos de endereco na lista de top consumidores
4. `64064f5` - feat: adicionar pagina Top 150 Consumidores por shopping
5. `3caa1bb` - feat: adicionar sistema de classificacao RFV por quintis (dashboard)

---

## Sincronizacao Local vs Repositorio

**IMPORTANTE:** Manter sempre o dashboard local sincronizado com o repositorio GitHub.

### Estrutura de Repositorios

```
C:\util\Docker_Airflow\                    # Repositorio principal (grupoalmeidajunior)
└── Estudo_Perfil_Cliente\
    └── deploy_streamlit\                  # Repositorio separado (carlosgravi/dashboard-perfil-cliente)
        ├── .git\                          # Git proprio deste diretorio
        ├── dashboard_perfil_cliente.py
        └── Resultados\
```

### Checklist Apos Alteracoes

1. **Apos modificar `dashboard_perfil_cliente.py`:**
   ```bash
   cd Estudo_Perfil_Cliente/deploy_streamlit
   git add dashboard_perfil_cliente.py
   git commit -m "descricao da alteracao"
   git push origin main
   ```

2. **Apos atualizar dados (CSVs):**
   ```bash
   # Copiar arquivos atualizados
   cp Resultados/top_consumidores_rfv.csv deploy_streamlit/Resultados/

   # Commitar no deploy
   cd deploy_streamlit
   git add Resultados/top_consumidores_rfv.csv
   git commit -m "data: atualizar dados"
   git push origin main
   ```

3. **Apos qualquer alteracao:**
   - Atualizar este documento (CONTEXTO_PROJETO.md)
   - Registrar o commit na secao "Commits Recentes"

### Verificar Sincronizacao

```bash
cd Estudo_Perfil_Cliente/deploy_streamlit
git status                    # Deve mostrar "up to date with origin/main"
git log --oneline -3          # Ver ultimos commits
```

---

## Proximos Passos Sugeridos

1. **Validacao:** Verificar se o dashboard esta funcionando corretamente com os toggles
2. **Testes:** Comparar classificacoes entre metodos (mesmo cliente pode ter perfis diferentes)
3. **Documentacao:** Criar apresentacao explicando a diferenca entre os metodos para a equipe
4. **Melhorias possiveis:**
   - Adicionar comparativo lado-a-lado dos metodos
   - Adicionar alerta de clientes que mudaram de perfil
   - Adicionar analise de churn baseada em Recencia baixa

---

## Contato/Repositorios

- **Dashboard:** https://dashboard-perfil-cliente.streamlit.app
- **GitHub (deploy):** https://github.com/carlosgravi/dashboard-perfil-cliente
- **Diretorio local:** C:\util\Docker_Airflow\Estudo_Perfil_Cliente

---

*Documento atualizado em 30/01/2026 - Adicionados campos de endereco e secao de sincronizacao*
