# ⚽ Brasileirão Data Cleaning — Pipeline ETL com Python e Power BI

![Python](https://img.shields.io/badge/Python-3.14-blue)
![Pandas](https://img.shields.io/badge/Pandas-2.0-green)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-blue)
![Power BI](https://img.shields.io/badge/Power%20BI-Dashboard-yellow)
![Status](https://img.shields.io/badge/Status-Concluído-brightgreen)

## 📌 Sobre o projeto

Este projeto aplica técnicas de limpeza e transformação de dados (ETL)
sobre o histórico completo do Campeonato Brasileiro Série A (2003–2024),
utilizando Python e Pandas. Os dados tratados são armazenados em um banco
de dados PostgreSQL e conectados a um dashboard interativo no Power BI.

**Objetivo:** demonstrar habilidades de qualidade de dados, pipeline ETL
e visualização — competências centrais para um analista de dados.

---

## 🗄️ Arquitetura do projeto

```
CSV bruto (GitHub) → Python/Pandas (limpeza) → PostgreSQL (armazenamento) → Power BI (visualização)
```

---

## 🔍 Problemas de qualidade encontrados e tratados

| Problema | Coluna afetada | Solução aplicada |
|---|---|---|
| Datas como texto | `data` | Conversão com `pd.to_datetime` |
| Nomes de colunas inconsistentes | todas | Renomeação com `df.rename()` |
| Nomes de times com variações | `mandante`, `visitante` | Dicionário de padronização |
| Espaços invisíveis nos textos | `estadio`, `mandante` | `.str.strip()` e remoção de `\xa0` |
| Valores nulos em estados | `mandante_estado` | Preenchimento com "Indefinido" |
| Linhas com placar nulo | `mandante_placar` | `dropna()` antes de `drop_duplicates()` |
| Duplicatas com ID diferente | todas | `drop_duplicates(subset=colunas_jogo)` |
| Tipos numéricos incorretos | `mandante_placar` | Cast para `int` |

---

## 🛠️ Tecnologias utilizadas

- **Python 3.14** — linguagem principal
- **Pandas** — manipulação e limpeza dos dados
- **SQLAlchemy + Psycopg2** — conexão Python → PostgreSQL
- **PostgreSQL 16** — armazenamento dos dados tratados
- **Power BI Desktop** — construção do dashboard
- **Jupyter Notebook** — desenvolvimento do pipeline
- **GitHub** — versionamento do projeto

---

## 📁 Estrutura do projeto

```
brasileirao-etl/
│
├── data/
│   └── raw/
│       └── brasileirao_original.csv
│
├── sql/
│   ├── create_table.sql        ← script de criação da tabela
│   └── analises.sql            ← queries de validação e análise
│
├── powerbi/
│   └── dashboard.pbix          ← arquivo do Power BI
│
├── Limpeza de Dados do.py      ← pipeline ETL completo
└── README.md
```

---

## 📊 Dashboard Power BI

> 🔗 Link do dashboard: *em breve*

<!-- Quando publicar no Power BI Service, substitua o texto acima pelo link:
> Acesse o dashboard interativo: [🔗 Ver no Power BI](COLE_SEU_LINK_AQUI)
-->

<!-- Após tirar o print do dashboard, salve como 'dashboard_preview.png'
     na pasta do projeto e descomente a linha abaixo:
![Preview do dashboard](dashboard_preview.png)
-->

---

## ▶️ Como reproduzir

```bash
# 1. Clone o repositório
git clone https://github.com/SEU_USUARIO/brasileirao-etl.git
cd brasileirao-etl

# 2. Instale as dependências
pip install pandas requests sqlalchemy psycopg2-binary

# 3. Crie o banco de dados no PostgreSQL
# Abra o pgAdmin e execute o script: sql/create_table.sql

# 4. Execute o pipeline
python "Limpeza de Dados do.py"
```

> ⚠️ Lembre de alterar a senha do PostgreSQL na linha do `create_engine` antes de rodar.

---

## 📈 Principais insights encontrados

- Times mandantes vencem aproximadamente **46%** dos jogos
- A média histórica é de **~2,7 gols por partida**
- Os meses de **outubro e novembro** concentram mais gols (pressão pelo título)
- O dataset cobre **mais de 8.000 partidas** entre 2003 e 2024

---

## 🗃️ Queries SQL utilizadas

```sql
-- Gols por ano
SELECT ano, SUM(total_gols) AS total_gols
FROM partidas
GROUP BY ano
ORDER BY ano;

-- Top 10 times com mais vitórias em casa
SELECT mandante, COUNT(*) AS vitorias
FROM partidas
WHERE resultado = 'Vitória mandante'
GROUP BY mandante
ORDER BY vitorias DESC
LIMIT 10;

-- Distribuição de resultados com percentual
SELECT resultado, COUNT(*) AS total,
       ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER(), 1) AS percentual
FROM partidas
GROUP BY resultado;
```

---

## 👤 Autor

Feito por **[Seu Nome]**

[![LinkedIn](https://img.shields.io/badge/LinkedIn-Perfil-blue)](https://linkedin.com/in/SEU_PERFIL)
[![GitHub](https://img.shields.io/badge/GitHub-Repositório-black)](https://github.com/SEU_USUARIO)
