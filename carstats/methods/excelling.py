from io import BytesIO

from xlsxwriter import Workbook
from xlsxwriter.format import Format

from carstats.methods.formatting import TITLE, HEADER
from carstats.model import CarReport


class XlsxGenerationContext:
    def __init__(self, workbook):
        self.workbook = workbook
        self.title_format = workbook.add_format(TITLE)
        self.header_format = workbook.add_format(HEADER)


def to_report(result):
    current_year = max(result.keys())
    oldest_year = min(result.keys())
    values = []
    for year in range(current_year, oldest_year - 1,-1):
        if year in result:
            values.append([year, result[year].value, result[year].value / result[current_year].value])
    return CarReport("Average price by year", "Average price by year",
                     headers=["Year", "Average price", "Year to now"],
                     values=values)


def generate_page_title(worksheet, title, style):
    worksheet.write(0, 0, title, style)
    worksheet.set_row(0, 35)


def write_to_row(worksheet, values, style, row, start_col=0):
    col = start_col
    for value in values:
        worksheet.write(row, col, value, style)
        col += 1


def write_to_row_with_styles(worksheet, values, row, start_col=0, styles=None):
    final_styles = None if not styles else [styles] if isinstance(styles, Format) else styles
    col = start_col
    counter = 0
    for value in values:
        style = final_styles[counter % len(final_styles)] if final_styles else None
        worksheet.write(row, col + counter, value, style)
        counter += 1
    worksheet.set_column(start_col, col + counter - 1, 30)


def generate_table_headers(worksheet, headers, style):
    write_to_row(worksheet, headers, style, 3)


def generate_chart(report, context: XlsxGenerationContext):
    chart = context.workbook.add_chart({"type": "line"})
    chart.add_series({
        "values": [report.title, 4, 1, 4 + len(report.values), 1],
        "categories": [report.title, 4, 0, 4 + len(report.values), 0],
        "name": "Average price",
        "color": "yellow"
    })
    chartsheet = context.workbook.add_chartsheet()

    chartsheet.set_chart(chart)
    pass


def generate_report_page(report, context: XlsxGenerationContext):
    worksheet = context.workbook.add_worksheet(report.title)
    generate_page_title(worksheet, report.page_header, context.title_format)
    generate_table_headers(worksheet, report.headers, context.header_format)
    row_no = 4
    for row in report.values:
        write_to_row_with_styles(worksheet, row, row_no)
        row_no += 1


def generate_xlsx_report(reports, output_stream):
    workbook = Workbook(output_stream)
    ctx = XlsxGenerationContext(workbook)
    for report in reports:
        generate_report_page(report, context=ctx)
        generate_chart(report, context=ctx)

    workbook.close()
