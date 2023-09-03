# Opetussovellus

Sovelluksella toteutetaan verkkokursseja ja niihin liittyviä automaattisesti tarkastettavia monivalintatehtäviä. Käyttäjä on kirjautuneena joko opettaja tai oppilas.

Kaikki käyttäjät voivat
- luoda ja poistaa tunnuksen sekä kirjautua sisään ja ulos
- nähdä olemassa olevat kurssit sisältöineen.

Opettaja voi
- luoda ja poistaa kurssin
- lisätä, poistaa ja muokata kurssin sivuja
- lisätä ja poistaa tehtäviä
- siirtää tehtävän eri sivulle
- nähdä kurssilla olevat opiskelijat ja heidän ratkaisemansa tehtävät.

Opiskelija voi
- ilmoittautua kurssille ja poistua kurssilta
- tehdä tehtäviä ja nähdä mitkä tehtävät on ratkaissut.

Sovellus on testattavissa vain paikallisesti. Ohjeet tähän ovat alla.

## Käynnistysohjeet

- **Kloonaa** tämä repositorio koneellesi.
- Siirry repositorion **juurikansioon**.
- Luo **.env**-tiedosto.
- Lisää .env-tiedostoon rivit **DATABASE_URL=[tietokannan paikallinen osoite]** ja **SECRET_KEY=[salainen avain]**
- Luo **virtuaaliympäristö** komennolla `python3 -m venv venv`
- Aktivoi virtuaaliympäristö: `source venv/bin/activate`
- Lataa sovelluksen **riippuvuudet:** `pip install -r requirements.txt`
- Määritä **tietokannan** skeema: `psql < schema.sql`
- **Käynnistä** sovellus: `flask run`
