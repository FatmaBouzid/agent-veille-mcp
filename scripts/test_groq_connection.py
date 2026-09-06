"""Script de vérification manuelle — pas un test automatisé, juste pour valider ta clé."""

from groq import Groq

from agent_veille.config import settings

client = Groq(api_key=settings.groq_api_key)

response = client.chat.completions.create(
    model=settings.llm_model_name,
    messages=[{"role": "user", "content": "Réponds juste 'ça marche'."}],
)

print(response.choices[0].message.content)