# Documentacao Completa - Dashboard Perfil de Cliente

## Almeida Junior Shoppings

**Versao:** 1.0
**Data:** Janeiro/2026
**Periodo dos Dados:** 11/12/2022 a 19/01/2026

---

## 1. Visao Geral do Dashboard

O Dashboard de Perfil de Cliente e uma ferramenta de Business Intelligence desenvolvida para analisar o comportamento de consumo dos clientes da rede Almeida Junior Shoppings. Ele consolida dados de 6 shoppings e apresenta insights sobre perfil demografico, comportamento de compra, segmentacao e clientes de alto valor.

### 1.1 Shoppings Analisados

| Sigla | Shopping | Cidade/Regiao |
|-------|----------|---------------|
| BS | Balneario Shopping | Balneario Camboriu |
| CS | Continente Shopping | Sao Jose |
| GS | Garten Shopping | Joinville |
| NK | Neumarkt Shopping | Blumenau |
| NR | Norte Shopping | Blumenau |
| NS | Nacoes Shopping | Criciuma |

### 1.2 Resumo Geral dos Dados

| Metrica | Valor | Observacao |
|---------|-------|------------|
| Clientes Unicos | 253.946 | Cada cliente contado uma vez |
| Clientes por Shopping | 271.110 | Soma inclui quem compra em multiplos shoppings |
| Total de Transacoes | 1.643.751 | |
| Valor Total | R$ 550.508.465,26 | |
| Ticket Medio Geral | R$ 2.167,82 | Valor Total / Clientes Unicos |
| High Spenders Unicos | 25.397 (10%) | Top 10% de cada shopping |
| High Spenders por Shopping | 27.115 | Soma inclui quem e HS em multiplos shoppings |

---

## 2. Paginas do Dashboard

### 2.1 Visao Geral

**Objetivo:** Apresentar um panorama consolidado de todos os shoppings.

**Metricas Exibidas:**
- **Total de Clientes:** Soma de clientes unicos de todos os shoppings
- **Valor Total:** Soma do faturamento de todos os shoppings
- **High Spenders:** Quantidade total de clientes no top 10% de cada shopping
- **Ticket Medio:** Valor Total / Total de Clientes

**Graficos:**
- Valor Total por Shopping (barras horizontais)
- Distribuicao de Clientes por Shopping (pizza)
- Tabela resumo com todas as metricas por shopping

---

### 2.2 Personas

**Objetivo:** Apresentar os perfis comportamentais de clientes identificados atraves de analise de cluster.

**Personas Identificadas:**

| Persona | % Clientes | % Valor | Caracteristicas |
|---------|------------|---------|-----------------|
| Mae Moderna | 20,5% | 26,5% | Mulheres 35-45 anos, alta frequencia, ticket medio-alto |
| Cliente Regular | 40,4% | 20,8% | Perfil diverso, frequencia media, ticket baixo |
| Executivo Exigente | 3,3% | 15,7% | Alta renda, ticket muito alto, baixa frequencia |
| Fashionista Premium | 2,2% | 10,5% | Jovens 25-35, altissima frequencia, foco em moda |
| Senior Tradicional | 12,7% | 6,7% | 55+ anos, baixa frequencia, ticket baixo |
| Comprador Seletivo | 4,1% | 6,4% | Compras pontuais de alto valor |
| Senior VIP | 1,1% | 5,7% | 60+ anos, alto poder aquisitivo |
| Jovem Engajado | 4,2% | 4,1% | 18-25 anos, alta frequencia, ticket baixo |
| Jovem Explorer | 11,6% | 3,6% | 18-25 anos, baixa frequencia, explorando marcas |

**Metricas por Persona:**
- **Qtd Clientes:** Numero de clientes na persona
- **Valor Total:** Soma do valor gasto pela persona
- **Ticket Medio:** Valor Total / Qtd Clientes
- **Freq Media:** Media de transacoes por cliente
- **Idade Media:** Media de idade dos clientes da persona
- **% Clientes:** Qtd Clientes / Total Clientes * 100
- **% Valor:** Valor Persona / Valor Total * 100

---

### 2.3 Por Shopping

**Objetivo:** Analise detalhada de cada shopping individualmente.

**Abas Disponiveis:**

#### 2.3.1 Demografia
- Distribuicao por genero (pizza)
- Distribuicao por faixa etaria (barras)

#### 2.3.2 Lojas & Segmentos
- Top 10 Segmentos por valor
- Top 10 Lojas por valor

#### 2.3.3 Comportamento
- Distribuicao por periodo do dia
- Distribuicao por dia da semana

#### 2.3.4 Detalhes
- Tabelas com dados completos de genero e faixa etaria

---

### 2.4 Perfil Demografico

**Objetivo:** Visao consolidada do perfil demografico de todos os shoppings.

#### 2.4.1 Por Genero

**Distribuicao Tipica:**
- Feminino: ~62%
- Masculino: ~37%
- Outros: ~1%

**Calculo:**
```
% Genero = (Clientes do Genero / Total Clientes) * 100
```

#### 2.4.2 Por Faixa Etaria

**Faixas Utilizadas:**
| Faixa | Geracao | Idade |
|-------|---------|-------|
| 16-24 | Gen Z | Nascidos 2001-2009 |
| 25-39 | Millennials | Nascidos 1986-2000 |
| 40-54 | Gen X | Nascidos 1971-1985 |
| 55-69 | Boomers | Nascidos 1956-1970 |
| 70+ | Silent | Nascidos antes de 1956 |

**Distribuicao Tipica:**
- Millennials (25-39): ~40%
- Gen X (40-54): ~38%
- Boomers (55-69): ~13%
- Gen Z (16-24): ~6%
- Silent (70+): ~2%

---

### 2.5 High Spenders

**Objetivo:** Analise dos clientes de maior valor (Top 10%).

#### 2.5.1 Definicao de High Spender

Um cliente e considerado **High Spender** se o valor total de suas compras esta no **percentil 90** ou superior dentro de seu shopping.

**Calculo do Threshold:**
```python
threshold = df_clientes['valor_total'].quantile(0.90)
high_spenders = df_clientes[df_clientes['valor_total'] >= threshold]
```

**Thresholds por Shopping:**
| Shopping | Threshold (R$) |
|----------|----------------|
| BS | 5.800,47 |
| NK | 5.176,86 |
| GS | 4.299,43 |
| CS | 3.999,97 |
| NR | 3.265,62 |
| NS | 3.128,53 |

#### 2.5.2 Metricas de High Spenders

**Comparacao HS vs Demais:**
| Metrica | High Spenders | Demais Clientes |
|---------|---------------|-----------------|
| Qtd Clientes | 20.415 (10%) | 183.733 (90%) |
| Valor Total | R$ 202M (49%) | R$ 207M (51%) |
| Ticket Medio | R$ 9.899 | R$ 1.126 |
| Freq Media | 24,8 compras | 4,0 compras |
| % Feminino | 66,8% | 62,0% |

#### 2.5.3 HS por Genero
- Feminino: 66,8% dos HS
- Masculino: 33,2% dos HS

#### 2.5.4 HS por Faixa Etaria
- Gen X (40-54): 46,2%
- Millennials (25-39): 33,8%
- Boomers (55-69): 14,1%
- Gen Z (16-24): 3,2%
- Silent (70+): 2,6%

---

### 2.6 Segmentos

**Objetivo:** Analise de consumo por categoria de produto.

#### 2.6.1 Principais Segmentos

| Segmento | Descricao |
|----------|-----------|
| Moda | Vestuario, acessorios |
| Beleza e Bem-estar | Cosmeticos, perfumaria, spas |
| Calcados | Sapatos, tenis, sandalias |
| Joalheria | Joias, relogios, oticas |
| Gastronomia | Restaurantes, fast-food, cafes |
| Telefonia | Celulares, acessorios |
| Eletronicos | Informatica, eletrodomesticos |
| Casa e Decoracao | Moveis, decoracao, cama/mesa/banho |

#### 2.6.2 Top Segmentos por Genero

**Feminino:**
1. Moda - R$ 94,6M
2. Beleza e Bem-estar - R$ 20,0M
3. Calcados - R$ 19,2M
4. Joalheria - R$ 18,8M
5. Gastronomia - R$ 14,6M

**Masculino:**
1. Moda - R$ 45,0M
2. Joalheria - R$ 18,5M
3. Calcados - R$ 7,8M
4. Telefonia - R$ 7,5M
5. Gastronomia - R$ 7,3M

#### 2.6.3 Matrizes Cruzadas

**Matriz de Clientes (Genero x Faixa Etaria):**
Quantidade de clientes em cada combinacao de genero e faixa etaria.

**Matriz de Valor (Genero x Faixa Etaria):**
Valor total gasto por cada combinacao.

**Matriz de Ticket (Genero x Faixa Etaria):**
Ticket medio de cada combinacao.

```
Ticket Medio = Valor Total / Quantidade de Clientes
```

---

### 2.7 Comportamento

**Objetivo:** Analise temporal do comportamento de compra.

#### 2.7.1 Periodo do Dia

| Periodo | Horario | % Valor Tipico |
|---------|---------|----------------|
| Manha | 6h-12h | ~18% |
| Tarde | 12h-18h | ~39% |
| Noite | 18h-22h | ~43% |

**Insight:** A maior parte das compras ocorre no periodo noturno, seguido da tarde.

#### 2.7.2 Dia da Semana

| Dia | % Valor Tipico |
|-----|----------------|
| Segunda | ~12% |
| Terca | ~12% |
| Quarta | ~13% |
| Quinta | ~13% |
| Sexta | ~15% |
| Sabado | ~20% |
| Domingo | ~15% |

**Insight:** Sabado e o dia de maior movimento, seguido de sexta e domingo.

#### 2.7.3 Heatmaps

Os heatmaps mostram a intensidade de consumo cruzando:
- Faixa Etaria x Periodo do Dia
- Faixa Etaria x Dia da Semana

---

### 2.8 Comparativo

**Objetivo:** Comparar metricas entre shoppings selecionados.

**Graficos:**
- **Radar Chart:** Comparativo normalizado (0-100%) de Clientes, Valor, Ticket e HS
- **Barras:** Valores absolutos de Valor Total e Ticket Medio

**Normalizacao do Radar:**
```
Valor Normalizado = (Valor do Shopping / Maior Valor) * 100
```

---

## 3. Metodologia de Calculo das Metricas

### 3.1 Metricas Basicas

| Metrica | Formula |
|---------|---------|
| **Total Clientes** | COUNT(DISTINCT id_cliente) |
| **Total Transacoes** | COUNT(*) |
| **Valor Total** | SUM(valor_transacao) |
| **Ticket Medio** | Valor Total / Total Clientes |
| **Frequencia Media** | Total Transacoes / Total Clientes |

### 3.2 Metricas de High Spenders

```python
# Threshold: Percentil 90 do valor total por cliente
threshold = clientes.groupby('id_cliente')['valor'].sum().quantile(0.90)

# Identificacao
high_spenders = clientes[clientes['valor_total'] >= threshold]

# Quantidade
qtd_hs = len(high_spenders)

# Percentual
pct_hs = (qtd_hs / total_clientes) * 100
```

### 3.3 Metricas de Personas

As personas foram identificadas atraves de **analise de cluster** considerando:
- Valor total gasto
- Frequencia de compras
- Ticket medio
- Idade
- Genero

**Algoritmo:** K-Means com 9 clusters otimizados via Silhouette Score.

### 3.4 Distribuicoes Demograficas

```python
# Por Genero
dist_genero = df.groupby('genero')['id_cliente'].nunique()
pct_genero = (dist_genero / dist_genero.sum()) * 100

# Por Faixa Etaria
df['faixa_etaria'] = pd.cut(df['idade'],
                            bins=[0, 24, 39, 54, 69, 120],
                            labels=['16-24', '25-39', '40-54', '55-69', '70+'])
dist_faixa = df.groupby('faixa_etaria')['id_cliente'].nunique()
```

### 3.5 Segmentos

Os segmentos sao definidos pela categoria da loja onde a compra foi realizada.

```python
# Top segmentos por valor
top_segmentos = df.groupby('segmento').agg({
    'valor': 'sum',
    'id_cliente': 'nunique'
}).sort_values('valor', ascending=False)
```

---

## 4. Fonte dos Dados

### 4.1 Arquivos Utilizados

| Arquivo | Descricao |
|---------|-----------|
| resumo_por_shopping.csv | Metricas consolidadas por shopping |
| personas_clientes.csv | Dados das 9 personas identificadas |
| comparacao_high_spenders.csv | Comparativo HS vs Demais |
| high_spenders_por_genero.csv | HS segmentado por genero |
| high_spenders_por_faixa.csv | HS segmentado por faixa etaria |
| matriz_clientes_genero_idade.csv | Matriz cruzada clientes |
| matriz_valor_genero_idade.csv | Matriz cruzada valor |
| matriz_ticket_genero_idade.csv | Matriz cruzada ticket |
| top_segmentos_por_genero.csv | Top 5 segmentos por genero |
| top_segmentos_por_faixa.csv | Top segmentos por faixa etaria |
| comportamento_periodo_dia.csv | Dados por periodo do dia |
| comportamento_dia_semana.csv | Dados por dia da semana |
| consolidado_genero_por_shopping.csv | Genero por shopping |
| consolidado_faixa_etaria_por_shopping.csv | Faixa etaria por shopping |
| consolidado_segmentos_por_shopping.csv | Segmentos por shopping |

### 4.2 Dados por Shopping

Cada shopping possui arquivos individuais em `Resultados/Por_Shopping/{SIGLA}/`:
- perfil_genero.csv
- perfil_faixa_etaria.csv
- top_segmentos.csv
- top_lojas.csv
- comportamento_periodo.csv
- comportamento_dia_semana.csv
- high_spenders_stats.csv
- lista_high_spenders.csv
- base_clientes.csv

---

## 5. Tecnologias Utilizadas

| Tecnologia | Versao | Uso |
|------------|--------|-----|
| Python | 3.11+ | Linguagem principal |
| Streamlit | 1.28+ | Framework web |
| Plotly | 5.18+ | Graficos interativos |
| Pandas | 2.0+ | Manipulacao de dados |

---

## 6. Glossario

| Termo | Definicao |
|-------|-----------|
| **Ticket Medio** | Valor medio gasto por cliente |
| **High Spender** | Cliente no top 10% de gastos |
| **Threshold** | Valor minimo para ser considerado High Spender |
| **Persona** | Perfil comportamental de cliente |
| **Frequencia** | Numero de compras por cliente |
| **Segmento** | Categoria de produto/loja |
| **Faixa Etaria** | Agrupamento por idade |

---

## 7. Contato e Suporte

**Desenvolvido para:** Almeida Junior Shoppings
**Dashboard:** https://dashboard-perfil-cliente-4oq9e2gaea8ztun4n7ltsg.streamlit.app/
**Repositorio:** https://github.com/carlosgravi/dashboard-perfil-cliente

---

*Documento gerado em Janeiro/2026*
