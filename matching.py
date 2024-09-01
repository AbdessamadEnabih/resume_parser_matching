import numpy as np
import torch
from transformers import AutoModel, AutoTokenizer

cvData = {
    "experience": [
        {
            "job_title": "Assistant Commercial Export",
            "company_name": "DANONE, Paris",
            "dateStart": "2015",
            "dateEnd": "2015",
            "nbrMonths": 12,
            "missions": [
                "Assurer la mise à jour des coordonnées administrative relatives au compte client",
                "Traiter les demandes d’échantillon depuis la saisie jusqu’à l’expédition",
                "Assurer l'interface entreprise-client export pour tout service sollicité"
            ],
            "technologies": ["JAVA", "SPRING BOOT", "JSP", "MySQL", "GIT"]
        },
        {
            "job_title": "Assistant Commercial Stagiaire",
            "company_name": "ORANGE, Paris",
            "dateStart": "2016",
            "dateEnd": "2019",
            "nbrMonths": 36,
            "missions": [
                "Etablir des documents nécessaires à l'expédition des commandes en fonction de son pays de destination, de l’incoterm ainsi que du mode de règlement convenu",
                "Assurer l'accueil téléphonique des clients, fournisseurs et autres tiers"
            ],
            "technologies": [
                "JAVA", "ANGULAR", "SPRING BOOT", "SPRING SECURITY", 
                "MySQL", "GIT", "REST"
            ]
        }
    ],
    "skills": {
        "hard_skills": ["Logique", "Rigueur", "Autonomie", "t1"],
        "soft_skills": [
            "Sens du contact", "Communication", 
            "Capacité d’adaptation", "Polyvalence"
        ]
    },
    "certifications": [
        {
            "certification_name": "Certified Project Management Professional",
            "type": "Project Management",
            "institution": "Project Management Institute",
            "year_obtained": "2022"
        },
        {
            "certification_name": "Full Stack Web Developer",
            "type": "Web Development",
            "institution": "Coursera",
            "year_obtained": "2021"
        },
        {
            "certification_name": "Data Science Professional Certificate",
            "type": "Data Science",
            "institution": "Harvard University",
            "year_obtained": "2020"
        },
        {
            "certification_name": "Certified Information Systems Security Professional (CISSP)",
            "type": "Cybersecurity",
            "institution": "ISC²",
            "year_obtained": "2023"
        },
        {
            "certification_name": "Google Analytics Individual Qualification",
            "type": "Digital Marketing",
            "institution": "Google",
            "year_obtained": "2019"
        }
    ],
    "competences_operationnelles": [
        "Méthodologies", "Frameworks", "Langage de devéloppement"
    ],
    "languages": ["Français", "Anglais", "Espagnol"],
}

def check_similarity(data: object, keywords: list) -> list:
    tokenizer = AutoTokenizer.from_pretrained("sentence-transformers/all-MiniLM-L6-v2")
    model = AutoModel.from_pretrained("sentence-transformers/all-MiniLM-L6-v2")

    # Flatten the data into a list of sentences
    sentences = []
    for key, value in data.items():
        if isinstance(value, list):
            for item in value:
                if isinstance(item, dict):
                    for subkey, subvalue in item.items():
                        if isinstance(subvalue, list):
                            sentences.extend(subvalue)
                        else:
                            sentences.append(subvalue)
                else:
                    sentences.append(item)
        else:
            sentences.append(value)
    
    # Tokenize and get embeddings for the sentences and keywords
    sentence_embeddings = model(**tokenizer(sentences, return_tensors='pt', padding=True, truncation=True)).last_hidden_state.mean(dim=1)
    keyword_embeddings = model(**tokenizer(keywords, return_tensors='pt', padding=True, truncation=True)).last_hidden_state.mean(dim=1)

    # Calculate cosine similarity between each sentence and each keyword
    similarities = torch.matmul(sentence_embeddings, keyword_embeddings.T)

    # Convert similarities to a list of scores
    similarity_scores = similarities.cpu().detach().numpy()

    # Return the similarity scores
    return similarity_scores.tolist()

# Example usage
keywords = ["JAVA", "Project Management", "Communication"]
similarity_scores = check_similarity(cvData, keywords)
print(similarity_scores)
