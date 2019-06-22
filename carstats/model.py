from carstats.report_templates import CarReportTemplate


class CarEntry:
    def __init__(self, title, brand, model, price, year, mileage, fuel, drive, url):
        self.title = title
        self.brand = brand
        self.model = model
        self.price = price
        self.year = year
        self.mileage = mileage
        self.fuel = fuel
        self.drive = drive
        self.url = url


class CarScrapResult:
    def __init__(self, brand, model, results):
        self.brand = brand
        self.model = model
        self.number_of_results = len(results)
        self.results = results

    def update_results(self, new_results):
        self.results += new_results
        self.number_of_results = len(self.results)

    @staticmethod
    def from_task_result(task_result):
        return CarScrapResult(brand=task_result['brand'],
                              model=task_result['model'],
                              results=[CarEntry(**c) for c in task_result['results']])


class YearResult:

    def __init__(self, value, url=None):
        self.value = round(value, 2)
        self.url = url


class YearRange:
    def __init__(self, min_year, max_year):
        self.min_year = min_year
        self.max_year = max_year


class CarAnalysisResult:

    def __init__(self, brand, model, result_map):
        self.brand = brand
        self.model = model
        self.result_map = result_map


class CarAnalysisReport:
    def __init__(self, brand, name, reporl_url, scrap_task):
        self.brand = brand
        self.name = name
        self.report_url = reporl_url
        self.scrap_task = scrap_task


class Car(object):
    pass


class CarReport:

    def __init__(self, car: Car = None, template=CarReportTemplate, values):
        self.title = title
        self.page_header = page_header
        self.headers = headers
        self.values = values
        self.report_type = None
        self.min_value = None
        self.max_value = None

    @staticmethod
    def from_template(car: Car, template: CarReportTemplate):
        return CarReport


class Car:
    def __init__(self, brand, model):
        self.brand = brand
        self.model = model
