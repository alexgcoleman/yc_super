from yc_super.readers import read_combined_file
from pathlib import Path
import typer


def main(data_dir: Path, filename: str):
    filepath = data_dir / filename

    super_data = read_combined_file(filepath)
    audit = super_data.audit_super_emp_quarter()

    results_path = data_dir / "yc_super_audit.csv"
    audit.to_csv(results_path)
    print(f'Saved audit results -> {results_path}')


if __name__ == "__main__":
    typer.run(main)
