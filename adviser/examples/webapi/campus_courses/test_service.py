# FIRST SET UP ENVIRONMENT

import sys
import os
from typing import List
import time
sys.path.append(os.path.abspath('../..'))

from services.service import Service, PublishSubscribe
from utils.topics import Topic
from services.service import DialogSystem
from utils.domain.domain import Domain
from utils.logger import DiasysLogger, LogLevel

class TestService(Service):
    def __init__(self, domain: str = "mydomain"):
        Service.__init__(self, domain=domain)

    @PublishSubscribe(sub_topics=["A", "B"], pub_topics=["C", "D"])
    def concatenate(self, A: int = None, B: str = None) -> dict(C=str,D=str):
        print("CONCATENATING ", A, "AND ", B)
        result = str(A) + " " + B
        if A == 3:
            print("Publish to D")
            return {'D': result}
        else:
            print("Publish to C")
            return  {'C': result}