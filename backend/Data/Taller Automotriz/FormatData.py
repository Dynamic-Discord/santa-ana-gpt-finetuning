import pandas as pd

# Import csv

df = pd.read_csv('./data_taller_automotriz.csv', delimiter=';')

print(df)

# Export dataframe into a csv
df.to_csv('data_taller_automotrizComma.csv', index=False)

