from configparser import ConfigParser
from os import path


class ConfigLoader:
    def __init__(self):
        self._path: str = "config.ini"
        self._config: ConfigParser = ConfigParser()
        self.__load()

        try:
            self.cache_server = (
                self._config["CacheServer"]["host"],
                int(self._config["CacheServer"]["port"])
            )
            self.forwarder_server = (
                self._config["Forwarder"]["host"],
                int(self._config["Forwarder"]["port"])
            )
        except ValueError:
            print("Ошибка в чтении конфига. Проверьте, что port - это число")

    def __load(self) -> None:
        self.__pre_load()
        self._config.read(self._path)

    def __pre_load(self) -> None:
        if not path.exists(self._path):
            self.__create_config()

    def __create_config(self) -> None:
        self._config.add_section("CacheServer")
        self._config.set("CacheServer", "host", "127.0.0.1")
        self._config.set("CacheServer", "port", "53")

        self._config.add_section("Forwarder")
        self._config.set("Forwarder", "host", "8.26.56.26")
        self._config.set("Forwarder", "port", "53")

        with open(self._path, "w") as config_file:
            self._config.write(config_file)
