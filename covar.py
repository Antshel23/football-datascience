import pandas as pd
#import seaborn as sns
#import matplotlib.pyplot as plt
from scipy.stats import pearsonr
import numpy as np

sheet_id = '1lehDw5lfvo5bCNoM4uHE-uMG_Db8vh1mTLmf_E4pl1o'
sheet_name = 'Raw'

csv_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet={sheet_name}"

df = pd.read_csv(csv_url)

# Calculate new statistics
df['npxG'] = (df['xG'] - (df['Total penalties'] * 0.78))
df['npxG per shot'] = df['npxG'] / df['Total shots']
df['High regain %'] = df['High recoveries'] / df['Total recoveries']
df['Med regain %'] = df['Med recoveries'] / df['Total recoveries']
df['Low regain %'] = df['Low recoveries'] / df['Total recoveries']
df['Open play box entries'] = df['Deep completed passes'] + df['Box entry via run'] + df['Box entry via cross']
df['Pass for box entry %'] = df['Deep completed passes'] / df['Open play box entries']
df['Run for box entry %'] = df['Box entry via run'] / df['Open play box entries']
df['Cross for box entry %'] = df['Box entry via cross'] / df['Open play box entries']
df['Cross distance'] = df['Deep completed crosses'] / df['Box entry via cross']

# Drop columns with NaN values and the 'Team' column
df = df.drop('Team', axis=1).dropna()

# Calculate correlation matrix
corrMat = df.corr()

# Calculate p-values
p_values = pd.DataFrame(np.zeros(corrMat.shape), columns=corrMat.columns, index=corrMat.index)

for i in range(len(corrMat.columns)):
    for j in range(len(corrMat.columns)):
        if i != j:
            _, p_values.iat[i, j] = pearsonr(df[corrMat.columns[i]], df[corrMat.columns[j]])

# Set significance level
alpha = 0.05

# Create a mask for significant correlations
significant_mask = p_values < alpha

# Filter correlation matrix for significant values
significant_corrMat = corrMat[significant_mask]

# Stack the significant correlation matrix
corrStack = significant_corrMat.stack()

# Drop self-correlations
corrStack = corrStack[corrStack.index.get_level_values(0) != corrStack.index.get_level_values(1)]

# Match values that contain npxG and not Oppo only
xg_corr = corrStack[((corrStack.index.get_level_values(0) == 'Oppo xG') & (~corrStack.index.get_level_values(1).astype(str).str.contains('Oppo')))]

sorted_xg_corr = xg_corr.sort_values(ascending=False)

# Print top 20 correlations involving npxG
print("\nStatistically signficant comparisons involving 'xPTS':")
for (var1, var2), corr in sorted_xg_corr.items():
    print(f"{var1} and {var2}: {corr:.2f}")


