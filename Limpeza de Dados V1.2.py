# Instale as bibliotecas necessárias (rode no terminal antes):
# pip install pandas requests sqlalchemy psycopg2-binary

import pandas as pd
from sqlalchemy import create_engine, text

# ════════════════════════════════════════════════════════
# ETAPA 1 — CARREGAR O DATASET
# ════════════════════════════════════════════════════════
url = "https://raw.githubusercontent.com/adaoduque/Brasileirao_Dataset/master/campeonato-brasileiro-full.csv"

df = pd.read_csv(url, encoding='utf-8')

print("✅ Dataset carregado com sucesso!")
print(f"   Shape: {df.shape}")
print(f"\nColunas originais:")
print(df.columns.tolist())

# ════════════════════════════════════════════════════════
# CORREÇÃO: renomear colunas para nomes padronizados
# ════════════════════════════════════════════════════════
df = df.rename(columns={
    'rodata'            : 'rodada',
    'mandante_Placar'   : 'mandante_placar',
    'visitante_Placar'  : 'visitante_placar',
    'mandante_Estado'   : 'mandante_estado',
    'visitante_Estado'  : 'visitante_estado',
    'arena'             : 'estadio',
})

# ════════════════════════════════════════════════════════
# ETAPA 2 — DIAGNÓSTICO
# ════════════════════════════════════════════════════════
print("\n" + "="*45)
print("ETAPA 2 — DIAGNÓSTICO")
print("="*45)
print("\nTipos de dados:")
print(df.dtypes)
print("\nValores nulos por coluna:")
nulos = df.isnull().sum()
print(nulos[nulos > 0] if nulos.sum() > 0 else "  Nenhum valor nulo!")
print(f"\nLinhas duplicadas: {df.duplicated().sum()}")
print("\nTimes únicos (mandante):")
print(df['mandante'].unique())
print("\nEstados únicos (mandante):")
print(df['mandante_estado'].unique())

# ════════════════════════════════════════════════════════
# ETAPA 3 — LIMPEZA
# ════════════════════════════════════════════════════════
print("\n" + "="*45)
print("ETAPA 3 — LIMPEZA")
print("="*45)

# 3.1 Corrigir datas
df['data'] = pd.to_datetime(df['data'], dayfirst=True, errors='coerce')
df['ano']        = df['data'].dt.year
df['mes']        = df['data'].dt.month
df['dia_semana'] = df['data'].dt.day_name()
print("\n✅ Datas convertidas")

# 3.2 Remover espaços extras (o dataset tem \xa0 antes dos estádios)
for col in ['mandante', 'visitante', 'mandante_estado',
            'visitante_estado', 'estadio']:
    df[col] = df[col].astype(str).str.strip().str.replace('\xa0', '', regex=False)
print("✅ Espaços extras e caracteres invisíveis removidos")

# 3.3 Tratar valores nulos
df['mandante_estado']  = df['mandante_estado'].replace('nan', 'Indefinido').fillna('Indefinido')
df['visitante_estado'] = df['visitante_estado'].replace('nan', 'Indefinido').fillna('Indefinido')
df['estadio']          = df['estadio'].replace('nan', 'Não informado').fillna('Não informado')

antes = len(df)
df = df.dropna(subset=['mandante_placar', 'visitante_placar'])
print(f"✅ Linhas removidas por placar nulo: {antes - len(df)}")

# 3.4 Padronizar nomes de times
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
print("✅ Nomes de times padronizados")

# 3.5 Remover duplicatas
colunas_jogo = ['data', 'mandante', 'visitante',
                'mandante_placar', 'visitante_placar']
antes = len(df)
df = df.drop_duplicates(subset=colunas_jogo)
print(f"✅ Duplicatas removidas: {antes - len(df)}")

# 3.6 Criar coluna de resultado
def resultado(row):
    if row['mandante_placar'] > row['visitante_placar']:
        return 'Vitória mandante'
    elif row['mandante_placar'] < row['visitante_placar']:
        return 'Vitória visitante'
    else:
        return 'Empate'

df['resultado']  = df.apply(resultado, axis=1)
df['total_gols'] = df['mandante_placar'] + df['visitante_placar']
print("✅ Colunas 'resultado' e 'total_gols' criadas")

# 3.7 Corrigir tipos numéricos
df['mandante_placar']  = df['mandante_placar'].astype(int)
df['visitante_placar'] = df['visitante_placar'].astype(int)
df['total_gols']       = df['total_gols'].astype(int)
print("✅ Tipos numéricos corrigidos")

# ════════════════════════════════════════════════════════
# ETAPA 4 — VALIDAÇÃO FINAL
# ════════════════════════════════════════════════════════
print("\n" + "="*45)
print("ETAPA 4 — VALIDAÇÃO FINAL")
print("="*45)
print(f"Total de partidas : {len(df)}")
print(f"Período           : {int(df['ano'].min())} a {int(df['ano'].max())}")
print(f"Times únicos      : {df['mandante'].nunique()}")
print(f"Nulos restantes   : {df.isnull().sum().sum()}")
print(f"Média gols/jogo   : {df['total_gols'].mean():.2f}")
print(f"\nDistribuição de resultados:")
print(df['resultado'].value_counts())

# ════════════════════════════════════════════════════════
# ETAPA 5 — SALVAR NO POSTGRESQL
# CORREÇÃO: client_encoding=utf8 resolve erro de acentos
#           na mensagem de resposta do servidor PostgreSQL
# ════════════════════════════════════════════════════════
print("\n" + "="*45)
print("ETAPA 5 — POSTGRESQL")
print("="*45)
try:
    engine = create_engine(
        'postgresql://postgres:7310@localhost:5432/brasileirao',
        connect_args={'client_encoding': 'utf8'}  # ← CORREÇÃO
    )

    # Testa a conexão antes de enviar os dados
    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))
    print("✅ Conexão com PostgreSQL estabelecida!")

    df.to_sql(
        name='partidas',
        con=engine,
        if_exists='replace',
        index=False,
        chunksize=500
    )
    print(f"✅ {len(df)} partidas salvas no PostgreSQL!")

except Exception as e:
    print(f"⚠️  PostgreSQL indisponível: {e}")
    print("   Exportando apenas o CSV...")

# ════════════════════════════════════════════════════════
# ETAPA 6 — EXPORTAR CSV LIMPO
# ════════════════════════════════════════════════════════
df.to_csv('brasileirao_limpo.csv', index=False, encoding='utf-8-sig')
print("\n✅ Arquivo 'brasileirao_limpo.csv' exportado com sucesso!")