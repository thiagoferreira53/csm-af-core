#!/usr/bin/env python3

import argparse
import json
import os
# import pathlib
import sys
from abc import ABC, abstractmethod
# from collections import OrderedDict
from os import path

from pydantic import ValidationError

from pipeline.db.core import DBConfig


class ProcessData(ABC):
    """Abstract class for ProcessData objects"""

    def __init__(self, analysis_request, *args, **kwargs):
        """Constructor.

        Args:
            analysis_request: Object with all required inputs to run analysis.
        """
        self.db_session = DBConfig.get_session()


