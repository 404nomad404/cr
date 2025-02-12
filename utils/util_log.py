# -*- coding: utf-8 -*-
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
import logging
import os.path
import sys

__author__ = 'Ishafizan'


# init logger
def logger():
    """
    Function returns logger instance
    :return: log
    :rtype: object
    """
    program = os.path.basename(sys.argv[0])
    log = logging.getLogger(program)
    logging.basicConfig(format='%(asctime)s : [%(filename)s] : %(levelname)s : %(message)s')
    logging.root.setLevel(level=logging.INFO)
    return log
