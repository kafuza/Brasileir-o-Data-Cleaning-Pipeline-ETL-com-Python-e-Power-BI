# Instale as bibliotecas necessárias
# pip install pandas requests sqlalchemy psycopg2-binary

import pandas as pd
from sqlalchemy import create_engine

# ── Carrega direto da URL ────────────────────────────────
url = "https://raw.githubusercontent.com/adaoduque/Brasileirao_Dataset/master/campeonato-brasileiro-full.csv"

df = pd.read_csv(url, encoding='latin-1')

# ── Visão geral ──────────────────────────────────────────
print("Shape:", df.shape)
print("\nColunas originais:")
print(df.columns.tolist())
print("\nPrimeiras linhas:")
print(df.head(2))
print("\nTipos de cada coluna:")
print(df.dtypes)

# ════════════════════════════════════════════════════════
# CORREÇÃO: renomear colunas para nomes padronizados
# Nomes reais do dataset: mandante_Placar, visitante_Placar,
#                         mandante_Estado, visitante_Estado
# ════════════════════════════════════════════════════════
df = df.rename(columns={
    'rodata'             : 'rodada',
    'mandante_Placar'    : 'mandante_placar',
    'visitante_Placar'   : 'visitante_placar',
    'mandante_Estado'    : 'mandante_estado',
    'visitante_Estado'   : 'visitante_estado',
    'arena'              : 'estadio',
    'formacao_mandante'  : 'formacao_mandante',
    'formacao_visitante' : 'formacao_visitante',
    'tecnico_mandante'   : 'tecnico_mandante',
    'tecnico_visitante'  : 'tecnico_visitante',
    'vencedor'           : 'vencedor',
})

print("\nColunas após renomear:")
print(df.columns.tolist())

# ── Valores nulos ────────────────────────────────────────
print("\nValores nulos por coluna:")
nulos = df.isnull().sum()
print(nulos[nulos > 0] if nulos.sum() > 0 else "Nenhum valor nulo!")

# ── Duplicatas ───────────────────────────────────────────
print("\nLinhas duplicadas:", df.duplicated().sum())

# ── Valores únicos ───────────────────────────────────────
print("\nTimes únicos (mandante):")
print(df['mandante'].unique())

print("\nEstados únicos (mandante):")
print(df['mandante_estado'].unique())

print("\nExemplo de datas:")
print(df['data'].head(5))

# ════════════════════════════════════════════════════════
# ETAPA 3 — LIMPEZA
# ════════════════════════════════════════════════════════

# ── 3.1 Corrigir tipos de dados ──────────────────────────
df['data'] = pd.to_datetime(df['data'], dayfirst=True, errors='coerce')

df['ano']        = df['data'].dt.year
df['mes']        = df['data'].dt.month
df['dia_semana'] = df['data'].dt.day_name()

# ── 3.2 Tratar valores nulos ─────────────────────────────
df['mandante_estado']  = df['mandante_estado'].fillna('Indefinido')
df['visitante_estado'] = df['visitante_estado'].fillna('Indefinido')
df['estadio']          = df['estadio'].fillna('Não informado')

# CORREÇÃO: remover espaços extras que o dataset tem nos valores
df['estadio']          = df['estadio'].str.strip()
df['mandante_estado']  = df['mandante_estado'].str.strip()
df['visitante_estado'] = df['visitante_estado'].str.strip()
df['mandante']         = df['mandante'].str.strip()
df['visitante']        = df['visitante'].str.strip()

# Remover linhas com placar nulo (ANTES de remover duplicatas)
antes = len(df)
df = df.dropna(subset=['mandante_placar', 'visitante_placar'])
print(f"\nLinhas removidas por placar nulo: {antes - len(df)}")

# ── 3.3 Padronizar nomes de times ────────────────────────
correcoes_times = {
    'Atletico MG'      : 'Atlético-MG',
    'Atletico-MG'      : 'Atlético-MG',
    'Atletico Mineiro' : 'Atlético-MG',
    'Atletico GO'      : 'Atlético-GO',
    'Athletico PR'     : 'Athletico-PR',
    'Atletico PR'      : 'Athletico-PR',
    'Sport Recife'     : 'Sport',
    'Nautico'          : 'Náutico',
}

df['mandante']  = df['mandante'].replace(correcoes_times)
df['visitante'] = df['visitante'].replace(correcoes_times)

# ── 3.4 Remover duplicatas (DEPOIS do dropna) ────────────
# CORREÇÃO: usar subset para ignorar coluna ID
colunas_jogo = ['data', 'mandante', 'visitante',
                'mandante_placar', 'visitante_placar']

antes = len(df)
df = df.drop_duplicates(subset=colunas_jogo)
print(f"Duplicatas removidas: {antes - len(df)}")

# ── 3.5 Criar coluna de resultado ────────────────────────
def resultado(row):
    if row['mandante_placar'] > row['visitante_placar']:
        return 'Vitória mandante'
    elif row['mandante_placar'] < row['visitante_placar']:
        return 'Vitória visitante'
    else:
        return 'Empate'

df['resultado'] = df.apply(resultado, axis=1)

# ── 3.6 Criar coluna de total de gols ────────────────────
df['total_gols'] = df['mandante_placar'] + df['visitante_placar']

# ── 3.7 Garantir tipos numéricos corretos ────────────────
df['mandante_placar']  = df['mandante_placar'].astype(int)
df['visitante_placar'] = df['visitante_placar'].astype(int)
df['total_gols']       = df['total_gols'].astype(int)

# ════════════════════════════════════════════════════════
# ETAPA 4 — VALIDAÇÃO FINAL
# ════════════════════════════════════════════════════════
print("\n=== Relatório final de qualidade ===")
print(f"Total de partidas : {len(df)}")
print(f"Período           : {df['ano'].min()} a {df['ano'].max()}")
print(f"Times únicos      : {df['mandante'].nunique()}")
print(f"Nulos restantes   : {df.isnull().sum().sum()}")
print(f"Média gols/jogo   : {df['total_gols'].mean():.2f}")
print(f"\nDistribuição de resultados:")
print(df['resultado'].value_counts())

# ════════════════════════════════════════════════════════
# ETAPA 5 — SALVAR NO POSTGRESQL
# ════════════════════════════════════════════════════════
try:
    engine = create_engine(
        'postgresql://postgres:7310@localhost:5432/brasileirao'
    )
    df.to_sql(
        name='partidas',
        con=engine,
        if_exists='replace',
        index=False,
        chunksize=500
    )
    print(f"\n✅ {len(df)} partidas salvas no PostgreSQL com sucesso!")
except Exception as e:
    print(f"\n⚠️  PostgreSQL não disponível: {e}")
    print("   O CSV será exportado normalmente.")

# ════════════════════════════════════════════════════════
# ETAPA 6 — EXPORTAR CSV LIMPO
# ════════════════════════════════════════════════════════
df.to_csv('brasileirao_limpo.csv', index=False, encoding='utf-8-sig')
print("\n✅ Arquivo 'brasileirao_limpo.csv' exportado com sucesso!")