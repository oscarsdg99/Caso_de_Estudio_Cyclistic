# %% [markdown]
# *------------------------------------- PREPARING THE DATA -------------------------------------*

# %%
import pandas as pd

# Load the datasets
df_2019 = pd.read_csv('Divvy_Trips_2019_Q1 - Divvy_Trips_2019_Q1.csv')
df_2020 = pd.read_csv('Divvy_Trips_2020_Q1 - Divvy_Trips_2020_Q1.csv')

# %% [markdown]
# *CHECKING FOR ROCCC (Reliability, Originality, Completeness, Consistency, Currency)*

# %%
# ==========================================
# 1. RELIABILITY (Accuracy & Outliers)
# ==========================================
print("--- RELIABILITY CHECK ---")
# Verify that every trip has a unique ID (no duplicates from the source)
is_unique_2019 = df_2019['trip_id'].is_unique
is_unique_2020 = df_2020['ride_id'].is_unique
print(f"2019 IDs are unique: {is_unique_2019}")
print(f"2020 IDs are unique: {is_unique_2020}")

# %%

# ==========================================
# 2. ORIGINALITY (Unique Source Identifiers)
# ==========================================
print("Data comes from a primary source")


# %%
# ==========================================
# 3. COMPLETENESS (Missing Values)
# ==========================================
print("\n--- COMPLETENESS CHECK ---")
# Calculate missing values per column
print("Missing values in 2019:\n", df_2019.isnull().sum())
print("\nMissing values in 2020:\n", df_2020.isnull().sum())

# Helper function to extract unique Station ID + Name pairs
def get_station_mapping(df, id_col, name_col):
    return df[[id_col, name_col]].drop_duplicates().dropna()

# 1. Extract mappings for 2019 and 2020
map_2019 = pd.concat([
    get_station_mapping(df_2019, 'from_station_id', 'from_station_name').rename(columns={'from_station_id': 'station_id', 'from_station_name': 'station_name'}),
    get_station_mapping(df_2019, 'to_station_id', 'to_station_name').rename(columns={'to_station_id': 'station_id', 'to_station_name': 'station_name'})
]).drop_duplicates()

map_2020 = pd.concat([
    get_station_mapping(df_2020, 'start_station_id', 'start_station_name').rename(columns={'start_station_id': 'station_id', 'start_station_name': 'station_name'}),
    get_station_mapping(df_2020, 'end_station_id', 'end_station_name').rename(columns={'end_station_id': 'station_id', 'end_station_name': 'station_name'})
]).drop_duplicates()

# 2. Check for INTERNAL CONSISTENCY (Does 1 ID map to multiple names in the same year?)
inconsistent_2019 = map_2019.groupby('station_id')['station_name'].nunique()
print(f"IDs with multiple names in 2019: {(inconsistent_2019 > 1).sum()}")

# 3. Check for INTER-TABLE CONSISTENCY (Do names change between 2019 and 2020?)
combined_map = pd.merge(map_2019, map_2020, on='station_id', how='inner', suffixes=('_2019', '_2020'))
mismatches = combined_map[combined_map['station_name_2019'] != combined_map['station_name_2020']]

print(f"Total station IDs with name changes: {len(mismatches)}")
if not mismatches.empty:
    print("\nSample of mismatches found:")
    print(mismatches[['station_id', 'station_name_2019', 'station_name_2020']].head())

# 4. Check for COMPLETENESS (Missing stations between periods)
only_2019 = set(map_2019['station_id']) - set(map_2020['station_id'])
only_2020 = set(map_2020['station_id']) - set(map_2019['station_id'])

print(f"\nStations existing only in 2019: {len(only_2019)}")
print(f"Stations existing only in 2020: {len(only_2020)}")

# %%
# ==========================================
# 4. CONSISTENCY (Formatting & Labels)
# ==========================================
print("\n--- CONSISTENCY CHECK ---")
# Check categorical labels to ensure they match or need mapping
print("User types in 2019:", df_2019['usertype'].unique())
print("User types in 2020:", df_2020['member_casual'].unique())

# Check column name alignment (Finding differences)
print("Columns in 2019 but not in 2020:", set(df_2019.columns) - set(df_2020.columns))

# %%
# ==========================================
# 5. CURRENCY (Time Relevance)
# ==========================================
print("\n--- CURRENCY CHECK ---")
# Convert to datetime and check the date range
df_2019['start_time'] = pd.to_datetime(df_2019['start_time'])
df_2020['started_at'] = pd.to_datetime(df_2020['started_at'])

print(f"2019 Range: {df_2019['start_time'].min()} to {df_2019['start_time'].max()}")
print(f"2020 Range: {df_2020['started_at'].min()} to {df_2020['started_at'].max()}")

print(f"Data is up to date (last version)")

# %% [markdown]
# *------------------------------------- PROCESSING THE DATA -------------------------------------*

# %%
import pandas as pd

# 1. Load original files
df_2019 = pd.read_csv('Divvy_Trips_2019_Q1 - Divvy_Trips_2019_Q1.csv')
df_2020 = pd.read_csv('Divvy_Trips_2020_Q1 - Divvy_Trips_2020_Q1.csv')

# %%
# 2. Rename 2019 columns to match 2020 format
df_2019 = df_2019.rename(columns={
    'trip_id': 'ride_id',
    'start_time': 'started_at',
    'end_time': 'ended_at',
    'from_station_id': 'start_station_id',
    'from_station_name': 'start_station_name',
    'to_station_id': 'end_station_id',
    'to_station_name': 'end_station_name',
    'usertype': 'member_casual'
})

# %%
# 3. Standardize User Labels (Subscriber -> member, Customer -> casual)
df_2019['member_casual'] = df_2019['member_casual'].replace({'Subscriber': 'member', 'Customer': 'casual'})

# %%
# 4. Create Canonical Station Mapping
all_pairs = pd.concat([
    df_2019[['start_station_id', 'start_station_name']].rename(columns={'start_station_id': 'id', 'start_station_name': 'name'}),
    df_2019[['end_station_id', 'end_station_name']].rename(columns={'end_station_id': 'id', 'end_station_name': 'name'}),
    df_2020[['start_station_id', 'start_station_name']].rename(columns={'start_station_id': 'id', 'start_station_name': 'name'}),
    df_2020[['end_station_id', 'end_station_name']].rename(columns={'end_station_id': 'id', 'end_station_name': 'name'})
]).dropna()

canonical_map = all_pairs.groupby('id')['name'].agg(lambda x: x.value_counts().index[0]).to_dict()

# Apply the consistent names
for df in [df_2019, df_2020]:
    df['start_station_name'] = df['start_station_id'].map(canonical_map).fillna(df['start_station_name'])
    df['end_station_name'] = df['end_station_id'].map(canonical_map).fillna(df['end_station_name'])

# %%
# 5. Merge and Calculate new columns
common_cols = ['ride_id', 'started_at', 'ended_at', 'start_station_name', 'start_station_id', 'end_station_name', 'end_station_id', 'member_casual']
df_final = pd.concat([df_2019[common_cols], df_2020[common_cols]], ignore_index=True)

# Convert to datetime
df_final['started_at'] = pd.to_datetime(df_final['started_at'])
df_final['ended_at'] = pd.to_datetime(df_final['ended_at'])

# Add calculated fields for Analysis
df_final['day_of_week'] = df_final['started_at'].dt.day_name()

# Remove trailing " (*)" from station names
df_final["start_station_name"] = df_final["start_station_name"].str.replace(r"\s*\(\*\)$", "", regex=True)
df_final["end_station_name"] = df_final["end_station_name"].str.replace(r"\s*\(\*\)$", "", regex=True)


# %%
# 6. Standarize columns in datetime format
# Calculating duration
df_final = df_final[df_final['ended_at'] > df_final['started_at']]

ride_length_td = df_final["ended_at"] - df_final["started_at"]

# Converting to HH:MM:SS (without '0 days')
df_final["ride_length"] = ride_length_td.apply(
    lambda x: f"{int(x.total_seconds()//3600):02d}:"
              f"{int((x.total_seconds()%3600)//60):02d}:"
              f"{int(x.total_seconds()%60):02d}"
)

# View results
print(df_final[["started_at", "ended_at", "ride_length"]].head())

# %%
# 7. EXPORT THE FILE
df_final.to_csv('cyclistic_final_clean_data.csv', index=False)
print("File 'cyclistic_final_clean_data.csv' has been created successfully!")

# %%
df_final.head()

# %%
df_final.info()


