# yc_super
Yellow Canary - Python Test

## Calculations
- Years/Quarters are using calander years, not financial years
  - `2020-Q1` represents the interval `[2020-01-01, 2020-03-31]`
- The calculation `payment_made - 28 days` determines which quarter a disbursement is applied to (the number of days is configurable)
  - See [What Quarter a Disbursement Applies To](#what-quarter-a-disbursement-applies-to) for some reasoning on this, was a little confused by some of the ambiguous wording.

## Installation
- requires python 3.10
- install `yc_super` package: `pip install .`
- install dev environment `pip install -r requirements.txt`
- VSCode settings for workspace in `.vscode/settings.json`
  - Notebook file root to project folder (makes notebooks less brittle to moving)
  - Only needed for dev environment

## Reasoning/Notes

### What Quarter a Disbursement Applies To
- The phrase "...must pay their staff 9.5% of pay codes treated as OTE **within** 28 days" implies only a **maximum** time period between 'earned' super and 'disbursed' super.
  - i.e. a Disbursement payed on the 22nd of January could either:
    - Apply to Q4 the previous year (within 28 days of end of the quarter)
    - Apply to Q1 of the current year (if a payslip came out before 22 of Jan)

- However the phrase "Super earned between 1st Jan and the 31 st of March (Q1) will need to be paid/Disbursed between the 29th Jan - 28th of Apr." indicates a hard limit 
  - i.e. disbursement payed on the 22nd of July could only be applied to Q4 on the previous quarter, as any super earned on the 1st of Jan **needs** to be paid between 29th Jan - 28th Apr

- Disbursements have 3 time columns:
  - `payment_made`
  - `pay_period_from`
  - `pay_period_to`
  
- The columns `pay_period_from` and `pay_period_to` represent a continous timespan series, which means a single payslip would match fall within only one disbursment pay period span.
  - *Update* This rule is broken for employee `2355`, who has an additional disbursement, with a pay period that is encompassed by its surrounding disbursements.
  - There are also some non-continious disbursement periods for some employees (gaps in disbursement pay period coverage)