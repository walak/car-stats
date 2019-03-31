import logging
from random import random
from time import sleep

from carstats.model import CarEntry
from httpapi.httpapi import get
from tools.methods import do

from lxml import html
from re import sub

LOG = logging.getLogger("CarStatsApi")

NUMBER_OF_PAGES_XPATH = "(//span[@class='page'])[last()]/text()"
RESULTS_XPATH = "//*[@class='offers list']//article"
FUEL_XPATH = ".//*[@data-code='fuel_type']/span/text()"
MILEAGE_XPATH = ".//*[@data-code='mileage']/span/text()"
YEAR_XPATH = ".//*[@data-code='year']/span/text()"
PRICE_XPATH = ".//span[@class='offer-price__number']/text()"
TITLE_XPATH = ".//h2/a/text()"
URL_XPATH = ".//h2/a/@href"
PAUSE_MIN_TIME = 0
PAUSE_ADDITIONAL_TIME = 3

OTOMOTO_HOST = "www.otomoto.pl"
BASE_URL = "https://www.otomoto.pl/osobowe/%s/%s/"
PAGE_URL = "https://www.otomoto.pl/osobowe/%s/%s/?page=%d"

STRIPPER = lambda v: v.strip()
NUMBER_FILTER = lambda v: sub(r"[^0-9,]", "", v).replace(",", ".")
TO_INT = lambda v: int(round(float(v)))

STRIPPER_AS_NUMBER = lambda v: TO_INT(NUMBER_FILTER(v))


def get_number_of_pages(parsed_page):
    number_of_pages_collection = parsed_page.xpath(NUMBER_OF_PAGES_XPATH)
    if number_of_pages_collection:
        return int(number_of_pages_collection[0])
    else:
        return 0


def get_page(http_connection, url):
    return get(http_connection, url)


def get_page_for_brand_and_model(http_connection, brand, model, page=None):
    url = BASE_URL % (brand, model)
    params = {"page": page} if page else {}
    return get(http_connection, url, **params)


def pause():
    pause_time = PAUSE_MIN_TIME + random() * PAUSE_ADDITIONAL_TIME
    LOG.info("Pausing for [ %.2f ] seconds" % pause_time)
    sleep(pause_time)


def load_main_page(http_connection, brand, model):
    main_page = do(action=get_page_for_brand_and_model,
                   max_attempts=5, wait_before_retry=5, before_retry_action=None,
                   retry_on_none=True, http_connection=http_connection,
                   brand=brand, model=model)
    return html.fromstring(main_page)


def load_result_page(http_connection, brand, model, page=1):
    page = do(action=get_page_for_brand_and_model, wait_before_retry=5, before_retry_action=None,
              retry_on_none=True, http_connection=http_connection,
              brand=brand, model=model, page=page)

    return html.fromstring(page)


def get_xpath(root, xpath, value_processor=STRIPPER, default_value=None, throw_exception=True):
    value = root.xpath(xpath)
    try:
        if value_processor:
            return value_processor(value[0])
        else:
            return value[0]
    except Exception as e:
        LOG.warning("Exception getting value of XPath [ %s ]: [ %s ]" % (xpath, e.__class__.__name__))
        if throw_exception:
            raise e
        else:
            return default_value


def get_single_result(root):
    try:
        title = get_xpath(root, TITLE_XPATH)
        url = get_xpath(root, URL_XPATH)
        price = get_xpath(root, PRICE_XPATH, value_processor=STRIPPER_AS_NUMBER)
        year = get_xpath(root, YEAR_XPATH, value_processor=STRIPPER_AS_NUMBER)
        mileage = get_xpath(root, MILEAGE_XPATH, value_processor=STRIPPER_AS_NUMBER)
        fuel = get_xpath(root, FUEL_XPATH)
        return CarEntry(title, None, None, price, year, mileage, fuel, "", url)
    except Exception as e:
        LOG.warning("Exception reading result [ %s ]. Returning None", e.__class__.__name__)
        return None


def get_results_from_page(parsed_page, brand, model):
    results = []
    articles = parsed_page.xpath(RESULTS_XPATH)
    for article in articles:
        result = get_single_result(article)
        if result:
            result.brand = brand
            result.model = model
            results.append(result)

    return results


def get_number_of_cars(http_connection, brand, model):
    results = []
    number_of_pages = get_number_of_pages(load_main_page(http_connection, brand, model))
    LOG.info("Found [ %d ] result pages" % number_of_pages)

    for i in range(1, number_of_pages + 1):
        pause()
        result_page = load_result_page(http_connection, brand, model, i)
        LOG.info("Scrapping page [ %d ]" % i)
        current_results = get_results_from_page(result_page, brand=brand, model=model)
        if current_results is not None:
            LOG.info("Scrapped [ %d ] results" % len(current_results))
            results += current_results
        else:
            LOG.warning("Unable to scrap page [ %d ]" % i)
    return results
