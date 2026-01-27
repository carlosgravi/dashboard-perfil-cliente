-# DOCUMENTACAO TECNICA - PERFIL DE CLIENTE E DEMOGRAFICO

## Estudo de Caracteristicas e Comportamento dos Clientes

**Data de Geracao:** 18/12/2025
**Periodo dos Dados:** 11/12/2022 a 30/11/2025
**Versao:** 1.0

---

## 1. OBJETIVO DO ESTUDO

Realizar uma analise completa do perfil demografico e comportamental dos clientes:
- **Perfil Demografico:** Idade, genero, faixa etaria (geracao)
- **Comportamento de Compra:** Frequencia, ticket medio, preferencias
- **High Spenders:** Caracteristicas dos clientes mais valiosos
- **Personas:** Segmentacao comportamental para acoes de marketing

---

## 2. FONTE DE DADOS

### 2.1 Arquivo de Origem

| Atributo | Valor |
|----------|-------|
| Arquivo | `base_cupons_completa_v3.csv` |
| Encoding | latin-1 |
| Total de Registros | 1.248.686 |
| Filtro Aplicado | `status == 'Validado'` |

### 2.2 Campos Utilizados

| Campo | Descricao | Preenchimento |
|-------|-----------|---------------|
| `cliente_id` | ID unico do cliente | 100% |
| `cliente_nome` | Nome do cliente | 100% |
| `data_nascimento` | Data de nascimento | 99,9% |
| `genero` | Genero do cliente | 99,9% |
| `valor` | Valor da compra | 100% |
| `data_envio` | Data da transacao | 100% |
| `segmento_loja` | Categoria da loja | 96,9% |
| `shopping_nome` | Nome do shopping | 100% |

### 2.3 Tratamento de Dados

```python
# Carregar e filtrar
df = pd.read_csv('base_cupons_completa_v3.csv', encoding='latin-1')
df = df[df['status'] == 'Validado'].copy()

# Calcular idade
df['data_nascimento'] = pd.to_datetime(df['data_nascimento'], errors='coerce')
data_ref = df['data_envio'].max()  # 30/11/2025
df['idade'] = ((data_ref - df['data_nascimento']).dt.days / 365.25).round()

# Limpar idades invalidas (< 16 ou > 100 anos)
df.loc[(df['idade'] < 16) | (df['idade'] > 100), 'idade'] = np.nan

# Padronizar genero
df['genero'] = df['genero'].str.lower().str.strip()
df['genero'] = df['genero'].replace({
    'masculino': 'Masculino',
    'feminino': 'Feminino',
    'outro': 'Outro'
})
```

---

## 3. CLASSIFICACOES UTILIZADAS

### 3.1 Faixas Etarias (Geracoes)

| Faixa | Idade | Geracao | Descricao |
|-------|-------|---------|-----------|
| 16-24 | 16-24 anos | Gen Z | Nativos digitais |
| 25-39 | 25-39 anos | Millennials | Geracao Y |
| 40-54 | 40-54 anos | Gen X | Geracao X |
| 55-69 | 55-69 anos | Boomers | Baby Boomers |
| 70+ | 70+ anos | Silent | Geracao Silenciosa |

```python
def classificar_faixa_etaria(idade):
    if pd.isna(idade):
        return 'Nao Informado'
    elif idade < 25:
        return '16-24 (Gen Z)'
    elif idade < 40:
        return '25-39 (Millennials)'
    elif idade < 55:
        return '40-54 (Gen X)'
    elif idade < 70:
        return '55-69 (Boomers)'
    else:
        return '70+ (Silent)'
```

### 3.2 Periodos do Dia

| Periodo | Horario |
|---------|---------|
| Manha | 06h - 12h |
| Tarde | 12h - 18h |
| Noite | 18h - 22h |

### 3.3 High Spenders

```python
# Definicao: Clientes no Percentil 90 de valor total gasto
threshold_hs = clientes['valor_total'].quantile(0.90)
clientes['is_high_spender'] = clientes['valor_total'] >= threshold_hs
```

**Threshold calculado:** R$ 4.410,45

### 3.4 Personas de Cliente

| Persona | Criterios |
|---------|-----------|
| **Fashionista Premium** | High Spender + Feminino + 25-39 anos |
| **Executivo Exigente** | High Spender + Masculino |
| **Senior VIP** | High Spender + 55+ anos |
| **Jovem Engajado** | < 30 anos + Frequencia >= 5 compras |
| **Mae Moderna** | Feminino + 30-50 anos + Frequencia >= 3 |
| **Comprador Seletivo** | Top 25% valor + Frequencia <= 3 |
| **Senior Tradicional** | 55+ anos (nao HS) |
| **Jovem Explorer** | < 30 anos (baixa frequencia) |
| **Cliente Regular** | Demais clientes |

```python
def classificar_persona(row):
    idade = row['idade'] if pd.notna(row['idade']) else 35
    valor = row['valor_total']
    freq = row['qtd_compras']
    genero = row['genero']

    if valor >= threshold_hs and genero == 'Feminino' and 25 <= idade < 40:
        return 'Fashionista Premium'
    elif valor >= threshold_hs and genero == 'Masculino':
        return 'Executivo Exigente'
    # ... demais regras
```

---

## 4. METRICAS CALCULADAS

### 4.1 Base de Clientes Unicos

```python
clientes = df.groupby('cliente_id').agg({
    'valor': ['sum', 'mean', 'count'],       # Valor total, ticket medio, qtd compras
    'data_envio': ['min', 'max'],            # Primeira e ultima compra
    'genero': 'first',                        # Genero
    'idade': 'first',                         # Idade
    'faixa_etaria': 'first',                  # Faixa etaria
    'shopping': lambda x: x.mode().iloc[0],   # Shopping preferido (moda)
    'segmento': lambda x: x.mode().iloc[0]    # Segmento preferido (moda)
})
```

### 4.2 Metricas por Genero

| Metrica | Formula |
|---------|---------|
| `qtd_clientes` | `COUNT(cliente_id)` |
| `valor_total` | `SUM(valor_total)` |
| `ticket_medio_cliente` | `MEAN(valor_total)` |
| `freq_media` | `MEAN(qtd_compras)` |
| `idade_media` | `MEAN(idade)` |
| `qtd_high_spenders` | `SUM(is_high_spender)` |
| `pct_clientes` | `qtd_clientes / total_clientes * 100` |
| `pct_valor` | `valor_total / total_valor * 100` |

### 4.3 Metricas por Faixa Etaria

Mesmas metricas do genero, agrupadas por faixa etaria.

### 4.4 Analise Cruzada

```python
# Matriz de valor: Genero x Faixa Etaria
matriz_valor = clientes.pivot_table(
    values='valor_total',
    index='faixa_etaria',
    columns='genero',
    aggfunc='sum'
)

# Matriz de ticket medio
matriz_ticket = clientes.pivot_table(
    values='valor_total',
    index='faixa_etaria',
    columns='genero',
    aggfunc='mean'
)
```

### 4.5 Preferencias de Segmento

```python
# Top 5 segmentos por faixa etaria (baseado em valor)
seg_por_faixa = df.groupby(['faixa_etaria', 'segmento']).agg({
    'valor': 'sum',
    'cliente_id': 'nunique'
})
```

### 4.6 Comportamento Temporal

```python
# Por periodo do dia
periodo_stats = df.groupby(['faixa_etaria', 'periodo_dia']).agg({
    'valor': 'sum',
    'id': 'count'
})

# Por dia da semana
dia_stats = df.groupby(['faixa_etaria', 'dia_semana']).agg({
    'valor': 'sum',
    'id': 'count'
})
```

---

## 5. RESULTADOS PRINCIPAIS

### 5.1 Metricas Gerais

| Metrica | Valor |
|---------|-------|
| Total de Clientes | 204.148 |
| Faturamento Total | R$ 408.896.151,06 |
| Idade Media | 41,6 anos |
| Ticket Medio por Cliente | R$ 2.002,94 |

### 5.2 Distribuicao por Genero

| Genero | Clientes | % Clientes | Valor | % Valor |
|--------|----------|------------|-------|---------|
| Feminino | 127.615 | 62,5% | R$ 268,9M | 65,8% |
| Masculino | 76.115 | 37,3% | R$ 139,5M | 34,1% |
| Outro | 214 | 0,1% | R$ 0,3M | 0,1% |
| Nao Informado | 204 | 0,1% | R$ 0,2M | 0,0% |

### 5.3 Distribuicao por Faixa Etaria

| Faixa Etaria | Clientes | % Clientes | Valor | Ticket Medio |
|--------------|----------|------------|-------|--------------|
| 25-39 (Millennials) | 81.790 | 40,1% | R$ 144,9M | R$ 1.771 |
| 40-54 (Gen X) | 77.780 | 38,1% | R$ 179,4M | R$ 2.307 |
| 55-69 (Boomers) | 26.157 | 12,8% | R$ 56,7M | R$ 2.167 |
| 16-24 (Gen Z) | 13.258 | 6,5% | R$ 16,8M | R$ 1.265 |
| 70+ (Silent) | 4.859 | 2,4% | R$ 10,8M | R$ 2.221 |

**Insight:** Gen X (40-54 anos) possui o maior ticket medio (R$ 2.307) e maior faturamento total (R$ 179,4M).

### 5.4 High Spenders

| Metrica | Valor |
|---------|-------|
| Quantidade | 20.415 (10,0%) |
| Valor Total | R$ 202,1M |
| % do Faturamento | 49,4% |
| Ticket Medio | R$ 9.898,72 |
| Threshold (P90) | R$ 4.410,45 |

**Insight:** Os 10% de clientes mais valiosos geram quase metade (49,4%) do faturamento total.

### 5.5 Personas Identificadas

| Persona | Clientes | % Clientes | Valor | % Valor |
|---------|----------|------------|-------|---------|
| Mae Moderna | 41.929 | 20,5% | R$ 108,3M | 26,5% |
| Cliente Regular | 82.390 | 40,4% | R$ 84,9M | 20,8% |
| Executivo Exigente | 6.775 | 3,3% | R$ 64,3M | 15,7% |
| Fashionista Premium | 4.533 | 2,2% | R$ 43,0M | 10,5% |
| Senior Tradicional | 25.862 | 12,7% | R$ 27,5M | 6,7% |
| Comprador Seletivo | 8.310 | 4,1% | R$ 26,1M | 6,4% |
| Senior VIP | 2.232 | 1,1% | R$ 23,3M | 5,7% |
| Jovem Engajado | 8.482 | 4,2% | R$ 16,7M | 4,1% |
| Jovem Explorer | 23.635 | 11,6% | R$ 14,8M | 3,6% |

---

## 6. ARQUIVOS GERADOS

### 6.1 Dados (CSV)

| Arquivo | Descricao |
|---------|-----------|
| `perfil_por_genero.csv` | Metricas completas por genero |
| `perfil_por_faixa_etaria.csv` | Metricas completas por faixa etaria |
| `matriz_clientes_genero_idade.csv` | Matriz de clientes Genero x Idade |
| `matriz_valor_genero_idade.csv` | Matriz de valor Genero x Idade |
| `matriz_ticket_genero_idade.csv` | Matriz de ticket medio Genero x Idade |
| `top_segmentos_por_faixa.csv` | Top 5 segmentos por faixa etaria |
| `top_segmentos_por_genero.csv` | Top 5 segmentos por genero |
| `comportamento_periodo_dia.csv` | Comportamento por periodo do dia |
| `comportamento_dia_semana.csv` | Comportamento por dia da semana |
| `comparacao_high_spenders.csv` | Comparativo HS vs demais |
| `high_spenders_por_faixa.csv` | HS por faixa etaria |
| `high_spenders_por_genero.csv` | HS por genero |
| `matriz_shopping_faixa_etaria.csv` | Perfil demografico por shopping |
| `matriz_shopping_genero.csv` | Genero por shopping |
| `perfil_idade_por_shopping.csv` | Idade media por shopping |
| `personas_clientes.csv` | Estatisticas por persona |
| `base_clientes_perfil.csv` | Base completa de clientes com perfil |

### 6.2 Visualizacoes (PNG)

| Arquivo | Descricao |
|---------|-----------|
| `perfil_01_genero.png` | Distribuicao por genero (pizza + barras) |
| `perfil_02_faixa_etaria.png` | Faturamento por faixa etaria |
| `perfil_03_piramide_etaria.png` | Piramide de faturamento por idade e genero |
| `perfil_04_heatmap_ticket.png` | Heatmap de ticket medio |
| `perfil_05_comparativo_hs.png` | Comparativo High Spenders vs Demais |
| `perfil_06_hs_faixa.png` | High Spenders por faixa etaria |
| `perfil_07_personas.png` | Grafico de personas |
| `perfil_08_segmentos_genero.png` | Segmentos preferidos por genero |
| `perfil_09_segmentos_faixa.png` | Segmentos preferidos por faixa etaria |
| `perfil_10_periodo_dia.png` | Preferencia de horario por perfil |
| `perfil_11_shopping_demografico.png` | Composicao demografica por shopping |
| `perfil_12_dashboard.png` | Dashboard resumo |

### 6.3 Apresentacao

| Arquivo | Descricao |
|---------|-----------|
| `Apresentacao_Perfil_Cliente.pptx` | Apresentacao PowerPoint (25 slides) |

---

## 7. SCRIPTS PYTHON

### 7.1 Scripts do Estudo

| Script | Funcao |
|--------|--------|
| `analise_perfil_cliente.py` | Analise principal e geracao de dados |
| `visualizacoes_perfil_cliente.py` | Geracao de graficos |
| `criar_apresentacao_perfil_cliente.py` | Geracao do PowerPoint |

### 7.2 Dependencias

```
pandas>=1.5.0
numpy>=1.21.0
matplotlib>=3.5.0
seaborn>=0.11.0
python-pptx>=0.6.21
```

---

## 8. GLOSSARIO

| Termo | Definicao |
|-------|-----------|
| **Faixa Etaria** | Classificacao por idade baseada em geracoes |
| **Gen Z** | Nascidos entre 2001-2009 (16-24 anos em 2025) |
| **Millennials** | Nascidos entre 1986-2000 (25-39 anos em 2025) |
| **Gen X** | Nascidos entre 1971-1985 (40-54 anos em 2025) |
| **Boomers** | Nascidos entre 1956-1970 (55-69 anos em 2025) |
| **Silent** | Nascidos ate 1955 (70+ anos em 2025) |
| **High Spender** | Cliente no percentil 90 de valor total gasto |
| **Threshold** | Valor minimo para ser considerado High Spender |
| **Persona** | Segmentacao comportamental de clientes |
| **Ticket Medio** | Valor medio gasto por cliente |
| **Frequencia** | Quantidade de compras do cliente |

---

## 9. CONSIDERACOES METODOLOGICAS

1. **Idades Invalidas:** Idades < 16 ou > 100 anos foram tratadas como nulas
2. **Genero Padronizado:** Valores convertidos para Masculino/Feminino/Outro
3. **Shopping Preferido:** Calculado como a moda (mais frequente) por cliente
4. **Segmento Preferido:** Calculado como a moda (mais frequente) por cliente
5. **Personas:** Classificacao hierarquica (primeira regra que atende)
6. **High Spenders:** Calculados sobre valor total acumulado (nao por periodo)

---

## 10. INSIGHTS E RECOMENDACOES

### 10.1 Principais Insights

1. **Predominancia Feminina:** Mulheres representam 62,5% da base e 65,8% do faturamento
2. **Gen X e Valor:** A geracao 40-54 anos possui o maior ticket medio e faturamento total
3. **Concentracao de Valor:** 10% dos clientes (HS) geram 49,4% do faturamento
4. **Mae Moderna:** Persona mais valiosa (26,5% do faturamento)
5. **Ticket vs Volume:** Millennials tem mais volume, Gen X tem maior ticket

### 10.2 Recomendacoes Estrategicas

1. **Retencao de High Spenders:** Programa VIP com beneficios exclusivos
2. **Foco em Millennials:** Campanhas digitais e experiencias personalizadas
3. **Engajamento Feminino:** Parcerias com Moda e Beleza
4. **Ativacao Gen Z:** Estrategias em redes sociais e gamificacao
5. **Upgrade de Clientes:** Identificar potenciais novos High Spenders

---

## 11. PROXIMOS PASSOS SUGERIDOS

1. Criar modelo preditivo de propensao a High Spender
2. Desenvolver jornadas personalizadas por persona
3. Implementar score de engajamento por cliente
4. Criar dashboard interativo para acompanhamento
5. Analisar churn por perfil demografico

---

*Documento gerado automaticamente em 18/12/2025*
