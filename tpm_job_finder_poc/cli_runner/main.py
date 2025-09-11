import os
import pandas as pd

class CLIRunner:
    def _export_results(self, df, out_path, fmt):
        if fmt == "csv":
            df.to_csv(out_path, index=False)
        elif fmt == "excel":
            # Always specify engine for Excel output
            df.to_excel(out_path, index=False, engine="openpyxl")
        elif fmt == "json":
            df.to_json(out_path, orient="records")
        else:
            raise ValueError(f"Unsupported export format: {fmt}")

    def _validate_args(self, args):
        for attr in ["input", "resume", "applied"]:
            path = getattr(args, attr, None)
            if path and not os.path.exists(str(path)):
                raise FileNotFoundError(f"File not found: {path}")
