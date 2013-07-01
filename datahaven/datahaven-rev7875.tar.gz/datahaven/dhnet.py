#!/usr/bin/python

import os
import sys
import logging
import time
import optparse
import urllib
import StringIO
import struct
import tempfile
import traceback

from SimpleXMLRPCServer import SimpleXMLRPCServer

sys.path.append(os.path.abspath('cs'))
sys.path.append(os.path.abspath(os.path.join('..', 'cs')))
sys.path.append(os.path.abspath('.'))

# print '\n'.join(sys.path)

from ncrypt0.rsa import RSAKey, RSAError
from ncrypt0.digest import DigestType, Digest
from nitro.selectreactor import SelectReactor
from nitro.http import HttpRequest
from nitro.tcp import tcpConnect, TCPStream, TCPMessageStream
from nitro.async import AsyncOp
from cspace.main.service import CSpaceService
from cspace.main.common import isValidUserName, localSettings, profileSettings, LocalSettings
from cspace.main.profile import Profile, Contact, createProfile, listProfiles, loadProfile, saveProfileContacts, clearProfileContacts
from cspace.main.appletserver import AppletServer
from cspace.network.sslutil import set_CA_cert_path, set_CA_key_path

#------------------------------------------------------------------------------ 

reactor = None

# CSpace can open a socket for us - directly to the remote machine
# after we sent a file we keep it opened ...
# to be able to send the next file as soon as possible
# we can send several files at same time - several opened sockets to this user
# of course we want to the socket after file sent ...
# but let's keep last socket opened ...    or last N sockets 
OPENED_SENDING_STREAMS_NUMBER = 1
# after we receive a file from this man
# we check if we have more files receiving at the moment from him
# if yes - close this stream because not needed
# so keep last N streams opened after receiving
# may be we want to have more streams opened to increase speed 
OPENED_RECEIVING_STREAMS_NUMBER = 2

_AppLogger = None
_TempLocation = None
_Notifier = None
_ReceivingStreams = {}
_SendingStreams = {}
_SendingDelay = 0.01
_OutgoingFilesDict = {}
_OutgoingQueue = []
_ContactStatus = {}

#------------------------------------------------------------------------------ 

class Application:
    def __init__(self, reactor, options, args):
        global _TempLocation
        
        self.reactor = reactor

        if options.homedir:
            self.homeDir = options.homedir.strip('"')
        else:
            self.homeDir = os.path.join("~", ".CSpace")
            self.homeDir = os.path.expanduser(self.homeDir)
        if not os.path.isdir(self.homeDir):
            try:
                os.makedirs(self.homeDir)
            except:
                logger().exception('can not create %s folder' % self.homeDir)
        os.environ['CSPACEHOMEDIR'] = self.homeDir

        if options.tmpdir:
            _TempLocation = options.tmpdir.strip('"')
        
        self.request_registration = False
        if options.register:
            self.request_registration = True
            if len(args) >= 2:
                self.username = args[0]
                self.password = args[1]
            else:
                import time
                self.username = 'dhn' + time.strftime('%Y%m%d%H%M%S')
                self.password = os.urandom(12)
        
        self.probeDict = {}
        self.xmlport = options.xmlport
        self.seedNodes = []
        for node in options.seednodes:
            n = node.split(':')
            self.seedNodes.append((n[0], int(n[1])))
        
    def init(self):
        self.service = CSpaceService(self.seedNodes, reactor=self.reactor)
        notify()
        self.server = SimpleXMLRPCServer(('localhost', self.xmlport), allow_none=True, logRequests=False)
        self.reactor.addReadCallback(self.server, self.server.handle_request)
        self.server.register_instance(self, allow_dotted_names = True)
        self.xmlrpcport = self.server.socket.getsockname()[1]
        self.appletport = self.service.appletServer.listenPort
        
        ca_key_path = os.path.join(self.homeDir, 'ca.key')
        ca_cert_path = os.path.join(self.homeDir, 'ca.pem')
        try:
            fout = open(ca_key_path, 'wb')
            fout.write(CA_KEY().decode('ascii'))
            fout.close()
            fout = open(ca_cert_path, 'wb')
            fout.write(CA_CERT().decode('ascii'))
            fout.close()
        except:
            logger().exception('error creating CA files')
        set_CA_key_path(ca_key_path)
        set_CA_cert_path(ca_cert_path)
        
        self.dispatcher = self.service.dispatcher
        self.dispatcher.register('service.start', self.onStarted)
        self.dispatcher.register('service.stop', self.onStopped)
        self.dispatcher.register('profile.connecting', self.onConnecting)
        self.dispatcher.register('profile.disconnecting', self.onDisconnecting)
        self.dispatcher.register('profile.online', self.onOnline)
        self.dispatcher.register('profile.offline', self.onOffline)
        self.dispatcher.register('profile.reconnecting', self.onReconnect)
        self.dispatcher.register('contact.online', self.onUserOnline)
        self.dispatcher.register('contact.action', self.onUserAction)
        self.dispatcher.register('contacts.probing', self.onContactsProbing)
        self.dispatcher.register('contacts.probed', self.onContactsProbed)
        self.dispatcher.register('contact.offline', self.onUserOffline)
        self.dispatcher.register('offlineim.get', self.onOfflineReceive)
        self.dispatcher.register('offlineim.put', self.onOfflineStore)
        self.dispatcher.register('offlineim.del', self.onOfflineDelete)
        self.dispatcher.register('error', self.onError)

        actionId = self.registerSendAction()
        logger().info('registered "send" action with ID %s' % str(actionId))

        self.registerReceiveService()
        logger().info('registered "receive" service')

        self.ProcessSending()

    def run(self):
        try:
            self.writePID(self.xmlrpcport, self.appletport)
            self.service.run()
            self.deletePID()
        except:
            logger().exception('ERROR!')

    def register(self, username, password):
        logger().info('register %s' % username)
        rsaKey = RSAKey()
        rsaKey.generate( bits=2048 )
        data = 'username:%s' % username
        digestType = DigestType('SHA1')
        digest = Digest(digestType).digest( data )
        signature = rsaKey.sign( digest, digestType )
        form = dict(username=username, public_key=rsaKey.toPEM_PublicKey(), signature=signature)
        postData = urllib.urlencode( form )
        self._reactor = SelectReactor()
        request = HttpRequest(self._reactor)
        httpOp = request.post('http://identity.datahaven.net/cspacekey', postData, self.onRegisterResponse )
        self._keyId = -1
        self._reactor.run()
        if self._keyId >= 0:
            st = self.settings()
            st.setString('Settings/SavedProfile', username)
            st.setString('Settings/SavedPassword', password)
            st.setInt('Settings/RememberKey', 1)
            self.createProfile(rsaKey, password, username, str(self._keyId))
            logger().info(username + ' registered, key id is ' + str(self._keyId))
        else:
            logger().info('registration failed')
        del self._keyId
        del self._reactor

    def sendControlCommand(self, command, data=''):
        controlCommand(command, data)

    def getPIDpath(self, appName="CSpace"):
        pidfile = "%s.run" % appName
        pidpath = self.homeDir
        if not os.path.exists(pidpath):
            os.makedirs(pidpath)
        pidpath = os.path.join(pidpath, pidfile)
        return pidpath

    def writePID(self, xmlrpcport, appletport):
        pidpath = self.getPIDpath()
        pidfile = file(pidpath, "wb")
        pidfile.write("%i\n%i\n%i\n" % (os.getpid(), xmlrpcport, appletport))
        pidfile.close()
    
    def deletePID(self):
        pidpath = self.getPIDpath()
        os.unlink(pidpath)

    def settings(self, location='CSpace'):
        return localSettings(location)
    
    def profile(self, settings_location='CSpace', profile_location='CSpaceProfiles'):
        if not self.settings(settings_location).getInt('Settings/RememberKey', 0):
            return None
        if not self.settings(settings_location).getInt('Settings/RememberKey', 0):
            return None
        entries = [entry for userName,keyId,entry in listProfiles(profile_location)]
        entry = self.settings(settings_location).getString('Settings/SavedProfile')
        password = self.settings(settings_location).getString('Settings/SavedPassword')
        if not (entry and password and (entry in entries)):
            return None
        return loadProfile(entry, password, profile_location)        

    def createProfile(self, rsaKey, password, userName, keyId, profile_location='CSpaceProfiles') :
        ps = profileSettings(profile_location)
        baseEntry = userName
        entry = baseEntry
        suffix = 0
        while ps.getData(entry+'/PrivateKey') :
            suffix += 1
            entry = '%s-%d' % (baseEntry,suffix)
        encKey = rsaKey.toPEM_PrivateKey( password )
        ps.setData(entry+'/PrivateKey', encKey)
        ps.setData(entry+'/Name', userName)
        if keyId is not None :
            ps.setData(entry+'/KeyID', keyId)
        profile = Profile(rsaKey, userName, keyId, entry)
        return profile

    def patchPermissions(self):
        import cspace.main.permissions        
        cspace.main.permissions.predefinedPermissions = "allow <any-user> service <any-service>\n"
        
    def setPermissions(self):
        self.service.session.permissions.setUserPermissions("allow <any-user> service receive\n")

    def registerSendAction(self):
        self.service.actionManager.activeActions.append(('send', 'send', '', 0))
        actionID = self.service.actionManager.registerAction('send', self.onAction, 0)
        self.service.appletServer.actions.append(actionID)
        self.service.actionManager.setDefaultAction(actionID)
        return actionID

    def registerReceiveService(self):
        logger().info('registerReceiveService callback id is %d' % id(self.onService))
        return self.service.session.registerService('receive', self.onService)

    def isContact(self, keyID):
        if self.service.profile is None:
            return False
        return keyID in self.service.profile.contactNames.keys()

    def contact(self, keyID):
        if self.service.profile is None:
            return None
        if not self.isContact(keyID):
            return None
        return self.service.profile.getContactByName(keyID)

    def state(self, keyID):
        global _ContactStatus
        return _ContactStatus.get(keyID, 'unknown')

    def status(self, keyID):
        c = self.contact(keyID)
        if c is None:
            return self.service.UNKNOWN
        return hasattr(c, 'status') and c.status or self.service.UNKNOWN
    
    #------------------------------------------------------------------------------ 

    def online(self):
        return self.service.online()
        
    def offline(self):
        return self.service.offline()
        
    def remove(self, buddy):
        return self.service.remove(buddy)
        
    def list(self):
        return self.service.list()
        
    def probe(self, keyID, cb=None):
        if not self.probeDict.has_key(keyID):
            self.probeDict[keyID] = []
        if cb is not None:
            self.probeDict[keyID].append(cb)
        return self.service.probe(keyID)
        
    def buddy(self, buddy):
        return self.service.contactinfo(buddy)

    def stop(self):
        return self.service.stop()
        
    def action(self, keyID, action):
        return self.service.action(keyID, action)

    def send(self, keyID, filename, transferID, description):
        def _do_send():
            if self.status(keyID) == self.service.ONLINE:
                pushFileName(keyID, filename, transferID, description)
            else:
                notify().sent(keyID, filename, transferID, 'failed', None, 'contact is offline')
        def _probed(contact, status):
            _do_send()
        def _do_probe():
            self.probe(str(keyID), _probed)
        def _added(contact):
            if contact is None:
                return
            _do_probe()
        if self.service.profile is None:
            logger().info('send ERROR, profile is None')
            return False
        if not self.isContact(keyID):
            self.add(keyID, _added)
            return True
        if self.status(keyID) == self.service.OFFLINE:
            _do_probe()
            return True
        _do_send()
        return True

    def add(self, keyID, add_callback=None):
        if self.service.profile.contactNames.has_key(keyID):
            if add_callback is not None:
                add_callback(self.service.profile.contactNames.get(keyID))
            return
        
        def _onLookupResponse(responseCode, data):
            if responseCode != 200 :
                if add_callback is not None:
                    add_callback(None)
                return
            inp = StringIO.StringIO( data )
            name = inp.readline().strip()
            pemPublicKey = inp.read()
            if name and not isValidUserName(name) :
                if add_callback is not None:
                    add_callback(None)
                return

            k = RSAKey()
            try:
                k.fromPEM_PublicKey( pemPublicKey )
            except:
                logger().exception('can not create a key for user %s, keyID=%s' %(name, keyID))
                if add_callback is not None:
                    add_callback(None)

            contact = Contact(k, str(keyID))
            if str(keyID) in self.service.profile.contactNames.keys():
                self.service.profile.removeContact(contact)
            self.service.profile.addContact(contact)
            saveProfileContacts(self.service.profile)
            if add_callback is not None:
                add_callback(contact)

        httpOp = HttpRequest( self.reactor )
        httpOp.get('http://identity.datahaven.net/cspacekeys/%s' % keyID, _onLookupResponse )
        
    #------------------------------------------------------------------------------ 

    def readSendingQueue(self):
        global _OutgoingQueue
        if len(_OutgoingQueue) == 0:
            return None
        return _OutgoingQueue.pop(0)
    
    def ProcessSending(self):
        global _SendingDelay
        keyID = self.readSendingQueue()
        if keyID:
            self.service.action(keyID, 'send')
            _SendingDelay = 0.01
        else:
            if _SendingDelay < 2.0:
                _SendingDelay *= 2.0
        # attenuation
        self.reactor.callLater(_SendingDelay, self.ProcessSending)

    #------------------------------------------------------------------------------ 

    def onRegisterResponse( self, returnCode, data ) :
        logger().info('onRegisterResponse retCode=%s' % str(returnCode))
        if returnCode != 200 :
            self._keyId = -1
        else:
            try :
                keyId = int(data)
                self._keyId = keyId
            except:
                self._keyId = -1
        self._reactor.stop()

    def onError(self, msg):
        self.sendControlCommand('error', '"%s"' % msg)

    def onSessionService(self):
        pass

    def onStarted(self):
        self.sendControlCommand('service-started')
        
    def onConnecting(self, profile):
        self.sendControlCommand('service-connecting')

    def onOnline(self, profile):
        self.sendControlCommand('online')
        if self.service.profile:
            self.setPermissions()
            # clearProfileContacts(self.service.profile)
            # self.service.profile.contactKeys.clear()
            # self.service.profile.contactNames.clear()
            # logger().info('all contacts was removed')
    
    def onDisconnecting(self, profile):
        self.sendControlCommand('disconnecting')

    def onOffline(self, profile):
        self.sendControlCommand('offline')

    def onReconnect(self, e):
        self.sendControlCommand('service-reconnect')

    def onStopped(self):
        global _SendingStreams
        global _ReceivingStreams
        for streams in _SendingStreams.values():
            for stream in streams:
                stream.close_stream()
        for streams in _ReceivingStreams.values():
            for stream in streams:
                stream.close_stream()
        self.sendControlCommand('service-stopped')
    
    def onContactsProbing(self, contacts):
        # self.sendControlCommand('probing')
        pass
    
    def onContactsProbed(self, contacts):
        # self.sendControlCommand('probed')
        pass
        
    def onUserOnline(self, contact):
        global _ContactStatus
        if self.probeDict.has_key(contact.name):
            for cb in self.probeDict[contact.name]:
                cb(contact, 'online')
            del self.probeDict[contact.name]
        _ContactStatus[contact.name] = 'online'
        notify().contact_status(contact.name, 'online')

    def onUserOffline(self, contact):
        global _ContactStatus
        if self.probeDict.has_key(contact.name):
            for cb in self.probeDict[contact.name]:
                cb(contact, 'offline')
            del self.probeDict[contact.name]
        _ContactStatus[contact.name] = 'offline'
        notify().contact_status(contact.name, 'offline')
        
    def onUserAction(self, contact, action, retval):
        pass
    
    def onOfflineReceive(self, ts, msg, peerPubKey):
        pass
        
    def onOfflineStore(self, msg):
        pass
        
    def onOfflineDelete(self, envelope):
        pass
        
    def onAction(self, contactName):
        global reactor
        (filename, transferID, description) = popFileName(contactName)
        if filename == '' or transferID is None:
            notify().sent(contactName, filename, transferID, 'failed', None, 'no files to that user found in the queue')
            return
        def onConnectUser( err, sock ) :
            global _SendingStreams
            if err < 0 :
                try:
                    if sock is not None:
                        sock.close()
                except:
                    logger().exception()
                notify().sent(contactName, filename, transferID, 'failed', err, 'error connecting')
                return
            if not _SendingStreams.has_key(contactName):
                _SendingStreams[contactName] = []
            stream = TCPMessageStream(sock, self.reactor)
            newSender = FileSender(self.reactor, stream, contactName)
            newSender.start(filename, transferID, description)
            _SendingStreams[contactName].append(newSender)
        def onConnect( connector ) :
            if connector.getError() != 0:
                notify().sent(contactName, filename, transferID, 'failed', None, 'connection error: ' + connector.getErrorMsg())
                return
            CSpaceConnector(connector.sock, contactName, 'receive', self.reactor, onConnectUser)
        tcpConnect(('127.0.0.1', self.appletport), self.reactor, onConnect)
        
    def onService(self, sslConn, peerKey, contactName, contactKeyID, incomingName):
        global reactor
        connectionId = self.service.appletServer.incoming.addIncoming(sslConn, peerKey)
        def onAccept(err, sock, contactName):
            global _ReceivingStreams
            if err < 0 :
                try:
                    if sock is not None:
                        sock.close()
                except:
                    logger().exception('onService.onAccept err=%d, contactName=%s' % (err, contactName))
                notify().receive('', 'failed', contactKeyID, err, 'error: ' + str(err))
                return
            if not _ReceivingStreams.has_key(contactKeyID):
                _ReceivingStreams[contactKeyID] = []
            stream = TCPMessageStream(sock, self.reactor)
            newReceiver = FileReceiver(self.reactor, contactKeyID, stream)
            _ReceivingStreams[contactKeyID].append(newReceiver)
        def onConnect(connector, contactKeyID):
            if connector.getError() != 0 :
                notify().receive('', 'failed', contactKeyID, None, 'error connecting to CSpace on local machine')
                return
            sock = connector.getSock()
            CSpaceAcceptor(sock, connectionId, self.reactor, lambda e,s: onAccept(e,s, contactKeyID))
        # logger().info('onService contactName=%s' % contactName)
        tcpConnect(('127.0.0.1', self.appletport), self.reactor, lambda c: onConnect(c, contactKeyID))
    
    #------------------------------------------------------------------------------
    
    def test_ssl0(self):
        from ncrypt0.rsa import RSAKey, RSAError
        # from cspace.network.sslutil import makeSSLContext
        from ncrypt0.ssl import SSLContext, SSLConnection, SSL_VERIFY_MODE_NONE, SSL_VERIFY_MODE_SELF_SIGNED, SSL_METHOD_TLSv1
        from socket import socket
        from OpenSSL.SSL import Context, Connection, WantReadError, TLSv1_METHOD, OP_NO_SSLv2, VERIFY_PEER, VERIFY_FAIL_IF_NO_PEER_CERT
        from OpenSSL.crypto import X509, FILETYPE_PEM, load_privatekey, load_certificate
        
        def b(s):
            return s
        
        def makeCertifiace(userName, rsaKey):
            key = load_privatekey(FILETYPE_PEM, rsaKey.toPEM_PrivateKey())
            cert = X509()
            cert.get_subject().CN = userName
            cert.set_issuer(cert.get_subject())
            cert.set_pubkey(key)
            cert.set_notBefore("20000101000000Z")
            cert.set_notAfter("22000101000000Z")
            cert.set_serial_number(1)
            cert.sign(key, "sha1")
            return cert

        def makeSSLContext(userName, rsaKey) :
            cert = makeCertifiace(userName, rsaKey)
            sslContext = SSLContext( SSL_METHOD_TLSv1 )
            # store = sslContext.c.get_cert_store()
            # store.add_cert(cert)
            # sslContext.c.set_verify(VERIFY_PEER | VERIFY_FAIL_IF_NO_PEER_CERT, lambda connection, x509, errno, depth, preverifyOK: preverifyOK)
            # sslContext.c.set_options(OP_NO_SSLv2)
            sslContext.setCertificate( cert )
            sslContext.setPrivateKey( rsaKey )
            sslContext.checkPrivateKey()
            sslContext.setVerifyMode(SSL_VERIFY_MODE_NONE)
            return sslContext
            
        def socket_pair():
            port = socket()
            port.bind(('', 0))
            port.listen(1)
            client = socket()
            client.setblocking(False)
            client.connect_ex(("127.0.0.1", port.getsockname()[1]))
            client.setblocking(True)
            server = port.accept()[0]
            server.send(b("x"))
            print client.recv(1024)
            client.send(b("y"))
            print server.recv(1024)
            server.setblocking(False)
            client.setblocking(False)
            return (server, client)

        def clientContext():
            ps = self.profile('CSpace_cli', 'CSpaceProfiles_cli')
            # entry = self.settings('CSpace_cli').getString('Settings/SavedProfile')
            userName = ps.name
            keyId = ps.keyId
            rsaKey = ps.rsaKey
            print 'clientContext', userName
            cont = makeSSLContext(userName, rsaKey)
            return cont
        
        def serverContext():         
            ps = self.profile('CSpace_srv', 'CSpaceProfiles_srv')
            # entry = self.settings('CSpace_srv').getString('Settings/SavedProfile')
            userName = ps.name
            keyId = ps.keyId
            rsaKey = ps.rsaKey
            print 'serverContext', userName
            cont = makeSSLContext(userName, rsaKey)
            return cont
       
        def clientFactory(context, socket):
            client = Connection(context, socket)
            client.set_connect_state()
            return client
        
        def serverFactory(context, socket):
            server = Connection(context, socket)
            server.set_accept_state()
            return server
        
        def handshake(client, server):
            conns = [client, server]
            while conns:
                for conn in conns:
                    try:
                        conn.do_handshake()
                    except WantReadError:
                        pass
                    else:
                        conns.remove(conn)
                        
        srvSock, cliSock = socket_pair()
        srvContext, cliContext = (serverContext(), clientContext())
        server, client = (serverFactory(srvContext.c, srvSock), clientFactory(cliContext.c, cliSock))
        handshake(client, server)
        server.setblocking(True)
        client.setblocking(True)
        count = server.send(b('xy'))
        print client.recv(2)
        count = client.send(b('yx'))
        print server.recv(2)
        print 'srv', server.get_peer_certificate()
        print 'cli', client.get_peer_certificate().get_subject().commonName

    def test_ssl1(self):
        dumped = '''-----BEGIN RSA PRIVATE KEY-----
MIIBDQIBAAKCAQEA0I3bi9M/Ee7DkrIIPUT41Qf5jVHmbnks5r5Oe96B9EzkTgFO
Wwi8/SkT03zHG+0X0+2eIlgHtT2eKMFfasRtmimAEHP3jI89vBY+BA64vnqmgQVo
CxVNnLkNcMICTdgq/qHpIKBG+6kUW0++KCierRJ0xqc7Xgs0RoN1DnznY2mQm69D
J8uynu9JAW2wIl+Iqz6DaXdnfXBHFEdB3/RTUUzjqL+ucr9HCqCYHeOcG/xszSxF
1q+nY8F+IovSI6Q+XXFiHwqdYXixeMtHNcSa5cJkpz98FXQJF7oDcLuo7MM9/GYW
94co66dHoQeNwoncupBFu+CEKJUBe95m1n1YnQIDAQAB
-----END RSA PRIVATE KEY-----'''
        k = RSAKey()
        k.fromPEM_PrivateKey(dumped)
        print k.toPEM_PublicKey()
        

    def test_ssl2(self):
        from nitro.ssl import sslConnect, sslAccept
        from nitro.tcp import tcpListen, tcpConnect
        from ncrypt0.ssl import SSLContext, SSLConnection
        from ncrypt0.rsa import RSAKey, RSAError
        from cspace.network.sslutil import makeClientSSLContext, makeServerSSLContext

        reactor = SelectReactor()
        
        def clientContextCertVerifyCallback(conn, cert, errno, depth, preverify_ok):
            print 'clientContextCertVerifyCallback', conn, errno, depth, preverify_ok, cert.get_pubkey(), cert.get_subject().CN
            return preverify_ok
        
        def clientContext():
            # ps = self.profile('CSpace_cli', 'CSpaceProfiles_cli')
            # entry = self.settings('CSpace_cli').getString('Settings/SavedProfile')
            # userName = ps.name
            # keyId = ps.keyId
            # rsaKey = ps.rsaKey
            rsaKey = RSAKey()
            rsaKey.fromPEM_PrivateKey(open('cs/CliPrivateKey', 'rb').read(), open('cs/CliSavedPassword', 'rb').read().strip('"'))
            userName = open('cs/CliName', 'rb').read()
            cont = makeClientSSLContext(userName, rsaKey, clientContextCertVerifyCallback)
            print 'clientContext', userName
            print rsaKey.toPEM_PublicKey()
            return cont
        
        def serverContextCertVerifyCallback(conn, cert, errno, depth, preverify_ok):
            print 'serverContextCertVerifyCallback', conn, errno, depth, preverify_ok, cert.get_pubkey(), cert.get_subject().CN
            return preverify_ok

        def serverContext():         
#            ps = self.profile('CSpace_srv', 'CSpaceProfiles_srv')
#            entry = self.settings('CSpace_srv').getString('Settings/SavedProfile')
#            userName = ps.name
#            keyId = ps.keyId
#            rsaKey = ps.rsaKey
            rsaKey = RSAKey()
            rsaKey.fromPEM_PrivateKey(open('cs/SrvPrivateKey', 'rb').read(), open('cs/SrvSavedPassword', 'rb').read().strip('"'))
            userName = open('cs/SrvName', 'rb').read()
            cont = makeServerSSLContext(userName, rsaKey, serverContextCertVerifyCallback)
            print 'serverContext', userName
            print rsaKey.toPEM_PublicKey()
            return cont

        def onConnect(connector, sslContext):
            print 'onConnect', connector
            # connector.getSock().write('xy')
            sslConn = SSLConnection( sslContext, connector.getSock() )
            print sslConn.getPeerCertificate()
            sslConn.conn.set_connect_state()
            connectOp = sslConnect( sslConn, reactor, lambda err: onSSLConnect(err, sslConn) )
            
        def onWrite(connector):
            print 'onWrite', connector

        def onSSLAccept(err, sslConn):
            peerCert = sslConn.conn.get_peer_certificate()
            peerKey = RSAKey()
            peerKey.fromPKey_PublicKey(peerCert.get_pubkey())
            print 'onSSLAccept', peerCert.get_subject().CN
            
        def onSSLConnect(err, sslConn):
            print 'onSSLConnect', err, sslConn.conn.get_peer_certificate().get_subject().CN
        
        def onIncomingTCP(sock, sslContext):
            print 'onIncomingTCP', sock
            # print sock.recv(2)
            sslConn = SSLConnection( sslContext, sock )
            # print sslConn.getPeerCertificate()
            sslConn.conn.set_accept_state()
            acceptOp = sslAccept( sslConn, reactor, lambda err: onSSLAccept(err, sslConn) )
            
        def onRead(sock):
            print 'onRead', sock
            
        if sys.argv.count('server'):
            listener = tcpListen( ('',0), reactor, None )
            localPort = listener.getSock().getsockname()[1]
            srvContext = serverContext()
            listener.setCallback( lambda sock: onIncomingTCP(sock, srvContext) )
            listener.enable( True )
            print 'server port is', localPort
        elif sys.argv.count('client'):
            localPort = int(sys.argv[sys.argv.index('client')+1])
            cliContext = clientContext()
            connector = tcpConnect(('127.0.0.1', localPort), reactor, lambda conn: onConnect(conn, cliContext))
        else:        
            listener = tcpListen( ('',0), reactor, None )
            localPort = listener.getSock().getsockname()[1]
            srvContext, cliContext = (serverContext(), clientContext())
            listener.setCallback( lambda sock: onIncomingTCP(sock, srvContext) )
            listener.enable( True )
            connector = tcpConnect(('127.0.0.1', localPort), reactor, lambda conn: onConnect(conn, cliContext))
        reactor.run()

#------------------------------------------------------------------------------ 

def controlCommand(command, data=''):
    # logger().info('controlCommand %s [%s]' % (command, str(data)))
    # request = HttpRequest(reactor)
    # postData = urllib.urlencode(dict(command=command, data=data), True)
    # return request.post(url, postData)
    sys.stdout.write('[%s] %s\n' % (command, str(data)))
    sys.stdout.flush()

#------------------------------------------------------------------------------ 

class Notifier():
    def sent(self, keyID, filename, transferID, status, err=None, msg=''):
        controlCommand('sent', (str(keyID), filename, transferID, status, err, msg))

    def receive(self, filename, status, peer, err=None, msg=''):
        controlCommand('receive', (str(peer), filename, status, err, msg))

    def contact_status(self, name, status):
        controlCommand('contact', (name, status))

def notify():
    global _Notifier
    if _Notifier is None:
        _Notifier = Notifier()
    return _Notifier

#------------------------------------------------------------------------------ 

class CSpace_stdout:
    softspace = 0
    def read(self): pass
    def write(self, s):
        # sys.stdout.write(time.strftime('%H:%M:%S') + '    ' + s)
        sys.stdout.write(s)
        sys.stdout.flush()
    def flush(self): pass
    def close(self): pass
    
#------------------------------------------------------------------------------ 
    
def popFileName(SendToKeyID):
    global _OutgoingFilesDict
    if not _OutgoingFilesDict.has_key(SendToKeyID):
        return '', None, ''
    try:
        (filename, transferID, description) = _OutgoingFilesDict[SendToKeyID].pop(0)
        # logger().info('popFileName %s %s %s %s' % (SendToKeyID, filename, str(transferID), description))
        return filename, transferID, description
    except:
        pass
        # logger().exception('exception in popFileName(%s)' % str(SendToKeyID))
    return '', None, ''

def pushFileName(SendToKeyID, filename, transferID, description):
    global _OutgoingQueue
    global _OutgoingFilesDict
    if not _OutgoingFilesDict.has_key(SendToKeyID):
        _OutgoingFilesDict[SendToKeyID] = list()
    _OutgoingFilesDict[SendToKeyID].append((filename, transferID, description))
    _OutgoingQueue.append(SendToKeyID)
    # logger().info('pushFileName %s %s %s %s' % (SendToKeyID, filename, str(transferID), description))

#------------------------------------------------------------------------------ 

class CSpaceConnector( object ) :
    def __init__( self, sock, remoteUser, remoteService, reactor, callback ) :
        self.stream = TCPStream( sock, reactor )
        self.stream.setCloseCallback( self._onClose )
        self.stream.setErrorCallback( self._onError )
        self.stream.setInputCallback( self._onInput )
        self.stream.initiateRead( 1 )
        self.stream.writeData( 'CONNECT %s %s\r\n' % (remoteUser,remoteService) )
        self.response = ''
        self.op = AsyncOp( callback, self.stream.close )

    def getOp( self ) : return self.op

    def _onClose( self ) :
        self.stream.close()
        self.op.notify( -1, None )

    def _onError( self, err, errMsg ) :
        self._onClose()

    def _onInput( self, data ) :
        self.response += data
        if self.response.endswith('\n') :
            if not self.response.startswith('OK') :
                self._onClose()
                return
            self.stream.shutdown()
            sock = self.stream.getSock()
            self.op.notify( 0, sock )

class CSpaceAcceptor( object ) :
    def __init__( self, sock, connectionId, reactor, callback ) :
        self.stream = TCPStream( sock, reactor )
        self.stream.setCloseCallback( self._onClose )
        self.stream.setErrorCallback( self._onError )
        self.stream.setInputCallback( self._onInput )
        self.stream.initiateRead( 1 )
        self.stream.writeData( 'ACCEPT %s\r\n' % connectionId )
        self.response = ''
        self.op = AsyncOp( callback, self.stream.close )

    def getOp( self ) : return self.op

    def _onClose( self ) :
        self.stream.close()
        self.op.notify( -1, None )

    def _onError( self, err, errMsg ) :
        self._onClose()

    def _onInput( self, data ) :
        self.response += data
        if self.response.endswith('\n') :
            if not self.response.startswith('OK') :
                self._onClose()
                return
            self.stream.shutdown()
            sock = self.stream.getSock()
            self.op.notify( 0, sock )

#------------------------------------------------------------------------------ 
# need to send files inside same stream
# close stream if only connection error or connection lost
class FileSender(object):
    CHUNK_SIZE = (2 ** 16) - 256

    def __init__(self, reactor, stream, peer):
        self.reactor = reactor
        self.stream = stream
        self.files2send = []
        self.peer = peer
        self.waitOp = None
        self.currentOp = None
        self.bytesSent = 0
        self.totalBytesSent = 0
        self.lastPacketTime = 0
        self.stream.setInputCallback(self.dataReceived)
        self.stream.setCloseCallback(self.connectionLost)
        self.stream.setErrorCallback(self.connectionError)
        self.stream.enableRead(True)
        self.state = 'ready'

    def start(self, filename, transferID, description):
        self.filename = filename
        self.transferID = transferID
        self.description = description
        if self.state != 'ready':
            self.close_file()
            self.state = 'lost'
            self.close_stream()
            return
        try:
            self.file = file(self.filename, 'rb')
            self.file.seek(0, 2)
            self.length = self.file.tell()
            self.file.seek(0)
        except:
            logger().exception('exception in FileSender.doWaitNewFiles')
            self.failed('failed', 'error reading input file')
            self.close_file()
            self.state = 'lost'
            self.close_stream()
            return
        try:
            self.stream.sendMessage(struct.pack("!Q", self.length))
        except:
            logger().exception('exception in FileSender.doWaitNewFiles')
            self.failed('failed', 'error writing, seems connection were lost')
            self.close_file()
            self.state = 'lost'
            self.close_stream()
            return
        self.bytesSent = 0
        self.state = 'sending'
        self.doSend()

    def doSend(self):
        self.currentOp = None
        chunk = self.file.read(self.CHUNK_SIZE)
        if not chunk:
            self.close_file()
            self.state = 'waiting'
            self.doWaitFinishSending()
            return
        self.stream.sendMessage(chunk)
        self.bytesSent += len(chunk)
        self.currentOp = self.reactor.callLater(0, self.doSend)

    def doWaitFinishSending(self):
        #all data was sent
        #now need to wait to finish receiving
        #but we do not want to wait too long
        #if we did not receive any response
        #we assume the connection was lost
        def sent_timeout():
            if time.time() - self.lastPacketTime > 30:
                self.waitOp = None
                self.failed('timeout', 'other side not responding')
                self.state = 'lost'
                self.close_stream()
            else:
                self.doWaitFinishSending()
        self.waitOp = self.reactor.callLater(60, sent_timeout)

    def dataReceived(self, data):
        self.lastPacketTime = time.time()
        bytesReceived ,= struct.unpack("!Q", data[:8])
        if bytesReceived == self.length:
            self.done()
            self.state = 'sent'
            self.close_wait_op()
            self.close_stream_if_has_other_opened()
            #self.doWaitNewFiles()
        elif bytesReceived > self.length:
            self.failed('failed', 'data did not sent correctly')
            self.close_wait_op()
            self.state = 'error'
            self.close_stream()
            #self.doWaitNewFiles()

    def connectionLost(self):
        if self.state in ['sending',]:
            self.failed('failed', 'connection lost while %s' % self.state)
        self.close_file()
        self.close_wait_op()
        self.state = 'lost'
        self.close_stream()

    def connectionError(self, err, errMsg):
        if self.state in ['sending',]:
            self.failed('failed', 'connection error while %s: %s' % (self.state, errMsg))
        self.close_file()
        self.close_wait_op()
        self.state = 'error'
        self.close_stream()

    def done(self):
        self.totalBytesSent += self.bytesSent
        notify().sent(self.peer, self.filename, self.transferID, 'finished')

    def failed(self, status, msg):
        notify().sent(self.peer, self.filename, self.transferID, status, None, msg)

    def close_wait_op(self):
        if self.waitOp is not None:
            self.waitOp.cancel()
            self.waitOp = None

    def close_file(self):
        try:
            self.file.close()
        except:
            pass
        self.file = None

    def close_stream(self):
        global _SendingStreams
        try:
            if not self.stream.stream.shutdownFlag:
                fileno = self.stream.stream.sock.fileno()
                self.stream.close()
        except:
            logger().exception('exception in FileSender.close_stream')
        if _SendingStreams.has_key(self.peer):
            if self in _SendingStreams[self.peer]:
                _SendingStreams[self.peer].remove(self)
        else:
            logger().critical('can not find %s in _SendingStreams' % self.peer)

    def close_stream_if_has_other_opened(self):
        return self.close_stream()


class FileReceiver(object):
    def __init__(self, reactor, peer, stream):
        self.reactor = reactor
        self.peer = peer
        self.stream = stream
        self.bytesReceived = 0
        self.totalBytesReceived = 0
        self.length = 0
        self.fd = None
        self.filename = ''
        self.gotLength = False
        self.close_op = None
        self.state = 'ready'
        self.stream.setInputCallback(self.dataReceived)
        self.stream.setCloseCallback(self.connectionLost)
        self.stream.setErrorCallback(self.connectionError)
        self.stream.enableRead(True)

    def openFile(self):
        global _TempLocation
        if _TempLocation:
            self.fd, self.filename = tempfile.mkstemp('', '', _TempLocation)
        else:
            self.fd, self.filename = tempfile.mkstemp()

    def closeFile(self):
        if self.fd is not None:
            os.fsync(self.fd)
            os.close(self.fd)
            self.fd = None

    def dataReceived(self, data):
        if self.state == 'ready':
            self.openFile()
            self.length ,= struct.unpack("!Q", data[:8])
            self.bytesReceived = 0
            data = data[8:]
            self.state = 'receiving'
            
        if self.state == 'receiving':
            os.write(self.fd, data)
            self.bytesReceived += len(data)
            self.stream.sendMessage(struct.pack("!Q", self.bytesReceived))
            if self.bytesReceived == self.length:
                self.closeFile()
                self.totalBytesReceived += self.bytesReceived
                notify().receive(self.filename, 'finished', self.peer)
                self.state = 'received'
                self.doWaitToClose()

    def doWaitToClose(self):
        # all data was received
        # now need to wait to close that stream
        # we want other side to do this
        # but if it is not - we will close it in 10 seconds
        def close_timeout():
            self.close_op = None
            self.state = 'finished'
            self.close_stream_if_has_other_opened()
        self.close_op = self.reactor.callLater(10, close_timeout)

    def stopWaitToClose(self):
        if self.close_op is not None:
            self.close_op.cancel()
            self.close_op = None

    def connectionLost(self):
        if self.state == 'receiving':
            self.closeFile()
            self.state = 'lost'
            notify().receive(self.filename, 'failed', self.peer, None, 'connection lost')
        self.stopWaitToClose()
        self.close_stream()

    def connectionError(self, err, errMsg):
        if self.state == 'receiving':
            self.closeFile()
            self.state = 'error'
            notify().receive(self.filename, 'failed', self.peer, err, 'connection error: ' + errMsg)
        self.stopWaitToClose()
        self.close_stream()

    def close_stream(self):
        global _ReceivingStreams
        try:
            if not self.stream.stream.shutdownFlag:
                fileno = self.stream.stream.sock.fileno()
                self.stream.close()
        except:
            logger().exception('exception in FileReceiver.close_stream')
        if _ReceivingStreams.has_key(self.peer):
            if self in _ReceivingStreams[self.peer]:
                _ReceivingStreams[self.peer].remove(self)
        else:
            logger().critical('can not find %s in _ReceivingStreams' % self.peer)

    def close_stream_if_has_other_opened(self):
        return self.close_stream()

#------------------------------------------------------------------------------ 

def CA_KEY():
    return '''-----BEGIN RSA PRIVATE KEY-----
MIIEpgIBAAKCAQEA1XegQ7Qr1lbIf0ldWLkVEve1rqahz1A6AjFGTkXXHagTlT5y
OncQoIZXDvswJGjawjgG2J1DetwLfK+Xw746QVp/SfQAl+F+hX29BppCctPL7avB
NmTvq2VTR2QpAdRo9tv3toy/LnuUWFxere1HWmTq6+tiNuVQALy56yex5HV1FSGT
gnEKbQCe8jYRoCf3mi9fx56Ynd9ZDY8Usxl3ZGS2W+8dbKrC8srBtN65DIWsmvQS
Xw3EOHF/zOGzGkYzp8BgxjOC6pgdSGjcW6NzrdnkCcps2g002gDOdHKrMs5qDznS
3xVm7BsGAfAjvywsCPY45AkUIFOTwBl6AKTIrQIDAQABAoIBAQDMhrl/JPl7e9rO
WjSd9XdDnSLuG6mdQHjT8PIzvKbHO2rH6/T2H25G33A6YmFWAUDYJWYp1UP6SyqW
ZIc8fN7EDzk2WhrXaq4WqMqbsOFJs7QIHDAbNcqMpaCNHmJL5oBLRaapuWDT4IPZ
xWbRri5XZanQMM8BWeS1UB2yOW4wPLnV66QAO85dWGPjrCu2blHdEOHUsXgY/OKC
rFJEwF9gcFumC67K8WOk53cVRb1WbIiSzI29IhprFnk8aNho7NAra1SFDL6VtDkZ
V9SFQE3U8Dn0yheb/KYuiQGSA25CffbBvzZuoZI2NkqB51tjZpfmGGfFCuaEN8xp
OdxxrDfhAoGBAO1jRp1hxTglTvBMEDzV2H1CHoCTc6wO5+u+klncNeV/di3VLLdR
YXy0b809s7Jiy5+BwWPD+3jNgVbV/JkB01GS3ndCkpV5vyuuLNC7phwlg7fiXBge
t408iV280BvNYVe0oMfiiPqN3ZXtfnhO3mTpU2zT+7NcpCF8ocIGhVWvAoGBAOY0
OvD9vZpGOz/3uB1hzT4W0s8RpZq/m9P7/DhwEuDadpbJMzqrDh2L1lsvdZMfGk3P
f5Zl6J0ZQ9WFnMYBVep+1hsF7EE4aTUgcayYTiae0RKYddCMany+xTpmZtb+9pL1
XgIGqMujpNvoA5IFFpQoq1GJRgym/Y7lWJSKxTpjAoGBANX0sGSRBmxAVBGIvOnX
47OhsFQ6kfr1xFpZ/RY4v+sFIsLUa+Ud2DvJdSsK/bc+DEDLdj4xGaobrwNRAsX1
Oz0+nnvm6K8IeCEqbwIC3whnV3yY7GBg7xbBBR4TW45zYdTm3DLMHqGU066Zy28r
xo41LhfcR/O0/8mexzxVHD/JAoGBAIUEly5boGx9uoza6jNoKP2AmK14J/YEU9mp
GHPQJshw0+eLOSPkZZKjE+i6wriRV1Sw2qugFUp5p93Ah/dOHEQUqEkTIhIJs5k0
NxshIr9kM7EIEcPA72NHpJV7SF9hEj+Wsox/JpgM5hz/sth0Qji4S04hAS4cbBVe
5tFmYlK7AoGBALr65+WrWsVWKM7rtzUNLD5DswXlwMX3peY3HrYt3Hyh/PZJeDGu
LTWy3ruVqCFbLwqOvIJNLJCPBY4/fY4NkgwCrsbxPpYmNmehgbQvP68XyxI9Jsuk
buF3X83VvHBpcuvJIvLq2/YLmH5SnxkR63aHBJRXEr2N2uRfGq7sv5Hi
-----END RSA PRIVATE KEY-----
'''

def CA_CERT():
    return '''-----BEGIN CERTIFICATE-----
MIIC7DCCAdSgAwIBAwIBATANBgkqhkiG9w0BAQUFADAUMRIwEAYDVQQDEwljYS5j
c3BhY2UwIhgPMjAwMDAxMDEwMDAwMDBaGA8yMjAwMDEwMTAwMDAwMFowFDESMBAG
A1UEAxMJY2EuY3NwYWNlMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA
1XegQ7Qr1lbIf0ldWLkVEve1rqahz1A6AjFGTkXXHagTlT5yOncQoIZXDvswJGja
wjgG2J1DetwLfK+Xw746QVp/SfQAl+F+hX29BppCctPL7avBNmTvq2VTR2QpAdRo
9tv3toy/LnuUWFxere1HWmTq6+tiNuVQALy56yex5HV1FSGTgnEKbQCe8jYRoCf3
mi9fx56Ynd9ZDY8Usxl3ZGS2W+8dbKrC8srBtN65DIWsmvQSXw3EOHF/zOGzGkYz
p8BgxjOC6pgdSGjcW6NzrdnkCcps2g002gDOdHKrMs5qDznS3xVm7BsGAfAjvyws
CPY45AkUIFOTwBl6AKTIrQIDAQABo0UwQzASBgNVHRMBAf8ECDAGAQH/AgEAMA4G
A1UdDwEB/wQEAwIBBjAdBgNVHQ4EFgQUl08vCVH5xDXQhHMBMaGDsO3GvMIwDQYJ
KoZIhvcNAQEFBQADggEBAKAuJUiwLp69665CBp0dag/wnA1qnVYzPUISc7FLaaZd
GjjRx3+e9I4pMWyNAA+50Y6wDKe3Qqva3xYwiZafysrj6kZaTwpH3FGuLhUlH6HH
1kiqxjUAVNPtxCaq+5bzLip8GurZPjW6LLSq+4sg1SGxWCnnYvURwlVsxpYIRh66
q6hJvlJXK8eXnzI7TV9s9KFV99iZ/zkfY0YpqMhLdyQiTCcVCIpefg9xnEi13fng
N8mjgjSWmdOeQ2wmPmWl2ueprNCeBMUxMWm4d/cIK00RiD4Z11mORMkE8qbb7Rs8
hIjsk+ffqMW/LsjgJkdsz9MhrNE7ffDyGMmZbqbBoqc=
-----END CERTIFICATE-----
'''

#------------------------------------------------------------------------------ 

class AppLogger():
    def __init__(self, write_method=sys.stdout.write):
        self._w = write_method
    def write(self, s):
        self._w(s)
    def info(self, s=''):
        self.write(s+'\n')
    def critical(self, s=''):
        self.write(s+'\n')
    def debug(self, s=''): 
        self.write(s+'\n')
    def exception(self, s=''):
        self.write(traceback.format_exc()+'\n')

def logger():
    global _AppLogger
    if _AppLogger is None:
        def _w(s):
            sys.stdout.write(s)
            sys.stdout.flush()
        _AppLogger = AppLogger(_w)
    return _AppLogger

def initLog(logLevel=0, logFilename='cspace.log', logWriteMode='wb', use_logging_module=True):
    global _AppLogger
    if _AppLogger is not None:
        logger().critical('CSpaceApplication.initLog WARNING AppLogger already initialized')
        return
    if use_logging_module:
        # if debug:
        #     logging.basicConfig(level=logLevel, stream=CSpace_stdout(), format='%(name)30s    %(levelname)5s   %(message)s', )
        # else:
        logging.basicConfig(level=logLevel, filename=logFilename, filemode=logWriteMode, format='%(name)30s    %(levelname)5s   %(message)s', )
        _AppLogger = logging.getLogger('dhn_cspace')
    else:
        # if debug is False:
        sys.stdout = open(logFilename, logWriteMode)
        sys.stderr = sys.stdout
        def _w(s):
            sys.stdout.write(s)
            sys.stdout.flush()
        _AppLogger = AppLogger(_w)

#------------------------------------------------------------------------------ 

def parseCommandLine():
    oparser = optparse.OptionParser()
    oparser.add_option("-r", "--register", dest="register", action="store_true", help="generate Private Key and register new key ID")
    oparser.add_option("-s", "--seednodes", dest="seednodes", action="append", help="seed nodes")
    oparser.add_option("-l", "--logfile", dest="logfile", help="where to put the output messages, default is cspace.log")
    oparser.add_option("-x", "--xmlrpc", dest="xmlport", type="int", help="specify port for XMLRPC control")
    oparser.add_option("-H", "--homedir", dest="homedir", help="home directory location")
    oparser.add_option("-t", "--tmpdir", dest="tmpdir", help="temporary files location")
    oparser.set_default('register', False)
    oparser.set_default('xmlport', 0)
    oparser.set_default('logfile', 'cspace.log')
    oparser.set_default('homedir', '')
    oparser.set_default('tmpdir', '')
    oparser.set_default("seednodes", ['208.78.96.185:10001'])  # ('210.210.1.102', 10001),
    (options, args) = oparser.parse_args()
    options.xmlport = int(options.xmlport)
    return options, args

#------------------------------------------------------------------------------ 

def test():
    (options, args) = parseCommandLine()
    initLog(logLevel=30, debug=options.debug)
    reactor = SelectReactor()
    a = Application(reactor, options, args)
    a.test_ssl2()
    # a.reactor.run()
    
def generateCA():
    import OpenSSL
    key = OpenSSL.crypto.PKey()
    key.generate_key(OpenSSL.crypto.TYPE_RSA, 2048)
    
    ca = OpenSSL.crypto.X509()
    ca.set_version(3)
    ca.set_serial_number(1)
    ca.get_subject().CN = "ca.cspace"
    ca.set_notBefore("20000101000000Z")
    ca.set_notAfter("22000101000000Z")
    ca.set_issuer(ca.get_subject())
    ca.set_pubkey(key)
    ca.add_extensions([
      OpenSSL.crypto.X509Extension("basicConstraints", True,
                                   "CA:TRUE, pathlen:0"),
      OpenSSL.crypto.X509Extension("keyUsage", True,
                                   "keyCertSign, cRLSign"),
      OpenSSL.crypto.X509Extension("subjectKeyIdentifier", False, "hash",
                                   subject=ca),
      ])
    ca.sign(key, "sha1")
    cert_str = OpenSSL.crypto.dump_certificate(OpenSSL.crypto.FILETYPE_PEM, ca)
    key_str = OpenSSL.crypto.dump_privatekey(OpenSSL.crypto.FILETYPE_PEM, key)
    fout = open('ca.pem', 'wb')
    fout.write(cert_str.decode('ascii'))
    fout.close()
    fout = open('ca.key', 'wb')
    fout.write(key_str.decode('ascii'))
    fout.close()
    fin = open('ca.pem', 'rb')
    ca_cert_ = OpenSSL.crypto.load_certificate(OpenSSL.crypto.FILETYPE_PEM, fin.read())
    fin.close()

def main():
    global reactor
    (options, args) = parseCommandLine()
    initLog(logFilename=options.logfile.strip('"'))
    reactor = SelectReactor()
    a = Application(reactor, options, args)
    if a.request_registration:
        try:
            a.register(a.username, a.password)
        except:
            logger().exception('ERROR during registration')
            return -1
        return 0
    try:
        a.init()
    except:
        logger().exception('ERROR during initialization')
        return -1
    try:
        a.run()
    except:
        logger().exception('ERROR:')
        return -1
    return 0

#------------------------------------------------------------------------------ 
        
if __name__ == "__main__":
    main()
    # test()
    # generateCA()
    
        
