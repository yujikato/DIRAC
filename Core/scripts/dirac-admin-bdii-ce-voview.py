#! /usr/bin/env python

import DIRAC
from DIRAC.Core.Base                                         import Script

Script.registerSwitch( "H:", "host=", "BDII host" )
Script.registerSwitch( "V:", "vo=", "vo" )

Script.parseCommandLine( ignoreErrors = True )
args = Script.getPositionalArgs()

from DIRAC.Interfaces.API.DiracAdmin                         import DiracAdmin

def usage():
  print 'Usage: %s ce' %(Script.scriptName)
  DIRAC.exit(2)

if not len(args)==1:
  usage()

ce = args[0]

host = None
vo = 'lhcb'
for unprocSw in Script.getUnprocessedSwitches():
  if unprocSw[0] in ( "H", "host" ):
        host = unprocSw[1]
  if unprocSw[0] in ( "V", "vo" ):
        vo = unprocSw[1]

diracAdmin = DiracAdmin()

result = diracAdmin.getBDIICEVOView(ce, vo=vo, host=host)
if not ['OK']:
  print test['Message']
  DIRAC.exit(2)
  

ces = result['Value']
for ce in ces:
  print "CEVOView: %s {"%ce.get('GlueChunkKey','Unknown')
  for item in ce.iteritems():
    print "%s: %s"%item
  print "}"


