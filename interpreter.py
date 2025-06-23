from langchain_community.vectorstores import FAISS
from langchain.text_splitter import CharacterTextSplitter
from langchain_community.document_loaders import JSONLoader
import json
import re
import requests

# --------- 1. Charger les documents JSON ---------
loader = JSONLoader(
    file_path="alerts_dataset.json",
    jq_schema=".[] | .alert.signature + \" : \" + .payload_printable",
    text_content=True
)
documents = loader.load()

# --------- 2. Diviser les documents ---------
text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
texts = text_splitter.split_documents(documents)

# --------- 3. Créer embeddings ---------
from sentence_transformers import SentenceTransformer
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

# --------- 4. Charger vecteur FAISS ---------
vectorstore = FAISS.load_local("vector_db", embedding_model, allow_dangerous_deserialization=True)

# --------- 5. Fonction pour appeler l'API OpenRouter ---------
def local_generate(prompt):
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": "Bearer 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",
        "Content-Type": "application/json"
    }
    body = {
        "model": "meta-llama/llama-3.3-8b-instruct:free",
        "messages": [
            {"role": "system", "content": "Tu es un analyste SOC. Ton rôle est d'expliquer clairement les alertes de sécurité."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0,
        "max_tokens": 800
    }

    try:
        response = requests.post(url, headers=headers, json=body)
        if response.status_code == 200:
            return response.json()["choices"][0]["message"]["content"]
        else:
            return f"Erreur API OpenRouter : {response.status_code} - {response.text}"
    except Exception as e:
        return f"Erreur d'appel API : {e}"

# --------- 6. Fonction d’analyse ---------
def run_interpreter(message):
    try:
        data = json.loads(message)
        
        # IP source : tester plusieurs chemins possibles
        src_ip = (
            data.get("source", {}).get("ip") or
            data.get("source", {}).get("address") or
            data.get("id.orig_h") or
            data.get("src_ip") or
            "IP source inconnue"
        )
        
        # IP destination
        dest_ip = (
            data.get("destination", {}).get("ip") or
            data.get("destination", {}).get("address") or
            data.get("id.resp_h") or
            data.get("dest_ip") or
            "IP destination inconnue"
        )
        
        # Signature
        signature = (
            data.get("rule", {}).get("name") or
            data.get("suricata", {}).get("eve", {}).get("alert", {}).get("signature") or
            data.get("alert", {}).get("signature") or
            data.get("signature") or
            "Signature inconnue"
        )
        
        # Catégorie
        category = (
            data.get("rule", {}).get("category") or
            data.get("suricata", {}).get("eve", {}).get("alert", {}).get("category") or
            data.get("alert", {}).get("category") or
            "Catégorie inconnue"
        )
        
        # Gravité
        severity = (
            str(data.get("event", {}).get("severity")) or
            str(data.get("alert", {}).get("severity")) or
            "Gravité inconnue"
        )
        
        question = f"""
Tu es un analyste SOC. Voici un message d’alerte brute :

{message}

Merci d’extraire et d’indiquer clairement ces informations :

- IP source
- Port source
- IP destination
- Port destination
- Protocole
- Signature
- Catégorie
- Gravité

Ensuite, analyse cette alerte selon ces points (3 à 6 phrases) :
1. Nature de l’alerte.
2. Rôle probable de l’IP source.
3. Cible et service visé.
4. Gravité et criticité.
5. Action recommandée immédiate.

Sois clair, concis et utilise un vocabulaire de cybersécurité. Ta réponse doit faire entre 3 et 6 phrases.
"""

        response = local_generate(question)
        return highlight_values(response)
    
    except json.JSONDecodeError:
        response = local_generate(f"Voici un message d'alerte : {message}\nExplique ce message en langage simple, de façon courte (3 à 4 phrases).")
        return highlight_values(response)
    
    except Exception as e:
        return f"Erreur lors de l'analyse : {e}"

# --------- 7. Mise en forme du texte ---------
def highlight_values(text):
    patterns = [
        r'\b\d{1,3}(?:\.\d{1,3}){3}\b',     # IP
        r'\bport\s*\d+\b',                  # Port
        r'\bTCP\b|\bUDP\b|\bHTTP\b|\bHTTPS\b',  # Protocoles
        r'\b\d{4}-\d{2}-\d{2}\b',          # Dates
        r'\b\d+\b(?=\s*:\s*)'              # Numéros
    ]
    for pattern in patterns:
        text = re.sub(pattern, lambda m: f"<strong>{m.group(0)}</strong>", text, flags=re.IGNORECASE)
    return text
