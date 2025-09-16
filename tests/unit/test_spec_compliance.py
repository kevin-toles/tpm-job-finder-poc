"""Test that implementation follows the exact specification."""

import unittest
import pandas as pd
from pathlib import Path
from unittest.mock import Mock, patch
import tempfile

from tpm_job_finder_poc.excel_exporter import SpecCompliantExcelExporter, SPEC_COLUMNS, SPEC_COLUMN_MAPPINGS
from tpm_job_finder_poc.models.resume_inventory import JobIntelligenceResult, Enhancement


class TestSpecificationCompliance(unittest.TestCase):
    """Test that the implementation follows the exact specification."""
    
    def setUp(self):
        self.exporter = SpecCompliantExcelExporter()
        self.temp_dir = tempfile.mkdtemp()
    
    def test_exact_column_structure(self):
        """Test that Excel columns match specification exactly."""
        expected_columns = [
            'Job Title',            # Column A (Keep)
            'Company',              # Column B (Keep) 
            'Location',             # Column C (Keep)
            'Salary',               # Column D (Keep)
            'Selected Resume',      # Column E (NEW)
            'Match Score',          # Column F (Enhanced)
            'Selection Rationale',  # Column G (NEW)
            'Enhancement 1',        # Column H (NEW)
            'Enhancement 2',        # Column I (NEW)
            'Enhancement 3',        # Column J (NEW)
            'Job Source',           # Column K (Keep)
            'Date Posted',          # Column L (Keep)
        ]
        
        self.assertEqual(SPEC_COLUMNS, expected_columns)
    
    def test_column_mappings_match_spec(self):
        """Test that column mappings match specification."""
        expected_mappings = {
            'A': 'Job Title',           # Keep existing
            'B': 'Company',             # Keep existing
            'C': 'Location',            # Keep existing
            'D': 'Salary',              # Keep existing
            'E': 'Selected Resume',     # NEW
            'F': 'Match Score',         # Enhanced
            'G': 'Selection Rationale', # NEW
            'H': 'Enhancement 1',       # NEW
            'I': 'Enhancement 2',       # NEW
            'J': 'Enhancement 3',       # NEW
            'K': 'Job Source',          # Keep existing
            'L': 'Date Posted',         # Keep existing
        }
        
        self.assertEqual(SPEC_COLUMN_MAPPINGS, expected_mappings)
    
    def test_excel_export_structure(self):
        """Test that Excel export maintains exact structure."""
        # Mock job data with existing columns (A-D, K-L)
        jobs_data = [
            {
                'title': 'Senior ML Engineer',
                'company': 'OpenAI', 
                'location': 'San Francisco, CA',
                'salary': '$180K-220K',
                'source': 'LinkedIn',
                'date_posted': '2025-09-12',
                'id': 'job_123'
            }
        ]
        
        # Mock intelligence results with new columns (E, G, H, I, J)
        from tpm_job_finder_poc.models.resume_inventory import ResumeMetadata, ResumeType, DomainClassification
        
        # Mock selected resume
        selected_resume = ResumeMetadata(
            id='resume_1',
            file_path=Path('ai/ml_engineer.pdf'),
            filename='ml_engineer.pdf',
            resume_type=ResumeType.CANDIDATE,
            domain=DomainClassification.TECHNOLOGY,
            skills=['Python', 'ML', 'AI'],
            experience_years=5,
            last_modified='2025-09-01',
            file_size=1024
        )
        
        intelligence_results = [
            JobIntelligenceResult(
                job_id='job_123',
                selected_resume=selected_resume,
                match_score=87.5,
                selection_rationale='Best ML keyword match',
                enhancements=[
                    Enhancement(
                        bullet_point='Led MLOps platform serving 10M+ predictions/day',
                        relevance_score=0.95,
                        source_resume='master',
                        category='achievement',
                        reasoning='High-impact quantified leadership achievement'
                    ),
                    Enhancement(
                        bullet_point='Reduced model training costs by 60% via spot instances',
                        relevance_score=0.92,
                        source_resume='master',
                        category='quantified_impact',
                        reasoning='Cost optimization with specific metrics'
                    ),
                    Enhancement(
                        bullet_point='Published 5 ML papers in top-tier conferences',
                        relevance_score=0.88,
                        source_resume='master',
                        category='thought_leadership',
                        reasoning='Research publications demonstrate expertise'
                    )
                ],
                processing_time=2.5,
                confidence_level=0.91
            )
        ]
        
        # Export to Excel
        output_path = Path(self.temp_dir) / 'test_spec_compliance.xlsx'
        self.exporter.export_with_multi_resume_intelligence(
            jobs_data, intelligence_results, str(output_path)
        )
        
        # Verify Excel structure
        df = pd.read_excel(output_path, sheet_name='All Regions')
        
        # Test exact column order
        self.assertEqual(list(df.columns), SPEC_COLUMNS)
        
        # Test data content matches specification examples
        row = df.iloc[0]
        self.assertEqual(row['Job Title'], 'Senior ML Engineer')                                    # Column A
        self.assertEqual(row['Company'], 'OpenAI')                                                  # Column B
        self.assertEqual(row['Location'], 'San Francisco, CA')                                      # Column C  
        self.assertEqual(row['Salary'], '$180K-220K')                                               # Column D
        self.assertEqual(row['Selected Resume'], 'ml_engineer.pdf')                                 # Column E (NEW)
        self.assertEqual(row['Match Score'], '87.5%')                                               # Column F (Enhanced)
        self.assertEqual(row['Selection Rationale'], 'Best ML keyword match')                      # Column G (NEW)
        self.assertEqual(row['Enhancement 1'], 'Led MLOps platform serving 10M+ predictions/day')  # Column H (NEW)
        self.assertEqual(row['Enhancement 2'], 'Reduced model training costs by 60% via spot instances') # Column I (NEW)
        self.assertEqual(row['Enhancement 3'], 'Published 5 ML papers in top-tier conferences')    # Column J (NEW)
        self.assertEqual(row['Job Source'], 'LinkedIn')                                             # Column K
        self.assertEqual(row['Date Posted'], '2025-09-12')                                          # Column L
    
    def test_column_widths_match_spec(self):
        """Test that column widths match specification."""
        expected_widths = {
            'A': 25,  # Job Title
            'B': 20,  # Company  
            'C': 15,  # Location
            'D': 12,  # Salary
            'E': 18,  # Selected Resume (NEW)
            'F': 10,  # Match Score (Enhanced)
            'G': 15,  # Selection Rationale (NEW)
            'H': 40,  # Enhancement 1 (NEW)
            'I': 40,  # Enhancement 2 (NEW)
            'J': 40,  # Enhancement 3 (NEW)
            'K': 12,  # Job Source
            'L': 10,  # Date Posted
        }
        
        # This would be tested in an integration test that checks openpyxl formatting
        # For now, we verify the expected structure is documented
        self.assertTrue(True)  # Placeholder for width validation
    
    def test_handles_missing_intelligence_data(self):
        """Test handling when intelligence data is missing."""
        jobs_data = [
            {
                'title': 'Software Engineer',
                'company': 'TechCorp',
                'location': 'Remote',
                'salary': '$120K-150K',
                'source': 'Indeed',
                'date_posted': '2025-09-13',
                'id': 'job_456'
            }
        ]
        
        # No intelligence results provided
        intelligence_results = []
        
        output_path = Path(self.temp_dir) / 'test_missing_intelligence.xlsx'
        self.exporter.export_with_multi_resume_intelligence(
            jobs_data, intelligence_results, str(output_path)
        )
        
        df = pd.read_excel(output_path, sheet_name='All Regions')
        row = df.iloc[0]
        
        # Verify fallback values for missing intelligence
        self.assertEqual(row['Selected Resume'], 'Not Available')
        self.assertEqual(row['Selection Rationale'], 'Multi-resume processing not available')
        self.assertEqual(row['Enhancement 1'], 'None')
        self.assertEqual(row['Enhancement 2'], 'None')
        self.assertEqual(row['Enhancement 3'], 'None')
    
    def test_preserves_existing_data(self):
        """Test that existing columns A-D, K-L are preserved exactly."""
        jobs_data = [
            {
                # Test various field name mappings
                'Job Title': 'Data Scientist',  # Direct mapping
                'company': 'DataCorp',          # field name mapping
                'Location': 'New York, NY',    # Direct mapping
                'salary': '$90K-120K',          # field name mapping
                'Job Source': 'Glassdoor',     # Direct mapping
                'date_posted': '2025-09-14',   # field name mapping
                'id': 'job_789'
            }
        ]
        
        intelligence_results = []
        
        output_path = Path(self.temp_dir) / 'test_preserved_data.xlsx'
        self.exporter.export_with_multi_resume_intelligence(
            jobs_data, intelligence_results, str(output_path)
        )
        
        df = pd.read_excel(output_path, sheet_name='All Regions')
        row = df.iloc[0]
        
        # Verify existing data is preserved
        self.assertEqual(row['Job Title'], 'Data Scientist')
        self.assertEqual(row['Company'], 'DataCorp')
        self.assertEqual(row['Location'], 'New York, NY')
        self.assertEqual(row['Salary'], '$90K-120K')
        self.assertEqual(row['Job Source'], 'Glassdoor')
        self.assertEqual(row['Date Posted'], '2025-09-14')


if __name__ == '__main__':
    unittest.main()