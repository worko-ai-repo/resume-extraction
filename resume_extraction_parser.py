import re
import spacy
from docx import Document
from pdfminer.high_level import extract_text
from spacy.matcher import Matcher


def extract_text_from_pdf(pdf_path):
    return extract_text(pdf_path)


def extract_text_from_docx(docx_path):
    text = ""
    doc = Document(docx_path)
    for paragraph in doc.paragraphs:
        text += paragraph.text + "\n"
    return text


def extract_name(resume_text):
    nlp = spacy.load('en_core_web_sm')
    matcher = Matcher(nlp.vocab)

    # Define name patterns
    patterns = [
        [{'POS': 'PROPN'}, {'POS': 'PROPN'}],  # First name and Last name
        [{'POS': 'PROPN'}, {'POS': 'PROPN'}, {'POS': 'PROPN'}],  # First name, Middle name, and Last name
        [{'POS': 'PROPN'}, {'POS': 'PROPN'}, {'POS': 'PROPN'}, {'POS': 'PROPN'}]
        # First name, Middle name, Middle name, and Last name
        # Add more patterns as needed
    ]

    for pattern in patterns:
        matcher.add('NAME', patterns=[pattern])

    doc = nlp(resume_text)
    matches = matcher(doc)

    for match_id, start, end in matches:
        span = doc[start:end]
        return span.text

    return None


def extract_contact_number_from_resume(text):
    contact_number = None

    # Use regex pattern to find a potential contact number
    pattern = r"\b(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b"
    match = re.search(pattern, text)
    if match:
        contact_number = match.group()

    return contact_number


def extract_email_from_resume(text):
    email = None

    # Use regex pattern to find a potential email address
    pattern = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"
    match = re.search(pattern, text)
    if match:
        email = match.group()

    return email


def extract_skills_from_resume(text, skills_list):
    skills = []

    for skill in skills_list:
        pattern = r"\b{}\b".format(re.escape(skill))
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            skills.append(skill)

    return skills


def extract_skills_from_resume1(text):
    pattern = r'\b([A-Za-z0-9]+)\b'
    skills = re.findall(pattern, text)
    return skills


def extract_education_from_resume(text):
    education = []

    # Use regex pattern to find education information
    pattern = r"(?i)(?:Bsc|\bB\.\w+|\bM\.\w+|\bPh\.D\.\w+|\bBachelor(?:'s)?|\bMaster(?:'s)?|\bPh\.D)\s(?:\w+\s)*\w+"
    matches = re.findall(pattern, text)
    for match in matches:
        education.append(match.strip())

    return education


if __name__ == '__main__':
    # file_path = 'C:\\Users\\Arup Acharya\\Downloads\\ARUP_ACHARYA_Resume.pdf'
    file_path = 'C:\\Users\\Arup Acharya\\Downloads\\ARUP_ACHARYA_Resume.docx'
    if file_path.lower().endswith('.pdf'):
        resume_text = extract_text_from_pdf(file_path)
    elif file_path.lower().endswith('.docx'):
        resume_text = extract_text_from_docx(file_path)
    else:
        print("Unsupported file format")

    print(resume_text)

    name = extract_name(resume_text)

    if name:
        print("Name:", name)
    else:
        print("Name not found")

    contact_number = extract_contact_number_from_resume(resume_text)
    if contact_number:
        print("Contact Number:", contact_number)
    else:
        print("Contact Number not found")

    email = extract_email_from_resume(resume_text)
    if email:
        print("Email:", email)
    else:
        print("Email not found")

    skills_list = ['Python', 'Data Analysis', 'Machine Learning', 'Communication', 'Java', 'UI Testing' 'Selenium',
                   'TOSCA', 'BDD  Testing', 'RPA']
    extracted_skills = extract_skills_from_resume(resume_text, skills_list)
    # extracted_skills = extract_skills_from_resume1(resume_text)
    if extracted_skills:
        print("Skills:", extracted_skills)
    else:
        print("No skills found")

    extracted_education = extract_education_from_resume(resume_text)
    if extracted_education:
        print("Education:", extracted_education)
    else:
        print("No education information found")
