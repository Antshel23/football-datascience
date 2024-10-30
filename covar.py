import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np

sheet_id = '1lehDw5lfvo5bCNoM4uHE-uMG_Db8vh1mTLmf_E4pl1o'
sheet_name = 'Raw'

csv_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet={sheet_name}"

df = pd.read_csv(csv_url)
print(df.head())

df = df.drop('Team', axis=1)
corrMat = df.corr()
print(corrMat)

corrStack = corrMat.stack()

# Drop self-correlations (diagonal elements)
corrStack = corrStack[corrStack.index.get_level_values(0) != corrStack.index.get_level_values(1)]

xg_corr = corrStack[(corrStack.index.get_level_values(0) == 'xG')]

sorted_xg_corr = xg_corr.sort_values(ascending=False)

# Print top 20 correlations involving 'xg'
print("\nTop 20 correlations involving 'xg':")
for (var1, var2), corr in sorted_xg_corr.head(20).items():
    print(f"Correlation between {var1} and {var2}: {corr:.2f}")

# Print bottom 20 correlations involving 'xg'
print("\nBottom 20 correlations involving 'xg':")
for (var1, var2), corr in sorted_xg_corr.tail(20).items():
    print(f"Correlation between {var1} and {var2}: {corr:.2f}")