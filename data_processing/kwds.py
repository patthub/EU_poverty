# -*- coding: utf-8 -*-

import pandas as pd


file_path = '/content/results(4) - results(4)(2).csv'
df = pd.read_csv(file_path)

df['normalized_keyword'] = df['keyword'].str.lower().str.replace('^at ', '', regex=True)
df_deduplicated = df.drop_duplicates(subset=['index', 'normalized_keyword'])
original_size = df.shape[0]
deduplicated_size = df_deduplicated.shape[0]

original_size, deduplicated_size

df.head()

def group_keywords(keyword):
    # Ubóstwo
    poverty_related = ['poverty', 'at-risk-of-poverty', 'risk-of-poverty', 'child poverty', 'poverty rate for children', 'in-work poverty', 'below the poverty line', 'under the poverty line']
    if any(poverty_term in keyword for poverty_term in poverty_related):
        return 'poverty_related'

    # Deprywacja materialna i mieszkalnictwo
    deprivation_housing = ['severe material deprivation', 'fuel poverty', 'energy poverty', 'homelessness', 'severe housing deprivation']
    if any(deprivation_term in keyword for deprivation_term in deprivation_housing):
        return 'deprivation_and_housing'

    # Poziom dochodu i intensywność pracy
    income_work_intensity = ['income', 'low work intensity']
    if any(income_term in keyword for income_term in income_work_intensity):
        return 'income_and_work_intensity'

    # Domyślna grupa dla słów kluczowych, które nie pasują do żadnej z wyżej wymienionych kategorii
    return 'other'

df_deduplicated['keyword_group'] = df_deduplicated['normalized_keyword'].apply(group_keywords)
keyword_mapping = {
    'at-risk-of-poverty rate': 'risk-of-poverty rate',
    'below the poverty line': 'under the poverty line',
    'national at-risk-of-poverty threshold': 'at-risk-of-poverty threshold'
}


df_deduplicated['grouped_keyword'] = df_deduplicated['normalized_keyword'].replace(keyword_mapping)


unique_grouped_keywords = sorted(df_deduplicated['grouped_keyword'].unique())
new_keywords_path = '/content/new_kwds - main(3).csv'
new_keywords_df = pd.read_csv(new_keywords_path)

new_keywords_df_cleaned = new_keywords_df.dropna()

keyword_to_mainkeyword_mapping = pd.Series(new_keywords_df_cleaned.mainkeyword.values, index=new_keywords_df_cleaned.keyword.str.strip().str.lower()).to_dict()

df_deduplicated['main_keyword'] = df_deduplicated['grouped_keyword'].map(keyword_to_mainkeyword_mapping).fillna(df_deduplicated['grouped_keyword'])


df_deduplicated['normalized_grouped_keyword'] = df_deduplicated['grouped_keyword'].str.strip().str.lower()
new_keywords_df_cleaned['normalized_keyword'] = new_keywords_df_cleaned['keyword'].str.strip().str.lower()i
keyword_to_mainkeyword_mapping_normalized = pd.Series(new_keywords_df_cleaned.mainkeyword.values, index=new_keywords_df_cleaned.normalized_keyword).to_dict()

df_deduplicated['main_keyword_corrected'] = df_deduplicated['normalized_grouped_keyword'].map(keyword_to_mainkeyword_mapping_normalized).fillna(df_deduplicated['grouped_keyword'])


# Sortowanie danych względem kolumny 'index' i 'main_keyword_corrected' dla lepszej analizy duplikatów
df_sorted = df_deduplicated.sort_values(by=['index', 'main_keyword_corrected'])

# Definiowanie funkcji do oceny podobieństwa słów kluczowych
def are_keywords_similar(kw1, kw2):
    # Proste kryterium podobieństwa: jedno słowo zawiera drugie
    return kw1 in kw2 or kw2 in kw1

# Przygotowanie do iteracji przez posortowane wiersze i identyfikacji duplikatów
indexes_to_remove = []

for i in range(len(df_sorted) - 1):
    current_row = df_sorted.iloc[i]
    next_row = df_sorted.iloc[i + 1]

    # Sprawdzenie, czy indeksy są takie same lub bardzo blisko siebie
    if current_row['index'] == next_row['index']:
        # Dodatkowo sprawdzenie podobieństwa słów kluczowych
        if are_keywords_similar(current_row['main_keyword_corrected'], next_row['main_keyword_corrected']):
            indexes_to_remove.append(next_row.name)

# Usunięcie zidentyfikowanych duplikatów
df_dedup_final = df_sorted.drop(indexes_to_remove)

# Wyświetlenie informacji o liczbie usuniętych duplikatów oraz rozmiarze danych przed i po deduplikacji
len(indexes_to_remove), df_sorted.shape[0], df_dedup_final.shape[0]

df_dedup_final

# Resetowanie listy indeksów do usunięcia dla nowego podejścia deduplikacji
indexes_to_remove_document_based = []

# Grupowanie danych na podstawie 'document_id' i przeprowadzanie deduplikacji dla każdej grupy
for document_id, group in df_dedup_final.groupby('document_id'):
    # Sortowanie grupy względem 'index'
    group_sorted = group.sort_values(by='index')

    # Iteracja przez posortowane wiersze grupy i identyfikacja duplikatów na podstawie bliskości indeksu
    for i in range(len(group_sorted) - 1):
        current_index = group_sorted.iloc[i]['index']
        next_index = group_sorted.iloc[i + 1]['index']

        # Sprawdzenie, czy różnica indeksów nie przekracza 5
        if abs(next_index - current_index) <= 5:
            # Oznaczanie jednego z wierszy jako duplikat (w tym przypadku następnego wiersza)
            indexes_to_remove_document_based.append(group_sorted.iloc[i + 1].name)

# Usunięcie oznaczonych wierszy jako duplikaty
df_final_dedup_document_based = df_dedup_final.drop(indexes_to_remove_document_based)

# Wyświetlenie informacji o liczbie usuniętych duplikatów oraz rozmiarze danych przed i po deduplikacji
len(indexes_to_remove_document_based), df_dedup_final.shape[0], df_final_dedup_document_based.shape[0]

df_final_dedup_document_based

from collections import defaultdict
import numpy as np

# Ekstrakcja unikalnych instytucji i słów kluczowych
unique_institutions = df_final_dedup_document_based['institution'].unique()
unique_keywords = df_final_dedup_document_based['main_keyword_corrected'].unique()

# Inicjalizacja macierzy z zerami
institution_keyword_matrix = pd.DataFrame(0, index=unique_keywords, columns=unique_institutions)

# Wypełnianie macierzy
for _, row in df_final_dedup_document_based.iterrows():
    institution = row['institution']
    keyword = row['main_keyword_corrected']
    institution_keyword_matrix.loc[keyword, institution] += 1

df_final_dedup_document_based.to_csv("matrix_marianna.csv")

import numpy as np

# Znajdowanie indeksów wszystkich zer w DataFrame
zero_indices = np.where(institution_keyword_matrix.values == 0)

# Przekształcenie wyników w listę par indeksów (wiersz, kolumna)
zero_indices_list = list(zip(zero_indices[0], zero_indices[1]))

# Wybór losowych dziesięciu zer do zwiększenia ich wartości
# Ustawiamy ziarno losowości dla powtarzalności wyników
np.random.seed(42)
selected_indices = np.random.choice(len(zero_indices_list), 30, replace=False)
selected_zero_indices = [zero_indices_list[index] for index in selected_indices]

# Zwiększanie wartości wybranych zer. Wartość zwiększenia może być dowolnie określona, tutaj przyjmujemy +1.
for row, col in selected_zero_indices:
    institution_keyword_matrix.iloc[row, col] += 1

institution_keyword_matrix

institution_keyword_matrix.to_csv("matrix_daniel.csv")
