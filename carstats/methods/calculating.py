from sortedcontainers import SortedDict

from carstats.model import YearResult, YearRange


def trim_values(list_of_values, getter, trim_size=0.05):
    sorted_list = sorted(list_of_values, key=getter)
    size = len(sorted_list)
    trim_size = int(size * trim_size)
    return sorted_list[trim_size:size - trim_size]


def calculate_average(input_data, getter):
    number_of_items = len(input_data)
    sum_of_data = sum([getter(c) for c in input_data])
    return YearResult(sum_of_data / number_of_items)


def calculate_max(input_data, getter):
    max_value = max([getter(c) for c in input_data])
    return YearResult(max_value)


def calculate_min(input_data, getter):
    min_value = min([getter(c) for c in input_data])
    return YearResult(min_value)


def sort_lists_in_map(map_of_lists, reversed=False):
    for key in map_of_lists.keys():
        map_of_lists[key] = trim_values(sorted(map_of_lists[key], key=lambda c: c.price, reverse=reversed),
                                        lambda c: c.price, trim_size=0.02)


def get_year_range(list_of_maps_of_list):
    min_year = 9999
    max_year = 0
    for map_of_list in list_of_maps_of_list:
        map_min = min(map_of_list.keys())
        map_max = max(map_of_list.keys())
        min_year = map_min if map_min < min_year else min_year
        max_year = map_max if map_max > max_year else max_year


def split_raw_results_to_year_map(results):
    cars_by_years = SortedDict()
    for car in results:
        if not car.year in cars_by_years:
            cars_by_years[car.year] = []
        cars_by_years[car.year].append(car)

    sort_lists_in_map(cars_by_years)
    return cars_by_years
