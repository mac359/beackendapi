#!/home/ubuntu/beackendapi/myenv/bin/python3.10


import sys
import logging
logging.basicConfig(stream=sys.stderr)

# Add the directory containing your project to the sys.path
sys.path.insert(0, '/home/ubuntu/beackendapi/api')

from app import app as application
