import pandas as pd
import pytest

def _validate_column(df: pd.DataFrame, column: str):
    """Zgłasza ValueError, jeśli kolumna nie znajduje się w df.columns[span_0](start_span)[span_0](end_span)."""
    if column not in df.columns:
        raise ValueError(f"Kolumna '{column}' nie istnieje w DataFrame.")

def filter_between(df: pd.DataFrame, column: str, low, high) -> pd.DataFrame:
    """Zwraca wartości włącznie z podanym zakresem[span_1](start_span)[span_1](end_span)."""
    _validate_column(df, column)
    return df[df[column].between(low, high, inclusive='both')]

def filter_by_values(df: pd.DataFrame, column: str, values: list) -> pd.DataFrame:
    """Wykorzystuje metodę Series.isin(values) do filtrowania[span_2](start_span)[span_2](end_span)."""
    _validate_column(df, column)
    return df[df[column].isin(values)]

def top_n(df: pd.DataFrame, column: str, n: int) -> pd.DataFrame:
    """Zwraca n największych wierszy na podstawie sortowania[span_3](start_span)[span_3](end_span)."""
    _validate_column(df, column)
    return df.sort_values(by=column, ascending=False).head(n)


# --- Testy jednostkowe pytest[span_4](start_span)[span_4](end_span) ---

@pytest.fixture
def sample_data():
    return pd.DataFrame({
        'quantity': [3, 25, 5, 12, 8, 40],
        'region': ['North', 'North', 'South', 'North', 'East', 'West']
    })

def test_filter_between(sample_data):
    result = filter_between(sample_data, 'quantity', 5, 12)
    assert len(result) == 2
    assert list(result['quantity']) == [5, 12]
    
    with pytest.raises(ValueError):
        filter_between(sample_data, 'nieistniejaca_kolumna', 1, 10)

def test_filter_by_values(sample_data):
    result = filter_by_values(sample_data, 'region', ['South', 'East'])
    assert len(result) == 2
    assert list(result['region']) == ['South', 'East']
    
    with pytest.raises(ValueError):
        filter_by_values(sample_data, 'brak_kolumny', ['North'])

def test_top_n(sample_data):
    result = top_n(sample_data, 'quantity', 2)
    assert len(result) == 2
    assert list(result['quantity']) == [40, 25]
    
    with pytest.raises(ValueError):
        top_n(sample_data, 'test_kolumny', 2)

# Chellange

def report(df: pd.DataFrame, **filters) -> pd.DataFrame:
    """Tworzy raport akceptujący dowolną liczbę filtrów column=value[span_0](start_span)[span_0](end_span)."""
    
    # 1. Walidacja każdej żądanej kolumny[span_1](start_span)[span_1](end_span)
    for column in filters.keys():
        if column not in df.columns:
            # Zgłoszenie błędu ValueError w przypadku nieznanej kolumny[span_2](start_span)[span_2](end_span)
            raise ValueError(f"Nieznana kolumna: '{column}'")

    filtered_df = df.copy()
    
    # 2. Aplikacja wszystkich filtrów (logika AND)[span_3](start_span)[span_3](end_span)
    for column, value in filters.items():
        # Wiersz musi pasować do każdej dostarczonej pary column=value[span_4](start_span)[span_4](end_span)
        filtered_df = filtered_df[filtered_df[column] == value]

    # 3. Wypisanie dopasowanych wierszy / całkowitej liczby wierszy[span_5](start_span)[span_5](end_span)
    print(f"Matched rows / Total rows: {len(filtered_df)} / {len(df)}")

    # 4. Wypisanie całkowitej wartości dopasowanej sprzedaży[span_6](start_span)[span_6](end_span)
    # Definicja całkowitej wartości: quantity * unit_price[span_7](start_span)[span_7](end_span)
    if 'quantity' in df.columns and 'unit_price' in df.columns:
        total_value = (filtered_df['quantity'] * filtered_df['unit_price']).sum()
    else:
        total_value = 0.0
    print(f"Total value of matching sales: {total_value:.2f}")

    # 5. Zwrócenie przefiltrowanego obiektu DataFrame[span_8](start_span)[span_8](end_span)
    return filtered_df
