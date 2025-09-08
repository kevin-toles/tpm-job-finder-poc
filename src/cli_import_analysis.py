import argparse
from src.import_analysis import ImportAnalysis

def main():
    parser = argparse.ArgumentParser(description="Run Import Analysis and save results.")
    parser.add_argument("excel_path", help="Path to Excel file to analyze")
    parser.add_argument("output_path", help="Path to save JSON results")
    args = parser.parse_args()

    analysis = ImportAnalysis()
    results = analysis.analyze(args.excel_path)
    analysis.save_results(results, args.output_path)
    print(f"Analysis complete. Results saved to {args.output_path}")

if __name__ == "__main__":
    main()
