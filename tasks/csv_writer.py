# csv_writer.py
import csv
import io

def format_csv_row(row):
    output = io.StringIO()
    writer = csv.writer(output, lineterminator='')
    writer.writerow(row)
    return output.getvalue()
