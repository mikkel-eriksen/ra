import pandas as pd
from rapidfuzz import fuzz

# Load census data
census_df = pd.read_csv('data/MF_census_1850_1846_cl.csv.gz')
# census_df.info()

# Remove individuals with no birth year and no name
census_df = census_df.dropna(subset=['inp_PR_BIR_YEAR_EST', 'inp_PR_NAME'])
census_df['inp_PR_BIR_YEAR_EST'] = census_df['inp_PR_BIR_YEAR_EST'].astype('int')

# Set NA-values for sex to Unknown
census_df['inp_PR_SEX_CODE'] = census_df['inp_PR_SEX_CODE'].fillna('Unknown')
# census_df.info()

# Merge datasets
linkage_columns = [
    'pa_id',
    'inp_PR_BIR_YEAR_EST',
    'inp_PR_SEX_CODE',
    'inp_PR_NAME',
    'inp_PR_BIR_PLACE_ORIG',
    'inp_EVENT_PLACE',
    'inp_PR_MARITAL_STATUS',
    'inp_PR_FLAG_FREE_OR_ENSLAVED_ORIG',
    'inp_EVENT_YEAR'
]

census_1846_df = census_df[census_df['inp_EVENT_YEAR'] == 1846][linkage_columns]
census_1850_df = census_df[census_df['inp_EVENT_YEAR'] == 1850][linkage_columns]

census_1846_df['name_first_letter'] = census_1846_df['inp_PR_NAME'].str[0].str.lower()
census_1850_df['name_first_letter'] = census_1850_df['inp_PR_NAME'].str[0].str.lower()

pairs_df = pd.merge(
    left=census_1846_df,
    right=census_1850_df,
    on=['inp_PR_BIR_YEAR_EST', 'inp_PR_SEX_CODE', 'name_first_letter'],
    how='inner',
    suffixes=['_1846', '_1850']
)
# pairs_df.info()

# Extract arrays for fuzzy matching
name_1 = pairs_df['inp_PR_NAME_1846'].fillna('').astype(str).values
name_2 = pairs_df['inp_PR_NAME_1850'].fillna('').astype(str).values

birth_place_1 = pairs_df['inp_PR_BIR_PLACE_ORIG_1846'].fillna('').astype(str).values
birth_place_2 = pairs_df['inp_PR_BIR_PLACE_ORIG_1850'].fillna('').astype(str).values

event_place_1 = pairs_df['inp_EVENT_PLACE_1846'].fillna('').astype(str).values
event_place_2 = pairs_df['inp_EVENT_PLACE_1850'].fillna('').astype(str).values

# Compute individual scores
pairs_df['score_name'] = [fuzz.WRatio(a, b) for a, b in zip(name_1, name_2)]
pairs_df['score_birth_place'] = [fuzz.WRatio(a, b) for a, b in zip(birth_place_1, birth_place_2)]
pairs_df['score_event_place'] = [fuzz.WRatio(a, b) for a, b in zip(event_place_1, event_place_2)]

pairs_df['score_marital'] = (
    (pairs_df['inp_PR_MARITAL_STATUS_1846'] == pairs_df['inp_PR_MARITAL_STATUS_1850']) &
    pairs_df['inp_PR_MARITAL_STATUS_1846'].notna()
).astype(float) * 100

pairs_df['score_free_enslaved'] = (
    (pairs_df['inp_PR_FLAG_FREE_OR_ENSLAVED_ORIG_1846'] == pairs_df['inp_PR_FLAG_FREE_OR_ENSLAVED_ORIG_1850']) &
    pairs_df['inp_PR_FLAG_FREE_OR_ENSLAVED_ORIG_1846'].notna()
).astype(float) * 100

pairs_df['linkage_score'] = (
    0.60 * pairs_df['score_name'] +
    0.15 * pairs_df['score_birth_place'] +
    0.15 * pairs_df['score_event_place'] +
    0.05 * pairs_df['score_marital'] +
    0.05 * pairs_df['score_free_enslaved']
)

# Filter and save results
pairs_df[pairs_df['linkage_score'] > 85].sort_values('linkage_score').to_csv('output/linking_results.csv', index=False)