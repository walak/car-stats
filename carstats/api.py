import logging

from asynctask.api import TaskExecutor
from asynctask.model import InterruptibleTask, Task
from carstats.methods.calculating import calculate_average, split_raw_results_to_year_map
from carstats.methods.excelling import generate_xlsx_report, to_report
from carstats.methods.scrapping import load_main_page, get_number_of_pages, \
    load_result_page, get_results_from_page, OTOMOTO_HOST, pause
from carstats.model import CarScrapResult, CarAnalysisReport
from files.service import FileService
from httpapi.httpapi import create_https_connection
from tools.utils import generate_name


def fetch_car_data(brand, model):
    connection = create_https_connection(OTOMOTO_HOST)
    return GetCarsFromOtomotoTask(http_connection=connection,
                                  brand=brand,
                                  model=model)

    # rounded_mileage = car.mileage // 10000
    # if rounded_mileage not in cars_by_mileage:
    #     cars_by_mileage[rounded_mileage] = []
    # cars_by_mileage[rounded_mileage].append(car)


class GetCarsFromOtomotoTask(InterruptibleTask):
    def __init__(self, http_connection, brand, model):
        super().__init__()
        self.http_connection = http_connection
        self.brand = brand
        self.model = model
        self.log = logging.getLogger("GetCarsFromOtomotoTask-%s-%s" % (self.brand, self.model))

    def try_interrupt(self):
        super().try_interrupt()

    def execute(self):
        self.progress = "?/?"
        car_scrap_result = CarScrapResult(brand=self.brand,
                                          model=self.model,
                                          results=[])
        main_page = load_main_page(self.http_connection, self.brand, self.model)
        number_of_pages = self.__get_number_result_pages(main_page)
        for i in range(1, number_of_pages + 1):
            self.progress = "%d/%d" % (i, number_of_pages)
            self.log.info("Scrapping page [ %d ]" % i)
            if self.should_interrupt():
                self.log.warning("Task was interrupted. Returning [ %d ] results" % len(car_scrap_result.results))
                self.result = car_scrap_result
                return car_scrap_result
            result_page = load_result_page(self.http_connection, self.brand, self.model, i)
            current_results = get_results_from_page(result_page, self.brand, self.model)
            pause()
            if current_results:
                car_scrap_result.update_results(current_results)
                self.log.info(
                    "Scrapped [ %d ] results from page [ %d/%d ]" % (len(current_results), i, number_of_pages))
            else:
                self.log.warning("Unable to scrap page [ %d ]" % i)

        self.log.info("Scrapped [ %d ] results" % len(car_scrap_result.results))
        self.result = car_scrap_result
        return car_scrap_result

    def __get_number_result_pages(self, main_page):
        number_of_pages = get_number_of_pages(main_page)
        self.progress = "0/%d" % number_of_pages
        return number_of_pages

    def __getstate__(self):
        state = self.__dict__.copy()
        del state['http_connection']
        del state['log']
        del state['interruption_lock']
        return state


class CalculateAveragePriceByYear(Task):

    def __init__(self, list_of_maps):
        super().__init__()
        self.results = list_of_maps

    def execute(self):
        cars_by_years = split_raw_results_to_year_map(self.results)
        self.result = {y: calculate_average(k, lambda c: c.price) for y, k in cars_by_years.items()}
        return self.result


class GetCarsToXls(InterruptibleTask):

    def __init__(self, brand, model, task_executor: TaskExecutor, file_service: FileService):
        super().__init__()
        self.file_service = file_service
        self.task_executor = task_executor
        self.brand = brand
        self.model = model

    def execute(self):
        http_connection = create_https_connection(OTOMOTO_HOST)
        get_data_task = GetCarsFromOtomotoTask(http_connection, self.brand, self.model)

        get_data_task_execution = self.task_executor.execute(get_data_task)

        get_data_result = get_data_task_execution.get_task_or_wait()
        if get_data_result.is_success():
            averages = self.task_executor.execute(
                CalculateAveragePriceByYear(get_data_result.result.results)).get_task_or_wait()

            output_file_name = "%s-%s-%s.xlsx" % (self.brand, self.model, generate_name())
            output_file = self.file_service.get_write_file_handle(output_file_name)
            generate_xlsx_report([to_report(averages.result)], output_file)
            output_file.close()

            self.result = CarAnalysisReport(self.brand, self.model, self.file_service.get_url(output_file_name),
                                            get_data_task.id)

            return self.result
        else:
            self.result = None
            return None

    def __getstate__(self):
        d = super().__getstate__()
        d.update({
            "brand": self.brand,
            "model": self.model
        })
        return d


if __name__ == "__main__":
    logFormatter = logging.Formatter('%(asctime)-15s [ %(name)s ] %(message)s')
    logging.basicConfig(level=logging.INFO)
    executor = TaskExecutor()
    executor.start()
    file_service = FileService("resources/data/files")

    executor.execute(GetCarsToXls("mazda", "6", executor, file_service))
