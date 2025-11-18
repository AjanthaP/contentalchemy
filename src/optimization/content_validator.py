from typing import Dict, List
from pydantic import BaseModel

class ValidationResult(BaseModel):
    """Content validation result"""
    is_valid: bool
    score: int  # 0-100
    issues: List[str]
    warnings: List[str]
    suggestions: List[str]

class ContentValidator:
    """Validates content quality"""
    
    def __init__(self):
        self.min_word_count = {
            "blog": 800,
            "linkedin": 100,
            "research": 500
        }
        
        self.max_word_count = {
            "blog": 3000,
            "linkedin": 600,
            "research": 5000
        }
    
    def validate_content(self, content: str, content_type: str = "blog") -> ValidationResult:
        """Validate content quality"""
        issues = []
        warnings = []
        suggestions = []
        score = 100
        
        # Word count validation
        word_count = len(content.split())
        min_words = self.min_word_count.get(content_type, 500)
        max_words = self.max_word_count.get(content_type, 3000)
        
        if word_count < min_words:
            issues.append(f"Content too short: {word_count} words (minimum: {min_words})")
            score -= 20
        elif word_count > max_words:
            warnings.append(f"Content quite long: {word_count} words (recommended max: {max_words})")
            score -= 5
        
        # Structure validation
        if content_type == "blog":
            if not self._has_headings(content):
                issues.append("Missing heading structure (H2/H3)")
                score -= 15
            
            if not self._has_introduction(content):
                warnings.append("Consider adding a clear introduction")
                score -= 5
        
        # Readability checks
        avg_sentence_length = self._avg_sentence_length(content)
        if avg_sentence_length > 25:
            suggestions.append("Consider shorter sentences for better readability")
            score -= 5
        
        # Paragraph length
        if self._has_long_paragraphs(content):
            suggestions.append("Break up long paragraphs for better scannability")
            score -= 5
        
        is_valid = len(issues) == 0 and score >= 60
        
        return ValidationResult(
            is_valid=is_valid,
            score=max(0, score),
            issues=issues,
            warnings=warnings,
            suggestions=suggestions
        )
    
    def _has_headings(self, content: str) -> bool:
        """Check if content has proper headings"""
        import re
        h2_count = len(re.findall(r'^## ', content, re.MULTILINE))
        return h2_count >= 2
    
    def _has_introduction(self, content: str) -> bool:
        """Check if content has introduction"""
        lines = content.split('\n')
        first_paragraph = '\n'.join(lines[:5])
        return len(first_paragraph.split()) >= 50
    
    def _avg_sentence_length(self, content: str) -> float:
        """Calculate average sentence length"""
        sentences = content.replace('!', '.').replace('?', '.').split('.')
        sentences = [s.strip() for s in sentences if s.strip()]
        if not sentences:
            return 0
        total_words = sum(len(s.split()) for s in sentences)
        return total_words / len(sentences)
    
    def _has_long_paragraphs(self, content: str) -> bool:
        """Check for paragraphs longer than 150 words"""
        paragraphs = content.split('\n\n')
        for para in paragraphs:
            if len(para.split()) > 150:
                return True
        return False
