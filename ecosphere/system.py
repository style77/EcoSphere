import time
from ecosphere.common.singleton import SingletonMeta
from ecosphere.common.systeminfo import SystemInfo
from ecosphere.config import HOUR_LENGTH

from ecosphere.overworld import Overworld


class System(metaclass=SingletonMeta):
    def __init__(self, overworld: Overworld, system_info: SystemInfo = None):
        self.overworld = overworld
        self.system_info = system_info

    def run(self):
        self.overworld.spawn_entities()

        while True:
            self.overworld.update()
            self.overworld.draw()

            if self.system_info:
                self.system_info.draw()

            time.sleep(HOUR_LENGTH)
