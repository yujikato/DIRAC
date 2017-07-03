#!/usr/bin/env python
""" This template will become the job wrapper that's actually executed.

    The JobWrapperTemplate is completed and invoked by the jobAgent and uses functionalities from JobWrapper module.
    It has to be an executable.

    The JobWrapperTemplate will reschedule the job according to certain criteria:
    - the working directory could not be created
    - the jobWrapper initialization phase failed
    - the inputSandbox download failed
    - the resolution of the inpt data failed
    - the payload ended with status '111'
"""

import sys
import json
import ast
import os

sitePython = "@SITEPYTHON@"
if sitePython:
  sys.path.insert( 0, "@SITEPYTHON@" )
from DIRAC.Core.Base import Script
Script.parseCommandLine()

from DIRAC.WorkloadManagementSystem.JobWrapper.JobWrapper   import JobWrapper, rescheduleFailedJob
from DIRAC.WorkloadManagementSystem.Client.JobReport        import JobReport

from DIRAC                                                  import gLogger


os.umask( 0o22 )

class JobWrapperError( Exception ):
  def __init__( self, value ):
    self.value = value
  def __str__( self ):
    return str( self.value )

gJobReport = None

def execute( arguments ):

  global gJobReport

  jobID = arguments['Job']['JobID']
  os.environ['JOBID'] = jobID
  jobID = int( jobID )

  if arguments.has_key( 'WorkingDirectory' ):
    wdir = os.path.expandvars( arguments['WorkingDirectory'] )
    if os.path.isdir( wdir ):
      os.chdir( wdir )
    else:
      try:
        os.makedirs( wdir )
        if os.path.isdir( wdir ):
          os.chdir( wdir )
      except Exception:
        gLogger.exception( 'JobWrapperTemplate could not create working directory' )
        rescheduleResult = rescheduleFailedJob( jobID, 'Could Not Create Working Directory' )
        return 1

  gJobReport = JobReport( jobID, 'JobWrapper' )

  try:
    job = JobWrapper( jobID, gJobReport )
    job.initialize( arguments )
  except Exception as e:
    gLogger.exception( 'JobWrapper failed the initialization phase', lException = e )
    rescheduleResult = rescheduleFailedJob( jobID, 'Job Wrapper Initialization', gJobReport )
    try:
      job.sendJobAccounting( rescheduleResult, 'Job Wrapper Initialization' )
    except Exception as e:
      gLogger.exception( 'JobWrapper failed sending job accounting', lException = e )
    return 1

  if arguments['Job'].has_key( 'InputSandbox' ):
    gJobReport.commit()
    try:
      result = job.transferInputSandbox( arguments['Job']['InputSandbox'] )
      if not result['OK']:
        gLogger.warn( result['Message'] )
        raise JobWrapperError( result['Message'] )
    except Exception:
      gLogger.exception( 'JobWrapper failed to download input sandbox' )
      rescheduleResult = rescheduleFailedJob( jobID, 'Input Sandbox Download', gJobReport )
      job.sendJobAccounting( rescheduleResult, 'Input Sandbox Download' )
      return 1
  else:
    gLogger.verbose( 'Job has no InputSandbox requirement' )

  gJobReport.commit()

  if arguments['Job'].has_key( 'InputData' ):
    if arguments['Job']['InputData']:
      try:
        result = job.resolveInputData()
        if not result['OK']:
          gLogger.warn( result['Message'] )
          raise JobWrapperError( result['Message'] )
      except Exception as x:
        gLogger.exception( 'JobWrapper failed to resolve input data' )
        rescheduleResult = rescheduleFailedJob( jobID, 'Input Data Resolution', gJobReport )
        job.sendJobAccounting( rescheduleResult, 'Input Data Resolution' )
        return 1
    else:
      gLogger.verbose( 'Job has a null InputData requirement:' )
      gLogger.verbose( arguments )
  else:
    gLogger.verbose( 'Job has no InputData requirement' )

  gJobReport.commit()

  try:
    result = job.execute( arguments )
    if not result['OK']:
      gLogger.error( 'Failed to execute job', result['Message'] )
      raise JobWrapperError( result['Message'] )
  except Exception as x:
    if str(x) == '0':
      gLogger.verbose( 'JobWrapper exited with status=0 after execution' )
    if str(x) == '111':
      gLogger.warn("Asked to reschedule job")
      rescheduleResult = rescheduleFailedJob( jobID, 'JobWrapper execution', gJobReport )
      job.sendJobAccounting( rescheduleResult, 'JobWrapper execution' )
      return 1
    else:
      gLogger.exception( 'Job failed in execution phase' )
      gJobReport.setJobParameter( 'Error Message', str( x ), sendFlag = False )
      gJobReport.setJobStatus( 'Failed', 'Exception During Execution', sendFlag = False )
      job.sendFailoverRequest( 'Failed', 'Exception During Execution' )
      return 1

  if arguments['Job'].has_key( 'OutputSandbox' ) or arguments['Job'].has_key( 'OutputData' ):
    try:
      result = job.processJobOutputs( arguments )
      if not result['OK']:
        gLogger.warn( result['Message'] )
        raise JobWrapperError( result['Message'] )
    except Exception as x:
      gLogger.exception( 'JobWrapper failed to process output files' )
      gJobReport.setJobParameter( 'Error Message', str( x ), sendFlag = False )
      gJobReport.setJobStatus( 'Failed', 'Uploading Job Outputs', sendFlag = False )
      job.sendFailoverRequest( 'Failed', 'Uploading Job Outputs' )
      return 2
  else:
    gLogger.verbose( 'Job has no OutputData or OutputSandbox requirement' )

  try:
    # Failed jobs will return 1 / successful jobs will return 0
    return job.finalize( arguments )
  except Exception:
    gLogger.exception( 'JobWrapper failed the finalization phase' )
    return 2

###################### Note ##############################
# The below arguments are automatically generated by the #
# JobAgent, do not edit them.                            #
##########################################################
ret = -3
try:
  jsonFileName = os.path.realpath( __file__ ) + '.json'
  with open( jsonFileName, 'r' ) as f:
    jobArgsFromJSON = json.loads( f.readlines()[0] )
  jobArgs = ast.literal_eval(jobArgsFromJSON)
  if not isinstance(jobArgs, dict):
    raise TypeError, "jobArgs is of type %s" %type(jobArgs)
  if 'Job' not in jobArgs:
    raise ValueError, "jobArgs does not contain 'Job' key: %s" %str(jobArgs)
  ret = execute( jobArgs )
  gJobReport.commit()
except Exception as e:
  try:
    gLogger.exception("JobWrapperTemplate exception", lException = e)
    gJobReport.commit()
    ret = -1
  except Exception:
    gLogger.exception()
    ret = -2

sys.exit( ret )
