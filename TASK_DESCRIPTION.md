Projekt 2018
------------

**Projekty należy przygotować indywidualnie.**

**Zmiany 29.05:**

1.  funkcje root i new dostają identyfikator nowego pracownika jako argument, nie zwracają argumentów.
2.  funkcje read/update pozwalają pracownikowi zmieniać dane o sobie
3.  funkcja remove usuwa wraz z pracownikiem podanym jako argument całe poddrzewo jego podwładnych
4.  komentarze do modelu konceptualnego powinny zawierać zwięzłą informację  o  sposobie implementacji funkcji API.

**Zmiany 2.06**

1.  wywołania funkcji new w czasie pierwszego uruchomienia będą miały argument admin ustawiony na pracownika będącego w korzeniu hierarchii (w szczególności oznacza to, że w trakcie inicjalizacji nie trzeba mieć już zbudowanego indeksu main-memory).
2.  baza danych oraz użytkownik init będą istnieli w momencie pierwszego uruchomienia bazy, należy utworzyć użytkownika app, nadać mu odpowiednie uprawnienia i hasło (moduł pgcrypto będzie dostępny), hasło użytkownika podanego jako argument `<admin>`  powinno być weryfikowane przy wywołaniach funkcji API i nie należy trzymać ich plaintextem.

**Zmiany 3.06**

 Poprawiłem kilka drobnych niejednoznaczności, pojawił się prosty test, identyfikatory pracowników są typu number (https://www.json.org/), dopuściłem możliwość zwracania krótkiej informacji przydatnej w debugowaniu.

Wprowadziłem ograniczenie na rozmiar danych pracownika (<100 znaków).

**Q&A:**

Co należy zwracać jeżeli zapytamy sie o dane użytkownika, który nie istnieje?  
`{"status": "OK", "data": "Null"}` czy `{"status": "ERROR"}`?

W tej sytuacji niemożliwe jest zwrócenie danych tego użytkownika więc należy zwracać komunikat o błędzie:

`{"status": "ERROR"}`

**C****o będzie oceniane?**
---------------------------

**Model konceptualny -** powinien składać się z diagramu E-R oraz komentarza zawierającego więzy pominięte w diagramie, powinien zawierać opis uprawnień użytkowników init i app. Komentarz powinien dodatkowo zawierać zwięzłą informację w jaki sposób zostaną zaimplementowane poszczególne funkcje API.

**Model fizyczny -** powinien być plikiem sql nadającym się do czytania (i oceny) przez człowieka. Powinien zawierać definicję wszystkich  tabel, więzów, indeksów, kluczy, akcji referencyjnych, funkcji, perspektyw i wyzwalaczy, a także użytkownika app z odpowiednimi uprawnieniami.  Nie jest niezbędne wykorzystanie wszystkich tych udogodnień, ale tam, gdzie pasują, powinny być wykorzystywane.

**Dokumentacja** projektu  - ma się składać z pojedynczego pliku pdf zawierającego ostateczny model konceptualny oraz dokładne instrukcje, jak należy aplikację uruchomić. Dokumentacja ma dotyczyć tego, co jest zaimplementowane; w szczególności, nie można oddać samej dokumentacji, bez projektu.

**Program -** oceniany będzie  kod źródłowy oraz poprawność i efektywność działania.

Oddajemy archiwum zawierające wszystkie pliki źródłowe programu, dokumentację w pliku pdf, model fizyczny w pliku sql oraz polecenie typu make (ew. skrypt run.sh, itp.) umożliwiające kompilację i uruchomienie systemu.

Projekt: System Zarządzania Korporacją X.
=========================================

Twoim zadaniem jest zaimplementowanie zdefiniowanego poniżej API.

Ze względu na to, że interesuje nas tematyka baz danych przedmiotem projektu jest stworzenie wersji deweloperskiej systemu, w której wywołania API będą wczytywane z dostarczonego pliku.

#### Opis problemu

W korporacji X wprowadzono nową organizację podległości służbowej. Od tej pory każdy z pracowników (za wyjątkiem prezesa) ma dokładnie jednego  bezpośredniego przełożonego. Hierarchia podległości ma strukturę drzewa. w którego korzeniu znajduje się prezes. W związku z nową organizacją potrzebny jest system bazodanowy. Podjęto już niektóre decyzje projektowe: dane mają zostać zapamiętane w relacyjnej bazie danych i przetwarzane za pomocą zdefiniowanego poniżej API.

#### Technologie

System Linux. Język programowania dowolny – wybór wymaga zatwierdzenia przez prowadzącego pracownię - zalecany język python.  Baza danych – postgresql w wersji >=9.1.23. Testy będą przeprowadzane na komputerze z Ubuntu 16.04, postgresql 9.5.12.

Twój program po uruchomieniu powinien przeczytać ze standardowego wejścia ciąg wywołań funkcji API, a wyniki ich działania wypisać na standardowe wyjście.

Wszystkie dane powinny być przechowywane w bazie danych, efekt działania każdej funkcji modyfikującej bazę, dla której wypisano potwierdzenie wykonania (wartość OK) powinien być utrwalony. Program będzie uruchamiany wielokrotnie z następującymi parametrami:

\- pierwsze uruchomienie - program wywołany z parametrem --init   -  wejście zawiera w pierwszym wierszu wywołanie funkcji open z następującymi danymi login: init, password: qwerty, w drugim wierszu wywołanie funkcji root, a następnie wyłącznie wywołania wywołania funkcji new **z argumentem  `<admin>` ustawionym na pracownika będącego w korzeniu hierarchii.**  Można założyć, że przed uruchomieniem z parametrem --init baza nie zawiera jakichkolwiek tabel.

\- kolejne uruchomienia - wejście zawiera w pierwszym wierszu wywołanie funkcji open z następującymi danymi  login: app, password: qwerty, a następnie wywołania dowolnych  funkcji API za wyjątkiem open i root.

Przy pierwszym uruchomieniu program powinien utworzyć wszystkie niezbędne elementy bazy danych (tabele, więzy, funkcje wyzwalacze, użytkownik app z odpowiednimi uprawnieniami) zgodnie z przygotowanym przez studenta modelem fizycznym. Baza nie będzie modyfikowana pomiędzy kolejnymi uruchomieniami. Program nie będzie miał praw do tworzenia i zapisywania jakichkolwiek plików. **Program będzie mógł czytać pliki z bieżącego katalogu.**

#### Format pliku wejściowego

Każda linia pliku wejściowego zawiera obiekt JSON ([http://www.json.org/json-pl.html](http://www.json.org/json-pl.html)). Każdy z obiektów opisuje wywołanie jednej funkcji API wraz z argumentami.

Przykład: obiekt `{ "function": { "arg1": "val1", "arg2": "val2" } }` oznacza wywołanie funkcji o nazwie function z argumentem arg1 przyjmującym wartość "val1" oraz arg2 – "val2".

W pierwszej linii wejścia znajduje się wywołanie funkcji open z argumentami umożliwiającymi nawiązanie połączenia z bazą danych.

#### Format wyjścia

Dla każdego wywołania wypisz **w osobnej linii** obiekt JSON zawierający status wykonania funkcji OK/ERROR oraz tabelę data zawierającą wynik działania tej funkcji wg specyfikacji.

Format zwracanych danych (dla czytelności zawiera zakazane znaki nowej linii):

```json
{   
  "status":"OK",  
  "data": \[ "v1", "v2" \],  
  "debug": "..."
}
```

Tabela data zawiera wszystkie wynikowe krotki. Każda krotka to dokładnie jedną wartość atrybutu podanego w specyfikacji. Dopuszczalna jest dodatkowa para o kluczu debug i wartości typu string  z ew. informacją przydatną w debugowaniu  (jest ona całkowicie dobrowolna i będzie ignorowana w czasie testowania, powinna mieć niewielki rozmiar).

#### Przykładowe wejście i wyjście

Pierwsze uruchomienie (z parametrem --init): 

```json
{ "open": { "database": "student", "login": "init", "password": "qwerty"}}  
{ "root": { "secret": "qwerty", "newpassword": "qwerty", "data": "dane prezesa", "emp":0} }  
{ "new": { "admin": 0, "passwd": "123456", "data":"dane wiceprezesa", "newpasswd":"qwerty", "emp1":0, "emp":1 } }  
{ "new": { "admin": 0, "passwd": "qwerty", "data":"dane wiceprezesa", "newpasswd":"qwerty", "emp1":0, "emp":1 } }
```

Oczekiwane wyjście

```json
{"status": "OK"}  
{"status": "OK"}  
{"status": "ERROR", "debug":"nieprawidłowe hasło"}  
{"status": "OK"}
```

#### Format opisu API

`<function> <arg1> <arg2> … <argn>` // nazwa funkcji oraz nazwy jej argumentów

// opis działania funkcji

// opis formatu wyniku: lista atrybutów wynikowych tabeli data

#### Nawiązywanie połączenia i definiowanie danych użytkowników bazy.

Każde z poniższych wywołań powinno zwrócić obiekt JSON zawierający status wykonania OK/ERROR.

```
open <database> <login> <password>
// przekazuje dane umożliwiające podłączenie Twojego programu do bazy - nazwę bazy, login oraz hasło, wywoływane dokładnie jeden raz, w pierwszej linii wejścia
// zwraca status OK/ERROR w zależności od tego czy udało się nawiązać połączenie z bazą 
  
root <secret> <newpassword> <data> <emp> // tworzy nowego pracownika **o unikalnym indentyfikatorze <emp>** z hasłem <newpassword>, jest to jedyny pracownik, który nie ma przełożonego, argument <secret> musi być równy 'qwerty'   
// zwraca status OK/ERROR
```

#### Operacje

Każde z poniższych wywołań powinno zwrócić obiekt JSON zawierający status wykonania OK/ERROR, oraz ew. tabelę data zawierającą kolejne krotki wyniku wg specyfikacji poniżej.

  
```
new <admin> <passwd> <data> <newpasswd> <emp1> <emp> dodawanie nowego pracownika o identyfikatorze <emp> z danymi <data> i hasłem dostępu <newpasswd>, pracownik <emp> staje się podwładnym pracownika <emp1>, <admin> musi być pracownikiem o identyfikatorze <emp1> lub jego bezpośrednim lub pośrednim przełożonym, <passwd> to hasło pracownika <admin>  
// nie zwraca danych  
  
remove <admin> <passwd> <emp> usuwanie pracownika <emp> wraz z wszystkimi pracownikami, którzy mu (bezpośrednio lub pośrednio) podlegają. <admin> musi być bezpośrednim lub pośrednim przełożonym pracownika <emp> (zauważ, że oznacza to , że nie da się usunąć prezesa), <passwd> to hasło pracownika <admin>  
// nie zwraca danych  
  
child <admin> <passwd> <emp>  zwraca identyfikatory wszystkich pracowników bezpośrednio podległych <emp>, <admin> może być dowolnym pracownikiem,, <passwd> to hasło pracownika <admin>  
// tabela data powinna zawierać kolejne wartości <emp>  
  
parent <admin> <passwd> <emp> zwraca identyfikator bezpośredniego przełożonego <emp>, <admin> może być dowolnym pracownikiem, <passwd> to hasło pracownika <admin>  
// tabela data powinna zawierać dokładnie jedną wartość <emp>  
  
ancestors <admin> <passwd> <emp> zwraca identyfikatory wszystkich pracowników, którym <emp> pośrednio lub bezpośrednio podlega, <admin> może być dowolnym pracownikiem, <passwd> to hasło pracownika <admin>  
// tabela data powinna zawierać kolejne wartości <emp>  
  
descendants <admin> <passwd> <emp> zwraca identyfikatory wszystkich pracowników bezpośrednio lub pośrednio podległych <emp>, <admin> może być dowolnym pracownikiem, <passwd> to hasło pracownika <admin>  
// tabela data powinna zawierać kolejne wartości <emp>  
  
ancestor <admin> <passwd> <emp1> <emp2> sprawdza czy <emp1> bezpośrednio lub pośrednio podlega <emp2>, <admin> może być dowolnym pracownikiem, <passwd> to hasło pracownika <admin>  
// tabela data powinna zawierać dokładnie jedną wartość: true albo false  
  
read <admin> <passwd> <emp> // zwraca dane <data> pracownika <emp>, <admin> musi być musi być pracownikiem <emp> lub bezpośrednim lub pośrednim przełożonym pracownika <emp>, <passwd> to hasło pracownika <admin>  
// tabela data powinna dokładnie jedną wartość <data>  
  
update <admin> <passwd> <emp> <newdata> // zmienia dane pracownika <emp> na <newdata>, <admin> musi być pracownikiem <emp> lub bezpośrednim lub pośrednim przełożonym pracownika <emp>, <passwd> to hasło pracownika <admin>  
// nie zwraca danych
```
Dane pracowników `<data>` będą miały ograniczony rozmiar do 100 znaków (nie trzeba tego sprawdzać).

#### Grupy (swój numer grupy można znaleźć w arkuszu z wynikami ćwiczeń).

Założ, że funkcje child, parent, update, read wywoływane są dość często. Częstość wywołań funkcji: ancestor, ancestors, descendants, new, remove zależy od przypisanej danemu studentowi grupy.

**Grupa 0**

Bardzo często wywoływana jest funkcja ancestor, stosunkowo często wywoływane są funkcje ancestors, descendants,  po wczytaniu danych na początku testu stan zatrudnienia zmienia się bardzo rzadko (new/remove).

Niektóre wierzchołki położone są na znacznej głębokości.

**Grupa 1**

Firma dynamicznie rozwija się, bardzo często dodawani są nowi pracownicy (new), stosunkowo często wywoływane są też funkcje ancestor, ancestors, descendants. Funkcja remove wywoływana jest rzadko.

Głębokość hierarchii nie przekracza 7 poziomów.

Ostatnia modyfikacja: środa, 6 czerwiec 2018, 16:30
