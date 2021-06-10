from services.service import Service, PublishSubscribe
import time
from utils.topics import Topic


class TestService2(Service):
    def __init__(self, domain: str = "mydomain", sub_topic_domains={'start': ''}):
        Service.__init__(self, domain=domain, sub_topic_domains=sub_topic_domains)  


    """
    publishes to A/mydomain, B/mydomain

    """

    @PublishSubscribe(sub_topics=["D"], pub_topics=[Topic.DIALOG_END])
    def print_d(self, D: str):
        print(f"RECEIVED D={D}")
        #return {Topic.DIALOG_END: True}
    
    @PublishSubscribe(sub_topics=["C"], pub_topics=[Topic.DIALOG_END])
    def print_c(self, C: str):
        print(f"RECEIVED C={C}")
        if "4" in C:
            return {Topic.DIALOG_END: True}


    @PublishSubscribe(sub_topics=["start"])
    def turn_start(self, start: bool = True):
        print('start method')
        a = 2
        while a < 5:
            time.sleep(0.5)
            self.send_a(a)
            self.send_b()
            a += 1
        time.sleep(0.5)
        #self.send_b()

    @PublishSubscribe(pub_topics=["A"])
    def send_a(self, a: int):
        print("SENDING A=", a)
        return {'A': a}

    @PublishSubscribe(pub_topics=["B"])
    def send_b(self):    
        print("SENDING B")
        return {'B': "messages dropped!"}