# yc_super
Yellow Canary - Python Test

Attempted to document my thought/dev process with [github issues](https://github.com/alexgcoleman/yc_super/issues?q=is%3Aissue+sort%3Acreated-asc)
## Installation
- requires python 3.10
- install `yc_super` package: `pip install .`
- install dev environment `pip install -r requirements.txt`
- VSCode settings for workspace in `.vscode/settings.json`
  - Notebook file root to project folder (makes notebooks less brittle to moving)
  - Only needed for dev environment

## Usage
After installation, run using:
```
> python -m yc_super [PATH_TO_DIRECTORY] [FILENAME]
```
It will audit the super file located at `PATH_TO_DIRECTORY/FILENAME` and output results in a `yc_super_audit.csv` file to the same directory, as well as print summarised results to the terminal:
```
➜ python -m yc_super data "Sample Super Data.xlsx"

Saved audit results -> data/yc_super_audit.csv

                             ote   payable disbursed payable-disbursed
employee_code quarter
1155          2017-Q3  $24396.73  $2317.68  $2638.08          -$320.40
              2017-Q4  $29534.91  $2805.81  $2672.81           $133.00
              2018-Q1    $401.92    $38.18     $0.00            $38.18
1963          2017-Q3  $21108.96  $2005.35  $2301.07          -$295.72
              2017-Q4  $25356.75  $2408.89  $2391.59            $17.30
              2018-Q1  $21132.91  $2007.62  $1976.52            $31.10
              2018-Q2  $31493.82  $2991.91  $2017.63           $974.28
2355          2017-Q3  $23602.52  $2242.23  $2591.52          -$349.29
              2017-Q4  $29319.54  $2785.35  $2765.40            $19.95
              2018-Q1  $34835.56  $3309.37  $3269.50            $39.87
              2018-Q2  $26333.16  $2501.65  $2361.78           $139.87
              2018-Q3  $33518.94  $3184.29  $2888.42           $295.87
              2018-Q4  $29271.78  $2780.81  $2755.41            $25.40
              2019-Q1  $25809.77  $2451.92  $2444.67             $7.25
              2019-Q2  $29631.62  $2815.00  $2814.98             $0.02
              2019-Q3      $0.00     $0.00   $393.63          -$393.63
50015418      2017-Q3  $24772.26  $2353.36  $2731.62          -$378.26
              2017-Q4  $34420.16  $3269.91  $3012.99           $256.92
              2018-Q1  $25161.16  $2390.31  $2347.98            $42.33
              2018-Q2  $26626.45  $2529.51  $2513.32            $16.19
              2018-Q3  $29607.93  $2812.75  $2993.65          -$180.90
              2018-Q4  $30873.71  $2933.00  $2807.77           $125.23
              2019-Q1  $25547.08  $2426.97  $2406.66            $20.31
              2019-Q2  $39200.36  $3724.03  $3322.93           $401.10
              2019-Q3  $26233.47  $2492.17  $2893.27          -$401.10
              2019-Q4  $28442.24  $2702.01  $2701.99             $0.02
              2020-Q2   $3293.31   $312.86   $312.86             $0.00
```


## Implementation Notes
- Years/Quarters are using calander years, not financial years
  - `2020-Q1` represents the interval `[2020-01-01, 2020-03-31]`
- Disbursements are applied to a quarter using `payment_made - 28 days` ([reasoning](#what-quarter-a-disbursement-applies-to))
- All money values are stored/manipulated internally as integer "cents"
  - When floating point operations are used, they are rounded to the nearest whole number, then converted back to an int.
  - Money values are converted to dollars on output.
  - Added the `.money` custom accessors to streamline this a bit
- Super is calculated using the total OTE for the quarter (rather than individually for each payslip)
  - This could produce different results to calculating per payslip, due to rounding
  - However, language of problem implies we only care about the quarter's total
- Tests! Ran out of time to finish them, currently only `YearQuarter` is tested (almost trivial)

### `SuperData`
Object that holds disbursement and payment data
- Convinent short-hand to bundle both sets of data together, and indicate intent with type hints
- Would ideally implement some validators at the class level, to enforce structure of each dataframe (i.e. enforcing that all `payment` data contains an `employee_code`)
- Thought here is that you could implement additional parsers, and as long as they return a validated `SuperData` object then it can be used by the rest of the pipeline without any changes.


## Pandas Extensions - Custom Accessors
Implemented additonal pandas accessors. Seems slightly more convinient than applying lambdas

Honestly, just wanted to try it after reading [this page](https://pandas.pydata.org/docs/development/extending.html). 

### Custom Series Accessors
- `.interval` -> Allows access to some `pd.Interval` attributes
- `.money` -> Adds convenience methods for dealing with money
- `yq` -> Allows access to some `yc_super.YearQuarter` attributes

### Custom Series Accessors
- `.money` -> Currently only used for formatting the cents to dollar strings for the whole dataframe

## Misc Notes

### What Quarter a Disbursement Applies To
- The phrase "...must pay their staff 9.5% of pay codes treated as OTE **within** 28 days" implies only a **maximum** time period between 'earned' super and 'disbursed' super.
  - i.e. a Disbursement payed on the 22nd of January could either:
    - Apply to Q4 the previous year (within 28 days of end of the quarter)
    - Apply to Q1 of the current year (if a payslip came out before 22 of Jan)

- However the phrase "Super earned between 1st Jan and the 31 st of March (Q1) will need to be paid/Disbursed between the 29th Jan - 28th of Apr." indicates a hard limit 
  - i.e. disbursement payed on the 22nd of July could only be applied to Q4 on the previous quarter, as any super earned on the 1st of Jan **needs** to be paid between 29th Jan - 28th Apr


### Disbursement Pay Periods
In disbursements, the columns `pay_period_from` and `pay_period_to` represent intervals of coverage for a given disbursement, with disbursement periods starting after another has ended.
  - There are some discontinuous disbursements, assuming this is due to incomplete data
  - Employee `2355`, has overlapping disbursement, with a pay period that is encompassed by its surrounding disbursements.
  - There are also some non-continious disbursement periods for some employees (gaps in disbursement pay period coverage)