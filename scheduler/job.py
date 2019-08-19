import calendar
from collections import namedtuple
import enum
from dataclasses import dataclass, field
from typing import List
import time
from time import mktime
import datetime
import re
import json
import logging

class Resource(enum.Enum):
  tttpipe = 1
  datapipe = 2
  spark = 3

class Frequency(namedtuple('Frequency', 'mon tue wed thu fri sat sun')):
  def __repr__(self):
    return '({},{},{},{},{},{},{})'.format(self.mon, self.tue, self.wed, self.thu, self.fri, self.sat, self.sun)

  def __str__(self):
    return '({},{},{},{},{},{},{})'.format(self.mon, self.tue, self.wed, self.thu, self.fri, self.sat, self.sun)

  @classmethod
  def from_str(cls, freq_str):
    days = [False, False, False, False, False, False, False]
    segments = freq_str.split(',')
    for segment in segments:
      if '-' in segment:
        (begin, end) = segment.split('-')
        for i in range(int(begin), int(end) + 1):
          days[i-1] = True
      else:
        days[int(segment) - 1] = True
    return cls(int(days[0]), int(days[1]), int(days[2]), int(days[3]), int(days[4]), int(days[5]), int(days[6]))

@dataclass
class Dependency:
  name: str
  days_ago: int = 0

@dataclass
class Job:
  name: str
  frequency: Frequency
  expected_runtime: int
  time_restriction_begin: time = datetime.time(0, 0, 0)
  time_restriction_end: time = datetime.time(23, 59, 59)
  resources: List[Resource] = field(default_factory=list)
  dependencies: List[Dependency] = field(default_factory=list)

class JobReader:
  def __init__(self, filename):
    self.jobs = []
    with open(filename, 'r') as fd:
      data = json.load(fd)
      for (jobname, jobdata) in data.items():
        job = Job(name=jobname, frequency=Frequency.from_str(jobdata['Frequency']), expected_runtime=int(jobdata['ExpectedTime']))
        if 'TimeRestriction' in jobdata:
          segments = jobdata['TimeRestriction'].split('-')
          if len(segments) == 2:
            try:
              job.time_restriction_begin = datetime.datetime.fromtimestamp(mktime(time.strptime(segments[0], '%H:%M')))
            except ValueError:
              pass
            try:
              job.time_restriction_end   = datetime.datetime.fromtimestamp(mktime(time.strptime(segments[1], '%H:%M')))
            except ValueError:
              pass
          else:
            logging.error('Invalid format for TimeRestriction {} for job {}'.format(jobdata['TimeRestriction'], jobname))
        if 'Resource' in jobdata:
          resources = jobdata['Resource'].split(',')
          for string in resources:
            job.resources.append(Resource[string.lower()])
        if 'Dependency' in jobdata:
          segments = jobdata['Dependency'].split(',')
          for seg in segments:
            detail = re.split('[()]+', seg)
            name = detail[0]
            days_ago = 0
            if len(detail) > 1:
              days_ago = int(detail[1])
            job.dependencies.append(Dependency(name, days_ago))
        self.jobs.append(job)
    #TODO: check dependencies for each job used legal names

  def jobs_for_date(self, date):
    day_of_week = calendar.weekday(date.year, date.month, date.day)
    ret = []
    for job in self.jobs:
      if job.frequency[day_of_week] == 1:
        ret.append(job)
    return ret

  def jobs_for_resource(self, date, resource):
    day_of_week = calendar.weekday(date.year, date.month, date.day)
    ret = []
    for job in self.jobs:
      if job.frequency[day_of_week] == 1 and resource in job.resources:
        ret.append(job)
    return ret
