from longtang.actors.inbound.inflate.strategies import *

available_formats = {'zip' : zippumping.ZipPumpingStrategy(),\
					 'rar': rarpumping.RarPumpingStrategy(),\
					 '7z': sevenzpumping.SevenzPumpingStrategy()} 