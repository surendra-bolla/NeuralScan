from typing import Dict, List
from datetime import datetime


class ExplainabilityEngine:
    """
    Generate human-readable explanations for match scores
    """
    
    @staticmethod
    def generate_explanation(
        overall_score: float,
        skill_match_percentage: float,
        experience_match: float,
        education_match: float,
        semantic_match: float,
        matched_skills: Dict,
        missing_skills: Dict,
        candidate_experience: int,
        top_matches: List[Dict]
    ) -> Dict:
        """
        Generate comprehensive explanation for match score
        
        Args:
            overall_score: Overall match score (0-100)
            skill_match_percentage: Percentage of skills matched
            experience_match: Experience level match (0-100)
            education_match: Education level match (0-100)
            semantic_match: Semantic similarity score (0-100)
            matched_skills: Matched skills by category
            missing_skills: Missing skills by category
            candidate_experience: Years of experience
            top_matches: Top sentence matches
            
        Returns:
            Dictionary with detailed explanation
        """
        
        # Determine verdict
        if overall_score >= 80:
            verdict = "HIGHLY RECOMMENDED"
            verdict_color = "green"
            verdict_reason = "Excellent match with strong skill alignment and relevant experience"
        elif overall_score >= 60:
            verdict = "RECOMMENDED"
            verdict_color = "yellow"
            verdict_reason = "Good match with some skill gaps that could be addressed"
        elif overall_score >= 40:
            verdict = "FAIR MATCH"
            verdict_color = "orange"
            verdict_reason = "Moderate match but significant skill gaps exist"
        else:
            verdict = "NOT RECOMMENDED"
            verdict_color = "red"
            verdict_reason = "Poor match with substantial skill and experience gaps"
        
        # Summarize matched skills
        matched_summary = []
        for category, skills in matched_skills.items():
            if skills:
                matched_summary.append(f"{category}: {', '.join(skills[:5])}")
        
        # Summarize missing skills
        missing_summary = []
        for category, skills in missing_skills.items():
            if skills:
                missing_summary.append(f"{category}: {', '.join(skills[:5])}")
        
        # Generate narrative explanation
        narrative = ExplainabilityEngine._generate_narrative(
            overall_score,
            skill_match_percentage,
            experience_match,
            education_match,
            candidate_experience,
            matched_skills,
            missing_skills
        )
        
        # Extract key matching requirements
        key_requirements_met = []
        if top_matches:
            for match in top_matches[:3]:
                if match['similarity_score'] > 0.6:
                    key_requirements_met.append({
                        'requirement': match['job_requirement'][:100],
                        'match_strength': ExplainabilityEngine._score_to_strength(match['similarity_score'])
                    })
        
        return {
            'overall_score': round(overall_score, 2),
            'verdict': verdict,
            'verdict_color': verdict_color,
            'verdict_reason': verdict_reason,
            'score_breakdown': {
                'skill_match': round(skill_match_percentage, 2),
                'experience_match': round(experience_match, 2),
                'education_match': round(education_match, 2),
                'semantic_similarity': round(semantic_match, 2)
            },
            'matched_skills_summary': matched_summary,
            'missing_skills_summary': missing_summary,
            'key_strengths': ExplainabilityEngine._extract_strengths(
                skill_match_percentage,
                candidate_experience,
                matched_skills
            ),
            'key_gaps': ExplainabilityEngine._extract_gaps(missing_skills),
            'narrative': narrative,
            'key_requirements_met': key_requirements_met,
            'timestamp': datetime.now().isoformat()
        }
    
    @staticmethod
    def _generate_narrative(overall_score: float, skill_match: float, 
                           experience_match: float, education_match: float,
                           years_exp: int, matched_skills: Dict, 
                           missing_skills: Dict) -> str:
        """Generate narrative explanation"""
        
        narrative = f"The candidate scores {overall_score:.1f}/100 on the job match assessment. "
        
        if skill_match > 80:
            narrative += f"With {skill_match:.0f}% of required skills possessed, the candidate demonstrates strong technical alignment. "
        elif skill_match > 60:
            narrative += f"The candidate possesses {skill_match:.0f}% of the required skills, indicating a good foundation. "
        else:
            narrative += f"The candidate has {skill_match:.0f}% of required skills, suggesting some learning curve. "
        
        if years_exp > 5:
            narrative += f"With {years_exp} years of experience, the candidate brings valuable industry knowledge. "
        elif years_exp > 2:
            narrative += f"The candidate's {years_exp} years of experience provides relevant background. "
        else:
            narrative += "The candidate appears to be early in their career. "
        
        # Count matched and missing skills
        total_matched = sum(len(skills) for skills in matched_skills.values())
        total_missing = sum(len(skills) for skills in missing_skills.values())
        
        if total_matched > 0:
            narrative += f"Key strengths include proficiency in {total_matched} in-demand technologies. "
        
        if total_missing > 0 and total_missing <= 3:
            narrative += f"Only {total_missing} significant skill gaps remain, which are highly trainable. "
        elif total_missing > 3:
            narrative += f"There are {total_missing} notable skill gaps that would require additional training. "
        
        return narrative
    
    @staticmethod
    def _score_to_strength(score: float) -> str:
        """Convert score to strength description"""
        if score > 0.8:
            return "Very Strong"
        elif score > 0.6:
            return "Strong"
        elif score > 0.4:
            return "Moderate"
        else:
            return "Weak"
    
    @staticmethod
    def _extract_strengths(skill_match: float, years_exp: int, 
                          matched_skills: Dict) -> List[str]:
        """Extract key strengths"""
        strengths = []
        
        if skill_match > 80:
            strengths.append(f"Strong technical skills alignment ({skill_match:.0f}% match)")
        
        if years_exp > 5:
            strengths.append(f"Substantial industry experience ({years_exp} years)")
        
        # Top matched categories
        top_categories = sorted(
            [(cat, len(skills)) for cat, skills in matched_skills.items() if skills],
            key=lambda x: x[1],
            reverse=True
        )
        
        if top_categories:
            top_cat = top_categories[0]
            strengths.append(f"Strong background in {top_cat[0]}")
        
        return strengths[:3]
    
    @staticmethod
    def _extract_gaps(missing_skills: Dict) -> List[str]:
        """Extract key gaps"""
        gaps = []
        
        for category, skills in missing_skills.items():
            if len(skills) > 2:
                gaps.append(f"Limited experience in {category}")
            elif len(skills) == 1 and skills[0].lower() not in ['others']:
                gaps.append(f"Missing {category}: {skills[0]}")
        
        return gaps[:3]
