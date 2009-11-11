#! /usr/bin/env python

import DIRAC
from DIRAC.Core.Base                                         import Script

Script.registerSwitch( "H:", "host=", "BDII host" )

Script.parseCommandLine( ignoreErrors = True )
args = Script.getPositionalArgs()

from DIRAC.Interfaces.API.DiracAdmin                         import DiracAdmin

def usage():
  print 'Usage: %s site' %(Script.scriptName)
  DIRAC.exit(2)

if not len(args)==1:
  usage()

site = args[0]

host = None

for unprocSw in Script.getUnprocessedSwitches():
  if unprocSw[0] in ( "h", "host" ):
        host = unprocSw[1]

diracAdmin = DiracAdmin()

result = diracAdmin.getBDIISite(site, host=host)
if not result['OK']:
  print test['Message']
  DIRAC.exit(2)
  

sites = result['Value']
for site in sites:
  print "Site: %s {"%site.get('GlueSiteName','Unknown')
  for item in site.iteritems():
    print "%s: %s"%item
  print "}"


