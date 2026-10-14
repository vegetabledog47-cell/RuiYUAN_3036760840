"""Single entry point for core replication, extension, validation and report."""
import argparse
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input',type=Path,default=ROOT/'01_DID/data/public.csv')
    args=parser.parse_args()
    sys.argv=[sys.argv[0],'--input',str(args.input)]
    import replicate
    import extension
    import validate
    import build_report
    replicate.main()
    extension.main()
    validate.main()
    build_report.main()
    print('\nAll stages completed. Open report.pdf for the submission report.')


if __name__=='__main__': main()
