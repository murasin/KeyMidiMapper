import time
import csv
from distutils.util import strtobool #文字列→bool型変換で使用
import threading
#外部ライブラリ
import rtmidi
from pyhooked import Hook, KeyboardEvent, MouseEvent
#自作ライブラリ
import KeyMidiGui as kmGui


class MapData():
    def __init__(self):
        self.mapData = []
        self.valData = {}
        self.ptime = time.time()

    def addMap(self, key, channel, CCNumber, shift=False, ctrl=False, alt=False ,method='set', value=63):
        self.mapData.append({
            'key':key,
            'channel':channel,
            'CCNumber':CCNumber,
            'shift':shift,
            'ctrl':ctrl,
            'alt':alt,
            'method':method,
            'value': value
        })
        cc_key = self.calcCCkey(channel, CCNumber)
        if cc_key not in self.valData:
            self.valData.update({cc_key:value})

    def readMapData(self, filePass):
        return None
    
    def calc_interval(self):
        ntime = time.time()
        sub =  ntime - self.ptime
        self.ptime = ntime
        return 1.0 + 0.25/max(0.0001,(sub-0.020))

    def calcCCkey(self, channel, CCNumber):
        return (channel << 8) + CCNumber

    def checkHandleEvent(self, args):
        if args.event_type != 'key down':
            return None
        
        for data in self.mapData:
            if(data['key'] != args.current_key):
                continue
            if(data['shift'] != ('Lshift' in args.pressed_key or 'Rshift' in args.pressed_key)):
                continue
            if(data['ctrl'] != ('Lctrl' in args.pressed_key or 'Rctrl' in args.pressed_key)):
                continue
            if(data['alt'] != ('Lalt' in args.pressed_key or 'Ralt' in args.pressed_key)):
                continue
            cc_key = self.calcCCkey(data['channel'], data['CCNumber'])
            ch = 0xB0 + data['channel']
            if(data['method'] == 'inc'):
                self.valData[cc_key] += int(data['value']*self.calc_interval())
                self.valData[cc_key] = min(127,self.valData[cc_key])
            elif(data['method'] == 'dec'):
                self.valData[cc_key] -= int(data['value']*self.calc_interval())
                self.valData[cc_key] = max(0, self.valData[cc_key])
            elif(data['method'] == 'set'):
                self.valData[cc_key] = data['value']

            return [ch, data['CCNumber'], self.valData[cc_key]]
        
        return None
 
class KeyMapper():
    def __init__(self):
        self.mapdata = MapData()

        self.myGui = kmGui.mainGui()
        #rtmidiのセットアップ
        self.midiout = rtmidi.MidiOut()
        self.available_ports = self.midiout.get_ports()
        
        self.myGui.setup(self.available_ports, self.midiout)
        if self.available_ports:
            self.midiout.open_port(1)
        else:
            self.midiout.open_virtual_port("My virtual output")

        #設定ファイルの読み込み
        filePass = self.myGui.getFilePass()
        if(filePass == ""):
            return
        with open(filePass) as f:
            reader = csv.reader(f)
            rowList = [row for row in reader]
        for l in rowList[1:]:
            self.mapdata.addMap(
                l[0],
                int(l[1]),
                int(l[2]),
                strtobool(l[3]),
                strtobool(l[4]),
                strtobool(l[5]),
                l[6],
                int(l[7])
                )

        #Guiループ
        #self.myGui.guiLoop()

    def __del__(self):
        del self.midiout

    def guiLoop(self):
        self.myGui.run()
        return

    def handle_events(self,args):
        
        if isinstance(args, KeyboardEvent):
            map_event = self.mapdata.checkHandleEvent(args)
            if(map_event != None):
                self.midiout.send_message(map_event)


if __name__ == "__main__":
    mapper = KeyMapper()
    hk = Hook()  # hookインスタンス作成
    hk.handler = mapper.handle_events  # コールバック関数をハンドラに登録

    thread_1 = threading.Thread(target=hk.hook)
    thread_1.setDaemon(True)
    thread_1.start()
    mapper.guiLoop()
    



