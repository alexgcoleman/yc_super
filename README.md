# yc_super
Yellow Canary - Python Test

## Calculations
- A payslip is matched to a super disbursement when the payslip `end` date falls within a disbursements `pay_period_from` and `pay_period_to`
- Super is only considered "earned" on the date of the payslip  `end`

## Install/Development Notes
- requires python 3.10
- install dev environment `pip install -r requirements.txt`
- VSCode settings for workspace in `.vscode/settings.json`
  - Notebook file root to project folder (makes notebooks less brittle to moving)

## Thoughts
For a company to correctly pay super for an employee they must pay their staff 9.5% of Pay Codes that are treated as Ordinary Time Earnings (OTE) within 28 days after the end of the quarter. Quarters run from Jan-March, Apr-June, Jul-Sept, Oct-Dec.

- Disbursements have 3 time columns:
  - `payment_made`
  - `pay_period_from`
  - `pay_period_to`

- These columns 'straddle' multiple quarters for some rows, i.e. some rows have different quarters for:
  - `payment_made` and `pay_period_from`
  - `payment_made` and `pay_period_to`
  - `pay_period_to` and `pay_period_from`

- The columns `pay_period_from` and `pay_period_to` represent a continous timespan series, which means a single payslip would match fall within only one disbursment pay period span.

- The phrase "...must pay their staff 9.5% of pay codes treated as OTE **within** 28 days" implies only a maximum time period between 'earned' super and 'disbursed' super.

- However example given as 