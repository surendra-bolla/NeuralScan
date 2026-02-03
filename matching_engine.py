from sentence_transformers import SentenceTransformer, util
import numpy as np
from typing import Dict, List, Tuple
import torch


class MatchingEngine:
    """
    Semantic matching engine using BERT embeddings
    """
    
    def __init__(self, model_name: str = 'all-MiniLM-L6-v2'):
        """
        Initialize matching engine with pre-trained model
        
        Args:
            model_name: Name of sentence transformer model
        """
        self.model = SentenceTransformer(model_name)
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.model.to(self.device)
    
    def compute_embeddings(self, texts: List[str]) -> np.ndarray:
        """
        Compute embeddings for list of texts
        
        Args:
            texts: List of text strings
            
        Returns:
            Array of embeddings
        """
        embeddings = self.model.encode(texts, convert_to_tensor=True, device=self.device)
        return embeddings
    
    def compute_sentence_similarity(self, sentence1: str, sentence2: str) -> float:
        """
        Compute similarity between two sentences
        
        Args:
            sentence1: First sentence
            sentence2: Second sentence
            
        Returns:
            Similarity score (0-1)
        """
        embeddings = self.model.encode([sentence1, sentence2], convert_to_tensor=True, device=self.device)
        similarity = util.pytorch_cos_sim(embeddings[0], embeddings[1])
        return float(similarity[0][0])
    
    def match_resume_to_job(self, resume_sentences: List[str], 
                           job_sentences: List[str], 
                           top_k: int = 5) -> Dict:
        """
        Match resume sentences to job description sentences
        
        Args:
            resume_sentences: List of resume sentences
            job_sentences: List of job description sentences
            top_k: Number of top matches to return per job sentence
            
        Returns:
            Dictionary with matching scores and details
        """
        # Compute embeddings
        resume_embeddings = self.model.encode(resume_sentences, convert_to_tensor=True, device=self.device)
        job_embeddings = self.model.encode(job_sentences, convert_to_tensor=True, device=self.device)
        
        # Compute similarity matrix
        similarity_matrix = util.pytorch_cos_sim(resume_embeddings, job_embeddings)
        similarity_matrix = similarity_matrix.cpu().numpy()
        
        matches = []
        
        for job_idx, job_sent in enumerate(job_sentences):
            similarities = similarity_matrix[:, job_idx]
            top_indices = np.argsort(similarities)[-top_k:][::-1]
            
            for rank, resume_idx in enumerate(top_indices):
                score = float(similarities[resume_idx])
                if score > 0.3:  # Only include meaningful matches
                    matches.append({
                        'job_requirement': job_sent,
                        'resume_match': resume_sentences[resume_idx],
                        'similarity_score': score,
                        'rank': rank + 1
                    })
        
        return {
            'total_matches': len(matches),
            'matches': matches,
            'similarity_matrix': similarity_matrix
        }
    
    def compute_overall_match_score(self, resume_text: str, job_description: str) -> float:
        """
        Compute overall match score between resume and job description
        
        Args:
            resume_text: Full resume text
            job_description: Full job description text
            
        Returns:
            Overall match score (0-100)
        """
        embeddings = self.model.encode([resume_text, job_description], convert_to_tensor=True, device=self.device)
        similarity = util.pytorch_cos_sim(embeddings[0], embeddings[1])
        score = float(similarity[0][0]) * 100
        
        return min(100, max(0, score))
