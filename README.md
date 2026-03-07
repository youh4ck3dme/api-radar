# API Radar MVP 🚀

API Radar je prvá MVP verzia nástroja na **objavovanie API endpointov zo serverových logov**. 
Cieľom je automaticky získať prehľad o tom, **aké endpointy sa na serveri reálne používajú**, vrátane potenciálne nezdokumentovaných alebo zabudnutých API ciest.

## Aktuálne MVP obsahuje

### 1. Log scanner
Python skript číta Nginx access logy a priebežne z nich extrahuje API requesty.

### 2. Endpoint parser
Zo záznamov sa spracujú:
- HTTP metóda
- path
- počet výskytov

### 3. Ukladanie dát
Výsledky sa ukladajú do SQLite databázy ako základná endpoint inventory vrstva.

### 4. Backend API
FastAPI endpoint sprístupňuje zozbierané dáta pre dashboard alebo ďalšie spracovanie.

### 5. Dashboard
React dashboard zobrazuje objavené endpointy a ich aktivitu v reálnom čase.

### 6. Docker deployment
Projekt je pripravený na spustenie na VPS cez Docker Compose.

## Overené v MVP
Testovací scenár potvrdil, že systém vie:
- načítať logy
- rozpoznať endpointy
- spočítať výskyty
- zobraziť ich cez API a dashboard

Príklad výsledku:
```bash
GET /api/users -> 2
POST /api/login -> 1
GET /api/dashboard/stats -> 1
```

## Čo je ďalší krok
Ďalšia fáza MVP bude zameraná na:
- porovnanie observed vs known endpoints
- detekciu shadow API
- základné risk scoring pravidlá
- filtrovanie interných / verejných endpointov
