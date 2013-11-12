import progressbar as pb
import bitcoin as btc
import cfg
import rsa_def

class ProgressBar():
    def __init__(self, **kwargs):
        self.progressbarvar = pb.progressbar(**kwargs)
        return None
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
      self.bitcoin = btc.BitCoin()
      return None
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
        self.cfgm = cfg.config(archivo, encryption)
        return None
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
        return None
    def GenerateKeys(self, bits=512): #Devuelve (clave_publica, clave_privada)
        return rsa_def.generar_claves(bits)
    def Crypt(self, mensaje, clave_publica):
        return rsa_def.encriptar(mensaje, clave_publica)
    def Decrypt(self, mensaje_encriptado, clave_privada, clave_publica):
        return rsa_def.desencriptar(mensaje_encriptado, clave_privada, clave_publica)
    def Sign(self, mensaje, clave_privada, clave_publica):
        return rsa_def.sign(mensaje, clave_privada, clave_publica)
    def CheckSign(self, mensaje, firma, clave_publica):
        return rsa_def.checksign(mensaje, firma, clave_publica)

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
__name__ = "CyfNet Network Library"
__version__ = "0.1"
