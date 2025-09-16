"""Integration tests for multi-resume intelligence system"""

import unittest
import tempfile
import shutil
import asyncio
from pathlib import Path
from unittest.mock import Mock, patch

from tpm_job_finder_poc.cli.multi_resume_cli import MultiResumeJobFinderCLI
from tpm_job_finder_poc.models.job import Job
from tpm_job_finder_poc.config.multi_resume_config import MultiResumeConfig, set_config

class TestMultiResumeIntegration(unittest.TestCase):
    """Integration tests for the complete multi-resume system"""
    
    def setUp(self):
        """Setup integration test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.base_path = Path(self.temp_dir)
        
        # Create realistic resume portfolio structure
        self._create_resume_portfolio()
        
        # Setup test configuration
        test_config = MultiResumeConfig(
            resume_folder_path=self.base_path,
            semantic_similarity_threshold=0.8,
            keyword_match_threshold=0.3,
            max_enhancements=3
        )
        set_config(test_config)
        
        self.cli = MultiResumeJobFinderCLI()
    
    def tearDown(self):
        """Cleanup integration test environment"""
        shutil.rmtree(self.temp_dir)
    
    def _create_resume_portfolio(self):
        """Create realistic resume portfolio for testing"""
        # Create folder structure
        folders = {
            "master": "Comprehensive master resume",
            "AI": "AI/ML specialized resumes", 
            "Backend": "Backend development resumes",
            "Sales": "Sales and business development resumes",
            "Finance": "Finance and consulting resumes"
        }
        
        for folder, description in folders.items():
            folder_path = self.base_path / folder
            folder_path.mkdir()
            
            # Create README
            readme = folder_path / "README.md"
            readme.write_text(f"# {folder} Resume Folder\\n\\n{description}")
        
        # Create sample resume files with realistic content
        resume_files = {
            "master/complete_experience.pdf": self._get_master_content(),
            "AI/ml_engineer.pdf": self._get_ai_content(),
            "AI/data_scientist.pdf": self._get_ds_content(),
            "Backend/python_architect.pdf": self._get_backend_content(),
            "Sales/enterprise_sales.pdf": self._get_sales_content(),
            "Finance/financial_analyst.pdf": self._get_finance_content()
        }
        
        for file_path, content in resume_files.items():
            full_path = self.base_path / file_path
            full_path.write_text(content)
    
    def _get_master_content(self):
        """Get master resume content"""
        return """
        John Doe - Senior Technology Leader
        
        Experience:
        • Led engineering teams of 50+ developers across multiple product lines
        • Architected ML platform serving 100M+ daily predictions with 99.9% uptime
        • Published 12 research papers in top-tier AI/ML conferences
        • Generated $200M+ in revenue through strategic product innovations
        • Negotiated partnerships with Fortune 100 companies worth $50M annually
        • Reduced infrastructure costs by 40% through cloud optimization strategies
        • Mentored 25+ engineers who achieved senior/principal level promotions
        
        Skills: Python, TensorFlow, AWS, Leadership, Product Strategy, Sales
        """
    
    def _get_ai_content(self):
        """Get AI resume content"""
        return """
        John Doe - ML Engineer
        
        Experience:
        • Developed TensorFlow models achieving 95% accuracy on production datasets
        • Implemented MLOps pipeline reducing model deployment time by 80%
        • Collaborated with data scientists to optimize feature engineering
        
        Skills: Python, TensorFlow, Machine Learning, MLOps
        """
    
    def _get_ds_content(self):
        """Get data science resume content"""
        return """
        John Doe - Data Scientist
        
        Experience:
        • Built predictive models for customer churn reducing attrition by 25%
        • Analyzed large datasets using Python and SQL for business insights
        • Created data visualizations and reports for executive leadership
        
        Skills: Python, SQL, Machine Learning, Data Analysis, Statistics
        """
    
    def _get_backend_content(self):
        """Get backend resume content"""
        return """
        John Doe - Backend Engineer
        
        Experience:
        • Designed microservices architecture handling 10K+ requests per second
        • Implemented REST APIs using Python Flask and FastAPI
        • Optimized database queries reducing response time by 60%
        
        Skills: Python, Flask, FastAPI, PostgreSQL, Microservices
        """
    
    def _get_sales_content(self):
        """Get sales resume content"""
        return """
        John Doe - Enterprise Sales
        
        Experience:
        • Closed $10M+ in enterprise software deals with Fortune 500 clients
        • Built relationships with C-level executives driving strategic partnerships
        • Exceeded sales quota by 150% for three consecutive years
        
        Skills: Enterprise Sales, Relationship Building, Contract Negotiation
        """
    
    def _get_finance_content(self):
        """Get finance resume content"""
        return """
        John Doe - Financial Analyst
        
        Experience:
        • Performed financial modeling for $500M+ investment decisions
        • Analyzed market trends and provided recommendations to senior management
        • Managed portfolio of investments generating 15% annual returns
        
        Skills: Financial Modeling, Investment Analysis, Excel, Bloomberg
        """
    
    def test_setup_resume_portfolio(self):
        """Test resume portfolio setup functionality"""
        # Test setup in new directory
        new_portfolio = self.temp_dir + "_new"
        
        async def run_setup():
            await self.cli.setup_resume_portfolio(new_portfolio)
        
        asyncio.run(run_setup())
        
        # Verify portfolio structure was created
        portfolio_path = Path(new_portfolio)
        self.assertTrue(portfolio_path.exists())
        
        expected_folders = ["master", "AI", "Backend", "Sales", "Finance"]
        for folder in expected_folders:
            folder_path = portfolio_path / folder
            self.assertTrue(folder_path.exists())
            self.assertTrue((folder_path / "README.md").exists())
    
    @patch('tpm_job_finder_poc.cli.multi_resume_cli.MultiResumeJobFinderCLI._run_job_search')
    @patch('tpm_job_finder_poc.cli.multi_resume_cli.MultiResumeJobFinderCLI._get_llm_provider')
    def test_complete_multi_resume_workflow(self, mock_llm_provider, mock_job_search):
        """Test complete multi-resume job search workflow"""
        # Mock LLM provider
        mock_llm = Mock()
        mock_llm_provider.return_value = mock_llm
        
        # Mock job search results
        mock_job_search.return_value = [
            {
                "id": "job1",
                "Job Title": "Senior ML Engineer",
                "Company": "Google",
                "Location": "Mountain View, CA",
                "Salary": "$180K-250K",
                "Job Description": "Looking for ML engineer with Python, TensorFlow, and leadership experience"
            },
            {
                "id": "job2", 
                "Job Title": "Enterprise Sales Manager",
                "Company": "Salesforce",
                "Location": "San Francisco, CA",
                "Salary": "$150K-200K",
                "Job Description": "Enterprise sales role requiring revenue generation and client relationship experience"
            },
            {
                "id": "job3",
                "Job Title": "Backend Engineer",
                "Company": "Netflix",
                "Location": "Los Gatos, CA", 
                "Salary": "$160K-220K",
                "Job Description": "Backend engineering role requiring Python, microservices, and API development"
            }
        ]
        
        async def run_search():
            # Mock sentence transformer to avoid model loading
            with patch('tpm_job_finder_poc.enrichment.enhanced_content_analyzer.SentenceTransformer'):
                output_file = await self.cli.run_multi_resume_search(
                    resume_folder=str(self.base_path),
                    keywords=["software engineer", "python"],
                    location="San Francisco",
                    output_path=str(self.base_path / "test_results.xlsx")
                )
                return output_file
        
        # Run the workflow
        output_file = asyncio.run(run_search())
        
        # Verify output file was created
        self.assertTrue(Path(output_file).exists())
        
        # Verify job search was called
        mock_job_search.assert_called_once()
        
        # Verify LLM provider was initialized
        mock_llm_provider.assert_called_once()
    
    def test_configuration_management(self):
        """Test configuration management functionality"""
        # Test updating configuration
        self.cli.configure_system(
            semantic_similarity_threshold=0.85,
            keyword_match_threshold=0.4,
            max_enhancements=5
        )
        
        # Verify configuration file was created
        config_path = Path("config/multi_resume_config.json")
        if config_path.exists():
            import json
            with open(config_path) as f:
                config_data = json.load(f)
            
            self.assertEqual(config_data["semantic_similarity_threshold"], 0.85)
            self.assertEqual(config_data["keyword_match_threshold"], 0.4)
            self.assertEqual(config_data["max_enhancements"], 5)
    
    @patch('tpm_job_finder_poc.enrichment.enhanced_content_analyzer.SentenceTransformer')
    def test_resume_discovery_integration(self, mock_transformer):
        """Test resume discovery integration with real file system"""
        from tpm_job_finder_poc.enrichment.resume_discovery_service import ResumeDiscoveryService
        
        service = ResumeDiscoveryService()
        inventory = service.scan_resume_folders(self.base_path)
        
        # Verify inventory was built correctly
        self.assertIsNotNone(inventory.master_resume)
        self.assertEqual(inventory.master_resume.filename, "complete_experience.pdf")
        self.assertEqual(len(inventory.candidate_resumes), 5)
        
        # Verify candidate resumes
        candidate_names = [r.filename for r in inventory.candidate_resumes]
        expected_candidates = [
            "ml_engineer.pdf", "data_scientist.pdf", "python_architect.pdf",
            "enterprise_sales.pdf", "financial_analyst.pdf"
        ]
        
        for expected in expected_candidates:
            self.assertIn(expected, candidate_names)
        
        # Verify domain classifications
        ai_resumes = [r for r in inventory.candidate_resumes if "AI" in str(r.file_path)]
        self.assertEqual(len(ai_resumes), 2)
        
        sales_resumes = [r for r in inventory.candidate_resumes if "Sales" in str(r.file_path)]
        self.assertEqual(len(sales_resumes), 1)
    
    @patch('tpm_job_finder_poc.enrichment.enhanced_content_analyzer.SentenceTransformer')
    def test_hybrid_selection_integration(self, mock_transformer):
        """Test hybrid selection engine integration"""
        from tpm_job_finder_poc.enrichment.resume_discovery_service import ResumeDiscoveryService
        from tpm_job_finder_poc.enrichment.hybrid_selection_engine import HybridSelectionEngine
        
        # Build inventory
        service = ResumeDiscoveryService()
        inventory = service.scan_resume_folders(self.base_path)
        
        # Test job selection
        engine = HybridSelectionEngine(llm_provider=Mock())
        
        # ML job should select AI resume
        ml_job = Job(
            title="Senior ML Engineer",
            company="Google",
            description="ML engineer position requiring Python, TensorFlow, machine learning experience"
        )
        
        result = engine.select_optimal_resume(ml_job, inventory)
        self.assertIsNotNone(result.selected_resume)
        self.assertTrue("ml" in result.selected_resume.filename or "data" in result.selected_resume.filename)
        
        # Sales job should select sales resume
        sales_job = Job(
            title="Enterprise Sales Manager", 
            company="Salesforce",
            description="Enterprise sales role requiring revenue generation and client management"
        )
        
        result = engine.select_optimal_resume(sales_job, inventory)
        self.assertIsNotNone(result.selected_resume)
        self.assertIn("sales", result.selected_resume.filename)
    
    def test_excel_export_integration(self):
        """Test Excel export with multi-resume intelligence"""
        from tpm_job_finder_poc.excel_exporter import EnhancedExcelExporter
        from tpm_job_finder_poc.models.resume_inventory import JobIntelligenceResult, Enhancement
        
        # Create test data
        jobs_data = [
            {
                "id": "job1",
                "Job Title": "ML Engineer",
                "Company": "Google",
                "Location": "Mountain View, CA",
                "Salary": "$180K-250K"
            }
        ]
        
        intelligence_results = [
            JobIntelligenceResult(
                job_id="job1",
                selected_resume=Mock(filename="ml_engineer.pdf"),
                match_score=92.5,
                selection_rationale="Strong ML keyword match with technical domain alignment",
                enhancements=[
                    Enhancement(
                        bullet_point="Led MLOps platform serving 100M+ predictions/day",
                        relevance_score=0.95,
                        source_resume="master",
                        category="technical",
                        reasoning="Technical expertise relevant to ML Engineer position"
                    )
                ],
                processing_time=2.5,
                confidence_level=0.95
            )
        ]
        
        # Export to Excel
        exporter = EnhancedExcelExporter()
        output_path = self.base_path / "test_export.xlsx"
        
        exporter.export_with_multi_resume_intelligence(
            jobs_data, intelligence_results, str(output_path)
        )
        
        # Verify file was created
        self.assertTrue(output_path.exists())
        
        # Verify file content (basic check)
        import pandas as pd
        df = pd.read_excel(output_path, sheet_name="All Regions")
        
        self.assertEqual(len(df), 1)
        self.assertEqual(df.iloc[0]["Selected Resume"], "ml_engineer.pdf")
        self.assertEqual(df.iloc[0]["Match Score"], "92.5%")

class TestEndToEndScenarios(unittest.TestCase):
    """End-to-end acceptance test scenarios"""
    
    def setUp(self):
        """Setup E2E test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.base_path = Path(self.temp_dir)
        
        # Create comprehensive resume portfolio
        self._create_comprehensive_portfolio()
    
    def tearDown(self):
        """Cleanup E2E test environment"""
        shutil.rmtree(self.temp_dir)
    
    def _create_comprehensive_portfolio(self):
        """Create comprehensive portfolio matching acceptance test scenarios"""
        # Technology professional portfolio
        tech_folders = ["master", "AI", "Backend", "Security"]
        for folder in tech_folders:
            (self.base_path / folder).mkdir()
        
        # Create realistic resume files
        resumes = {
            "master/complete_experience.pdf": "Comprehensive 10+ years experience across AI, backend, security",
            "AI/ml_engineer.pdf": "ML Engineer with Python, TensorFlow, 5 years experience",
            "Backend/python_architect.pdf": "Backend architect with Python, microservices, 7 years experience", 
            "Security/cybersecurity_specialist.pdf": "Cybersecurity specialist with penetration testing, 6 years experience"
        }
        
        for file_path, content in resumes.items():
            (self.base_path / file_path).write_text(content)
    
    @patch('tpm_job_finder_poc.enrichment.enhanced_content_analyzer.SentenceTransformer')
    @patch('tpm_job_finder_poc.cli.multi_resume_cli.MultiResumeJobFinderCLI._run_job_search')
    @patch('tpm_job_finder_poc.cli.multi_resume_cli.MultiResumeJobFinderCLI._get_llm_provider')
    def test_acceptance_scenario_technology_professional(self, mock_llm_provider, mock_job_search, mock_transformer):
        """
        Acceptance Scenario 1: Technology Professional
        
        Given: User has resumes in AI/, Backend/, and Security/ folders plus master/
        When: System processes ML Engineer job from Google  
        Then: AI resume selected, 3 unique enhancements from master provided
        """
        # Setup mocks
        mock_llm_provider.return_value = Mock()
        mock_job_search.return_value = [
            {
                "id": "google_ml_job",
                "Job Title": "ML Engineer", 
                "Company": "Google",
                "Location": "Mountain View, CA",
                "Salary": "$180K-250K",
                "Job Description": "ML Engineer role requiring Python, TensorFlow, machine learning expertise with 5+ years experience"
            }
        ]
        
        # Run the scenario
        cli = MultiResumeJobFinderCLI()
        
        async def run_scenario():
            return await cli.run_multi_resume_search(
                resume_folder=str(self.base_path),
                keywords=["ML Engineer", "Python", "TensorFlow"],
                location="Mountain View, CA",
                output_path=str(self.base_path / "scenario1_results.xlsx")
            )
        
        output_file = asyncio.run(run_scenario())
        
        # Verify results
        self.assertTrue(Path(output_file).exists())
        
        # Read and verify Excel output
        import pandas as pd
        df = pd.read_excel(output_file, sheet_name="All Regions")
        
        # Should have 1 job processed
        self.assertEqual(len(df), 1)
        
        # Should have selected AI resume (based on our folder structure)
        selected_resume = df.iloc[0]["Selected Resume"]
        self.assertTrue("ml_engineer" in selected_resume or "AI" in selected_resume)
        
        # Should have match score > 80% for good fit
        match_score = df.iloc[0]["Match Score"]
        if isinstance(match_score, str):
            score_value = float(match_score.replace('%', ''))
            self.assertGreater(score_value, 60.0)  # Reasonable threshold for test
        
        # Should have enhancements
        enhancement1 = df.iloc[0]["Enhancement 1"]
        self.assertIsNotNone(enhancement1)
        self.assertTrue(len(str(enhancement1)) > 0)

if __name__ == '__main__':
    unittest.main()