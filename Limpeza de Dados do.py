# Instale as API necessárias
# pip install pandas requests

import pandas as pd
from sqlalchemy import create_engine

# Carrega direto da URL - sem precisar baixar nada
url = "https://raw.githubusercontent.com/adaoduque/Brasileirao_Dataset/master/campeonato-brasileiro-full.csv"

df = pd.read_csv(url, encoding='utf-8')

# Mostra todas as colunas do dataset real
print(df.columns.tolist())
print(df.head(2))

print(df.shape)         #quantas linhas e colunas
print(df.head() )          # primeiras linhas
print(df.columns.tolist())      #nome de todas as colunas

#----- Visão Geral ------------------
print("Shape:", df.shape)
print("\nTipos de cada coluna:")
print(df.dtypes)

#-------- Valores Nulos ---------------
print("\nValores nulos por coluna:")
nulos = df.isnull().sum()
print(nulos[nulos > 0]) #mostra só quem tem nulo

#-------- Duplicatas ----------------
print("\nLinhas duplicadas:", df.duplicated().sum())

#------ Valores Únicos (para colunas categoricas) --------
print("\nTimes únicos (mandante):")
print(df['mandante'].unique())

print("\nEstados únicos :")
print(df['mandante_estado'].unique())

#----- Datas: Estão no formato correto? ------
print("\nExemplo de datas:")
print(df['data'].head(10))

#------- 3.1 Corrigir tipos de dados -----------
df['data'] = pd.to_datetime(df['data'], dayfirst=True, errors='coerce')

# Extrair infos uteis da data
df['ano']       = df['data'].dt.year
df['mes']       = df['data'].dt.month
df['dia_semana']       = df['data'].dt.day_name()

#----- 3.2 Tratas valores nulos -----
# Ver quais colunas tem nulos e decidir o que fazer
print(df.isnull().sum())

# Preencher estado desconhecido como 'Indefinido'
df['mandante_estado'] = df['mandante_estado'].fillna('Indefinido')
df['visitante_estado'] = df['visitante_estado'].fillna('Indefinido')

# Remove linhas onde o placar esta nulo
df = df.dropna(subset=['mandante_placar', 'visitante_placar'])

#------- 3.3 Padronizar nomes de times ------
# Dicionario de correções (adicione conforme encontrar variações)
correcoes_times = {
    'Atletico MG'       : 'Atlético-MG',
    'Atletico-MG'       : 'Atlético-MG',
    'Atletico Mineiro'  : 'Atlético-MG',
    'Atletico GO'       : 'Atlético-GO',
    'Athletico PR'      : 'Athletico-PR',
    'Atletico PR'       : 'Athletico-PR',
    'Sport Recife'      : 'Sport',
    'Nautico'           : 'Náutico',
}

df['mandante'] = df['mandante'].replace(correcoes_times)
df['visitante'] = df['visitante'].replace(correcoes_times)

#----- 3.4 Remover duplicatas ----------
antes = len(df)
df = df.drop_duplicates()
depois = len(df)
print(f"Duplicatas removidas: {antes - depois}")

#----- 3.5 Criar colunas de resultados ---------
# Útil para analises no power bi
def resultado(row):
    if row ['mandante_placar'] > row['visitante_placar']:
        return 'Vitória mandante'
    elif row ['mandante_placar'] < row['visitante_placar']:
        return 'Vitória visitante'
    else:
        return 'Empate'

df['resultado'] = df.apply(resultado, axis=1)

#--------- 3.6 Criar coluna de total de gols -------------
df['total_gols'] = df['mandante_placar'] + df['visitante_placar']

#------- 3.7 Garantir tipos numericos corretos ---------
df['mandante_placar'] = df['mandante_placar'].astype(int)
df['visitante_placar'] = df['visitante_placar'].astype(int)

# ── Configuração da conexão ──────────────────────────────
# Formato: postgresql://usuario:senha@host:porta/banco
engine = create_engine(
    'postgresql://postgres:7310@localhost:5432/brasileirao'
)

# ── Envia o DataFrame limpo para o banco ─────────────────
df.to_sql(
    name='partidas',       # nome da tabela
    con=engine,
    if_exists='replace',   # substitui se já existir
    index=False,           # não salva o índice do pandas
    chunksize=500          # envia em lotes de 500 linhas
)

print(f"✅ {len(df)} partidas salvas no PostgreSQL com sucesso!")

#--- Validação antes de exportar ------
print("=== Relatório final de qualidade ===")
print(f"Total de partidas: {len(df)}")
print(f"Período: {df['ano'].min()} a {df['ano'].max()}")
print(f"Times únicos: {df['mandante'].nunique()}")
print(f"Nulos restantes:\n{df.isnull().sum()[df.isnull().sum() > 0]}")
print(f"\nDistribuição de resultados:")
print(df['resultado'].value_counts())
print(f"\nMédia de gols por jogo: {df['total_gols'].mean():.2f}")

# ── Exportar CSV limpo ───────────────────────────────────
df.to_csv('brasileirao_limpo.csv', index=False, encoding='utf-8-sig')
# utf-8-sig é importante para o Power BI ler acentos corretamente

print("\nArquivo 'brasileirao_limpo.csv' exportado com sucesso!")