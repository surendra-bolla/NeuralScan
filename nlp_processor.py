import nltk
import spacy
import re
from typing import List, Set, Dict
from datetime import datetime
from nltk.tokenize import sent_tokenize
from nltk.corpus import stopwords

# Download required NLTK data
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')

# Load spaCy model
try:
    nlp = spacy.load('en_core_web_sm')
except OSError:
    print("Downloading spaCy model...")
    import subprocess
    subprocess.run(['python', '-m', 'spacy', 'download', 'en_core_web_sm'])
    nlp = spacy.load('en_core_web_sm')


class NLPProcessor:
    """
    Natural Language Processing module for resume and job description analysis
    """
    
    def __init__(self):
        self.nlp = nlp
        self.stop_words = set(stopwords.words('english'))
        
        # Common technical skills database
        self.skill_keywords = {
            'Programming Languages': [
                'python', 'java', 'javascript', 'c++', 'c#', 'go', 'rust', 'kotlin',
                'swift', 'objective-c', 'perl', 'ruby', 'php', 'scala', 'r', 'matlab',
                'typescript', 'c', 'groovy', 'elixir', 'clojure'
            ],
            'Web Development': [
                'react', 'angular', 'vue', 'nodejs', 'express', 'django', 'flask',
                'spring', 'fastapi', 'asp.net', 'jsp', 'html', 'css', 'webpack',
                'gulp', 'next.js', 'nuxt', 'laravel', 'symfony', 'rails'
            ],
            'Data & Analytics': [
                'pandas', 'numpy', 'scikit-learn', 'tensorflow', 'pytorch', 'keras',
                'spark', 'hadoop', 'kafka', 'elasticsearch', 'sql', 'mysql', 'postgresql',
                'mongodb', 'cassandra', 'redis', 'hbase', 'tableau', 'power bi', 'looker'
            ],
            'Cloud & DevOps': [
                'aws', 'azure', 'gcp', 'docker', 'kubernetes', 'jenkins', 'gitlab',
                'github', 'terraform', 'ansible', 'prometheus', 'grafana', 'elk',
                'ci/cd', 'devops', 'iaas', 'paas', 'saas'
            ],
            'Databases': [
                'sql', 'mysql', 'postgresql', 'mongodb', 'dynamodb', 'cassandra',
                'redis', 'elasticsearch', 'neo4j', 'oracle', 'sqlserver', 'firestore'
            ],
            'Other Technologies': [
                'git', 'rest api', 'graphql', 'linux', 'windows', 'macos', 'agile',
                'scrum', 'jira', 'confluence', 'slack', 'trello', 'microservices'
            ]
        }
        
        # Flatten skills for quick lookup
        self.all_skills = set()
        for category in self.skill_keywords.values():
            self.all_skills.update(category)
    
    def clean_text(self, text: str) -> str:
        """Clean and normalize text"""
        text = text.lower()
        text = re.sub(r'\s+', ' ', text)  # Remove extra whitespace
        text = re.sub(r'[^\w\s\-\.]', ' ', text)  # Remove special characters
        return text.strip()
    
    def extract_sentences(self, text: str) -> List[str]:
        """Extract sentences from text"""
        try:
            sentences = sent_tokenize(text)
            return [self.clean_text(sent) for sent in sentences if len(sent.strip()) > 10]
        except:
            # Fallback to simple splitting
            return [self.clean_text(line) for line in text.split('.') if len(line.strip()) > 10]
    
    def extract_skills(self, text: str) -> Dict[str, List[str]]:
        """Extract technical and soft skills from text"""
        text_lower = text.lower()
        extracted_skills = {category: [] for category in self.skill_keywords}
        
        for category, keywords in self.skill_keywords.items():
            for keyword in keywords:
                # Use word boundaries for more accurate matching
                pattern = r'\b' + re.escape(keyword) + r'\b'
                if re.search(pattern, text_lower):
                    extracted_skills[category].append(keyword)
        
        # Remove duplicates
        for category in extracted_skills:
            extracted_skills[category] = list(set(extracted_skills[category]))
        
        return extracted_skills
    
    def extract_entities(self, text: str) -> Dict:
        """Extract named entities like education, organization, location"""
        doc = self.nlp(text)
        
        entities = {
            'PERSON': [],
            'ORG': [],
            'GPE': [],
            'DATE': []
        }
        
        for ent in doc.ents:
            if ent.label_ in entities:
                entities[ent.label_].append(ent.text)
        
        # Remove duplicates
        for key in entities:
            entities[key] = list(set(entities[key]))
        
        return entities
    
    def extract_education(self, text: str) -> List[str]:
        """Extract education qualifications"""
        education_keywords = [
            'bachelor', 'btech', 'b.tech', 'b tech', 'be',
            'master', 'mtech', 'm.tech', 'm tech', 'ms',
            'phd', 'ph.d',
            'diploma', 'associate', 'certification', 'certified',
            'bca', 'mca', 'bsc', 'msc', 'ba', 'ma', 'mba',
            'b.a', 'b.s', 'm.a', 'm.s'
        ]
        
        text_lower = text.lower()
        found_education = []
        
        for edu in education_keywords:
            pattern = r'\b' + re.escape(edu) + r'\b'
            if re.search(pattern, text_lower):
                found_education.append(edu.upper())
        
        return list(set(found_education))
    
    def extract_experience_years(self, text: str) -> int:
        """Extract total years of experience from text and date calculations"""
        # First, try to extract explicit experience mentions
        explicit_patterns = [
            r'(\d+\.?\d*)\s*(?:\+)?\s*years?\s+(?:of\s+)?experience',
            r'experience:\s*(\d+\.?\d*)\s*years?',
            r'(\d+\.?\d*)\s*years?\s+in\s+industry',
            r'(\d+\.?\d*)\s*years?\s+(?:of\s+)?professional',
            r'(\d+\.?\d*)\s*years?\s+(?:of\s+)?expertise',
            r'(\d+\.?\d*)\s*years?\s+(?:of\s+)?relevant',
        ]
        
        text_lower = text.lower()
        years = []
        
        # Extract explicit years
        for pattern in explicit_patterns:
            matches = re.findall(pattern, text_lower)
            if matches:
                for m in matches:
                    try:
                        year_value = float(m)
                        if 0 < year_value < 100:
                            years.append(int(year_value))
                    except (ValueError, TypeError):
                        continue
        
        # If explicit years found, return max
        if years:
            return max(years)
        
        # Otherwise, try to extract date ranges and calculate
        try:
            # Date patterns (month year format)
            date_pattern = r'(january|february|march|april|may|june|july|august|september|october|november|december|jan|feb|mar|apr|may|jun|jul|aug|sep|sept|oct|nov|dec)\s+(\d{4})'
            dates = re.findall(date_pattern, text_lower)
            
            if len(dates) >= 2:
                # Map month names to numbers
                months = {
                    'january': 1, 'jan': 1,
                    'february': 2, 'feb': 2,
                    'march': 3, 'mar': 3,
                    'april': 4, 'apr': 4,
                    'may': 5,
                    'june': 6, 'jun': 6,
                    'july': 7, 'jul': 7,
                    'august': 8, 'aug': 8,
                    'september': 9, 'sep': 9, 'sept': 9,
                    'october': 10, 'oct': 10,
                    'november': 11, 'nov': 11,
                    'december': 12, 'dec': 12,
                }
                
                # Get all dates found
                all_dates = []
                for month_name, year in dates:
                    month = months.get(month_name, 1)
                    try:
                        date_obj = datetime(int(year), month, 1)
                        all_dates.append(date_obj)
                    except ValueError:
                        continue
                
                if len(all_dates) >= 2:
                    # Sort dates
                    all_dates.sort()
                    start_date = all_dates[0]
                    end_date = all_dates[-1]
                    
                    # Calculate years difference
                    years_diff = (end_date - start_date).days / 365.25
                    
                    # If years diff is reasonable, return it
                    if 0 < years_diff < 100:
                        return int(years_diff) if years_diff < 1 else int(years_diff)
        
        except Exception as e:
            print(f"Error calculating experience from dates: {e}")
        
        return 0
    
    def tokenize_and_lemmatize(self, text: str) -> List[str]:
        """Tokenize and lemmatize text"""
        doc = self.nlp(text)
        tokens = [token.lemma_ for token in doc if not token.is_stop and token.is_alpha]
        return tokens