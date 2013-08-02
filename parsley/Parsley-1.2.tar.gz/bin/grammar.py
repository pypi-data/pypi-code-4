from ometa.runtime import OMetaBase as GrammarBase
def createParserClass(GrammarBase, ruleGlobals):
    if ruleGlobals is None:
        ruleGlobals = {}
    class Parser(GrammarBase):
        def rule_byte(self):
            _locals = {'self': self}
            self.locals['byte'] = _locals
            self._trace(' anything', (8, 17), self.input.position)
            _G_apply_1, lastError = self._apply(self.rule_anything, "anything", [])
            self.considerError(lastError, 'byte')
            _locals['b'] = _G_apply_1
            _G_python_2, lastError = eval('ord(b)', self.globals, _locals), None
            self.considerError(lastError, 'byte')
            return (_G_python_2, self.currentError)


        def rule_short(self):
            _locals = {'self': self}
            self.locals['short'] = _locals
            self._trace(' byte', (37, 42), self.input.position)
            _G_apply_3, lastError = self._apply(self.rule_byte, "byte", [])
            self.considerError(lastError, 'short')
            _locals['high'] = _G_apply_3
            self._trace(' byte', (47, 52), self.input.position)
            _G_apply_4, lastError = self._apply(self.rule_byte, "byte", [])
            self.considerError(lastError, 'short')
            _locals['low'] = _G_apply_4
            _G_python_5, lastError = eval('(high << 8) | low', self.globals, _locals), None
            self.considerError(lastError, 'short')
            return (_G_python_5, self.currentError)


        def rule_cstring(self):
            _locals = {'self': self}
            self.locals['cstring'] = _locals
            def _G_consumedby_6():
                def _G_many_7():
                    def _G_not_8():
                        self._trace("'\\x00'", (91, 97), self.input.position)
                        _G_exactly_9, lastError = self.exactly('\x00')
                        self.considerError(lastError, None)
                        return (_G_exactly_9, self.currentError)
                    _G_not_10, lastError = self._not(_G_not_8)
                    self.considerError(lastError, None)
                    self._trace(' anything', (97, 106), self.input.position)
                    _G_apply_11, lastError = self._apply(self.rule_anything, "anything", [])
                    self.considerError(lastError, None)
                    return (_G_apply_11, self.currentError)
                _G_many_12, lastError = self.many(_G_many_7)
                self.considerError(lastError, None)
                return (_G_many_12, self.currentError)
            _G_consumedby_13, lastError = self.consumedby(_G_consumedby_6)
            self.considerError(lastError, 'cstring')
            _locals['string'] = _G_consumedby_13
            self._trace(" '\\x00'", (116, 123), self.input.position)
            _G_exactly_14, lastError = self.exactly('\x00')
            self.considerError(lastError, 'cstring')
            _G_python_15, lastError = eval('string', self.globals, _locals), None
            self.considerError(lastError, 'cstring')
            return (_G_python_15, self.currentError)


        def rule_ipv4Address(self):
            _locals = {'self': self}
            self.locals['ipv4Address'] = _locals
            def _G_consumedby_16():
                def _G_repeat_17():
                    self._trace('anything', (150, 158), self.input.position)
                    _G_apply_18, lastError = self._apply(self.rule_anything, "anything", [])
                    self.considerError(lastError, None)
                    return (_G_apply_18, self.currentError)
                _G_repeat_19, lastError = self.repeat(4, 4, _G_repeat_17)
                self.considerError(lastError, None)
                return (_G_repeat_19, self.currentError)
            _G_consumedby_20, lastError = self.consumedby(_G_consumedby_16)
            self.considerError(lastError, 'ipv4Address')
            _locals['packed'] = _G_consumedby_20
            _G_python_21, lastError = eval('socket.inet_ntop(socket.AF_INET, packed)', self.globals, _locals), None
            self.considerError(lastError, 'ipv4Address')
            return (_G_python_21, self.currentError)


        def rule_ipv6Address(self):
            _locals = {'self': self}
            self.locals['ipv6Address'] = _locals
            def _G_consumedby_22():
                def _G_repeat_23():
                    self._trace('anything', (229, 237), self.input.position)
                    _G_apply_24, lastError = self._apply(self.rule_anything, "anything", [])
                    self.considerError(lastError, None)
                    return (_G_apply_24, self.currentError)
                _G_repeat_25, lastError = self.repeat(16, 16, _G_repeat_23)
                self.considerError(lastError, None)
                return (_G_repeat_25, self.currentError)
            _G_consumedby_26, lastError = self.consumedby(_G_consumedby_22)
            self.considerError(lastError, 'ipv6Address')
            _locals['packed'] = _G_consumedby_26
            _G_python_27, lastError = eval('socket.inet_ntop(socket.AF_INET6, packed)', self.globals, _locals), None
            self.considerError(lastError, 'ipv6Address')
            return (_G_python_27, self.currentError)


        def rule_SOCKS4Command(self):
            _locals = {'self': self}
            self.locals['SOCKS4Command'] = _locals
            def _G_or_28():
                self._trace(" '\\x01'", (313, 320), self.input.position)
                _G_exactly_29, lastError = self.exactly('\x01')
                self.considerError(lastError, None)
                _G_python_30, lastError = 'tcp-connect', None
                self.considerError(lastError, None)
                return (_G_python_30, self.currentError)
            def _G_or_31():
                self._trace(" '\\x02'", (355, 362), self.input.position)
                _G_exactly_32, lastError = self.exactly('\x02')
                self.considerError(lastError, None)
                _G_python_33, lastError = 'tcp-bind', None
                self.considerError(lastError, None)
                return (_G_python_33, self.currentError)
            _G_or_34, lastError = self._or([_G_or_28, _G_or_31])
            self.considerError(lastError, 'SOCKS4Command')
            return (_G_or_34, self.currentError)


        def rule_SOCKS4HostUser(self):
            _locals = {'self': self}
            self.locals['SOCKS4HostUser'] = _locals
            self._trace(' ipv4Address', (411, 423), self.input.position)
            _G_apply_35, lastError = self._apply(self.rule_ipv4Address, "ipv4Address", [])
            self.considerError(lastError, 'SOCKS4HostUser')
            _locals['host'] = _G_apply_35
            self._trace(' cstring', (428, 436), self.input.position)
            _G_apply_36, lastError = self._apply(self.rule_cstring, "cstring", [])
            self.considerError(lastError, 'SOCKS4HostUser')
            _locals['user'] = _G_apply_36
            _G_python_37, lastError = eval('(host, user)', self.globals, _locals), None
            self.considerError(lastError, 'SOCKS4HostUser')
            return (_G_python_37, self.currentError)


        def rule_SOCKS4aHostUser(self):
            _locals = {'self': self}
            self.locals['SOCKS4aHostUser'] = _locals
            def _G_or_38():
                def _G_repeat_39():
                    self._trace(" '\\x00'", (477, 484), self.input.position)
                    _G_exactly_40, lastError = self.exactly('\x00')
                    self.considerError(lastError, None)
                    return (_G_exactly_40, self.currentError)
                _G_repeat_41, lastError = self.repeat(3, 3, _G_repeat_39)
                self.considerError(lastError, None)
                def _G_not_42():
                    self._trace("'\\x00'", (489, 495), self.input.position)
                    _G_exactly_43, lastError = self.exactly('\x00')
                    self.considerError(lastError, None)
                    return (_G_exactly_43, self.currentError)
                _G_not_44, lastError = self._not(_G_not_42)
                self.considerError(lastError, None)
                self._trace(' anything', (495, 504), self.input.position)
                _G_apply_45, lastError = self._apply(self.rule_anything, "anything", [])
                self.considerError(lastError, None)
                self._trace(' cstring', (504, 512), self.input.position)
                _G_apply_46, lastError = self._apply(self.rule_cstring, "cstring", [])
                self.considerError(lastError, None)
                _locals['user'] = _G_apply_46
                self._trace(' cstring', (517, 525), self.input.position)
                _G_apply_47, lastError = self._apply(self.rule_cstring, "cstring", [])
                self.considerError(lastError, None)
                _locals['host'] = _G_apply_47
                _G_python_48, lastError = eval('(host, user)', self.globals, _locals), None
                self.considerError(lastError, None)
                return (_G_python_48, self.currentError)
            def _G_or_49():
                self._trace(' SOCKS4HostUser', (566, 581), self.input.position)
                _G_apply_50, lastError = self._apply(self.rule_SOCKS4HostUser, "SOCKS4HostUser", [])
                self.considerError(lastError, None)
                return (_G_apply_50, self.currentError)
            _G_or_51, lastError = self._or([_G_or_38, _G_or_49])
            self.considerError(lastError, 'SOCKS4aHostUser')
            return (_G_or_51, self.currentError)


        def rule_SOCKS4Request(self):
            _locals = {'self': self}
            self.locals['SOCKS4Request'] = _locals
            self._trace(" '\\x04'", (618, 625), self.input.position)
            _G_exactly_52, lastError = self.exactly('\x04')
            self.considerError(lastError, 'SOCKS4Request')
            self._trace(' SOCKS4Command', (625, 639), self.input.position)
            _G_apply_53, lastError = self._apply(self.rule_SOCKS4Command, "SOCKS4Command", [])
            self.considerError(lastError, 'SOCKS4Request')
            _locals['command'] = _G_apply_53
            self._trace(' short', (647, 653), self.input.position)
            _G_apply_54, lastError = self._apply(self.rule_short, "short", [])
            self.considerError(lastError, 'SOCKS4Request')
            _locals['port'] = _G_apply_54
            self._trace(' SOCKS4aHostUser', (658, 674), self.input.position)
            _G_apply_55, lastError = self._apply(self.rule_SOCKS4aHostUser, "SOCKS4aHostUser", [])
            self.considerError(lastError, 'SOCKS4Request')
            _locals['hostuser'] = _G_apply_55
            _G_python_56, lastError = eval('(command, port) + hostuser', self.globals, _locals), None
            self.considerError(lastError, 'SOCKS4Request')
            return (_G_python_56, self.currentError)


        def rule_SOCKS4Response(self):
            _locals = {'self': self}
            self.locals['SOCKS4Response'] = _locals
            self._trace(" '\\x00'", (730, 737), self.input.position)
            _G_exactly_57, lastError = self.exactly('\x00')
            self.considerError(lastError, 'SOCKS4Response')
            self._trace(' byte', (737, 742), self.input.position)
            _G_apply_58, lastError = self._apply(self.rule_byte, "byte", [])
            self.considerError(lastError, 'SOCKS4Response')
            _locals['status'] = _G_apply_58
            def _G_repeat_59():
                self._trace(' anything', (749, 758), self.input.position)
                _G_apply_60, lastError = self._apply(self.rule_anything, "anything", [])
                self.considerError(lastError, None)
                return (_G_apply_60, self.currentError)
            _G_repeat_61, lastError = self.repeat(6, 6, _G_repeat_59)
            self.considerError(lastError, None)
            _G_python_62, lastError = eval('status', self.globals, _locals), None
            self.considerError(lastError, 'SOCKS4Response')
            return (_G_python_62, self.currentError)


        def rule_SOCKS4ServerState_initial(self):
            _locals = {'self': self}
            self.locals['SOCKS4ServerState_initial'] = _locals
            self._trace(' SOCKS4Request', (801, 815), self.input.position)
            _G_apply_63, lastError = self._apply(self.rule_SOCKS4Request, "SOCKS4Request", [])
            self.considerError(lastError, 'SOCKS4ServerState_initial')
            _locals['request'] = _G_apply_63
            _G_python_64, lastError = eval('state.clientRequest(*request)', self.globals, _locals), None
            self.considerError(lastError, 'SOCKS4ServerState_initial')
            return (_G_python_64, self.currentError)


        def rule_SOCKS4ClientState_initial(self):
            _locals = {'self': self}
            self.locals['SOCKS4ClientState_initial'] = _locals
            self._trace(' SOCKS4Response', (884, 899), self.input.position)
            _G_apply_65, lastError = self._apply(self.rule_SOCKS4Response, "SOCKS4Response", [])
            self.considerError(lastError, 'SOCKS4ClientState_initial')
            _locals['status'] = _G_apply_65
            _G_python_66, lastError = eval('state.serverResponse(status)', self.globals, _locals), None
            self.considerError(lastError, 'SOCKS4ClientState_initial')
            return (_G_python_66, self.currentError)


        def rule_SOCKS5Command(self):
            _locals = {'self': self}
            self.locals['SOCKS5Command'] = _locals
            def _G_or_67():
                self._trace('SOCKS4Command', (958, 971), self.input.position)
                _G_apply_68, lastError = self._apply(self.rule_SOCKS4Command, "SOCKS4Command", [])
                self.considerError(lastError, None)
                return (_G_apply_68, self.currentError)
            def _G_or_69():
                self._trace(" '\\x03'", (973, 980), self.input.position)
                _G_exactly_70, lastError = self.exactly('\x03')
                self.considerError(lastError, None)
                _G_python_71, lastError = 'udp-associate', None
                self.considerError(lastError, None)
                return (_G_python_71, self.currentError)
            _G_or_72, lastError = self._or([_G_or_67, _G_or_69])
            self.considerError(lastError, 'SOCKS5Command')
            return (_G_or_72, self.currentError)


        def rule_SOCKS5Hostname(self):
            _locals = {'self': self}
            self.locals['SOCKS5Hostname'] = _locals
            self._trace(' byte', (1017, 1022), self.input.position)
            _G_apply_73, lastError = self._apply(self.rule_byte, "byte", [])
            self.considerError(lastError, 'SOCKS5Hostname')
            _locals['length'] = _G_apply_73
            def _G_consumedby_74():
                def _G_repeat_75():
                    self._trace('anything', (1031, 1039), self.input.position)
                    _G_apply_76, lastError = self._apply(self.rule_anything, "anything", [])
                    self.considerError(lastError, None)
                    return (_G_apply_76, self.currentError)
                _G_repeat_77, lastError = self.repeat(_locals["length"], _locals["length"], _G_repeat_75)
                self.considerError(lastError, None)
                return (_G_repeat_77, self.currentError)
            _G_consumedby_78, lastError = self.consumedby(_G_consumedby_74)
            self.considerError(lastError, 'SOCKS5Hostname')
            _locals['host'] = _G_consumedby_78
            _G_python_79, lastError = eval('host', self.globals, _locals), None
            self.considerError(lastError, 'SOCKS5Hostname')
            return (_G_python_79, self.currentError)


        def rule_SOCKS5Address(self):
            _locals = {'self': self}
            self.locals['SOCKS5Address'] = _locals
            def _G_or_80():
                self._trace(" '\\x01'", (1079, 1086), self.input.position)
                _G_exactly_81, lastError = self.exactly('\x01')
                self.considerError(lastError, None)
                self._trace(' ipv4Address', (1086, 1098), self.input.position)
                _G_apply_82, lastError = self._apply(self.rule_ipv4Address, "ipv4Address", [])
                self.considerError(lastError, None)
                _locals['address'] = _G_apply_82
                _G_python_83, lastError = eval('address', self.globals, _locals), None
                self.considerError(lastError, None)
                return (_G_python_83, self.currentError)
            def _G_or_84():
                self._trace(" '\\x03'", (1135, 1142), self.input.position)
                _G_exactly_85, lastError = self.exactly('\x03')
                self.considerError(lastError, None)
                self._trace(' SOCKS5Hostname', (1142, 1157), self.input.position)
                _G_apply_86, lastError = self._apply(self.rule_SOCKS5Hostname, "SOCKS5Hostname", [])
                self.considerError(lastError, None)
                _locals['host'] = _G_apply_86
                _G_python_87, lastError = eval('host', self.globals, _locals), None
                self.considerError(lastError, None)
                return (_G_python_87, self.currentError)
            def _G_or_88():
                self._trace(" '\\x04'", (1188, 1195), self.input.position)
                _G_exactly_89, lastError = self.exactly('\x04')
                self.considerError(lastError, None)
                self._trace(' ipv6Address', (1195, 1207), self.input.position)
                _G_apply_90, lastError = self._apply(self.rule_ipv6Address, "ipv6Address", [])
                self.considerError(lastError, None)
                _locals['address'] = _G_apply_90
                _G_python_91, lastError = eval('address', self.globals, _locals), None
                self.considerError(lastError, None)
                return (_G_python_91, self.currentError)
            _G_or_92, lastError = self._or([_G_or_80, _G_or_84, _G_or_88])
            self.considerError(lastError, 'SOCKS5Address')
            return (_G_or_92, self.currentError)


        def rule_SOCKS5ServerAuthSelection(self):
            _locals = {'self': self}
            self.locals['SOCKS5ServerAuthSelection'] = _locals
            self._trace(" '\\x05'", (1273, 1280), self.input.position)
            _G_exactly_93, lastError = self.exactly('\x05')
            self.considerError(lastError, 'SOCKS5ServerAuthSelection')
            self._trace(' anything', (1280, 1289), self.input.position)
            _G_apply_94, lastError = self._apply(self.rule_anything, "anything", [])
            self.considerError(lastError, 'SOCKS5ServerAuthSelection')
            return (_G_apply_94, self.currentError)


        def rule_SOCKS5ServerLoginResponse(self):
            _locals = {'self': self}
            self.locals['SOCKS5ServerLoginResponse'] = _locals
            self._trace(' anything', (1317, 1326), self.input.position)
            _G_apply_95, lastError = self._apply(self.rule_anything, "anything", [])
            self.considerError(lastError, 'SOCKS5ServerLoginResponse')
            self._trace(' anything', (1326, 1335), self.input.position)
            _G_apply_96, lastError = self._apply(self.rule_anything, "anything", [])
            self.considerError(lastError, 'SOCKS5ServerLoginResponse')
            _locals['status'] = _G_apply_96
            _G_python_97, lastError = eval("status == '\\x00'", self.globals, _locals), None
            self.considerError(lastError, 'SOCKS5ServerLoginResponse')
            return (_G_python_97, self.currentError)


        def rule_SOCKS5ServerResponse(self):
            _locals = {'self': self}
            self.locals['SOCKS5ServerResponse'] = _locals
            self._trace(" '\\x05'", (1385, 1392), self.input.position)
            _G_exactly_98, lastError = self.exactly('\x05')
            self.considerError(lastError, 'SOCKS5ServerResponse')
            self._trace(' byte', (1392, 1397), self.input.position)
            _G_apply_99, lastError = self._apply(self.rule_byte, "byte", [])
            self.considerError(lastError, 'SOCKS5ServerResponse')
            _locals['status'] = _G_apply_99
            self._trace(" '\\x00'", (1404, 1411), self.input.position)
            _G_exactly_100, lastError = self.exactly('\x00')
            self.considerError(lastError, 'SOCKS5ServerResponse')
            self._trace(' SOCKS5Address', (1411, 1425), self.input.position)
            _G_apply_101, lastError = self._apply(self.rule_SOCKS5Address, "SOCKS5Address", [])
            self.considerError(lastError, 'SOCKS5ServerResponse')
            _locals['address'] = _G_apply_101
            self._trace(' short', (1433, 1439), self.input.position)
            _G_apply_102, lastError = self._apply(self.rule_short, "short", [])
            self.considerError(lastError, 'SOCKS5ServerResponse')
            _locals['port'] = _G_apply_102
            _G_python_103, lastError = eval('(status, address, port)', self.globals, _locals), None
            self.considerError(lastError, 'SOCKS5ServerResponse')
            return (_G_python_103, self.currentError)


        def rule_SOCKS5ClientGreeting(self):
            _locals = {'self': self}
            self.locals['SOCKS5ClientGreeting'] = _locals
            self._trace(" '\\x05'", (1495, 1502), self.input.position)
            _G_exactly_104, lastError = self.exactly('\x05')
            self.considerError(lastError, 'SOCKS5ClientGreeting')
            self._trace(' byte', (1502, 1507), self.input.position)
            _G_apply_105, lastError = self._apply(self.rule_byte, "byte", [])
            self.considerError(lastError, 'SOCKS5ClientGreeting')
            _locals['authMethodCount'] = _G_apply_105
            def _G_repeat_106():
                self._trace(' byte', (1523, 1528), self.input.position)
                _G_apply_107, lastError = self._apply(self.rule_byte, "byte", [])
                self.considerError(lastError, None)
                return (_G_apply_107, self.currentError)
            _G_repeat_108, lastError = self.repeat(_locals["authMethodCount"], _locals["authMethodCount"], _G_repeat_106)
            self.considerError(lastError, None)
            _locals['authMethods'] = _G_repeat_108
            _G_python_109, lastError = eval('authMethods or []', self.globals, _locals), None
            self.considerError(lastError, 'SOCKS5ClientGreeting')
            return (_G_python_109, self.currentError)


        def rule_SOCKS5ClientRequest(self):
            _locals = {'self': self}
            self.locals['SOCKS5ClientRequest'] = _locals
            self._trace(" '\\x05'", (1600, 1607), self.input.position)
            _G_exactly_110, lastError = self.exactly('\x05')
            self.considerError(lastError, 'SOCKS5ClientRequest')
            self._trace(' SOCKS5Command', (1607, 1621), self.input.position)
            _G_apply_111, lastError = self._apply(self.rule_SOCKS5Command, "SOCKS5Command", [])
            self.considerError(lastError, 'SOCKS5ClientRequest')
            _locals['command'] = _G_apply_111
            self._trace(" '\\x00'", (1629, 1636), self.input.position)
            _G_exactly_112, lastError = self.exactly('\x00')
            self.considerError(lastError, 'SOCKS5ClientRequest')
            self._trace(' SOCKS5Address', (1636, 1650), self.input.position)
            _G_apply_113, lastError = self._apply(self.rule_SOCKS5Address, "SOCKS5Address", [])
            self.considerError(lastError, 'SOCKS5ClientRequest')
            _locals['address'] = _G_apply_113
            self._trace(' short', (1658, 1664), self.input.position)
            _G_apply_114, lastError = self._apply(self.rule_short, "short", [])
            self.considerError(lastError, 'SOCKS5ClientRequest')
            _locals['port'] = _G_apply_114
            _G_python_115, lastError = eval('(command, address, port)', self.globals, _locals), None
            self.considerError(lastError, 'SOCKS5ClientRequest')
            return (_G_python_115, self.currentError)


        def rule_SOCKS5ServerState_initial(self):
            _locals = {'self': self}
            self.locals['SOCKS5ServerState_initial'] = _locals
            self._trace(' SOCKS5ClientGreeting', (1727, 1748), self.input.position)
            _G_apply_116, lastError = self._apply(self.rule_SOCKS5ClientGreeting, "SOCKS5ClientGreeting", [])
            self.considerError(lastError, 'SOCKS5ServerState_initial')
            _locals['authMethods'] = _G_apply_116
            _G_python_117, lastError = eval('state.authRequested(authMethods)', self.globals, _locals), None
            self.considerError(lastError, 'SOCKS5ServerState_initial')
            return (_G_python_117, self.currentError)


        def rule_SOCKS5ServerState_readRequest(self):
            _locals = {'self': self}
            self.locals['SOCKS5ServerState_readRequest'] = _locals
            self._trace(' SOCKS5ClientRequest', (1828, 1848), self.input.position)
            _G_apply_118, lastError = self._apply(self.rule_SOCKS5ClientRequest, "SOCKS5ClientRequest", [])
            self.considerError(lastError, 'SOCKS5ServerState_readRequest')
            _locals['request'] = _G_apply_118
            _G_python_119, lastError = eval('state.clientRequest(*request)', self.globals, _locals), None
            self.considerError(lastError, 'SOCKS5ServerState_readRequest')
            return (_G_python_119, self.currentError)


        def rule_SOCKS5ClientState_initial(self):
            _locals = {'self': self}
            self.locals['SOCKS5ClientState_initial'] = _locals
            self._trace(' SOCKS5ServerAuthSelection', (1918, 1944), self.input.position)
            _G_apply_120, lastError = self._apply(self.rule_SOCKS5ServerAuthSelection, "SOCKS5ServerAuthSelection", [])
            self.considerError(lastError, 'SOCKS5ClientState_initial')
            _locals['selection'] = _G_apply_120
            _G_python_121, lastError = eval('state.authSelected(selection)', self.globals, _locals), None
            self.considerError(lastError, 'SOCKS5ClientState_initial')
            return (_G_python_121, self.currentError)


        def rule_SOCKS5ClientState_readLoginResponse(self):
            _locals = {'self': self}
            self.locals['SOCKS5ClientState_readLoginResponse'] = _locals
            self._trace(' SOCKS5ServerLoginResponse', (2025, 2051), self.input.position)
            _G_apply_122, lastError = self._apply(self.rule_SOCKS5ServerLoginResponse, "SOCKS5ServerLoginResponse", [])
            self.considerError(lastError, 'SOCKS5ClientState_readLoginResponse')
            _locals['response'] = _G_apply_122
            _G_python_123, lastError = eval('state.loginResponse(response)', self.globals, _locals), None
            self.considerError(lastError, 'SOCKS5ClientState_readLoginResponse')
            return (_G_python_123, self.currentError)


        def rule_SOCKS5ClientState_readResponse(self):
            _locals = {'self': self}
            self.locals['SOCKS5ClientState_readResponse'] = _locals
            self._trace(' SOCKS5ServerResponse', (2126, 2147), self.input.position)
            _G_apply_124, lastError = self._apply(self.rule_SOCKS5ServerResponse, "SOCKS5ServerResponse", [])
            self.considerError(lastError, 'SOCKS5ClientState_readResponse')
            _locals['response'] = _G_apply_124
            _G_python_125, lastError = eval('state.serverResponse(*response)', self.globals, _locals), None
            self.considerError(lastError, 'SOCKS5ClientState_readResponse')
            return (_G_python_125, self.currentError)


        def rule_SOCKSState_readData(self):
            _locals = {'self': self}
            self.locals['SOCKSState_readData'] = _locals
            self._trace(' anything', (2215, 2224), self.input.position)
            _G_apply_126, lastError = self._apply(self.rule_anything, "anything", [])
            self.considerError(lastError, 'SOCKSState_readData')
            _locals['data'] = _G_apply_126
            _G_python_127, lastError = eval('state.dataReceived(data)', self.globals, _locals), None
            self.considerError(lastError, 'SOCKSState_readData')
            return (_G_python_127, self.currentError)


    if Parser.globals is not None:
        Parser.globals = Parser.globals.copy()
        Parser.globals.update(ruleGlobals)
    else:
        Parser.globals = ruleGlobals
    return Parser