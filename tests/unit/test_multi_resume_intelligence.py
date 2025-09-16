"""Unit tests for multi-resume intelligence components"""

import unittest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

from tpm_job_finder_poc.models.resume_inventory import (
    ResumeMetadata, ResumeType, DomainClassification, ResumeInventory
)
from tpm_job_finder_poc.models.job import Job
from tpm_job_finder_poc.enrichment.resume_discovery_service import ResumeDiscoveryService
from tpm_job_finder_poc.enrichment.hybrid_selection_engine import HybridSelectionEngine
from tpm_job_finder_poc.enrichment.enhanced_content_analyzer import EnhancedContentAnalyzer
from tpm_job_finder_poc.enrichment.multi_resume_orchestrator import MultiResumeIntelligenceOrchestrator
from tpm_job_finder_poc.config.multi_resume_config import MultiResumeConfig, set_config

class TestResumeDiscoveryService(unittest.TestCase):
    """Test resume discovery and cataloging functionality"""
    
    def setUp(self):
        """Setup test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.base_path = Path(self.temp_dir)
        
        # Create test folder structure
        (self.base_path / "master").mkdir()
        (self.base_path / "AI").mkdir()
        (self.base_path / "Sales").mkdir()
        
        # Create test resume files
        (self.base_path / "master" / "complete_resume.pdf").touch()
        (self.base_path / "AI" / "ml_engineer.pdf").touch()
        (self.base_path / "AI" / "data_scientist.pdf").touch()
        (self.base_path / "Sales" / "enterprise_sales.pdf").touch()
        
        # Setup test config
        test_config = MultiResumeConfig()
        set_config(test_config)
        
        self.service = ResumeDiscoveryService()
    
    def tearDown(self):
        """Cleanup test environment"""
        shutil.rmtree(self.temp_dir)
    
    def test_scan_resume_folders(self):
        """Test complete folder scanning"""
        inventory = self.service.scan_resume_folders(self.base_path)
        
        self.assertIsNotNone(inventory.master_resume)
        self.assertEqual(len(inventory.candidate_resumes), 3)
        self.assertEqual(inventory.total_resumes, 4)
        
        # Check master resume identification
        self.assertEqual(inventory.master_resume.resume_type, ResumeType.MASTER)
        self.assertEqual(inventory.master_resume.filename, "complete_resume.pdf")
        
        # Check candidate resumes
        candidate_names = [r.filename for r in inventory.candidate_resumes]
        self.assertIn("ml_engineer.pdf", candidate_names)
        self.assertIn("data_scientist.pdf", candidate_names)
        self.assertIn("enterprise_sales.pdf", candidate_names)
    
    def test_identify_master_folder(self):
        """Test master folder identification"""
        folders = [
            self.base_path / "AI",
            self.base_path / "master",
            self.base_path / "Sales"
        ]
        
        master_folder = self.service.identify_master_folder(folders)
        self.assertEqual(master_folder, self.base_path / "master")
    
    def test_domain_classification(self):
        """Test resume domain classification"""
        # Create AI resume with tech skills
        ai_resume = ResumeMetadata(
            id="test1",
            file_path=self.base_path / "AI" / "ml_engineer.pdf",
            filename="ml_engineer.pdf",
            resume_type=ResumeType.CANDIDATE,
            domain=DomainClassification.GENERIC,
            skills=["python", "machine learning", "tensorflow"],
            experience_years=5,
            last_modified="2025-01-01",
            file_size=1000
        )
        
        domain = self.service.classify_resume_domain(ai_resume)
        self.assertEqual(domain, DomainClassification.TECHNOLOGY)
        
        # Create sales resume with business skills
        sales_resume = ResumeMetadata(
            id="test2",
            file_path=self.base_path / "Sales" / "enterprise_sales.pdf",
            filename="enterprise_sales.pdf",
            resume_type=ResumeType.CANDIDATE,
            domain=DomainClassification.GENERIC,
            skills=["sales", "revenue", "client management"],
            experience_years=7,
            last_modified="2025-01-01",
            file_size=1000
        )
        
        domain = self.service.classify_resume_domain(sales_resume)
        self.assertEqual(domain, DomainClassification.BUSINESS)

class TestHybridSelectionEngine(unittest.TestCase):
    """Test hybrid resume selection functionality"""
    
    def setUp(self):
        """Setup test environment"""
        self.mock_llm = Mock()
        self.engine = HybridSelectionEngine(llm_provider=self.mock_llm)
        
        # Create test job
        self.test_job = Job(
            title="Senior ML Engineer",
            company="TechCorp",
            description="Looking for ML engineer with Python, TensorFlow, and 5+ years experience"
        )
        
        # Create test inventory
        self.test_inventory = self._create_test_inventory()
    
    def _create_test_inventory(self):
        """Create test resume inventory"""
        master_resume = ResumeMetadata(
            id="master1",
            file_path=Path("/test/master/complete.pdf"),
            filename="complete.pdf",
            resume_type=ResumeType.MASTER,
            domain=DomainClassification.TECHNOLOGY,
            skills=["python", "tensorflow", "leadership"],
            experience_years=10,
            last_modified="2025-01-01",
            file_size=2000
        )
        
        ai_resume = ResumeMetadata(
            id="ai1",
            file_path=Path("/test/ai/ml_engineer.pdf"),
            filename="ml_engineer.pdf",
            resume_type=ResumeType.CANDIDATE,
            domain=DomainClassification.TECHNOLOGY,
            skills=["python", "tensorflow", "machine learning"],
            experience_years=5,
            last_modified="2025-01-01",
            file_size=1000
        )
        
        sales_resume = ResumeMetadata(
            id="sales1",
            file_path=Path("/test/sales/enterprise.pdf"),
            filename="enterprise.pdf",
            resume_type=ResumeType.CANDIDATE,
            domain=DomainClassification.BUSINESS,
            skills=["sales", "revenue", "client management"],
            experience_years=7,
            last_modified="2025-01-01",
            file_size=1000
        )
        
        return ResumeInventory(
            master_resume=master_resume,
            candidate_resumes=[ai_resume, sales_resume],
            base_path=Path("/test")
        )
    
    def test_analyze_job_keywords(self):
        """Test job keyword analysis"""
        keywords = self.engine.analyze_job_keywords(self.test_job)
        
        self.assertIn("python", keywords.technical_skills)
        self.assertIn("tensorflow", keywords.technical_skills)
        self.assertTrue(len(keywords.experience_requirements) > 0)
    
    def test_filter_candidate_resumes(self):
        """Test keyword-based candidate filtering"""
        keywords = self.engine.analyze_job_keywords(self.test_job)
        candidates = self.engine.filter_candidate_resumes(keywords, self.test_inventory)
        
        # Should select AI resume over sales resume for ML job
        self.assertEqual(len(candidates), 1)
        self.assertEqual(candidates[0].filename, "ml_engineer.pdf")
    
    def test_select_optimal_resume(self):
        """Test complete resume selection"""
        result = self.engine.select_optimal_resume(self.test_job, self.test_inventory)
        
        self.assertIsNotNone(result.selected_resume)
        self.assertEqual(result.selected_resume.filename, "ml_engineer.pdf")
        self.assertGreater(result.match_score, 0)
        self.assertTrue(len(result.selection_rationale) > 0)

class TestEnhancedContentAnalyzer(unittest.TestCase):
    """Test content analysis and enhancement generation"""
    
    def setUp(self):
        """Setup test environment"""
        # Mock the sentence transformer to avoid model loading in tests
        with patch('tpm_job_finder_poc.enrichment.enhanced_content_analyzer.SentenceTransformer'):
            self.analyzer = EnhancedContentAnalyzer()
            self.analyzer.model = Mock()
    
    def test_extract_bullet_points(self):
        """Test bullet point extraction"""
        resume_content = """
        Experience:
        • Led team of 5 engineers to deliver ML platform
        • Implemented TensorFlow models improving accuracy by 20%
        • Collaborated with product managers on feature development
        
        Other content without bullets.
        """
        
        bullets = self.analyzer.extract_bullet_points(resume_content)
        
        self.assertEqual(len(bullets), 3)
        self.assertIn("Led team of 5 engineers", bullets[0])
        self.assertIn("Implemented TensorFlow models", bullets[1])
        self.assertIn("Collaborated with product managers", bullets[2])
    
    def test_calculate_semantic_similarity(self):
        """Test semantic similarity calculation"""
        # Mock embedding calculation with more realistic responses
        def mock_embedding(text):
            if "similar" in text:
                return [0.1, 0.2, 0.3]
            elif "engineering" in text or "team" in text:
                return [0.8, 0.1, 0.2]  # Engineering-related embedding
            elif "financial" in text or "data" in text:
                return [0.2, 0.8, 0.1]  # Finance-related embedding  
            else:
                return [0.5, 0.5, 0.5]
                
        self.analyzer._get_embedding = Mock(side_effect=mock_embedding)
        
        # Test similar bullets
        similarity = self.analyzer.calculate_semantic_similarity(
            "Led similar team project", 
            "Managed similar engineering team"
        )
        self.assertGreater(similarity, 0.7)
        
        # Test different bullets  
        similarity = self.analyzer.calculate_semantic_similarity(
            "Led engineering team",
            "Analyzed financial data"
        )
        self.assertLess(similarity, 0.5)
    
    def test_identify_unique_content(self):
        """Test unique content identification"""
        master_bullets = [
            "Led engineering team of 10 developers",
            "Implemented machine learning algorithms",
            "Published research papers on AI"
        ]
        
        selected_bullets = [
            "Managed team of 5 engineers",  # Similar to first master bullet
            "Developed web applications"
        ]
        
        # Mock similarity calculation
        def mock_similarity(bullet1, bullet2):
            if "Led" in bullet1 and "Managed" in bullet2:
                return 0.85  # Above threshold
            return 0.3  # Below threshold
        
        self.analyzer.calculate_semantic_similarity = Mock(side_effect=mock_similarity)
        
        unique_bullets = self.analyzer.identify_unique_content(master_bullets, selected_bullets)
        
        # Should exclude the similar "Led engineering team" bullet
        self.assertEqual(len(unique_bullets), 2)
        self.assertIn("Implemented machine learning algorithms", unique_bullets)
        self.assertIn("Published research papers on AI", unique_bullets)

class TestMultiResumeOrchestrator(unittest.TestCase):
    """Test complete multi-resume orchestration"""
    
    def setUp(self):
        """Setup test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.base_path = Path(self.temp_dir)
        
        # Create test resume structure
        (self.base_path / "master").mkdir()
        (self.base_path / "AI").mkdir()
        
        # Create test files
        (self.base_path / "master" / "complete.pdf").touch()
        (self.base_path / "AI" / "ml_engineer.pdf").touch()
        
        # Mock components
        self.mock_llm = Mock()
        self.orchestrator = MultiResumeIntelligenceOrchestrator(llm_provider=self.mock_llm)
        
        # Create test job
        self.test_job = Job(
            id="job123",
            title="ML Engineer",
            company="TechCorp",
            description="ML engineering position requiring Python and TensorFlow"
        )
    
    def tearDown(self):
        """Cleanup test environment"""
        shutil.rmtree(self.temp_dir)
    
    @patch('tpm_job_finder_poc.enrichment.resume_discovery_service.ResumeDiscoveryService.scan_resume_folders')
    @patch('tpm_job_finder_poc.enrichment.hybrid_selection_engine.HybridSelectionEngine.select_optimal_resume')
    @patch('tpm_job_finder_poc.enrichment.enhanced_content_analyzer.EnhancedContentAnalyzer.select_top_enhancements')
    def test_process_job_with_multi_resume_intelligence(self, 
                                                       mock_enhancements, 
                                                       mock_selection, 
                                                       mock_inventory):
        """Test complete job processing workflow"""
        # Mock inventory
        mock_resume = ResumeMetadata(
            id="test1",
            file_path=self.base_path / "AI" / "ml_engineer.pdf",
            filename="ml_engineer.pdf",
            resume_type=ResumeType.CANDIDATE,
            domain=DomainClassification.TECHNOLOGY,
            skills=["python", "tensorflow"],
            experience_years=5,
            last_modified="2025-01-01",
            file_size=1000
        )
        
        mock_inventory.return_value = ResumeInventory(
            master_resume=mock_resume,
            candidate_resumes=[mock_resume],
            base_path=self.base_path
        )
        
        # Mock selection
        mock_selection.return_value = Mock(
            selected_resume=mock_resume,
            match_score=85.0,
            selection_rationale="Strong technical match",
            confidence_level=0.9,
            keyword_matches=5  # Add missing field that orchestrator expects
        )
        
        # Mock enhancements
        mock_enhancements.return_value = []
        
        # Process job
        result = self.orchestrator.process_job_with_multi_resume_intelligence(
            self.test_job, self.base_path
        )
        
        # Verify result
        self.assertEqual(result.job_id, "job123")
        self.assertIsNotNone(result.selected_resume)
        self.assertEqual(result.match_score, 85.0)
        self.assertGreater(result.processing_time, 0)

class TestAcceptanceScenarios(unittest.TestCase):
    """End-to-end acceptance test scenarios"""
    
    def setUp(self):
        """Setup comprehensive test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.base_path = Path(self.temp_dir)
        
        # Create realistic folder structure
        folders = ["master", "AI", "Backend", "Sales", "Finance"]
        for folder in folders:
            (self.base_path / folder).mkdir()
        
        # Create test resume files
        test_files = [
            "master/complete_experience.pdf",
            "AI/ml_engineer.pdf", 
            "AI/data_scientist.pdf",
            "Backend/python_architect.pdf",
            "Sales/enterprise_sales.pdf",
            "Finance/financial_analyst.pdf"
        ]
        
        for file_path in test_files:
            (self.base_path / file_path).touch()
    
    def tearDown(self):
        """Cleanup test environment"""
        shutil.rmtree(self.temp_dir)
    
    def test_scenario_1_technology_professional(self):
        """
        Scenario 1: Technology Professional
        Given: User has resumes in AI/, Backend/, and Security/ folders plus master/
        When: System processes ML Engineer job from Google
        Then: AI resume selected, 3 unique enhancements from master provided
        """
        # Create test job
        job = Job(
            title="ML Engineer",
            company="Google",
            description="Looking for ML engineer with Python, TensorFlow experience"
        )
        
        # Mock orchestrator with realistic responses
        with patch.multiple(
            'tpm_job_finder_poc.enrichment.multi_resume_orchestrator.MultiResumeIntelligenceOrchestrator',
            _get_resume_inventory=Mock(return_value=self._create_tech_inventory()),
        ):
            orchestrator = MultiResumeIntelligenceOrchestrator()
            
            # Mock selection engine to return AI resume
            with patch.object(orchestrator.selection_engine, 'select_optimal_resume') as mock_selection:
                mock_selection.return_value = Mock(
                    selected_resume=self._get_ai_resume(),
                    match_score=92.0,
                    selection_rationale="Strong ML keyword match",
                    confidence_level=0.95,
                    keyword_matches=8  # Add missing field
                )
                
                # Mock content analyzer for enhancements
                with patch.object(orchestrator.content_analyzer, 'select_top_enhancements') as mock_enhancements:
                    mock_enhancements.return_value = self._get_sample_enhancements()
                    
                    result = orchestrator.process_job_with_multi_resume_intelligence(job, self.base_path)
                    
                    # Assertions
                    self.assertEqual(result.selected_resume.filename, "ml_engineer.pdf")
                    self.assertGreaterEqual(result.match_score, 90.0)
                    self.assertEqual(len(result.enhancements), 3)
                    self.assertIn("technology", result.selection_rationale.lower())
    
    def test_scenario_2_sales_professional(self):
        """
        Scenario 2: Sales Professional
        Given: User has resumes in Enterprise/, SMB/, and Channel/ folders plus master/
        When: System processes Enterprise Sales role from Salesforce
        Then: Enterprise resume selected, 3 revenue-focused enhancements provided
        """
        job = Job(
            title="Enterprise Sales",
            company="Salesforce", 
            description="Enterprise sales role requiring revenue generation experience"
        )
        
        with patch.multiple(
            'tpm_job_finder_poc.enrichment.multi_resume_orchestrator.MultiResumeIntelligenceOrchestrator',
            _get_resume_inventory=Mock(return_value=self._create_sales_inventory()),
        ):
            orchestrator = MultiResumeIntelligenceOrchestrator()
            
            with patch.object(orchestrator.selection_engine, 'select_optimal_resume') as mock_selection:
                mock_selection.return_value = Mock(
                    selected_resume=self._get_sales_resume(),
                    match_score=88.0,
                    selection_rationale="Strong revenue experience match",
                    confidence_level=0.92,
                    keyword_matches=6  # Add missing field
                )
                
                with patch.object(orchestrator.content_analyzer, 'select_top_enhancements') as mock_enhancements:
                    mock_enhancements.return_value = self._get_revenue_enhancements()
                    
                    result = orchestrator.process_job_with_multi_resume_intelligence(job, self.base_path)
                    
                    # Assertions
                    self.assertEqual(result.selected_resume.filename, "enterprise_sales.pdf")
                    self.assertGreaterEqual(result.match_score, 85.0)
                    self.assertEqual(len(result.enhancements), 3)
                    self.assertTrue(any("revenue" in e.bullet_point.lower() for e in result.enhancements))
    
    def _create_tech_inventory(self):
        """Create technology professional inventory"""
        master = ResumeMetadata(
            id="master1", file_path=self.base_path / "master" / "complete_experience.pdf",
            filename="complete_experience.pdf", resume_type=ResumeType.MASTER,
            domain=DomainClassification.TECHNOLOGY, skills=["python", "leadership", "architecture"],
            experience_years=10, last_modified="2025-01-01", file_size=2000
        )
        
        ai_resume = self._get_ai_resume()
        backend_resume = ResumeMetadata(
            id="backend1", file_path=self.base_path / "Backend" / "python_architect.pdf",
            filename="python_architect.pdf", resume_type=ResumeType.CANDIDATE,
            domain=DomainClassification.TECHNOLOGY, skills=["python", "architecture", "backend"],
            experience_years=7, last_modified="2025-01-01", file_size=1000
        )
        
        return ResumeInventory(
            master_resume=master,
            candidate_resumes=[ai_resume, backend_resume],
            base_path=self.base_path
        )
    
    def _create_sales_inventory(self):
        """Create sales professional inventory"""
        master = ResumeMetadata(
            id="master1", file_path=self.base_path / "master" / "complete_experience.pdf",
            filename="complete_experience.pdf", resume_type=ResumeType.MASTER,
            domain=DomainClassification.BUSINESS, skills=["sales", "leadership", "strategy"],
            experience_years=12, last_modified="2025-01-01", file_size=2000
        )
        
        sales_resume = self._get_sales_resume()
        
        return ResumeInventory(
            master_resume=master,
            candidate_resumes=[sales_resume],
            base_path=self.base_path
        )
    
    def _get_ai_resume(self):
        """Get AI resume metadata"""
        return ResumeMetadata(
            id="ai1", file_path=self.base_path / "AI" / "ml_engineer.pdf",
            filename="ml_engineer.pdf", resume_type=ResumeType.CANDIDATE,
            domain=DomainClassification.TECHNOLOGY, skills=["python", "tensorflow", "machine learning"],
            experience_years=5, last_modified="2025-01-01", file_size=1000
        )
    
    def _get_sales_resume(self):
        """Get sales resume metadata"""
        return ResumeMetadata(
            id="sales1", file_path=self.base_path / "Sales" / "enterprise_sales.pdf",
            filename="enterprise_sales.pdf", resume_type=ResumeType.CANDIDATE,
            domain=DomainClassification.BUSINESS, skills=["sales", "revenue", "enterprise"],
            experience_years=8, last_modified="2025-01-01", file_size=1000
        )
    
    def _get_sample_enhancements(self):
        """Get sample ML enhancements"""
        from tpm_job_finder_poc.models.resume_inventory import Enhancement
        return [
            Enhancement(
                bullet_point="Led MLOps platform serving 10M+ predictions/day",
                relevance_score=0.95,
                source_resume="master",
                category="technical",
                reasoning="Technical expertise relevant to ML Engineer position"
            ),
            Enhancement(
                bullet_point="Reduced model training costs by 60% via spot instances",
                relevance_score=0.89,
                source_resume="master",
                category="impact",
                reasoning="Quantifiable achievements aligned with Google goals"
            ),
            Enhancement(
                bullet_point="Published 5 ML papers in top-tier conferences",
                relevance_score=0.87,
                source_resume="master",
                category="leadership",
                reasoning="Leadership experience valuable for ML Engineer role"
            )
        ]
    
    def _get_revenue_enhancements(self):
        """Get sample revenue-focused enhancements"""
        from tpm_job_finder_poc.models.resume_inventory import Enhancement
        return [
            Enhancement(
                bullet_point="Generated $50M+ in new revenue through strategic partnerships",
                relevance_score=0.93,
                source_resume="master",
                category="impact",
                reasoning="Revenue generation aligned with Salesforce goals"
            ),
            Enhancement(
                bullet_point="Led enterprise sales team of 15 reps across 3 regions",
                relevance_score=0.88,
                source_resume="master",
                category="leadership",
                reasoning="Leadership experience valuable for Enterprise Sales role"
            ),
            Enhancement(
                bullet_point="Negotiated multi-million dollar deals with Fortune 500 clients",
                relevance_score=0.85,
                source_resume="master",
                category="technical",
                reasoning="Deal experience relevant to Enterprise Sales position"
            )
        ]

if __name__ == '__main__':
    # Run all tests
    unittest.main()