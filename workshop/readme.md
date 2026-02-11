# Basic Frågor

## Vad gör FastAPI?

- Det är webbramverk som byyga APIer. Det hanterar HTTPS- request, validering.

## Vad gör Pydantic ?

- Kollar att data är korrekt(Automatisk validering)

## Vad gör psycopg3?

- Det är python bibliotek som låter oss att arbeta med PostgreSQL-databaser.
- Du använder psycopg3 för att:
  - Hämta data från PostgreSQL till dina data pipelines
  - Lagra processad data i databasen
  - Köra ETL-processer (Extract, Transform, Load)
  - Integrera databaser med dina FastAPI-endpoints

# Var “försvinner” datan mellan request → databas ?

- Data försvinner inte, men den transformeras mellan olika format och platser. Om du inte sparar i databasen så finns data bara i RAM-minnet och försvinner när servern stängs av. Därför vi använder postgreSQl och psycop3 för att göra data blir permanent.
  - Request (JSON) → FastAPI tar emot
  - Pydantic validerar och skapar Python-objekt
  - FastAPI-route processar logik
  - Psycopg3 översätter Python-data till SQL-parametrar
  - PostgreSQL tar emot och sparar

# Transaction

## Vad betyder “Allt eller inget”, vad tror du?

- Det är en ACID principens Atomcity, En transaction antingen lyckas helt eller misslyckas helt.

## Vad händer om någotkraschar mitt i? Konsekvens?

- Om något kraschar innan kommit körs en automatisk rollback, alla ändringar sedan transaktion började ångras. Databasen återgår till sitt tidigare tillstånd

## Varför är .transaction() viktigare än .commit()

- .transaction() hanterar hela livscyckeln. Medan .commit() är bara ett kommando, du måste hantera fel och rollback manuell.

# Data - types

## Vad är ett Python-objekt?

- En instans av en klass med attribut och metoder. Ex: pydantic-modell eller en dictionary

## Vad förstår PostgreSQL?

- Det förstår SQL datatyper : integer,varchar,bool,decimal,JSONB, TIMESTAMP

## Varför måste vi “översätta” data?

- Python och PostgreSQL använder olika datarepresentationer. Psycopg3 konverterar:
  - Python dict → PostgreSQL JSONB
  - Python datetime → PostgreSQL TIMESTAMP
  - Python int → PostgreSQL INTEGER

# Data Structure

## När är JSONB bra?

- Flexibel, varierad data (metadata, inställningar), Snabb prototyping, Data som inte behöver joins, Semi-strukturerad data.

## När är kolumner bättre?

- Data som söks/filtreras ofta, Relationer mellan tabeller (foreign keys), Dataintegritet krävs (constraints), Strukturerad, förutsägbar data

## Varför har vi “raw tables”?

- Bevara källdata, Möjliggör ombearbetning, Audit trail, Separation mellan ingestion och transformation

# Code & Logic

## Om vi skickar product:ProductSchema till databasen, vad är det? Fungerar det? (varför-/inte)

- Nej, det fungerar inte direkt! ProductSchema är ett Pydantic-objekt. Du måste:
  - extrahera individuella värden: product.name, product.price
  - Eller konvertera till dict: product.model()
  - Eller till JSON: product.model_json()

## Vad är SQL och vad är parametrar?

- SQL: Själva query-strängen (INSERT INTO products (name) VALUES (%s))
- Parametrar: Värdena som fylls i säkert (("Pizza",))

## Varför är tuples viktiga? (.execute())

- Psycopg3 kräver parametrar som tuples för att:
  - Säkerställa rätt ordning
  - Hantera multipla värden
  - Förhindra injection
  - Matcha SQL-placeholders

# Problems

## Vad är skillnaden på Python-fel, psycopg-fel och SQL-fel

- Python-fel:TypeError, ValueError, AttributeError. Uppstår i din Python-kod
- Psycopg-fel: ConnectionError, InterfaceError Problem med databasanslutning eller adapter
- SQL-fel: IntegrityError, DataError, ProgrammingError. Problem i databasen (constraint violations, syntax errors)

## postgresql://postgres:mypassword@localhost:5432/food_db
