import DIRAC
from DIRAC import gLogger
from DIRAC.Core.DISET.RPCClient import RPCClient
from DIRAC.FrameworkSystem.Client.LoggerClient import LoggerClient


LClient = LoggerClient()

retval = LClient.getSites()
if not retval['OK']: print retval['Message']
else: print retval['Value'][0:2]

conditions = { 'SystemName': ['Framework/SecurityLog', 'DataManagement/TransferDBMonitoring']}
retval = LClient.getMessages( conds = conditions, beginDate = '2008-10-06' )
if not retval['OK']: print retval['Message']
else:
  print retval['Value']['ParameterNames'] 
  print retval['Value']['Records'][0:2]

retval = LClient.getSystems()
if not retval['OK']: print retval['Message']
else: print retval['Value'][0:2]

retval = LClient.getSubSystems()
if not retval['OK']: print retval['Message']
else: print retval['Value'][0:2]

retval = LClient.getGroups()
if not retval['OK']: print retval['Message']
else: print retval['Value'][0:2]

retval = LClient.getFixedTextStrings()
if not retval['OK']: print retval['Message']
else: print retval['Value'][0:2]

retval = LClient.getMessagesByFixedText( 'File not found!' )
if not retval['OK']: print retval['Message']
else:
  print retval['Value']['ParameterNames']
  print retval['Value']['Records'][0:4]

showFields= [ 'SystemName', 'SubSystemName', 'OwnerDN' ]
conditions={ 'SystemName': [ 'WorkloadManagement/Matcher', 'Framework/ProxyManager' ],  
             'LogLevel': 'ERROR' }
orderFields = [ [ 'OwnerDN', 'ASC' ], ['SystemName', 'ASC' ] ]
retval = LClient.getGroupedMessages( fieldList = showFields, conds = conditions, 
                                     beginDate = '2008-09-18',endDate = '2008-09-20',
                                     groupField = 'SystemName', orderList = orderFields )
if not retval['OK']: print retval['Message']
else:
  print retval['Value']['ParameterNames']
  print retval['Value']['Records'][0:4]

orderFields = [ [ 'recordCount', 'DESC' ] ]
retval =  LClient.getGroupedMessages( groupField = 'FixedTextString', orderList = orderFields,
                                      maxRecords = 10 )
if not retval['OK']: print retval['Message']
else:
  print retval['Value']['ParameterNames']
  print retval['Value']['Records'][0:4]
