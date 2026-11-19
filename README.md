# Ricerca Sentenze Tributarie

App web minimale per la ricerca di sentenze in materia tributaria (per anno e oggetto) tramite chat, basata sull'API Mistral (modello `mistral-small-latest`) con l'SDK ufficiale TypeScript `@mistralai/mistralai`.

Livelli giudiziari coperti:
- Corte di Giustizia (primo grado / giudice tributario)
- Corte d'Appello (secondo grado)
- Cassazione — Sezioni Tributarie
- Corte di Giustizia UE (CGUE)
- Corte Costituzionale

## Installazione

```bash
npm install
```

Configura la chiave API (resta solo sul server, mai esposta al client):

```bash
cp .env.example .env
# poi inserisci la tua MISTRAL_API_KEY in .env
```

## Esecuzione locale

```bash
npm start        # http://localhost:3000
# oppure in modalità sviluppo con ricarica automatica:
npm run dev
```

## Struttura

- `server.ts` — server Express: serve la UI e chiama l'API Mistral con l'SDK TypeScript; `MISTRAL_API_KEY` resta nel backend (`.env`).
- `public/index.html` — interfaccia chat minimale con filtri per anno, oggetto e livello giudiziario.
- `tsconfig.json` — configurazione TypeScript.

## Note

I riferimenti alle sentenze proposti dal modello vanno sempre verificati sulle fonti ufficiali.
