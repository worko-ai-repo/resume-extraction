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
    pattern = (r"(?i)(?:Bsc|\bB\.\w+|\bM\.\w+|\bPh\.D\.\w+|\bBachelor(?:'s)?|\bMaster("
               r"?:'s)?|\bPh\.D|B\.E|MTech|MCA|BCA)\s(?:\w+\s)*\w+")
    matches = re.findall(pattern, text)
    for match in matches:
        education.append(match.strip())

    return education


def extract_experience_from_resume(resume_text):
    nlp = spacy.load("en_core_web_sm")
    matcher = Matcher(nlp.vocab)

    experience_pattern = [
        {"IS_SPACE": True, "OP": "?"},  # Optional space
        {"IS_DIGIT": True, "OP": "+"},  # Match one or more digits
        {"IS_SPACE": True, "OP": "?"},  # Optional space
        {"ORTH": {"in": ["+", ""]}},  # Match the plus sign or an empty string
        {"IS_SPACE": True, "OP": "?"},  # Optional space
        {"LOWER": {"in": ["year", "years", "Years"]}},  # Match "year" or "years"
    ]

    matcher.add("Experience", [experience_pattern])

    doc = nlp(resume_text)

    matches = matcher(doc)

    for match_id, start, end in matches:
        span = doc[start:end]
        return span.text

    return None


def extract_experience_from_resume_retry(resume_text):
    pattern = r'(\d+)\s+years\s+of\s+experience'
    match = re.search(pattern, resume_text)

    if match:
        years_of_experience = match.group(1)
        return years_of_experience
    else:
        return None


def extracted_education_from_resume_retry(resume_text):
    # Split the text into lines
    lines = resume_text.split('\n')

    # Search for the line containing "BE (Computer Science)"
    for line in lines:
        if " BE (Computer Science)" in line:
            academic_details = line.strip()
            break
    else:
        return None

    return academic_details

if __name__ == '__main__':
    # file_path = 'C:\\Users\\Arup Acharya\\Downloads\\Bhupendra Kumar Patwa Resume.pdf'
    # file_path = 'C:\\Users\\Arup Acharya\\Downloads\\Sushma Iralapalle_Automation Architect (1).pdf'
    file_path = 'C:\\Users\\Arup Acharya\\Downloads\\Resume of Ilangathir Joseph.pdf'
    # file_path = 'C:\\Users\\Arup Acharya\\Downloads\\Rupa Bhagwat_Resume1.pdf'
    # file_path = 'C:\\Users\\Arup Acharya\\Downloads\\Sushant_CV_Automation_SDET_7Yrs.pdf'
    # file_path = 'C:\\Users\\Arup Acharya\\Downloads\\ARUP_ACHARYA_Resume.pdf'

    resume_text = extract_text_from_pdf(file_path)

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

    skills_list = ['Python', 'Data Analysis', 'Machine Learning', 'Communication', 'UI Testing' 'Selenium',
                   'TOSCA', 'BDD  Testing', 'RPA', 'Data Visualization', 'Predictive Analysis', 'Statistical Modeling',
                   'Data Mining', 'Clustering & Classification', 'Data Analytics', 'Quantitative Analysis',
                   'Web Scraping', 'ML Algorithms', 'Keras', 'Pytorch', 'Probability', 'Scikit-learn', 'Tensorflow',
                   "Flask", 'Streamlit', 'React', 'Django', 'Node JS', 'React JS', 'php', 'laravel', 'Magento',
                   'wordpress', 'Javascript', 'Angular JS', 'c#', 'Flask', 'SDK', 'Android', 'Android development',
                   'Flutter', 'Kotlin', 'XML', 'Java', 'Kivy', 'GIT', 'IOS', 'IOS Development',
                   'Swift', 'Cocoa', 'Cocoa Touch', 'Xcode', 'Objective-C', 'SQLite', 'Plist', 'StoreKit', "UI-Kit",
                   'AV Foundation', 'Auto-Layout', 'Adobe XD', 'Prototyping', 'Storyframes', 'Adobe Photoshop', 'Solid',
                   'ux', 'adobe xd', 'figma', 'zeplin', 'balsamiq', 'ui', 'prototyping', 'wireframes',
                   'adobe photoshop', 'photoshop', 'editing', 'adobe illustrator', 'illustrator', 'adobe after effects',
                   'after effects', 'adobe premier pro', 'adobe indesign', 'indesign', 'wireframe', 'solid', 'grasp',
                   'user research', 'user experience', 'Selenium WebDriver(Java)', 'QTP', 'HP ALM', 'Python',
                   'Appium', 'docker', 'Postman', 'Jira', 'SOAPUI', 'Rational ClearQuest', 'GITHUB', 'BitBucket',
                   'TestNG', 'Unix ', 'Solaris', 'SQL', 'Agile Scrum', 'Waterfall', 'V-model', 'Functional',
                   'System', ' Integration', ' Regression', ' Black Box', ' GUI testing', ' compatibility', ' API',
                   'security', 'performance testing']

    extracted_skills = extract_skills_from_resume(resume_text, skills_list)

    if extracted_skills:
        print("Skills:", extracted_skills)
    else:
        print("No skills found")

    extracted_education = extract_education_from_resume(resume_text)
    if extracted_education:
        print("Education:", extracted_education)
    else:
        extracted_education = extracted_education_from_resume_retry(resume_text)
        if extracted_education:
            print("Education:", extracted_education)
        else:
            print("No education information found")

    experience_entities = extract_experience_from_resume(resume_text)

    if experience_entities:
        print("Experience:", experience_entities.strip())
    else:
        experience_entities = extract_experience_from_resume_retry(resume_text)
        if experience_entities:
            print("Experience:", experience_entities)
        else:
            print("No experience information found")