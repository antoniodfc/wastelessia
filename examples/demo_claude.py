"""Démo réelle : tracker sa propre dépense Claude avec @track.

Prérequis :
    pip install -e ".[examples]"
    export ANTHROPIC_API_KEY=sk-ant-...

Voir les events captés sans backend (mode debug) :
    WASTELESSIA_DEBUG=1 python examples/demo_claude.py

Envoyer les events vers le backend Wastelessia :
    export WASTELESSIA_API_KEY=proj_xxx
    python examples/demo_claude.py
"""

import os
import sys

import anthropic

from wastelessia import track

client = anthropic.Anthropic()  # lit ANTHROPIC_API_KEY


@track(team="founder", feature="demo", env="dev")
def ask_claude(prompt: str) -> str:
    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=200,
        messages=[{"role": "user", "content": prompt}],
    )
    return response.content[0].text


def main() -> None:
    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("ANTHROPIC_API_KEY manquant. export ANTHROPIC_API_KEY=sk-ant-...", file=sys.stderr)
        sys.exit(1)

    prompts = [
        "Résume Wastelessia en une phrase.",
        "Donne-moi 3 raisons pour lesquelles un CTO ignore sa dépense IA.",
        "Quel est le risque d'un agent LLM mal configuré ?",
    ]

    for prompt in prompts:
        print(f"\n→ {prompt}")
        answer = ask_claude(prompt)
        print(f"  {answer.strip()}")

    print("\n✓ 3 appels trackés. Les events partent en asynchrone.")
    print("  Active WASTELESSIA_DEBUG=1 pour les voir, ou configure WASTELESSIA_API_KEY pour les envoyer.")


if __name__ == "__main__":
    main()
