from twisted.application import internet, service
import sys, os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from queue_manager import TelephonyFactory

application = service.Application("queue_manager")
telephonyService = internet.TCPServer(5678, TelephonyFactory())
telephonyService.setServiceParent(application)
