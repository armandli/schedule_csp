import calendar
import math
from datetime import datetime
from datetime import time

from ortools.sat.python import cp_model

from job import JobReader

class InfeasibleSolutionException(Exception):
  pass

def quantize_minute(minutes, quantization_const = 15):
  return math.floor(minutes / quantization_const)

def dequantize_minute(state, quantization_const = 15):
  total_minutes = state * quantization_const
  hour = int(total_minutes / 60)
  minutes = int(total_minutes % 60)
  return time(hour, minutes)

def time_range_to_integer_range(time_begin, time_end, quantization_const = 15):
  min_begin = quantize_minute(time_begin.hour * 60 + time_begin.minute, quantization_const)
  min_end   = quantize_minute(time_end.hour * 60 + time_end.minute, quantization_const)
  return (min_begin, min_end)

def gen_schedule(jobs, date, quantization_const = 15):
  model = cp_model.CpModel()
  job_list = jobs.jobs_for_date(date)
  # create variables
  schedule_assignment = {}
  variables = {}
  for job in job_list:
    (begin, end) = time_range_to_integer_range(job.time_restriction_begin, job.time_restriction_end)
    variables[job.name] = (job, model.NewIntVar(begin, end, job.name))
  # create job dependency constraints
  for job in job_list:
    if job.dependencies:
      for dep in job.dependencies:
        if dep.days_ago == 0:
          model.Add(variables[dep.name][1] + quantize_minute(variables[dep.name][0].expected_runtime, quantization_const) < variables[job.name][1])
  # create resource dependency constraints
  for job in job_list:
    for resource in job.resources:
      conflict_jobs = jobs.jobs_for_resource(date, resource)
      for cjob in conflict_jobs:
        if cjob.name != job.name:
          for i in range(quantize_minute(job.expected_runtime, quantization_const)):
            model.Add(variables[job.name][1] + i != variables[cjob.name][1])
  #TODO: create optimization goal ?
  solver = cp_model.CpSolver()
  status = solver.Solve(model)
  if status != cp_model.INFEASIBLE and status != cp_model.MODEL_INVALID and status != cp_model.UNKNOWN:
    ret = {var : dequantize_minute(solver.Value(data[1])) for (var, data) in variables.items()}
    return ret
  else:
    raise InfeasibleSolutionException('No feasible solution exist')
