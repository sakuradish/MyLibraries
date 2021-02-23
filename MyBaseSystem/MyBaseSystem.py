#============================================================================================================================================================
import sys
sys.path.append('../MyLogger/')
from MyLogger import MyLogger
MyLogger = MyLogger.GetInstance()
#============================================================================================================================================================
# import os
# import shutil
#============================================================================================================================================================
@MyLogger.deco
def myopen(filepath, mode, encoding=''):
   if mode == 'w':
      return open(filepath, mode, encoding='utf-8')
   elif encoding == '':
      from chardet.universaldetector import UniversalDetector
      detector = UniversalDetector()
      with open(filepath, mode='rb') as f:
         for binary in f:
            detector.feed(binary)
            if detector.done:
                  break
      detector.close()
      encoding = detector.result['encoding']
   return open(filepath, mode, encoding=encoding)
#============================================================================================================================================================
if __name__ == '__main__':
   pass
#============================================================================================================================================================
