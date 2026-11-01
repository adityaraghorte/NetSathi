"""Local explanations only. AI questions live in ai_client.py and are sent only when the user asks."""
from .plain import GLOSSARY

def local_explanation(dx) -> str:
    terms = [f"**{k}**: {v}" for k, v in GLOSSARY.items() if k.lower() in (dx.title + dx.meaning + " ".join(dx.causes)).lower()]
    return dx.meaning + ("\n\n" + "\n\n".join(terms) if terms else "")
