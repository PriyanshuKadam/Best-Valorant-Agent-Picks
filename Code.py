import pandas as pd

#Read the Excel file into a pandas DataFrame
df = pd.read_excel('/content/drive/MyDrive/Agent_stats.xlsx')

#Calculate the KDA (Kill/Death/Assist) ratio
df['KDA'] = (df['Kill'] + df['Assist']) / df['Death']

# Print the first few rows of the data frame.
df.head()

from statsmodels.multivariate.manova import MANOVA
from statsmodels.formula.api import ols
from statsmodels.stats.anova import anova_lm
from statsmodels.stats.multicomp import pairwise_tukeyhsd
import scipy.stats as stats

#Perform MANOVA analysis
manova = MANOVA.from_formula('KD + Win + Pick + AvgScore + Kill + Death + Assist + KDA ~ Name + Map + (Name * Map)', data=df)
print(manova.mv_test())

#Perform ANOVA analysis for each variable of interest
fit1 = ols('KD ~ Name', data=df).fit()
annova1 = anova_lm(fit1)
annova1

# Repeat ANOVA for other variables
# ...

#Perform Tukey's HSD test for pairwise comparisons
tukey = pairwise_tukeyhsd(df["Assist"], groups=df["Map"] + df['Name'])
results_df = pd.DataFrame(data=tukey._results_table.data[1:], columns=tukey._results_table.data[0])
results_df

#Filter significant results based on p-value
results_df = results_df[results_df['reject'] == True]
results_df[['Map1', 'Agent1']] = results_df['group1'].str.extract(r'([A-Z][a-z]*)([A-Z][a-z]*)')
results_df[['Map2', 'Agent2']] = results_df['group2'].str.extract(r'([A-Z][a-z]*)([A-Z][a-z]*)')
results_df = results_df.replace('K', 'KAY/O')
results_df

# Perform t-tests for each comparison
p_values = []
f_statistics = []

for _, row in results_df.iterrows():
    agent1 = df[(df['Name'] == row['Agent1']) & (df['Map'] == row['Map1'])]['Assist']
    agent2 = df[(df['Name'] == row['Agent2']) & (df['Map'] == row['Map2'])]['Assist']
    t_statistic, p_value = stats.ttest_ind(agent1, agent2, equal_var=True, alternative='two-sided')
    p_values.append(p_value)
    f_statistics.append(t_statistic)

results_df['p_value'] = p_values
results_df['f_statistic'] = f_statistics
results_df

# Filter results based on p-value
results_df = results_df[results_df['p_value'] < 0.05]
results_df['operator'] = results_df['f_statistic'].apply(lambda x: '>' if x > 0 else '<')
results_df

x = input('Enter the Map:')
df1 = df1[df1['Map1'] == x]

rankings = {}

for index, row in df1.iterrows():
    agent1 = row['Agent1']
    operator = row['operator']
    agent2 = row['Agent2']

    if operator == '>':
        if agent1 not in rankings:
            rankings[agent1] = {'greater': 0, 'less': 0}
        if agent2 not in rankings:
            rankings[agent2] = {'greater': 0, 'less': 0}
        rankings[agent1]['greater'] += 1
        rankings[agent2]['less'] += 1
    elif operator == '<':
        if agent1 not in rankings:
            rankings[agent1] = {'greater': 0, 'less': 0}
        if agent2 not in rankings:
            rankings[agent2] = {'greater': 0, 'less': 0}
        rankings[agent1]['less'] += 1
        rankings[agent2]['greater'] += 1

sorted_rankings = sorted(rankings.items(), key=lambda x: x[1]['greater'], reverse=True)

print('    Agent Rankings:')
print('--------------------------')
for i, (agent, counts) in enumerate(sorted_rankings):
    greater_count = counts['greater']
    less_count = counts['less']
    total_count = greater_count + less_count
    if total_count == 0:
        rank = 'N/A'
    else:
        rank = str(i+1)
        print(f'{rank}.{agent}: {greater_count} wins, {less_count} losses')

rankings = {}

for _, row in df1.iterrows():
    agent1, agent2 = row['Agent1'], row['Agent2']
    operator = row['operator']

    if operator == '>':
        rankings[agent1] = rankings.get(agent1, 0) + 1
        rankings[agent2] = rankings.get(agent2, 0) - 1
    elif operator == '<':
        rankings[agent1] = rankings.get(agent1, 0) - 1
        rankings[agent2] = rankings.get(agent2, 0) + 1

df2 = pd.DataFrame({'Agent': list(rankings.keys()), 'Points': list(rankings.values())})
df2 = df2.sort_values('Points', ascending=False)
df2['Rank'] = df2['Points'].rank(ascending=False).astype(int)
df2 = df2[['Rank', 'Agent', 'Points']]
df2 = df2.reset_index(drop=True)

print('Agent Rankings:')
df2

