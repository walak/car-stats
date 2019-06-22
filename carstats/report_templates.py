from carstats.model import CarAnalysisResult


class CarReportTemplate:

    def __init__(self, report_title_pattern, sheet_title_pattern, column_pattern):
        self.report_title_pattern = report_title_pattern
        self.sheet_title_pattern = sheet_title_pattern
        self.column_pattern = column_pattern

    def get_report_title(self, *args):
        return self.report_title_pattern % (tuple(args))

    def get_sheet_title(self, *args):
        return self.sheet_title_pattern % (tuple(args))

    def get_column(self, *args):
        return self.column_pattern % (tuple(args))

class AveragePricePerYearReportTemplate(CarReportTemplate):

    @staticmethod
    def from_scrapping_result(result:CarAnalysisResult):

AVERAGE_PRICE_PER_YEAR = CarReportTemplate(
    report_title_pattern="Average price of cars over years",
    sheet_title_pattern="Average price of selected %d cars over years %d - %d",
    column_pattern="%s %s")
