from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import FAISS
import json

# Charger le dataset JSON
with open("alerts_dataset.json", "r", encoding="utf-8") as f:
    data = json.load(f)

# Extraire les messages à vectoriser (ici on prend les "interpretation")
texts = [d["interpretation"] for d in data]

# Créer les embeddings avec un modèle HuggingFace
embedding_model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

# Créer la base vectorielle FAISS à partir des textes
db = FAISS.from_texts(texts, embedding_model)

# Sauvegarder la base sur disque dans un dossier "vector_db"
db.save_local("vector_db")

print("✅ Base vectorielle créée.")
