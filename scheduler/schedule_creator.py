import argparse
import datetime
import time
from time import mktime

from job import JobReader
from csp import gen_schedule

def parse_args():
  parser = argparse.ArgumentParser()
  parser.add_argument('--input', '-i', type=str, required=True)
  parser.add_argument('--date', '-d', type=str, required=False)
  return parser.parse_args()

def main():
  args = parse_args()
  if not args.date:
    args.date = datetime.datetime.now().strftime('%Y%m%d')
  reader = JobReader(args.input)
  the_date = datetime.datetime.fromtimestamp(mktime(time.strptime(args.date, '%Y%m%d'))).date()
  schedule = gen_schedule(reader, the_date)
  for (job, assignment) in schedule.items():
    print('{}: {}'.format(job, assignment))
  #TODO

if __name__ == "__main__":
  main()
