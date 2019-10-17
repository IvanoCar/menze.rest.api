# MenzeAPI dokumentacija

v01. *REST API for Menze desktop application*.

## Uvod

Menze projekt je softversko rješenje koje omogućava studentima (sveučilišta u Rijeci i drugih) pregled jelovnika studentskih restorana u realnom vremenu. *Ovo je primjer moguće implementacije sustava i on nije u produkciji*.

REST API se nalazi na adresi <https://menzeapi.herokuapp.com/> . 

Više o projektu: <https://github.com/IvanoCar/menze.rest.api>

Primjer klijent aplikacije administratora kuhinje: <https://github.com/IvanoCar/menze.desktop>

Ova verzija API omogućuje rad s korisnicima (administratori restorana), restoranima i hranom. 

## Spajanje na sučelje

Za spajanje na sučelje potrebno je imati *client_id* i pripadajući set API ključeva koji su različiti ovisno radi li se o pregledu podataka ili uređivanju podataka. Ovi parametri se šalju kao *header* requesta. Obvezni headeri kod **svakog** request-a su:

```json
{
    "client_id": "VašID",
    "api-key": "GET/EDIT ključ",
    "content-type": "application/json"
}
```

## Popis resursa

```
GET: /health
```

vraća stanje API u formatu:

```json
{
    "status": "running",
    "version": 1.1
}
```

Klijent može pregledavati i uređivati samo one korisnike i restorane koji mu pripadaju (po *client_id*)

#### Pregled korisnika:

```
GET: /users
```

#### Stvaranje novog korisnika:

```
POST: /users
```

Parametri u JSON formatu:

```json
{
    "restaurant_id": "ID",
    "username": "USERNAME",
    "password": "PASSWORD"
}
```

#### Pregled podataka određenog korisnika

```
GET: /users/:user_id
```

**Uređivanje podataka određenog korisnika**

```
PUT: /users/:user_id
```

Parametri u JSON formatu:

```json
{
    "restaurant_id": "ID",
    "username": "USERNAME",
    "password": "PASSWORD"
}

```

#### Brisanje korisnika

```
DELETE: /users/:user_id

```



#### Pregled restorana

```
GET: /restaurants

```

#### Stvaranje novog restorana

```
POST: /restaurants

```

Parametri u JSON formatu:

```json
{
    "name": "IME",
    "address": "ADRESA",
    "city": "GRAD",
    "postal_code": 00000
}

```

#### Pregled podataka određenog restorana

```
GET: /restaurants/:restaurant_id

```

**Uređivanje podataka određenog restorana**

```
PUT: /restaurants/:restaurant_id

```

Parametri u JSON formatu:

```json
{
    "name": "IME",
    "address": "ADRESA",
    "city": "GRAD",
    "postal_code": 00000
}

```

#### Brisanje restorana (s pripadajućom hranom i statistikom)

```
DELETE: /restaurants/:restaurant_id

```

#### Pregled hrane određenog restorana

```
GET: /restaurants/:restaurant_id/food

```

#### Uređivanje hrane određenog restorana

```
PUT /restaurants/:restaurant_id/food

```

Hrana se mora formirati u format JSON te poslati na sljedeći način: 

```json
{
    "food_data": {}
}

```

Dakle *value* vrijednost je JSON.

#### Pregled podataka o više restorana istovremeno

```
GET: /retaurants/multiple/:restaurant_ids

```

ID-evi restorana se odvajaju znakom **+**, npr:

```
GET: /retaurants/multiple/ID001+ID002+ID010

```

#### Pregled podataka o hrani više restorana istovremeno

```
GET: /retaurants/multiple/:restaurant_ids/food

```

ID-evi restorana se odvajaju znakom **+**, npr:

```
GET: /retaurants/multiple/ID001+ID002+ID010/food

```

#### Pregled statistike restorana

```
GET: /retaurants/multiple/:restaurant_id/analytics

```

Ažuriranje statistike ide na način da se automatski ažurira nakon ažuriranje hrane. Jedina statistika koja se može pregledati je koliko puta dnevno su podatci ažurirani.

## Return vrijednosti

Kod ažuriranja vrijednosti vraća se ažurirani objekt, u slučaju brisanja ne vraća se ništa. Status kodovi koji se vraćaju po REST standardima opisuju povratnu vrijednost.

U slučaju greške, u return vrijednosti uz pripadajući status kod dostupan je opis greške u formatu:

```json
{
    "error":"KRATAK OPIS GREŠKE",
    "message": "OPIS"
}

```

ili u slučaju dohvaćanja više restorana ili hrane:

```json
{
    "has_errors": True,
    "errors": {
        "count": 2,
        "restaurants": [
            "ID001",
            "ID005"
        ]
    },
    "results": [ {} ]
}

```

s tim da će uspješno dohvaćeni podati biti unutar "results" liste. Rezultati kod svakog uspješnog dohvaćanja će se enkapsulirati na način:

```json
{
    "results": [ {}, {} ]
}

```

Kod dohvaćanja hrane jednog restorana:

```json
{
    "results": {}
}

```

