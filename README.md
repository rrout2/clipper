# Clipper Ride History Parser

## Usage:
```sh
usage: parser.py [-h] [-o OUTPUT] [-fp FASTPASS] [-w WORTHIT] pdf_path

Convert Clipper Card ride history PDF to CSV

positional arguments:
  pdf_path              Path to the Clipper Card transaction history PDF

options:
  -h, --help            show this help message and exit
  -o OUTPUT, --output OUTPUT
                        Output CSV file
  -fp FASTPASS, --fastpass FASTPASS
                        Whether to print fastpass info
  -w WORTHIT, --worthit WORTHIT
                        Whether to check if fastpass would have been worth it
```

## Where to find ride history
1. Navigate to [The Clipper Website](https://www.clippercard.com/ClipperWeb/) and login.
1. On your account page, under "More Options", click "View Activity".
1. Select your desired date range, and click "Download PDF".