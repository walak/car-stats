from os import path

from storage.service import StorageService


class FileService(StorageService):
    def __init__(self, directory):
        super().__init__(directory)

    def get_open_file_handle(self, name):
        filename = path.join(self.directory, name)
        try:
            file_handle = open(filename, "rb")
            return file_handle
        except:
            self.log.error("Cannot open [ %s ]" % filename, exc_info=1)
            return None

    def get_write_file_handle(self, name):
        filename = path.join(self.directory, name)
        try:
            file_handle = open(filename, "wb")
            return file_handle
        except:
            self.log.error("Cannot open [ %s ]" % filename, exc_info=1)
            return None

    def get_url(self, file):
        return "/download/" + file
