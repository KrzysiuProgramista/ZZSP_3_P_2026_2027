import pandas as pd
import numpy as np


def quality_report(df):
    report = pd.DataFrame({
        'dtype': df.dtypes.astype(str),
        'missing': df.isna().sum(),
        'missing_%': (df.isna().mean() * 100).round(2),
        'unique': df.nunique()
    })
    report[['min', 'max', 'mean', 'outliers']] = np.nan
    for col in df.select_dtypes(include='number'):
        s = df[col]
        report.loc[col, ['min', 'max', 'mean']] = [s.min(), s.max(), s.mean()]
        report.loc[col, 'outliers'] = ((s - s.mean()).abs() > 3 * s.std()).sum()
    print('\nDuplicate rows:', df.duplicated().sum())
    print('Constant columns:', report.index[report['unique'] == 1].tolist())
    print('Possible IDs:', report.index[(report['unique'] == len(df)) & (report['missing'] == 0)].tolist())
    print('Consider category:', [c for c in df.select_dtypes(include=['object', 'string'])
                                 if df[c].nunique() < 20])
    print(report.to_string())
    return report


df = pd.read_csv('/Users/barteksieradzki/ZZSP_3_P_2026_2027/SIERADZKI_BARTOSZ/27_10_2026/dirty_data.csv')
df['price'] = pd.to_numeric(df['price'].astype('string').str.replace(' ', '', regex=False), errors='coerce')
df['quantity'] = pd.to_numeric(df['quantity'], errors='coerce').astype('Int64')
df['order_date'] = pd.to_datetime(df['order_date'], format='%d.%m.%Y', errors='coerce')

print('DATASET 1: SALES')
sales_report = quality_report(df)
sales_report.to_csv('challenge2_quality_report.csv', encoding='utf-8-sig')
print('Repeated IDs:', df.duplicated('id').sum())
print('Negative quantities:', (df['quantity'] < 0).sum())
print('Future dates:', (df['order_date'] > pd.Timestamp.today()).sum())

print('\nDATASET 2: EMPLOYEES')
quality_report(pd.DataFrame({'id': [1, 2, 3], 'salary': [3000, 4000, 5000], 'city': ['Lodz'] * 3}))

print('\nDATASET 3: GRADES')
quality_report(pd.DataFrame({'grade': [3, 3, None, 5], 'subject': ['Math', 'Math', None, 'English']}))
