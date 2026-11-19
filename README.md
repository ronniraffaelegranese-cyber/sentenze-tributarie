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

## Workflow: riepilogo settimanale delle sentenze tributarie

Nella cartella [`workflow/`](workflow/) c'è un progetto Mistral Workflows che una volta distribuito ricerca sul web le novità della giurisprudenza tributaria italiana (Commissioni Tributarie, Cassazione, CGUE, Corte Costituzionale, circolari dell'Agenzia delle Entrate) e produce un riepilogo in italiano con le fonti.

Il workflow `riepilogo-sentenze-tributarie` accetta in input:

```json
{"giorni": 7, "temi": ["accertamento", "IVA", "IRPEF", "IRES", "riscossione", "penalità"]}
```

e restituisce data, finestra temporale, temi, riepilogo markdown ed elenco delle fonti citate.

Per lo sviluppo locale: `cd workflow && uv sync --all-packages && bun install`, poi imposta `MISTRAL_API_KEY` in `workflow/.env` e avvia il worker con `mistral dev`. Per la distribuzione gestita: `mistral apps deploy`. Una volta attivo, si può schedulare (es. ogni lunedì) da AI Studio o tramite l'API dei schedule di Mistral.
