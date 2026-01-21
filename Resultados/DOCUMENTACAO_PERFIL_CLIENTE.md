# Documentação Técnica - Estudo de Perfil de Cliente por Shopping

## 1. Objetivo

Analisar o perfil demográfico e comportamental dos clientes de cada shopping da rede Almeida Junior, identificando padrões de consumo, segmentação por gênero e faixa etária, e caracterização dos High Spenders.

---

## 2. Fonte de Dados

| Item | Descrição |
|------|-----------|
| **Arquivo** | base_cupons_completa_v3.csv |
| **Período** | 11/12/2022 a 19/01/2026 |
| **Filtro** | status = 'Validado' |
| **Total Transações** | 1.643.751 |
| **Total Clientes** | 253.946 |

---

## 3. Metodologia

### 3.1 Tratamento de Dados

#### Idade
- Calculada com base na data de nascimento
- Idades inválidas (< 16 ou > 100 anos) desconsideradas
- Fórmula: `(data_referência - data_nascimento) / 365.25`

#### Gênero
- Padronização: Masculino, Feminino, Outro, Não Informado
- Valores nulos classificados como "Não Informado"

#### Faixas Etárias
| Faixa | Idade | Geração |
|-------|-------|---------|
| 16-24 | 16 a 24 anos | Gen Z |
| 25-39 | 25 a 39 anos | Millennials |
| 40-54 | 40 a 54 anos | Gen X |
| 55-69 | 55 a 69 anos | Boomers |
| 70+ | 70 anos ou mais | Silent |

### 3.2 Métricas Calculadas

| Métrica | Descrição | Fórmula |
|---------|-----------|---------|
| **Valor Total** | Soma de todas as compras do cliente | `SUM(valor)` |
| **Ticket Médio** | Valor médio por transação | `valor_total / qtd_compras` |
| **Frequência** | Quantidade de compras | `COUNT(transações)` |
| **Tempo como Cliente** | Dias entre primeira e última compra | `última_compra - primeira_compra` |

### 3.3 High Spenders

- **Definição:** Top 10% dos clientes em valor total de compras
- **Cálculo:** Percentil 90 do valor total por shopping
- **Threshold:** Calculado individualmente para cada shopping

---

## 4. Resultados por Shopping

### 4.1 Visão Geral

| Shopping | Sigla | Clientes | Valor Total | Ticket Médio | High Spenders | Threshold HS |
|----------|-------|----------|-------------|--------------|---------------|--------------|
| Balneário Shopping | BS | 69.722 | R$ 181.161.894 | R$ 2.598 | 6.973 | R$ 5.751 |
| Garten Shopping | GS | 49.963 | R$ 98.132.953 | R$ 1.964 | 4.997 | R$ 4.247 |
| Neumarkt Shopping | NK | 42.725 | R$ 97.548.332 | R$ 2.283 | 4.273 | R$ 5.065 |
| Continente Shopping | CS | 53.052 | R$ 94.699.585 | R$ 1.785 | 5.306 | R$ 3.864 |
| Norte Shopping | NR | 30.636 | R$ 43.005.957 | R$ 1.403 | 3.064 | R$ 3.013 |
| Nações Shopping | NS | 25.012 | R$ 35.959.742 | R$ 1.437 | 2.502 | R$ 3.052 |
| **TOTAL** | - | **271.110** | **R$ 550.508.465** | **R$ 2.030** | **27.115** | - |

### 4.2 Participação por Shopping

| Shopping | % Clientes | % Valor |
|----------|------------|---------|
| BS | 25,7% | 32,9% |
| CS | 19,6% | 17,2% |
| GS | 18,4% | 17,8% |
| NK | 15,8% | 17,7% |
| NR | 11,3% | 7,8% |
| NS | 9,2% | 6,5% |

---

## 5. Perfil Demográfico

### 5.1 Distribuição por Gênero (Consolidado)

| Gênero | % Típico | Observação |
|--------|----------|------------|
| Feminino | 55-65% | Maioria em todos os shoppings |
| Masculino | 25-35% | Segunda maior participação |
| Não Informado | 5-15% | Dados não preenchidos |

### 5.2 Distribuição por Faixa Etária (Consolidado)

| Faixa Etária | % Típico | Perfil de Consumo |
|--------------|----------|-------------------|
| 25-39 (Millennials) | 35-45% | Maior volume e frequência |
| 40-54 (Gen X) | 25-30% | Alto ticket médio |
| 16-24 (Gen Z) | 10-15% | Alta frequência, baixo ticket |
| 55-69 (Boomers) | 8-12% | Ticket médio elevado |
| 70+ (Silent) | 2-4% | Baixa frequência |

---

## 6. Análise Comportamental

### 6.1 Período do Dia

| Período | Horário | % Transações Típico |
|---------|---------|---------------------|
| Manhã | 6h - 12h | 25-30% |
| Tarde | 12h - 18h | 45-50% |
| Noite | 18h - 22h | 25-30% |

### 6.2 Dia da Semana

| Dia | % Transações Típico |
|-----|---------------------|
| Sábado | 18-22% (pico) |
| Sexta | 14-16% |
| Domingo | 12-15% |
| Segunda a Quinta | 10-13% cada |

---

## 7. High Spenders - Características

### 7.1 Perfil Típico

| Característica | High Spenders | Demais Clientes |
|----------------|---------------|-----------------|
| % do Total de Clientes | 10% | 90% |
| % do Valor Total | 35-45% | 55-65% |
| Ticket Médio | 5-8x maior | Base |
| Frequência Média | 2-3x maior | Base |
| Idade Média | 38-42 anos | 35-38 anos |
| % Feminino | 55-60% | 58-62% |

### 7.2 Concentração de Valor

Os High Spenders representam aproximadamente:
- **10% dos clientes**
- **40% do valor total de vendas**

Isso demonstra a importância de estratégias de retenção e fidelização desse grupo.

---

## 8. Arquivos Gerados

### 8.1 Consolidados (Resultados/)

| Arquivo | Descrição |
|---------|-----------|
| `ESTUDO_PERFIL_CLIENTE_POR_SHOPPING.xlsx` | Excel com todas as análises em abas |
| `resumo_por_shopping.csv` | Métricas principais por shopping |
| `consolidado_genero_por_shopping.csv` | Perfil por gênero de todos os shoppings |
| `consolidado_faixa_etaria_por_shopping.csv` | Perfil por faixa etária de todos os shoppings |
| `consolidado_segmentos_por_shopping.csv` | Top segmentos por shopping |
| `consolidado_clientes_todos_shoppings.csv` | Base completa de clientes |

### 8.2 Por Shopping (Resultados/Por_Shopping/{SIGLA}/)

| Arquivo | Descrição |
|---------|-----------|
| `perfil_genero.csv` | Distribuição por gênero |
| `perfil_faixa_etaria.csv` | Distribuição por faixa etária |
| `matriz_genero_faixa.csv` | Cruzamento gênero x faixa etária |
| `top_segmentos.csv` | Top 10 segmentos por valor |
| `top_lojas.csv` | Top 10 lojas por valor |
| `comportamento_periodo.csv` | Vendas por período do dia |
| `comportamento_dia_semana.csv` | Vendas por dia da semana |
| `high_spenders_stats.csv` | Estatísticas dos High Spenders |
| `lista_high_spenders.csv` | Lista completa de High Spenders |
| `base_clientes.csv` | Base de clientes do shopping |

---

## 9. Glossário

| Termo | Definição |
|-------|-----------|
| **High Spender** | Cliente no top 10% de valor de compras |
| **Ticket Médio** | Valor médio gasto por transação |
| **Threshold** | Valor mínimo para ser considerado High Spender |
| **Gen Z** | Geração nascida entre 1997-2012 |
| **Millennials** | Geração nascida entre 1981-1996 |
| **Gen X** | Geração nascida entre 1965-1980 |
| **Boomers** | Geração nascida entre 1946-1964 |
| **Silent** | Geração nascida antes de 1946 |

---

## 10. Considerações Técnicas

1. **Clientes únicos por shopping:** Um cliente pode aparecer em mais de um shopping. O total consolidado (271.110) é maior que o total de clientes únicos da base (253.946) devido a essa sobreposição.

2. **Threshold de High Spender:** Calculado individualmente para cada shopping, refletindo a realidade de consumo de cada unidade.

3. **Dados não informados:** Percentual de idade e gênero não informados varia por shopping. Recomenda-se ações para melhorar a captação desses dados.

4. **Período de análise:** Base completa desde dezembro/2022, permitindo análise de comportamento ao longo do tempo.

---

**Documento gerado em:** Janeiro/2026
**Base de dados:** base_cupons_completa_v3.csv
**Atualização:** 20/01/2026
