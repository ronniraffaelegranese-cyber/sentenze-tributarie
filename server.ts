import "dotenv/config";
import express from "express";
import path from "node:path";
import { Mistral } from "@mistralai/mistralai";

const app = express();
app.use(express.json());
app.use(express.static(path.join(process.cwd(), "public")));

const client = new Mistral({ apiKey: process.env.MISTRAL_API_KEY });

const LIVELLI = [
  "Corte di Giustizia (primo grado / giudice tributario)",
  "Corte d'Appello (Commissione territoriale / secondo grado)",
  "Corte di Cassazione (Sezioni Tributarie)",
  "Corte di Giustizia UE (CGUE)",
  "Corte Costituzionale",
];

const SYSTEM_PROMPT = `Sei un assistente specializzato in ricerca di sentenze in materia tributaria italiana ed europea.
Ricerchi sentenze in base all'anno e all'oggetto indicati dall'utente (es. "IRPEF", "IVA", "trust", "interessi dedotti").
Organizza sempre la risposta per livello giudiziario, in questo ordine:
1) Corte di Giustizia (primo grado / giudice tributario)
2) Corte d'Appello (Commissione territoriale / secondo grado)
3) Corte di Cassazione - Sezioni Tributarie
4) Corte di Giustizia UE (CGUE)
5) Corte Costituzionale
Per ciascun livello indica, se disponibili, i provvedimenti pertinenti all'anno e all'oggetto richiesti
(numero sentenza, data, massima sintetica). Se un livello non ha pronunce pertinenti, dichiaralo.
Avvisa chiaramente l'utente che i riferimenti vanno sempre verificati su fonti ufficiali
(banche dati, sito Cassazione, GURI, EUR-Lex, Corte Costituzionale), perché puoi commettere errori.`;

interface ChatBody {
  anno?: string;
  oggetto?: string;
  livello?: string;
  message: string;
}

app.post("/api/chat", async (req, res) => {
  const { anno, oggetto, livello, message } = req.body as ChatBody;
  if (!message || !process.env.MISTRAL_API_KEY) {
    return res.status(400).json({ error: "Messaggio mancante o MISTRAL_API_KEY non configurata" });
  }

  const livelloTxt = livello && livello !== "tutti" ? `Livello giudiziario richiesto: ${livello}.\n` : `Livelli da considerare: ${LIVELLI.join("; ")}.\n`;
  const userContent = `Anno: ${anno || "non specificato"}\nOggetto: ${oggetto || "non specificato"}\n${livelloTxt}\nDomanda: ${message}`;

  try {
    const response = await client.chat.complete({
      model: "mistral-small-latest",
      messages: [
        { role: "system", content: SYSTEM_PROMPT },
        { role: "user", content: userContent },
      ],
    });
    res.json({ reply: response.choices?.[0]?.message?.content ?? "" });
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: "Errore nella chiamata all'API Mistral" });
  }
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`Server avviato su http://localhost:${PORT}`);
});
