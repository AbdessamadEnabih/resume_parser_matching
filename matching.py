import jellyfish
from typing import Dict, List, Union
from collections import defaultdict
import logging
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import nltk

nltk.download("punkt")
nltk.download("stopwords")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def prepare_data():
    """Prepares the data for candidate information."""
    candidate_info = defaultdict(lambda: {})
    cvData = {
        "experience": [
            {
                "job_title": "Assistant Commercial Export",
                "company_name": "DANONE, Paris",
                "dateStart": "2015",
                "dateEnd": "2015",
                "nbrMonths": 12,
                "technologies": ["JAVA", "SPRING BOOT", "JSP", "MySQL", "GIT"],
            },
            {
                "job_title": "Assistant Commercial Stagiaire",
                "company_name": "ORANGE, Paris",
                "dateStart": "2016",
                "dateEnd": "2019",
                "nbrMonths": 36,
                "technologies": [
                    "JAVA",
                    "ANGULAR",
                    "SPRING BOOT",
                    "SPRING SECURITY",
                    "MySQL",
                    "GIT",
                    "REST",
                    "Python",
                    "OpenAPI",
                ],
            },
        ],
        "skills": {
            "hard_skills": ["Logique", "Rigueur", "Autonomie", "t1"],
            "soft_skills": [
                "Sens du contact",
                "Communication",
                "Capacité d'adaptation",
                "Polyvalence",
            ],
        },
        "certifications": [
            {
                "certification_name": "Certified Project Management Professional",
                "type": "Project Management",
                "institution": "Project Management Institute",
                "year_obtained": "2022",
            },
            {
                "certification_name": "Full Stack Web Developer",
                "type": "Web Development",
                "institution": "Coursera",
                "year_obtained": "2021",
            },
            {
                "certification_name": "Data Science Professional Certificate",
                "type": "Data Science",
                "institution": "Harvard University",
                "year_obtained": "2020",
            },
            {
                "certification_name": "Certified Information Systems Security Professional (CISSP)",
                "type": "Cybersecurity",
                "institution": "ISC²",
                "year_obtained": "2023",
            },
            {
                "certification_name": "Google Analytics Individual Qualification",
                "type": "Digital Marketing",
                "institution": "Google",
                "year_obtained": "2019",
            },
        ],
        "competences_operationnelles": [
            "Méthodologies",
            "Frameworks",
            "Langage de développement",
        ],
        "languages": ["Français", "Anglais", "Espagnol"],
    }

    get_skills(candidate_info, cvData)

    return dict(candidate_info)


def get_skills(
    candidate_info: Dict[str, List[Union[str, int]]],
    skills: Dict[str, Union[Dict[str, List[str]], str]],
) -> None:
    """
    Extracts skills from the given skills dictionary and adds them to the candidate_info dictionary.
    Removes duplicate skills.
    """
    EXPERIENCE_KEY = "experience"
    TECHNOLOGIES_KEY = "technologies"
    LANGUAGES_KEY = "languages"
    SKILLS_KEY = "skills"

    # Initialize experience-total to 0 if it doesn't exist
    if "experience-total" not in candidate_info:
        candidate_info["experience-total"] = 0

    if EXPERIENCE_KEY in skills:
        candidate_info["skills"] = set()
        for exp in skills[EXPERIENCE_KEY]:
            if TECHNOLOGIES_KEY in exp:
                candidate_info["skills"].update(exp[TECHNOLOGIES_KEY])
            if "nbrMonths" in exp:
                candidate_info["experience-total"] += exp["nbrMonths"]

    if LANGUAGES_KEY in skills:
        candidate_info["skills"].update(skills[LANGUAGES_KEY])

    if SKILLS_KEY in skills:
        candidate_info["skills"].update(
            set.union(
                *[
                    set(sublist)
                    for sublist in [
                        skills[SKILLS_KEY]["hard_skills"],
                        skills[SKILLS_KEY]["soft_skills"],
                    ]
                ]
            )
        )


def match_candidate_with_job(resume_data, job_description):
    """
    Matches a candidate with a job description using fuzzy matching.
    Returns a dictionary with the score, matched skills, and experience match.
    """

    # Tokenize and preprocess text
    def preprocess_text(text):
        stop_words = set(stopwords.words("english"))
        tokens = word_tokenize(text.lower())
        return [
            token for token in tokens if token.isalnum() and token not in stop_words
        ]

    # Tokenize job description and candidate skills
    job_keywords = preprocess_text(job_description)
    candidate_skills = resume_data["skills"]

    matched_skills = set()

    # Iterate over the skills and compare them with the job description
    for skill in candidate_skills:
        skill_tokens = preprocess_text(skill)
        for token in skill_tokens:
            for keyword in job_keywords:
                # Check exact match or fuzzy match using Jaro-Winkler similarity
                if (
                    token == keyword
                    or jellyfish.jaro_winkler_similarity(token, keyword) > 0.80
                ):
                    matched_skills.add(skill)
                    break

    # Calculate the match score based on the number of matched skills
    score = len(matched_skills) / len(candidate_skills) if candidate_skills else 0

    # Add a check for minimum years of experience
    min_years_experience = 8  # Adjust this value as needed
    
    # Handle both integer and list cases for experience-total
    if isinstance(resume_data["experience-total"], int):
        total_months = resume_data["experience-total"]
    elif isinstance(resume_data["experience-total"], list):
        total_months = sum(exp.get("nbrMonths", 0) for exp in resume_data["experience-total"])
    else:
        raise ValueError("Invalid type for experience-total")

    candidate_years_experience = total_months // 12
    candidate_years_experience = total_months // 12
    
    if candidate_years_experience >= min_years_experience:
        experience_match = "Experienced"
    else:
        experience_match = f"Not enough experience ({candidate_years_experience} years)"

    return {
        "score": score,
        "matched_skills": list(matched_skills),
        "experience_match": experience_match
    }


def main():
    # Prepare data
    candidate_info = prepare_data()

    # Example usage
    job_description = """
    We're looking for a Software Development Manager with expertise and passion in building teams, coaching individuals, and solving difficult problems in distributed systems, and highly available services.
    
    Our work environment is very technically challenging: you need to understand complex code very quickly. You must be able to conceptualize the interaction of software components and products together in a stack. You need to be prepared to expect the unexpected and have a strong focus on customer satisfaction. We're looking for people who are fast learners, highly motivated, and have great communications skills. If the opportunity to resolve real-world customer problems in the world's most important software products is exciting to you, then come join us. You can be guaranteed never to be bored!
    
    As a manager, you will apply your technical and organizational skills to solve delivery, support, and operational optimizations, while driving execution of roadmap commitments. Build enhancements within an existing software architecture and occasionally suggest improvements to the architecture. You will work with a variety of technical, functional, and business stakeholders to ensure consistent delivery of product advancements.

    Responsibilities
    As a manager, you will apply your knowledge of software architecture to manage software development tasks associated with developing, debugging or designing software applications, operating systems and databases according to provided design specifications.
    Build enhancements within an existing software architecture and suggest improvements to the architecture.
    Build and mentor a high-performing development team, fostering a culture of collaboration, innovation, and continuous improvement.
    Effectively manage resources, priorities, and schedules to ensure timely delivery of high-quality software solutions.
    Collaborate with product management, architecture, and other cross-functional teams to define project requirements and priorities.
    Communicate effectively with stakeholders to provide updates on project status, solicit feedback, and address concerns or issues as they arise.
    Required Qualifications:
    Have 8+ years of professional experience in developing large scale web applications, UI, high performance REST APIs.
    Hands-on experience of Micro-service architecture and modern UI framework.
    BS or MS in Computer Science or an equivalent area
    Minimum 3 years of experience leading small- to medium-scale cross-organizational initiatives.
    Experience with Cloud Applications and technologies. Experience in scalability, performance, security, concurrency for cloud-based Apps is a plus.
    Experience of database design/modelling, knowledge of RDBMS concepts and working SQL knowledge is required.
    Knowledge/Experience with: Python, PL-SQL, API Integration, Linux, Analytics and Reporting experience, OCI
    Ability to navigate in cloud-based development environment
    Solid grasp of REST and related Server-side technologies (e.g. SWAGGER, OpenAPI, NodeJS)
    Excellent understanding of System Architecture and Implementation experience of working / released products with considerable complexity.
    Good working knowledge of Micro-service architecture and various design patterns.
    Proven ability to deliver high-quality SaaS applications.
    Excellent diagnostics, debugging and troubleshooting experience on Linux / Unix environments, along with ability to identify product improvements.
    Knowledge of Project Management concepts / software (Jira, Sprints, etc.) and ability to multi-task and deal with shifting priorities
    Should have excellent written (including product documentation) and verbal (with presentation) communication skill
    Strong analytical and problem-solving skills.
    About Us
    As a world leader in cloud solutions, Oracle uses tomorrow"""
    result = match_candidate_with_job(candidate_info, job_description)

    print(f"Candidate Score: {result['score']:.2f}")
    print("Matched Skills:", result["matched_skills"])
    print("Candidate Total Experience:", candidate_info["experience-total"])
    print("Experience Match:", result["experience_match"])

    # Update candidate_info with matched skills
    candidate_info["matched_skills"] = result["matched_skills"]
    candidate_info["experience_match"] = result["experience_match"]


if __name__ == "__main__":
    main()
