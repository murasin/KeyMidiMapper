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
        #print("time:{0:.4f}, val:time:{1:.4f}".format(sub ,127*pow(max(0 , 0.5-sub)/0.45, 3.0) + 1))
        #return 127*pow(max(0 , 0.5-sub)/0.45, 3.0) + 1
        #print("time:{0:.4f}, val:time:{1:.4f}".format(sub , 1.0 + 0.25/max(0.0001,(sub-0.05))))
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
        # self.mapdata.addMap('N', 1, 11, shift=True, ctrl=False, alt=False, method='inc', value=1)
        
        self.myGui = kmGui.mainGui()
        #rtmidiのセットアップ
        self.midiout = rtmidi.MidiOut()
        self.available_ports = self.midiout.get_ports()
        
        self.myGui.setup(self.available_ports, self.midiout)
        if self.available_ports:
            self.midiout.open_port(1)
        else:
            self.midiout.open_virtual_port("My virtual output")

        # self.midiout.get_ports
        # self.midiout.is_port_open
        # self.midiout.close_port()

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
            # print("keyevent:{0}:{1}".format(args.key_code,args.event_type))
            #print("open? : {0}".format(self.midiout.is_port_open()))
            map_event = self.mapdata.checkHandleEvent(args)
            #print(map_event)
            if(map_event != None):
                self.midiout.send_message(map_event)
            # if (args.current_key == 'N' 
            # and args.event_type == 'key down' 
            # and 'Lshift' in args.pressed_key):
            #     self.slVal -= int(self.calc_interval())
            #     self.slVal = max(0, self.slVal)
            #     # print("val:{0}".format(self.slVal))
            #     self.midiout.send_message([0xB0, 10, self.slVal])
            # elif (args.current_key == 'M' 
            # and args.event_type == 'key down' 
            # and 'Lshift' in args.pressed_key):
            #     self.slVal += int(self.calc_interval())
            #     self.slVal = min(127, self.slVal)
            #     # print("val:{0}".format(self.slVal))
            #     self.midiout.send_message([0xB0, 10, self.slVal])

        #マウスクリックの座標によるイベント
        # if isinstance(args, MouseEvent):
        #     if args.mouse_x < 300 and args.mouse_y < 400:
        #         print(args.mouse_x, args.mouse_y) 


if __name__ == "__main__":
    mapper = KeyMapper()
    hk = Hook()  # hookインスタンス作成
    hk.handler = mapper.handle_events  # コールバック関数をハンドラに登録

    thread_1 = threading.Thread(target=hk.hook)
    thread_1.setDaemon(True)
    thread_1.start()
    mapper.guiLoop()
    



