import pandas as pd

def top_words(df, year):
    word_counts = (
        df['handicaps']
        .str.lower()
        .str.findall(r'[a-zæøå]+')
        .explode()
        .value_counts()
    )
    word_counts.to_csv(f'output/word_counts_{year}.csv', index=True)
    return word_counts.head(20)


# Load census handicaps data
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
    census_df_year = pd.read_csv(filelist[i], usecols=['handicaps'], dtype={'handicaps': str})
    census_df_year['census_year'] = census_years[i]
    census_df_list.append(census_df_year)

# Concat all censuses
census_df = pd.concat(census_df_list, ignore_index=True)

# Handle '-', ' -' and '(-)' as NA
census_df['handicaps'] = census_df['handicaps'].replace(['-', ' -', '(-)'], None)

print('Handicaps data')
print(
    census_df.groupby('census_year')['handicaps'].agg(
        total_values = 'size',
        non_null_values = 'count',
        unique_values = 'nunique'
    )
)

# Count words
for i in range(len(census_years)):
    top_words(census_df_list[i], census_years[i])

top_words(census_df, 'complete')

# Apply standardization
census_df = census_df.dropna()

labels = {
    'forstand berøvet': [r'forstand'],
    'blind':            [r'blind', r'\bb\b'],
    'døvstum':          [r'døvstum', r'\bd\b'],
    'sindssyg':         [r'sindssyg', r'sindsyg', r'\bs\b'],
    'døv':              [r'døv\b'],
    'aandssvag':        [r'aandssvag', r'aandsvag', r'\ba\b']
}

for label, patterns in labels.items():
    combined_pattern = '|'.join(patterns)
    census_df.loc[census_df['handicaps'].str.contains(combined_pattern, regex=True, case=False), 'handicaps_std'] = label

print('After standardization')
print(
    census_df.groupby('census_year')['handicaps_std'].agg(
        total_values = 'size',
        standardized_values = 'count'
    )
)

census_df.to_csv('output/handicaps_std.csv', index=False)