#!usr\bin\env python
__name__ = "CyfNet Network Library"
__version__ = "0.0.9"

class ProgressBar():
    def __init__(self, **kwargs):
        import progressbar
        self.progressbarvar = progressbar(**kwargs)
    def Update(self, message=None):
        self.progressbarvar.print_progress_bar(message)
    def Increment(self, incremento):
        self.progressbarvar.increment(incremento)
    def Reset(self):
        self.progressbarvar.progress = 0
    def Percentage(self):
        return self.progressbarvar.progress
    def PrintBar(self):
        return self.progressbarvar.return_barra()

class BitCoin():
    def __init__(self):
      import bitcoin as btc
      self.bitcoin = btc.BitCoin()
    def GetAddress(self, seed):
      return self.bitcoin.GetAddress(seed)
    def GetPrivateKey(self, seed):
      return self.bitcoin.GetPrivKey(seed)
    def CheckBalance(self, address):
      return self.bitcoin.CheckBalance(address)
    def ConvertAmount(self, decimal):
      return self.bitcoin.TransformBTC(decimal)
    def AddressByPrivateKey(self, privatekey):
      return self.bitcoin.AddressByPrivateKey(privatekey)
    def RandomSeed(self):
      return self.bitcoin.RandomSeed()

class ConfigManager():
    def __init__(self, archivo, encryption=True):
        import cfg
        self.cfgm = cfg.config(archivo, encryption)
    def Load(self):
        return self.cfgm.load()
    def Save(self):
        return self.cfgm.save()
    def GetValue(self, variable):
        return self.cfgm.get_value(variable)
    def SetValue(self, variable, valor):
        return self.cfgm.set_value(variable, valor)
    def Create(self):
        self.cfgm.create()
    def Reload(self):
        return self.cfgm.load()

class RSA():
    def __init__(self):
        import rsa_def
        self.rsa_def = rsa_def
    def Generar_claves(self, bits=512): #Devuelve (clave_publica, clave_privada)
        return self.rsa_def.generar_claves(bits)
    def Encriptar(self, mensaje, clave_publica):
        return self.rsa_def.encriptar(mensaje, clave_publica)
    def Desencriptar(self, mensaje_encriptado, clave_privada, clave_publica):
        return self.rsa_def.desencriptar(mensaje_encriptado, clave_privada, clave_publica)
    def Firmar(self, mensaje, clave_privada, clave_publica):
        return self.rsa_def.sign(mensaje, clave_privada, clave_publica)
    def Comprobar_firma(self, mensaje, firma, clave_publica):
        return self.rsa_def.checksign(mensaje, firma, clave_publica)

class Colors():
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    ORANGE = '\033[93m'
    RED = '\033[91m'
    OK = 0
    INFO = 1
    WARNING = 2
    FAIL = 3
    ERROR = 4
    def __init__(self):
        import colors
        self.colors = colors
    def Reset(self):
        return self.colors.reset_color()
    def StatusText(self, style, text):
        return self.colors.status(style, text)
