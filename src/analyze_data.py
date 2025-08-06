import pandas as pd
from sqlalchemy import create_engine, text
from pathlib import Path

# Caminho para o banco de dados
db_path = Path(__file__).parent / "database.db"

# Verificar se o arquivo existe
if not db_path.exists():
    print(f"Erro: Arquivo de banco não encontrado em {db_path}")
    exit()

print(f"Banco encontrado: {db_path}")

# Cria engine de leitura
engine = create_engine(f"sqlite:///{db_path}")

# Carregar todos os dados
print("Carregando dados...")
df = pd.read_sql("SELECT * FROM srag_table", con=engine)
print(f"Dados carregados: {len(df)} linhas x {len(df.columns)} colunas\n")

# 1. Informações sobre dtypes
print("=" * 60)
print("1. DTYPE DE CADA COLUNA:")
print("=" * 60)
for col in df.columns:
    print(f"{col:15} -> {df[col].dtype}")

# 2. Verificar valores nulos
print("\n" + "=" * 60)
print("2. VALORES NULOS POR COLUNA:")
print("=" * 60)
null_counts = df.isnull().sum()
for col in df.columns:
    null_count = null_counts[col]
    null_percent = (null_count / len(df)) * 100
    print(f"{col:15} -> {null_count:8} valores nulos ({null_percent:5.2f}%)")

# 3. Valores únicos (excluindo DT_SIN_PRI)
print("\n" + "=" * 60)
print("3. VALORES ÚNICOS POR COLUNA (exceto DT_SIN_PRI):")
print("=" * 60)

# Colunas para analisar (excluindo DT_SIN_PRI)
columns_to_analyze = [col for col in df.columns if col != 'DT_SIN_PRI']

for col in columns_to_analyze:
    unique_values = df[col].nunique()
    print(f"\n{col}:")
    print(f"  - Valores únicos: {unique_values}")
    
    # Mostrar os valores únicos se não forem muitos
    if unique_values <= 20:
        unique_list = sorted(df[col].unique())
        print(f"  - Valores: {unique_list}")
    else:
        print(f"  - Valores: Muitos valores únicos ({unique_values} total)")
        # Mostrar alguns exemplos
        sample_values = sorted(df[col].unique())[:10]
        print(f"  - Exemplos: {sample_values}...")

# 4. Informações gerais sobre datas
print("\n" + "=" * 60)
print("4. INFORMAÇÕES SOBRE DATAS:")
print("=" * 60)
# if 'DT_SIN_PRI_DATETIME' in df.columns:
#     print(f"Data mais antiga: {df['DT_SIN_PRI_DATETIME'].min()}")
#     print(f"Data mais recente: {df['DT_SIN_PRI_DATETIME'].max()}")
#     print(f"Período: {df['DT_SIN_PRI_DATETIME'].max() - df['DT_SIN_PRI_DATETIME'].min()}")

# 5. Shape dos dados
print("\n" + "=" * 60)
print("5. SHAPE DOS DADOS:")
print("=" * 60)
print(f"Shape: {df.shape[0]} linhas x {df.shape[1]} colunas")
print(f"Colunas: {list(df.columns)}")

# 6. Últimas 5 linhas dos dados
print("\n" + "=" * 60)
print("6. ÚLTIMAS 5 LINHAS DOS DADOS:")
print("=" * 60)
print(df.tail())

print("\n" + "=" * 60)
print("ANÁLISE CONCLUÍDA!")
print("=" * 60) 