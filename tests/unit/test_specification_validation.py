"""Final validation test to verify the enhanced Excel export matches specification exactly."""

import unittest
import tempfile
from pathlib import Path

import pandas as pd

from tpm_job_finder_poc.cli.geographic_excel_exporter import GeographicExcelExporter
from tpm_job_finder_poc.models.resume_inventory import (
    JobIntelligenceResult, Enhancement, ResumeMetadata, 
    ResumeType, DomainClassification
)


class TestSpecificationValidation(unittest.TestCase):
    """Final validation that implementation matches specification exactly."""
    
    def setUp(self):
        self.exporter = GeographicExcelExporter()
        self.temp_dir = tempfile.mkdtemp()
    
    def test_enhanced_export_matches_specification_exactly(self):
        """Test that enhanced export produces exactly the column structure from specification."""
        
        # Create test data matching specification example
        jobs = [
            {
                'id': 'job_123',
                'title': 'Senior ML Engineer',
                'company': 'OpenAI',
                'location': 'United States',
                'match_score': 75.0,  # Original score (will be enhanced)
                'usd_equivalent': 200000,  # Salary
                'source_site': 'LinkedIn',
                'posted_date': '2025-09-12'
            }
        ]
        
        # Create intelligence result matching specification example
        selected_resume = ResumeMetadata(
            id='resume_123',
            filename='ai_ml_engineer.pdf',  # This becomes "ai_ml_engineer.pdf" in Column E
            file_path=Path('ai/ml_engineer.pdf'),
            resume_type=ResumeType.CANDIDATE,
            domain=DomainClassification.TECHNOLOGY,
            skills=['Python', 'ML', 'TensorFlow'],
            experience_years=5,
            last_modified='2025-09-01',
            file_size=1024
        )
        
        intelligence_results = [
            JobIntelligenceResult(
                job_id='job_123',
                selected_resume=selected_resume,
                match_score=87.5,  # Enhanced score
                selection_rationale='Best ML keyword match',  # Column G
                enhancements=[
                    Enhancement(
                        bullet_point='Led MLOps platform serving 10M+ predictions/day',  # Column H
                        relevance_score=0.95,
                        source_resume='master',
                        category='achievement',
                        reasoning='High-impact quantified leadership'
                    ),
                    Enhancement(
                        bullet_point='Reduced model training costs by 60% via spot instances',  # Column I
                        relevance_score=0.92,
                        source_resume='master',
                        category='cost_optimization',
                        reasoning='Quantified cost savings'
                    ),
                    Enhancement(
                        bullet_point='Published 5 ML papers in top-tier conferences',  # Column J
                        relevance_score=0.88,
                        source_resume='master',
                        category='thought_leadership',
                        reasoning='Research publications'
                    )
                ],
                processing_time=2.5,
                confidence_level=0.91
            )
        ]
        
        # Create enhanced workbook
        workbook = self.exporter.create_enhanced_regional_workbook(jobs, intelligence_results)
        
        # Save and read back
        output_path = Path(self.temp_dir) / 'spec_validation.xlsx'
        workbook.save(output_path)
        
        # Find the regional sheet with data
        sheet_names = [ws.title for ws in workbook.worksheets]
        regional_sheet = None
        for name in sheet_names:
            if name != '📊 Summary':
                regional_sheet = name
                break
        
        self.assertIsNotNone(regional_sheet, f"No regional sheet found in {sheet_names}")
        
        # Read the data
        df = pd.read_excel(output_path, sheet_name=regional_sheet)
        
        # The data table should start after the regional intelligence section
        # Find the header row
        header_row_idx = None
        for i in range(len(df)):
            if 'Job Title' in str(df.iloc[i, 0]):  # Look for specification column A header
                header_row_idx = i
                break
        
        self.assertIsNotNone(header_row_idx, "Could not find 'Job Title' header in Excel export")
        
        # Extract the headers
        headers = []
        for col in range(12):  # Columns A through L
            header_val = df.iloc[header_row_idx, col]
            if pd.notna(header_val):
                headers.append(str(header_val))
            else:
                break
        
        # Verify exact column structure from specification
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
        
        # Verify headers match exactly
        self.assertEqual(headers, expected_columns, 
                        f"Column headers don't match specification.\nExpected: {expected_columns}\nActual: {headers}")
        
        # Verify data values match specification examples
        data_row_idx = header_row_idx + 1
        self.assertLess(data_row_idx, len(df), "No data row found after headers")
        
        # Extract data row values
        row_data = []
        for col in range(12):
            val = df.iloc[data_row_idx, col]
            row_data.append(str(val) if pd.notna(val) else '')
        
        # Verify specific values match specification examples
        self.assertEqual(row_data[0], 'Senior ML Engineer')                                           # Column A: Job Title
        self.assertEqual(row_data[1], 'OpenAI')                                                      # Column B: Company
        self.assertEqual(row_data[2], 'United States')                                               # Column C: Location
        self.assertEqual(row_data[3], '$200,000')                                                    # Column D: Salary
        self.assertEqual(row_data[4], 'ai_ml_engineer.pdf')                                          # Column E: Selected Resume
        self.assertEqual(row_data[5], '87.5%')                                                       # Column F: Match Score (Enhanced)
        self.assertEqual(row_data[6], 'Best ML keyword match')                                       # Column G: Selection Rationale
        self.assertEqual(row_data[7], 'Led MLOps platform serving 10M+ predictions/day')            # Column H: Enhancement 1
        self.assertEqual(row_data[8], 'Reduced model training costs by 60% via spot instances')     # Column I: Enhancement 2
        self.assertEqual(row_data[9], 'Published 5 ML papers in top-tier conferences')              # Column J: Enhancement 3
        self.assertEqual(row_data[10], 'LinkedIn')                                                   # Column K: Job Source
        self.assertEqual(row_data[11], '2025-09-12')                                                 # Column L: Date Posted
        
        print("✅ SUCCESS: Enhanced Excel export matches specification exactly!")
        print(f"   Columns A-L: {headers}")
        print(f"   Data values match specification examples")
        print(f"   Multi-resume intelligence properly integrated")


if __name__ == '__main__':
    unittest.main()