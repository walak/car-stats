import logging
from time import sleep

LOG = logging.getLogger("do_action")


class BasicDoExecutionException(Exception):

    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class DoExecutionException(BasicDoExecutionException):

    def __init__(self, previous_exceptions=None, *args: object) -> None:
        super().__init__(*args)
        if previous_exceptions is None:
            previous_exceptions = []
        self.previous_exceptions = previous_exceptions


class NoValueReturnedException(BasicDoExecutionException):

    def __init__(self, *args: object):
        super().__init__(*args)


def do(action, max_attempts=0, wait_before_retry=0, before_retry_action=None, retry_on_none=False, **kwargs):
    counter = 0
    last_exceptions = []
    while counter <= max_attempts:
        try:
            result = action(**kwargs)
            if not result and retry_on_none:
                LOG.warning("Function [ %s ] was expected to return a value but got None. Retrying" % action.__name__)
                raise NoValueReturnedException()
            else:
                return result
        except Exception as e:
            counter += 1
            LOG.error("Error [ %s ] call function [ %s ]. Attempts left [ %d ] " %
                      (e.__class__.__name__, action.__name__, max_attempts - counter), exc_info=1)
            sleep(wait_before_retry)
            last_exceptions.append(e)
            if before_retry_action:
                try:
                    LOG.info("Running before-retry action [ %s ]" % before_retry_action.__name__)
                    before_retry_action()
                except Exception as e:
                    LOG.error("Exception [ %s ] when running retry action!", e.__class__.__name__)
                    last_exceptions.append(e)

    return last_exceptions

