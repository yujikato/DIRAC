# $Header: /tmp/libdirac/tmp.stZoy15380/dirac/DIRAC3/DIRAC/Core/Utilities/Mail.py,v 1.3 2008/08/26 17:40:30 paterson Exp $
__RCSID__ = "$Id: Mail.py,v 1.3 2008/08/26 17:40:30 paterson Exp $"
"""
    Extremely simple utility class to send mails
"""
import socket
from smtplib import SMTP
from DIRAC import gLogger,S_OK,S_ERROR

class Mail( SMTP ):
  def __init__( self ):
    from getpass import getuser
    self._hostname = socket.getfqdn()
    self._subject = ''
    self._message = ''
    self._mailAddress = ''
    self._fromAddress = getuser() + '@' + self._hostname
    self.esmtp_features = {}
    self.local_hostname = '[127.0.0.1]'

  def _send( self ):
    try:
      self.connect( )
      self.ehlo( self._hostname )
    except socket.error:
      gLogger.info( 'Could not connect to mail server' )
      return S_ERROR( 'Could not connect to mail server' )


    self.set_debuglevel( None )

    if not self._mailAddress:
      gLogger.warn( "No mail address was provided. Mail not sent." )
      return S_ERROR( "No mail address was provided. Mail not sent." )

    if not self._message:
      gLogger.warn( "Message body is empty" )
      if not self._subject:
        gLogger.warn( "Subject and body empty. Mail not sent" )
        return S_ERROR ( "Subject and body empty. Mail not sent" )

    mailString = "From: %s\nTo: %s\nSubject: %s\n%s\n"
    addresses = self._mailAddress
    if not type(self._mailAddress)==type([]):
      addresses = [self._mailAddress]

    text = mailString % ( self._fromAddress, ', '.join( addresses ),
                          self._subject, self._message )

    try:
      self.sendmail( self._fromAddress, self._mailAddress, text )
    except Exception, v:
      gLogger.error( "Sending mail failed", str( v ) )
      return S_ERROR("Sending mail failed %s" % str( v ) )

    self.quit()
    gLogger.info( "The mail was succesfully sent", "to %s" \
                  % ', '.join( addresses ) )
    return S_OK( "The mail was succesfully sent" )
