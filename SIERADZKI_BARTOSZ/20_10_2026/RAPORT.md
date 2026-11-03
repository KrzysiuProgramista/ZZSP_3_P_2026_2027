# Lokalna analiza ocen z Librusa

## Cel i wykonanie

Aplikacja wczytuje lokalny plik `grades.csv` do DataFrame biblioteki Pandas.
Sprawdza obecność kolumn `date`, `subject`, `grade`, `description`,
interpretuje daty w formacie `YYYY-MM-DD`, usuwa skrajne spacje z nazw
przedmiotów i ocen oraz tworzy kolumnę `grade_base`.

Oceny z plusem lub minusem otrzymują wartość bazową bez tego znaku.
Niepoprawne daty stają się `NaT`, a wpisy niebędące ocenami pozostają bez
wartości bazowej. Program pokazuje lokalnie typy kolumn, pierwsze rekordy
i liczby brakujących lub nierozpoznanych wartości. Użytkownik powinien
sprawdzić i poprawić dane źródłowe po ekstrakcji PDF.

## Zaimplementowane zapytania

- `grades_below`: maska logiczna wybiera oceny bazowe niższe od progu.
- `grades_for_subject`: wyszukuje dosłowny fragment nazwy, ignorując wielkość liter.
- `grades_between_dates`: wybiera rekordy z zakresu obejmującego obie daty graniczne.
- `report`: łączy dokładne filtry kolumna/wartość operatorem AND.
  Nieznana kolumna powoduje czytelny `ValueError`; brak filtrów zwraca wszystkie rekordy.
- `summary_by_subject`: używa `groupby` i `agg` do obliczenia liczby rekordów
  oraz średniej ocen bazowych dla każdego przedmiotu.

Menu udostępnia wszystkie zapytania i inspekcję danych. W raporcie konsolowym
wartości liczbowe i daty są konwertowane do właściwych typów przed filtrowaniem.

## Dlaczego średnia nie jest oficjalną oceną semestralną

Średnia bazowa jest prostą średnią arytmetyczną rozpoznanych ocen.
Pomija wagi, znaczenie plusów i minusów, kategorie ocen, zasady uwzględniania
popraw oraz kryteria nauczyciela. Nie wyznacza więc oficjalnej oceny semestralnej.
Liczba rekordów obejmuje również wpisy takie jak nieprzygotowanie,
które nie wchodzą do średniej. Brak danych liczbowych daje brak średniej.

## Sprawdzenie działania

Testy korzystają wyłącznie z fikcyjnych rekordów. Obejmują wczytywanie,
brak wymaganych kolumn, nierozpoznane oceny i daty, filtrowanie poniżej progu,
wyszukiwanie bez rozróżniania wielkości liter, dosłowne traktowanie znaków,
granice przedziału dat, błędne zakresy, łączenie filtrów, nieznane kolumny,
podsumowanie i przejście przez menu.

Wynik uruchomienia zestawu: **12 testów zakończonych powodzeniem**.

Nie wykonano analizy rzeczywistego eksportu Librusa. Raport opisuje działanie
programu, nie zawiera identyfikatorów osoby ani jej rzeczywistych ocen.
Plik `fictional_grades.csv` służy wyłącznie do demonstracji.

## Prywatność i ograniczenia

Program analizuje dane lokalnie, bez wysyłania ich do usług internetowych.
Do oddania należy użyć kodu i tego raportu; ewentualna demonstracja powinna
korzystać wyłącznie z danych fikcyjnych. Prywatny PDF, `grades.csv`,
folder `private_work` i wyniki zawierające osobiste oceny pozostają na komputerze.
Plik `.gitignore` ogranicza ryzyko przypadkowego dodania nowych plików z danymi
do Git, ale nie usuwa danych już wcześniej śledzonych.

Inspektor PDF tworzy jedynie kandydatów na tabele. Układ eksportu może wymagać
ręcznego uporządkowania danych do czterech wymaganych kolumn.
