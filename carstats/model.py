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

    def to_dict(self):
        return {
            "brand": self.brand,
            "model": self.model,
            "title": self.title,
            "price": self.price,
            "year": self.year,
            "fuel_id": self.fuel,
            "url": self.url
        }


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


class CarReport:

    def __init__(self, title, page_header, headers, values):
        self.title = title
        self.page_header = page_header
        self.headers = headers
        self.values = values
