from typing import Dict, List, Tuple
from collections import Counter


class SkillAnalyzer:
    """
    Analyze skill gaps between candidate and job requirements
    """
    
    def __init__(self):
        self.weight_mapping = {
            'Programming Languages': 0.25,
            'Web Development': 0.20,
            'Data & Analytics': 0.20,
            'Cloud & DevOps': 0.15,
            'Databases': 0.15,
            'Other Technologies': 0.05
        }
    
    def analyze_skill_gap(self, candidate_skills: Dict[str, List[str]], 
                         job_skills: Dict[str, List[str]]) -> Dict:
        """
        Analyze skill gaps between candidate and job requirements
        
        Args:
            candidate_skills: Skills extracted from resume
            job_skills: Skills extracted from job description
            
        Returns:
            Dictionary with skill gap analysis
        """
        matched_skills = {}
        missing_skills = {}
        extra_skills = {}
        
        for category in job_skills:
            job_category_skills = set(job_skills[category])
            candidate_category_skills = set(candidate_skills.get(category, []))
            
            matched = job_category_skills.intersection(candidate_category_skills)
            missing = job_category_skills - candidate_category_skills
            extra = candidate_category_skills - job_category_skills
            
            matched_skills[category] = list(matched)
            missing_skills[category] = list(missing)
            extra_skills[category] = list(extra)
        
        return {
            'matched_skills': matched_skills,
            'missing_skills': missing_skills,
            'extra_skills': extra_skills
        }
    
    def compute_skill_match_percentage(self, candidate_skills: Dict[str, List[str]], 
                                      job_skills: Dict[str, List[str]]) -> float:
        """
        Compute percentage of skills matched
        
        Args:
            candidate_skills: Skills extracted from resume
            job_skills: Skills extracted from job description
            
        Returns:
            Skill match percentage (0-100)
        """
        total_required = sum(len(skills) for skills in job_skills.values())
        
        if total_required == 0:
            return 100.0
        
        total_matched = 0
        weighted_score = 0
        
        for category in job_skills:
            job_category_skills = set(job_skills[category])
            candidate_category_skills = set(candidate_skills.get(category, []))
            matched = len(job_category_skills.intersection(candidate_category_skills))
            
            total_matched += matched
            weight = self.weight_mapping.get(category, 0.05)
            category_percentage = (matched / len(job_category_skills)) if len(job_category_skills) > 0 else 0
            weighted_score += category_percentage * weight
        
        return min(100.0, weighted_score * 100)
    
    def get_skill_priority_recommendations(self, missing_skills: Dict[str, List[str]]) -> List[Dict]:
        """
        Get prioritized recommendations for missing skills
        
        Args:
            missing_skills: Missing skills by category
            
        Returns:
            List of skill recommendations
        """
        recommendations = []
        
        for category, skills in missing_skills.items():
            if skills:
                weight = self.weight_mapping.get(category, 0.05)
                priority = "High" if weight > 0.15 else "Medium" if weight > 0.10 else "Low"
                
                recommendations.append({
                    'category': category,
                    'missing_skills': skills,
                    'priority': priority,
                    'weight': weight
                })
        
        # Sort by weight (importance)
        recommendations.sort(key=lambda x: x['weight'], reverse=True)
        
        return recommendations
