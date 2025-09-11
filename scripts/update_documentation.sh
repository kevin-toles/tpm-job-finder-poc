#!/bin/bash

# Documentation Update Script - Fix Outdated Architecture References
# This script updates all documentation to reflect the current clean architecture

echo "🔄 Updating all documentation to reflect current architecture..."

# Fix component README files that moved to docs/components/
echo "📝 Updating component documentation references..."

# Update job aggregator documentation
if [ -f "docs/components/job_aggregator.md" ]; then
    sed -i 's/scraping_service_v2/tpm_job_finder_poc.scraping_service/g' docs/components/job_aggregator.md
    sed -i 's/via scraping_service_v2/via tpm_job_finder_poc.scraping_service/g' docs/components/job_aggregator.md
    echo "✅ Updated job_aggregator.md"
fi

# Update docs README
sed -i 's|../scraping_service_v2/README.md|../tpm_job_finder_poc/scraping_service/README.md|g' docs/README.md
sed -i 's|Built into scraping_service_v2|Built into tpm_job_finder_poc.scraping_service|g' docs/README.md
echo "✅ Updated docs/README.md"

# Update STUB_CATALOG.md
sed -i 's|scraping_service_v2/scrapers/|tpm_job_finder_poc/scraping_service/scrapers/|g' docs/STUB_CATALOG.md
sed -i 's|from scraping_service_v2.scrapers.base|from tpm_job_finder_poc.scraping_service.scrapers.base_scraper|g' docs/STUB_CATALOG.md
sed -i 's|./scraping_service_v2/README.md|../tpm_job_finder_poc/scraping_service/README.md|g' docs/STUB_CATALOG.md
echo "✅ Updated STUB_CATALOG.md"

# Update STUBS_README.md
sed -i 's|scraping_service_v2/|tpm_job_finder_poc/scraping_service/|g' docs/STUBS_README.md
sed -i 's|from scraping_service_v2.orchestrator|from tpm_job_finder_poc.scraping_service.core.orchestrator|g' docs/STUBS_README.md
sed -i 's|src/output_utils.py|tpm_job_finder_poc/storage/output_utils.py|g' docs/STUBS_README.md
sed -i 's|src/enrichment/|tpm_job_finder_poc/enrichment/|g' docs/STUBS_README.md
sed -i 's|src/ml_scoring_api.py|tpm_job_finder_poc/enrichment/ml_scorer.py|g' docs/STUBS_README.md
sed -i 's|src/embeddings_service.py|tpm_job_finder_poc/enrichment/embeddings.py|g' docs/STUBS_README.md
sed -i 's|src/import_analysis.py|scripts/import_analysis.py|g' docs/STUBS_README.md
sed -i 's|src/analytics_shared.py|tpm_job_finder_poc/enrichment/analytics_shared.py|g' docs/STUBS_README.md
echo "✅ Updated STUBS_README.md"

# Update Careerjet Integration Plan
sed -i 's|scraping_service_v2/|tpm_job_finder_poc/scraping_service/|g' docs/Careerjet_Integration_Plan.md
echo "✅ Updated Careerjet_Integration_Plan.md"

# Update docs/api/README.md if it exists
if [ -f "docs/api/README.md" ]; then
    sed -i 's|from each Python module in `src/`|from each Python module in `tpm_job_finder_poc/`|g' docs/api/README.md
    echo "✅ Updated docs/api/README.md"
fi

# Update any remaining files in root that were moved to docs/
for file in AUTOMATION_README.md CODECOV.md RELEASE.md STUBS_README.md STUB_CATALOG.md; do
    if [ -f "docs/$file" ]; then
        # Update path references
        sed -i 's|scraping_service_v2/|tpm_job_finder_poc/scraping_service/|g' "docs/$file"
        sed -i 's|./scraping_service_v2/|../tpm_job_finder_poc/scraping_service/|g' "docs/$file"
        sed -i 's|cross_component_tests/|tests/cross_component_tests/|g' "docs/$file"
        sed -i 's|src/|tpm_job_finder_poc/|g' "docs/$file"
        echo "✅ Updated docs/$file"
    fi
done

echo "🎉 Documentation update complete!"
echo ""
echo "📋 Summary of updates:"
echo "• Updated all scraping_service_v2 references to tpm_job_finder_poc.scraping_service"
echo "• Fixed old src/ path references to tpm_job_finder_poc/"
echo "• Updated cross_component_tests paths to tests/cross_component_tests"
echo "• Corrected component documentation paths"
echo ""
echo "✅ All documentation now reflects the current clean architecture!"
