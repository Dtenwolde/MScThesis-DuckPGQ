import pandas as pd

df = pd.read_csv('/home/daniel/Documents/Programming/duckdb-pgq/data/csv/sf0.1/Person_knows_Person.csv', sep="|")
df['weight'] = 1
df.to_csv('/home/daniel/Documents/Programming/duckdb-pgq/data/csv/sf0.1/Person_knows_Person_weighted.csv', sep="|", index=False)

pass