"""
Psychological Tests Module

Provides various psychological assessments and tests for mood tracking.
"""

from typing import Dict, List, Any


class PsychologicalTests:
    """Class containing various psychological assessment tools."""
    
    def __init__(self):
        self.tests = {
            'phq9': self._phq9_questions(),
            'gad7': self._gad7_questions(),
            'dass21': self._dass21_questions()
        }
    
    def _phq9_questions(self) -> List[Dict[str, Any]]:
        """PHQ-9 Depression Assessment questions."""
        return [
            {
                'id': 1,
                'question': 'Little interest or pleasure in doing things',
                'scale': 'Over the last 2 weeks, how often have you been bothered by:'
            },
            {
                'id': 2,
                'question': 'Feeling down, depressed, or hopeless',
                'scale': 'Over the last 2 weeks, how often have you been bothered by:'
            },
            {
                'id': 3,
                'question': 'Trouble falling or staying asleep, or sleeping too much',
                'scale': 'Over the last 2 weeks, how often have you been bothered by:'
            },
            {
                'id': 4,
                'question': 'Feeling tired or having little energy',
                'scale': 'Over the last 2 weeks, how often have you been bothered by:'
            },
            {
                'id': 5,
                'question': 'Poor appetite or overeating',
                'scale': 'Over the last 2 weeks, how often have you been bothered by:'
            }
        ]
    
    def _gad7_questions(self) -> List[Dict[str, Any]]:
        """GAD-7 Anxiety Assessment questions."""
        return [
            {
                'id': 1,
                'question': 'Feeling nervous, anxious, or on edge',
                'scale': 'Over the last 2 weeks, how often have you been bothered by:'
            },
            {
                'id': 2,
                'question': 'Not being able to stop or control worrying',
                'scale': 'Over the last 2 weeks, how often have you been bothered by:'
            },
            {
                'id': 3,
                'question': 'Worrying too much about different things',
                'scale': 'Over the last 2 weeks, how often have you been bothered by:'
            }
        ]
    
    def _dass21_questions(self) -> List[Dict[str, Any]]:
        """DASS-21 Stress Assessment questions (subset)."""
        return [
            {
                'id': 1,
                'question': 'I found it hard to wind down',
                'scale': 'Please read each statement and select how much it applied to you over the past week'
            },
            {
                'id': 2,
                'question': 'I was aware of dryness of my mouth',
                'scale': 'Please read each statement and select how much it applied to you over the past week'
            }
        ]
    
    def get_test(self, test_name: str) -> List[Dict[str, Any]]:
        """Get questions for a specific test."""
        return self.tests.get(test_name, [])
    
    def calculate_score(self, test_name: str, responses: List[int]) -> Dict[str, Any]:
        """Calculate score for a completed test."""
        total_score = sum(responses)
        
        if test_name == 'phq9':
            return self._interpret_phq9_score(total_score)
        elif test_name == 'gad7':
            return self._interpret_gad7_score(total_score)
        elif test_name == 'dass21':
            return self._interpret_dass21_score(total_score)
        
        return {'score': total_score, 'interpretation': 'Unknown test'}
    
    def _interpret_phq9_score(self, score: int) -> Dict[str, Any]:
        """Interpret PHQ-9 depression score."""
        if score <= 4:
            severity = 'Minimal'
        elif score <= 9:
            severity = 'Mild'
        elif score <= 14:
            severity = 'Moderate'
        elif score <= 19:
            severity = 'Moderately Severe'
        else:
            severity = 'Severe'
        
        return {
            'score': score,
            'severity': severity,
            'interpretation': f'PHQ-9 Depression Score: {score} ({severity})'
        }
    
    def _interpret_gad7_score(self, score: int) -> Dict[str, Any]:
        """Interpret GAD-7 anxiety score."""
        if score <= 4:
            severity = 'Minimal'
        elif score <= 9:
            severity = 'Mild'
        elif score <= 14:
            severity = 'Moderate'
        else:
            severity = 'Severe'
        
        return {
            'score': score,
            'severity': severity,
            'interpretation': f'GAD-7 Anxiety Score: {score} ({severity})'
        }
    
    def _interpret_dass21_score(self, score: int) -> Dict[str, Any]:
        """Interpret DASS-21 stress score."""
        if score <= 7:
            severity = 'Normal'
        elif score <= 9:
            severity = 'Mild'
        elif score <= 12:
            severity = 'Moderate'
        elif score <= 16:
            severity = 'Severe'
        else:
            severity = 'Extremely Severe'
        
        return {
            'score': score,
            'severity': severity,
            'interpretation': f'DASS-21 Stress Score: {score} ({severity})'
        }
