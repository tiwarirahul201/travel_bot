activate_this = '/var/www/SIAIDev/honda_bot/env/bin/activate_this.py'
with open(activate_this) as file_:
    exec(file_.read(), dict(__file__=activate_this))


import sys
import hashlib
#import logging
#logging.basicConfig(stream=sys.stderr)



sys.path.insert(0,"/var/www/Spotlight-AI/nsfw/flask")

from app import app as application

#application.secret_key = hashlib.sha256(os.urandom(1024)).hexdigest()
