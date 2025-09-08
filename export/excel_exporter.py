# ...existing code from job_normalizer/export/excel_exporter.py...
# Excel Exporter for job/resume matching results
import pandas as pd
from typing import List, Dict, Any, Optional

EXPORT_COLUMNS = [
	"Job Title",
	"Company",
	"Location",
	"Salary",
	"Job Description",
	"Resume Name",
	"Resume Match Score",
	"Heuristic Score",
	"ML Score",
	"Application Status",
	"Resume Feedback Score",
	"Resume Feedback Summary",
	"Actionable Recommendations"
]

def export_to_excel(records: List[Dict[str, Any]], output_path: str, columns: Optional[List[str]] = None) -> None:
	"""
	Export job/resume matching results to Excel, including feedback columns.
	Args:
		records: List of dicts, each representing a job/resume match with feedback.
		output_path: Path to save the Excel file.
		columns: Optional list of columns to export (defaults to EXPORT_COLUMNS).
	"""
	cols = columns if columns else EXPORT_COLUMNS
	df = pd.DataFrame(records)
	# Ensure all columns exist
	for col in cols:
		if col not in df.columns:
			df[col] = ""
	df = df[cols]
	# Formatting: set column widths, wrap text for feedback columns
	with pd.ExcelWriter(output_path, engine="openpyxl") as writer:
		df.to_excel(writer, index=False)
		worksheet = writer.sheets["Sheet1"]
		for idx, col in enumerate(cols):
			width = 20 if col not in ["Resume Feedback Summary", "Actionable Recommendations"] else 40
			worksheet.column_dimensions[chr(65 + idx)].width = width
		# Optionally, set text wrap for feedback columns (requires openpyxl)
		try:
			from openpyxl.styles import Alignment
			for row in worksheet.iter_rows(min_row=2, max_row=worksheet.max_row, min_col=cols.index("Resume Feedback Summary")+1, max_col=cols.index("Actionable Recommendations")+1):
				for cell in row:
					cell.alignment = Alignment(wrap_text=True)
		except Exception:
			pass
