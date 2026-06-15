from __future__ import annotations

import re
import unicodedata
from collections import Counter
from pathlib import Path

from pypdf import PdfReader


PDF_PATH = Path("materials/pdfcoffee.com_livro-fenomenos-de-transporte-birdpdf-pdf-free.pdf")
OUT_PATH = Path("notes/bird-transport-phenomena-source-map.md")


TOPICS = {
    "fluid properties and viscosity": [
        "viscosity",
        "viscosidade",
        "viscous",
        "viscoso",
        "density",
        "densidade",
        "Newtonian",
        "newtoniano",
        "non-Newtonian",
        "nao-newtoniano",
        "não-newtoniano",
    ],
    "fluid statics and pressure": [
        "hydrostatic",
        "hidrostatica",
        "hidrostática",
        "pressure",
        "pressao",
        "pressão",
        "manometer",
        "manometro",
        "manômetro",
        "buoyancy",
        "empuxo",
    ],
    "mass and momentum conservation": [
        "equation of continuity",
        "equacao da continuidade",
        "equação da continuidade",
        "continuity equation",
        "equation of motion",
        "equacao do movimento",
        "equação do movimento",
        "momentum",
        "quantidade de movimento",
        "Navier-Stokes",
    ],
    "Bernoulli and mechanical energy": [
        "Bernoulli",
        "mechanical energy",
        "energia mecanica",
        "energia mecânica",
        "friction factor",
        "fator de atrito",
    ],
    "dimensional analysis": [
        "dimensional analysis",
        "analise dimensional",
        "análise dimensional",
        "dimensionless",
        "adimensional",
        "Reynolds number",
        "numero de Reynolds",
        "número de Reynolds",
        "Buckingham",
    ],
    "heat transfer and conduction": [
        "thermal conductivity",
        "condutividade termica",
        "condutividade térmica",
        "Fourier",
        "heat conduction",
        "conducao de calor",
        "condução de calor",
        "temperature distribution",
        "distribuicao de temperatura",
        "distribuição de temperatura",
    ],
    "convection heat transfer": [
        "convection",
        "conveccao",
        "convecção",
        "heat-transfer coefficient",
        "coeficiente de transferencia de calor",
        "coeficiente de transferência de calor",
        "Nusselt",
    ],
    "radiation": [
        "radiation",
        "radiacao",
        "radiação",
        "emissivity",
        "emissividade",
        "Stefan-Boltzmann",
    ],
    "mass transfer and diffusion": [
        "diffusivity",
        "difusividade",
        "diffusion",
        "difusao",
        "difusão",
        "Fick",
        "mass transfer",
        "transferencia de massa",
        "transferência de massa",
        "concentration distribution",
        "distribuicao de concentracao",
        "distribuição de concentração",
    ],
}


def clean_text(text: str) -> str:
    try:
        text = text.encode("latin1").decode("utf-8")
    except UnicodeError:
        pass
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def ascii_fold(text: str) -> str:
    text = unicodedata.normalize("NFKD", text)
    return text.encode("ascii", "ignore").decode("ascii")


def find_chapter_lines(page_text: str) -> list[str]:
    lines = []
    for line in page_text.splitlines():
        compact = clean_text(line)
        if re.search(r"\bCAP[ÍI]TULO\b", compact, re.IGNORECASE):
            lines.append(ascii_fold(compact))
    return lines[:8]


def page_has_any(text_lower: str, terms: list[str]) -> bool:
    return any(term.lower() in text_lower for term in terms)


def main() -> None:
    reader = PdfReader(str(PDF_PATH))
    pages = reader.pages
    page_count = len(pages)

    page_texts: list[str] = []
    chapter_hits: list[tuple[int, str]] = []
    topic_pages: dict[str, list[int]] = {topic: [] for topic in TOPICS}

    for idx, page in enumerate(pages):
        text = page.extract_text() or ""
        page_texts.append(text)
        text_lower = text.lower()

        for topic, terms in TOPICS.items():
            if page_has_any(text_lower, terms):
                topic_pages[topic].append(idx + 1)

        for line in find_chapter_lines(text):
            chapter_hits.append((idx + 1, line))

    words = Counter()
    for text in page_texts:
        for word in re.findall(r"[A-Za-z][A-Za-z-]{4,}", text.lower()):
            if word not in {"transport", "phenomena", "chapter", "figure", "problem"}:
                words[word] += 1

    def summarize_pages(page_numbers: list[int], limit: int = 20) -> str:
        if not page_numbers:
            return "No direct keyword hits found."
        head = ", ".join(str(p) for p in page_numbers[:limit])
        suffix = "" if len(page_numbers) <= limit else f", ... ({len(page_numbers)} pages total)"
        return head + suffix

    lines = [
        "# Bird Transport Phenomena Source Map",
        "",
        f"Main source: [`{PDF_PATH.name}`](../materials/{PDF_PATH.name})",
        "",
        "Course context: HID-31 Transport Phenomena.",
        "",
        "This note turns the Bird, Stewart, and Lightfoot textbook PDF into a usable study base for HID-31. It is an index and study guide, not a copy of the book.",
        "",
        "> Copyright note: use this map to locate ideas, formulas, and examples in the PDF. Do not copy long textbook passages into notes.",
        "",
        "## Extraction Status",
        "",
        f"- PDF text layer: extractable with `pypdf`.",
        f"- Total PDF pages detected: {page_count}.",
        "- Output created from keyword and page-text scanning, so page lists are a starting point, not a final citation system.",
        "",
        "## How To Use This Book For HID-31",
        "",
        "Use Bird as the main theory reference when the teacher material is short. For each class topic:",
        "",
        "1. Start with the teacher PDF, slide, or syllabus topic.",
        "2. Use the map below to find the related Bird pages.",
        "3. Read only the needed section.",
        "4. Create your own short note in simple English.",
        "5. Add formulas, variables, units, assumptions, and one small example.",
        "",
        "## Best Bird Chapters For HID-31",
        "",
        "| HID-31 need | Bird chapters to start with | Role in your study |",
        "|---|---|---|",
        "| General transport idea | Chapter 0 | Big-picture introduction to momentum, energy, and mass transport. |",
        "| Fluid properties and viscosity | Chapter 1 | Main base for viscosity and molecular momentum transport. |",
        "| Momentum balances | Chapters 2 and 3 | Main base for shell balances, continuity, and equations of motion. |",
        "| Velocity distributions and viscous flow | Chapters 4 and 5 | Support for laminar and turbulent velocity profiles. |",
        "| Macroscopic flow balances | Chapter 7 | Support for engineering balance forms, including mechanical-energy reasoning. |",
        "| Heat transfer by conduction | Chapters 9 and 10 | Main base for thermal conductivity, Fourier law, and shell energy balances. |",
        "| Energy equation and convection | Chapters 11 to 15 | Main base for energy balances, temperature profiles, and interphase heat transfer. |",
        "| Radiation | Chapter 16 | Supporting base; use teacher material first if the class treats radiation briefly. |",
        "| Mass transfer and diffusion | Chapters 17 to 19 | Main base for diffusivity, Fick law, and species balances. |",
        "| Advanced mass transfer | Chapters 20 to 23 | Support for concentration profiles, interphase transfer, and macroscopic species balances. |",
        "",
        "## HID-31 Topic Map",
        "",
        "| HID-31 topic | Bird PDF pages with keyword hits | How to use it |",
        "|---|---:|---|",
    ]

    guidance = {
        "fluid properties and viscosity": "Base theory for viscosity, Newtonian behavior, and material properties.",
        "fluid statics and pressure": "Use as support. Bird is stronger in transport theory than basic hydrostatics.",
        "mass and momentum conservation": "Main base for continuity, momentum balance, and differential equations.",
        "Bernoulli and mechanical energy": "Use for energy-balance reasoning and flow losses.",
        "dimensional analysis": "Use for dimensionless groups and similarity ideas.",
        "heat transfer and conduction": "Main base for Fourier law, conduction, and energy balances.",
        "convection heat transfer": "Main base for heat-transfer coefficients and dimensionless correlations.",
        "radiation": "Supporting base. Use teacher material first if radiation is treated briefly.",
        "mass transfer and diffusion": "Main base for Fick law, diffusion, and species balances.",
    }

    for topic, page_numbers in topic_pages.items():
        lines.append(f"| {topic} | {summarize_pages(page_numbers)} | {guidance[topic]} |")

    lines.extend(
        [
            "",
            "## Chapter Signals Found",
            "",
            "These are text signals found by scanning pages for chapter-like headings. Use them to locate the book structure quickly.",
            "",
        ]
    )

    if chapter_hits:
        for page, line in chapter_hits[:80]:
            safe_line = line.replace("|", "\\|")
            lines.append(f"- PDF page {page}: {safe_line}")
        if len(chapter_hits) > 80:
            lines.append(f"- More chapter-like signals found: {len(chapter_hits) - 80}.")
    else:
        lines.append("- No chapter-like heading lines were found by the simple scanner.")

    lines.extend(
        [
            "",
            "## First Notes To Create",
            "",
            "| Priority | Note file | Purpose |",
            "|---:|---|---|",
            "| 1 | `notes/transport-phenomena-core-ideas.md` | Explain flux, gradients, conservation balances, and analogies between momentum, heat, and mass transfer. |",
            "| 2 | `notes/viscosity-and-momentum-transport.md` | Explain viscosity, shear stress, Newtonian fluids, and momentum flux. |",
            "| 3 | `notes/continuity-and-momentum-balance.md` | Build the bridge from conservation of mass to momentum balance and Navier-Stokes. |",
            "| 4 | `notes/energy-transport-and-fourier-law.md` | Explain heat flux, thermal conductivity, shell energy balances, and Fourier law. |",
            "| 5 | `notes/mass-transport-and-fick-law.md` | Explain concentration, molar flux, diffusivity, Fick law, and simple diffusion problems. |",
            "",
            "## Common Mistakes When Using A Big Textbook",
            "",
            "- Trying to read the whole book from start to finish.",
            "- Copying definitions instead of rewriting them in your own words.",
            "- Studying formulas without units or assumptions.",
            "- Ignoring the teacher material and using the textbook as if it were the course plan.",
            "- Forgetting that Bird is advanced; some derivations are deeper than HID-31 needs.",
            "",
            "## Useful Search Terms",
            "",
            "Search inside the PDF for these terms when you need a topic quickly:",
            "",
            "- `viscosity`",
            "- `shell momentum balance`",
            "- `equation of continuity`",
            "- `Navier-Stokes`",
            "- `Bernoulli`",
            "- `dimensional analysis`",
            "- `Fourier`",
            "- `thermal conductivity`",
            "- `Fick`",
            "- `diffusivity`",
            "",
            "## Frequent Technical Words In The Extracted Text",
            "",
            ", ".join(word for word, _ in words.most_common(30)),
            "",
        ]
    )

    OUT_PATH.write_text("\n".join(lines), encoding="utf-8")
    print(f"Created {OUT_PATH} from {page_count} PDF pages.")


if __name__ == "__main__":
    main()
