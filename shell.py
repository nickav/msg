#!/usr/bin/env python
import os
import readline
from pprint import pprint

from flask import *
from app import *
from app.models import *

os.environ['PYTHONINSPECT'] = 'True'
