import sys
import logging
import getpass
from optparse import OptionParser
import sleekxmpp

#for weather
import urllib3
import pywapi
import string

# ensure unicode is handled properly incase python is not v3.0
if sys.version_info < (3, 0):
	reload(sys)
	sys.setdefaultencoding('utf8')
else:
	raw_input = input


class MUCBot (sleekxmpp.ClientXMPP):

	def __init__ (self, jid, password, room, nick):
		sleekxmpp.ClientXMPP.__init__(self, jid, password)

		self.room = room
		self.nick = nick
		
		self.add_event_handler("session_start", self.start)
		self.add_event_handler("groupchat_message", self.bot_message)
	
	def start(self, event):
		self.get_roster()
		self.send_presence()
		self.plugin['xep_0045'].joinMUC(self.room, self.nick)

	def bot_message(self, msg):
		#reply if username is mentioned
		#always make sure the message we're replying to didn't come from self
		if msg['mucnick'] != self.nick and self.nick in msg['body']:
			self.send_message(mto=msg['from'].bare,
					mbody="I heard that, %s." % msg['mucnick'], mtype='groupchat')



if __name__ == '__main__':
    # Setup the command line arguments.
    optp = OptionParser()

    # Output verbosity options.
    optp.add_option('-q', '--quiet', help='set logging to ERROR',
                    action='store_const', dest='loglevel',
                    const=logging.ERROR, default=logging.INFO)
    optp.add_option('-d', '--debug', help='set logging to DEBUG',
                    action='store_const', dest='loglevel',
                    const=logging.DEBUG, default=logging.INFO)
    optp.add_option('-v', '--verbose', help='set logging to COMM',
                    action='store_const', dest='loglevel',
                    const=5, default=logging.INFO)

    opts, args = optp.parse_args()

    # Setup logging.
    logging.basicConfig(level=opts.loglevel,
                        format='%(levelname)-8s %(message)s')

    # Setup the MUCBot and register plugins. Note that while plugins may
    # have interdependencies, the order in which you register them does
    # not matter.
    xmpp = MUCBot("cube@obnauticus.com", "chickentender23", "#emc2@conference.obnauticus.com", "cube")
    xmpp.register_plugin('xep_0030') # Service Discovery
    xmpp.register_plugin('xep_0045') # Multi-User Chat
    xmpp.register_plugin('xep_0199') # XMPP Ping

    # Connect to the XMPP server and start processing XMPP stanzas.
    if xmpp.connect(('obnauticus.com', 5222)):
        # If you do not have the dnspython library installed, you will need
        # to manually specify the name of the server if it does not match
        # the one in the JID. For example, to use Google Talk you would
        # need to use:
        #
        # if xmpp.connect(('talk.google.com', 5222)):
        #     ...
        xmpp.process(block=True)
        print("Done")
    else:
        print("Unable to connect.")
