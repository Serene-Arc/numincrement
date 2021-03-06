# numincrement

This is a simple tool to increment numbers in a filename or sequence of file names. 

The program can be run with `python3 -m numincrement` or the shorter `numincrement` commands.

Additionally, the format of the supplied numbers will be preserved. For example, 001 will be incremented to 002, not simply 2. This is also the case for decimal numbers

## Arguments and Options

The following arguments and options are available for the program:

  - `expression` is the regex expression; see [here](#regex-expression)
  - `files` are the files to be incremented; at least one file must be supplied
  - `-i, --increment` is the number to increment numbers by; the flag can be supplied without a value in which case the increment number will be 1. The supplied number can be negative or positive
  - `-d, --decrement` is the number to decrement numbers by; the flag without a value will assume a default of -1. This flag can only be negative
  - `-n, --no-act` will print the proposed changes but not actually move any files
  - `-v, --verbose` will increase the verbosity of the output; can be supplied multiple times

### Regex Expression

The regex expression for the tool is in Python regex format, and must contain at least one capture group. This capture group must be the number to be incremented. For example:

  - `^(\d+)` will increment the number found at the beginning of a filename
  - `page_(\d+)` will increment the number found after the string `page_` in the filename
  - `doc_(\d+)_page_(\d+)` will increment both of the captured numbers, after the `doc_` and `page_` strings
  - `doc_\d+_page_(\d+)` will only increment the second number, after the string `page_`

## Example Commands

The following commands showcase the use of the tool:

  - `numincrement -i 1 '^(\d+)' *.txt`
  - `numincrement -i -1 'image_(\d+)' *.png`

In the case of the last example, the files would be renamed in the following manner:
  - `image_01.png` -> `image_00.png`
  - `image_02.png` -> `image_01.png`
  - `image_03.png` -> `image_02.png`

### Decimal Increments

The tool can handle incrementing decimal numbers, or applying decimals to a number in the filename. For example, an increment of `-i 0.5` on a file named `image_1.png` will result in a file named `image_1.5.png`.

The decimal increment will also preserve formatting as much as possible. For example, a decimal represented as `01.000` and incremented by 0.5 will retain the same number of digits, becoming `01.500`. However, the increment will add the necessary digits required to represent the number, so `1.0` incremented by `0.01` will become `1.01`.

When incrementing a decimal already in a name, note that the decimal point must be included in the capture group, as the `\d` regex group does not include it. For the capture for the above example, `image_([\d.]+)` would be required in order to properly increment the filename. 
