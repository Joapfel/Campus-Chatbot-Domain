import sys
import os
from typing import List
sys.path.append(os.path.abspath('../..'))

from services.service import DialogSystem
from utils.logger import DiasysLogger, LogLevel
from examples.webapi.campus_courses import TestService, TestService2
from utils.domain.domain import Domain
from utils.domain.jsonlookupdomain import JSONLookupDomain
from services.nlu.nlu import HandcraftedNLU
from services.bst import HandcraftedBST
from services.policy import HandcraftedPolicy
from services.nlg import HandcraftedNLG
from services.domain_tracker import DomainTracker
from services.hci import ConsoleInput, ConsoleOutput

# create logger to log everything to a file
logger = DiasysLogger(console_log_lvl=LogLevel.NONE, file_log_lvl=LogLevel.DIALOGS) 

campus_domain = JSONLookupDomain(name='campus_courses')
nlu = HandcraftedNLU(domain=campus_domain)
bst = HandcraftedBST(domain=campus_domain)
policy = HandcraftedPolicy(domain=campus_domain)
nlg = HandcraftedNLG(domain=campus_domain)
d_tracker = DomainTracker(domains=[campus_domain])

user_in = ConsoleInput(domain="")
user_out = ConsoleOutput(domain="")

ds = DialogSystem(services=[d_tracker, user_in, user_out, nlu, bst, policy, nlg], debug_logger=logger)
error_free = ds.is_error_free_messaging_pipeline()
if not error_free:
    print("The SDS contains errors.")
    ds.print_inconsistencies()

ds.draw_system_graph(name='system', show=False)

# start dialog
for _ in range(1):
    ds.run_dialog({'gen_user_utterance': ""})
ds.shutdown()

"""
user_input = input('>>> ')
while user_input.strip().lower() not in ('', 'exit', 'bye', 'goodbye'):
    user_acts = nlu.extract_user_acts(user_input)['user_acts']
    print('\n'.join([repr(user_act) for user_act in user_acts]))
    user_input = input('>>> ')
"""

#test1 = TestService()
#test2 = TestService2()
#ds = DialogSystem(services=[test2, test1], debug_logger=logger)

#ds.print_inconsistencies()
#ds.run_dialog({"start": True})
#ds.shutdown()