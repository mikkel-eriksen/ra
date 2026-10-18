import pandas as pd

# Load census data
census_years = [1801, 1850, 1860, 1880, 1901]

filelist = [
    'data/census_1801__v1__cl.csv.gz',
    'data/census_1850__v1__cl.csv.gz',
    'data/census_1860__v1__cl.csv.gz',
    'data/census_1880__v1__cl.csv.gz',
    'data/census_1901__v1__cl.csv.gz'
]

census_df_list = []
for i in range(len(census_years)):
    census_df_year = pd.read_csv(filelist[i], usecols=['handicaps'])
    census_df_year['census_year'] = census_years[i]
    census_df_list.append(census_df_year)

census_df = pd.concat(census_df_list, ignore_index=True)
census_df.dropna().info()

# row_counts = census_df.groupby('census_year').size()

# print('Row counts per census year:')
# print(row_counts)
census_df.info()
distinct_counts = census_df.groupby('census_year').nunique()

print('Distinct values per census year:')
print(distinct_counts)

distinct_counts.to_csv('output/distinct_counts.csv')
census_df = census_df.dropna()

census_df = census_df.drop_duplicates()

census_df.to_csv('output/handicaps_distinct.csv')
word_counts = (
    census_df['handicaps']
    .str.lower()
    .str.findall(r'[a-zæøå]+')
    .explode()
    .value_counts()
)

word_counts.to_csv('output/word_counts.csv')
labels = {
    'forstand berøvet': ['forstand'],
    'blind':            ['blind'],
    'døvstum':          ['døvstum'],
    'døv':              ['døv']
}

for label, words in labels.items():
    for word in words:
        census_df.loc[census_df['handicaps'].str.contains(word,  case=False, na=False), 'handicaps_std'] = label
len(census_df) - len(census_df.dropna())