#!/usr/bin/env python3

import unittest
import json
import os
from llm_compatibility_analyzer import KimiCompatibilityAnalyzer
from models import UserRequest, CompatibilityResult

class TestCompatibilityAnalyzer(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures"""
        # Skip tests if no API key is available
        if not os.getenv('KIMI_API_KEY'):
            self.skipTest("KIMI_API_KEY not available")
            
        self.analyzer = KimiCompatibilityAnalyzer()
        
        # Create test profile data
        self.test_profile_a = {
            "profile": {
                "name": {"display_name": "Test Person A"},
                "personality": {"mbti_type": "INTJ"},
                "professional": {"current_role": "Software Engineer"}
            }
        }
        
        self.test_profile_b = {
            "profile": {
                "name": {"display_name": "Test Person B"},
                "personality": {"mbti_type": "ENFP"},
                "professional": {"current_role": "Product Manager"}
            }
        }
    
    def test_user_request_creation(self):
        """Test UserRequest data structure"""
        request = UserRequest(
            request_type="找队友",
            description="Test description"
        )
        self.assertEqual(request.request_type, "找队友")
        self.assertEqual(request.description, "Test description")
    
    def test_user_request_validation(self):
        """Test UserRequest validation"""
        with self.assertRaises(ValueError):
            UserRequest(
                request_type="invalid_type",
                description="Test description"
            )
    
    def test_extract_user_request(self):
        """Test extracting user request from profile"""
        profile_with_request = {
            "user_request": {
                "request_type": "找对象",
                "description": "Looking for partner"
            }
        }
        
        result = self.analyzer.extract_user_request(profile_with_request)
        self.assertIsInstance(result, UserRequest)
        self.assertEqual(result.request_type, "找对象")
        self.assertEqual(result.description, "Looking for partner")
    
    def test_extract_user_request_default(self):
        """Test extracting user request with default values"""
        profile_without_request = {}
        
        result = self.analyzer.extract_user_request(profile_without_request)
        self.assertIsInstance(result, UserRequest)
        self.assertEqual(result.request_type, "找队友")
        self.assertEqual(result.description, "寻找志同道合的合作伙伴")
    
    def test_compatibility_result_structure(self):
        """Test CompatibilityResult data structure"""
        result = CompatibilityResult(
            person_a="Person A",
            person_b="Person B",
            mutual_interest_score=8.0,
            a_to_b_interest=7.0,
            b_to_a_interest=9.0,
            request_matching_score=8.5,
            personality_matching_score=7.5,
            compatibility_factors=["Factor 1"],
            potential_conflicts=["Conflict 1"],
            request_analysis="Analysis",
            recommendation="Recommendation",
            detailed_analysis="Detailed analysis"
        )
        
        self.assertEqual(result.person_a, "Person A")
        self.assertEqual(result.person_b, "Person B")
        self.assertEqual(result.mutual_interest_score, 8.0)
        self.assertEqual(result.request_matching_score, 8.5)

if __name__ == '__main__':
    unittest.main() 