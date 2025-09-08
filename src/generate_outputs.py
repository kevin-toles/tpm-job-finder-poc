"""
Demo script: Generate job/resume matching results and save as JSON, CSV, Excel
"""
from output_utils import save_json, save_csv, save_excel

# Sample records (replace with real scoring/feedback results)
records = [
    {
        "Job Title": "TPM",
        "Company": "Acme Corp",
        "Location": "Remote",
        "Salary": "$150k",
        "Job Description": "Lead projects",
        "Resume Name": "resume1.pdf",
        "Resume Match Score": 92,
        "Heuristic Score": 88,
        "ML Score": 85,
        "Application Status": "Applied",
        "Resume Feedback Score": 4.5,
        "Resume Feedback Summary": "Strong skills, missing certifications.",
        "Actionable Recommendations": "Add AWS certification."
    },
    {
        "Job Title": "TPM",
        "Company": "Beta Inc",
        "Location": "NYC",
        "Salary": "$140k",
        "Job Description": "Manage teams",
        "Resume Name": "resume2.pdf",
        "Resume Match Score": 80,
        "Heuristic Score": 75,
        "ML Score": 70,
        "Application Status": "Interview",
        "Resume Feedback Score": 3.8,
        "Resume Feedback Summary": "Good fit, improve impact statements.",
        "Actionable Recommendations": "Add quantifiable results."
    }
]

save_json(records)
save_csv(records)
save_excel(records)
print("All outputs saved to secure_storage/files/ folder via SecureStorage.")
