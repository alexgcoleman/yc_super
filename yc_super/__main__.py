from yc_super.readers import read_combined_file
from yc_super.super_audit import audit_super_emp_qtr
from pathlib import Path
import typer


def main(data_dir: Path, filename: str):
    filepath = data_dir / filename

    super_data = read_combined_file(filepath)
    audit = audit_super_emp_qtr(super_data)

    audit_formatted = audit.money.format_c_as_d()

    results_path = data_dir / "yc_super_audit.csv"
    audit_formatted.to_csv(results_path)
    print(f'\nSaved audit results -> {results_path}\n')

    print(audit_formatted[['ote', 'payable',
          'disbursed', 'payable-disbursed']])


if __name__ == "__main__":
    typer.run(main)
