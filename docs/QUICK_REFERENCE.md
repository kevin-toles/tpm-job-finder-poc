# Quick Structure Reference

**📁 Where does my file go?**

| File Type | Location | Example |
|-----------|----------|---------|
| 🐍 **Application Code** | `tpm_job_finder_poc/[component]/` | `tpm_job_finder_poc/new_service/main.py` |
| 📝 **Component Docs** | `docs/components/` | `docs/components/new_service.md` |
| 🔧 **Dev Scripts** | `scripts/` | `scripts/my_automation.py` |
| 🧪 **Unit Tests** | `tests/unit/test_[component]/` | `tests/unit/test_new_service/` |
| ⚙️ **Config Files** | `tpm_job_finder_poc/config/` | `tpm_job_finder_poc/config/settings.json` |
| 📊 **Log Files** | `logs/` | `logs/app.log` |
| 📈 **Results** | `output/` | `output/data.xlsx` |

**🔄 Quick Commands:**

```bash
# Run tests
python scripts/run_tests.py

# Clean cache
find . -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true

# Check imports
python -c "from tpm_job_finder_poc.job_aggregator.main import JobAggregatorService; print('✅ OK')"

# Generate docs
python scripts/generate_html.py

# Run automation
python scripts/demo_automation.py
```

**📚 Full Guide**: See [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md)
