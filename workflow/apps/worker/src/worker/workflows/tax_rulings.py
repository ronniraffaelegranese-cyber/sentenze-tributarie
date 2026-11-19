"""Riepilogo settimanale delle novità di giurisprudenza tributaria."""

from __future__ import annotations

from datetime import timedelta
from typing import Any

from pydantic import BaseModel, Field

import mistralai.workflows as workflows
from mistralai.workflows.plugins.mistralai import get_mistral_client

MODEL = "mistral-medium-latest"

TEMI_DEFAULT = [
    "accertamento",
    "IVA",
    "IRPEF",
    "IRES",
    "riscossione",
    "penalità",
]


class RiepilogoInput(BaseModel):
    giorni: int = Field(default=7, ge=1, le=90, description="Finestra temporale in giorni.")
    temi: list[str] = Field(default_factory=lambda: list(TEMI_DEFAULT))


class Fonte(BaseModel):
    url: str


class RiepilogoOutput(BaseModel):
    generato_il: str
    giorni: int
    temi: list[str]
    riepilogo: str
    fonti: list[Fonte]


def _tipo(entry: Any) -> str:
    return getattr(getattr(entry, "type", None), "value", getattr(entry, "type", ""))


def _prompt(giorni: int, temi: list[str]) -> str:
    return (
        f"Ricerca le novità degli ultimi {giorni} giorni in materia di "
        "giustizia tributaria italiana: sentenze delle Commissioni Tributarie, "
        "della Corte di Cassazione (Sezioni Tributarie), pronunce della Corte "
        "di Giustizia UE e della Corte Costituzionale, nonché circolari e "
        "risoluzioni rilevanti dell'Agenzia delle Entrate. "
        f"Concentrati su questi temi: {', '.join(temi)}. "
        "Cerca più volte con query diverse e poi redigi un report in italiano "
        "in markdown con, per ciascuna novità: numero e data della sentenza o "
        "del provvedimento, organo che l'ha emessa, principio affermato, "
        "rilevanza pratica per il contribuente e orientamento (favorevole o "
        "sfavorevole). Cita sempre le fonti. Se non trovi novità per un tema, "
        "dichiaralo. Ricorda che i riferimenti vanno verificati sulle fonti "
        "ufficiali."
    )


@workflows.activity(
    start_to_close_timeout=timedelta(minutes=5),
    retry_policy_max_attempts=2,
)
async def genera_riepilogo(giorni: int, temi: list[str]) -> tuple[str, list[str]]:
    """Interroga il web con un agente Mistral e restituisce testo e fonti."""
    client = get_mistral_client()
    response = await client.beta.conversations.start_async(
        model=MODEL,
        instructions=(
            "Sei un esperto di diritto tributario italiano incaricato di "
            "monitorare la giurisprudenza tributaria. Usi sempre il tool "
            "web_search per trovare notizie recenti e verificate."
        ),
        tools=[{"type": "web_search"}],
        inputs=[
            {
                "role": "user",
                "content": [{"type": "text", "text": _prompt(giorni, temi)}],
            }
        ],
        store=False,
    )
    testi: list[str] = []
    url_fonti: list[str] = []
    for output in response.outputs:
        if _tipo(output) != "message.output":
            continue
        for chunk in output.content:
            if _tipo(chunk) == "text" and chunk.text.strip():
                testi.append(chunk.text)
            elif _tipo(chunk) == "tool_reference" and chunk.url not in url_fonti:
                url_fonti.append(chunk.url)
    return "\n\n".join(testi), url_fonti


@workflows.workflow.define(
    name="riepilogo-sentenze-tributarie",
    workflow_display_name="Riepilogo Sentenze Tributarie",
    workflow_description=(
        "Ricerca sul web le novità della giurisprudenza tributaria italiana "
        "e produce un riepilogo con fonti."
    ),
)
class RiepilogoSentenzeTributarieWorkflow:
    @workflows.workflow.entrypoint
    async def run(self, input: RiepilogoInput) -> RiepilogoOutput:
        riepilogo, url_fonti = await genera_riepilogo(input.giorni, input.temi)
        return RiepilogoOutput(
            generato_il=workflows.workflow.now().date().isoformat(),
            giorni=input.giorni,
            temi=input.temi,
            riepilogo=riepilogo,
            fonti=[Fonte(url=url) for url in url_fonti],
        )
