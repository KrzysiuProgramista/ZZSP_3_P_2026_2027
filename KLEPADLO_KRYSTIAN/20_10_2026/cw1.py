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
