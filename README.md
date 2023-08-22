# Opetussovellus

Sovelluksella toteutetaan verkkokursseja ja niihin liittyviä automaattisesti tarkastettavia monivalintatehtäviä. Käyttäjä on joko opettaja tai oppilas. 

Kaikki käyttäjät voivat
- [x] luoda tunnuksen sekä kirjautua sisään ja ulos
- [x] nähdä olemassa olevat kurssit

Opettaja voi
- [x] luoda kurssin
- [ ] poistaa kurssin
- [x] poistaa sivun kurssilta
- [x] lisätä kurssille materiaalia ja muokata sitä (tällä hetkellä vain tekstiä)
- [x] lisätä tehtäviä
- [ ] muokata tehtäviä
- [x] nähdä kurssilla olevat opiskelijat ja heidän ratkaisemansa tehtävät

Opiskelija voi
- [x] ilmoittautua kurssille ja poistua kurssilta
- [x] lukea kurssin materiaalia (tällä hetkellä kaikki voivat)
- [x] tehdä tehtäviä ja nähdä mitkä tehtävät on ratkaissut

## Huom.

Sovellusta pystyy ainakin toistaiseksi käyttämään **vain paikallisesti.** Ohjeet tähän ovat alla.

## Käynnistysohjeet

- **Kloonaa** tämä repositorio koneellesi
- Siirry repositorion **juurikansioon**
- Luo **.env**-tiedosto
- Lisää .env-tiedostoon rivit **DATABASE_URL=[tietokannan paikallinen osoite]** ja **SECRET_KEY=[salainen avain]**
- Luo **virtuaaliympäristö** komennolla `python3 -m venv venv`
- Aktivoi virtuaaliympäristö: `source venv/bin/activate`
- Lataa sovelluksen **riippuvuudet:** `pip install -r requirements.txt`
- Määritä **tietokannan** skeema: `psql < schema.sql`
- **Käynnistä** sovellus: `flask run`
