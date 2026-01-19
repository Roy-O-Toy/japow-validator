from validator import ResortValidator
import sys

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python validate_resort_data.py [datafile.json|csv]")
    else:
        ResortValidator.run_validation(sys.argv[1])
