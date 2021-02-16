#============================================================================================================================================================
import sys
sys.path.append('../MyLogger/')
sys.path.append('../MyDataBase/')
from MyLogger import MyLogger
MyLogger = MyLogger.GetInstance()
from MyDataBase import MyDataBase
db = MyDataBase.GetInstance('plantuml.xlsx')
db.DFAppendColumn(['compoundname', 'definition', 'argsstring', 'name', 'bodyfile', 'bodystart', 'bodyend'])
#============================================================================================================================================================
import re
import os
import glob
from bs4 import BeautifulSoup
#============================================================================================================================================================
@MyLogger.deco
def __myopen(filepath, mode, encoding=''):
   if encoding == '':
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
@MyLogger.deco
def main(doxygenpath):
   files = [file for file in glob.glob(doxygenpath+'/**/*', recursive=True) if file.find('class_') != -1]
   # files = [file for file in glob.glob(doxygenpath+'/**/*', recursive=True) if file.find('.xml') != -1]
   MyLogger.SetFraction(len(files))
   for file in files:
      MyLogger.SetNumerator(files.index(file))
      analyzeXML(file)
#============================================================================================================================================================
@MyLogger.deco
def analyzeXML(xmlpath):
   xml = ''.join(__myopen(xmlpath, 'r').readlines())
   soup = BeautifulSoup(xml, 'lxml')
   componddef = soup.find('compounddef')
   if not componddef:
      MyLogger.warning('not found compoundname in ', xmlpath)
      return
   compoundname = componddef.find('compoundname').text
   functions = componddef.find_all('memberdef', {'kind':'function'})
   for function in functions:
      definition = function.find('definition').text
      argsstring = function.find('argsstring').text
      name = function.find('name').text
      location = function.find('location')
      if not location.has_attr('bodyfile'):
         MyLogger.warning('not found bodyfile of ', definition)
         continue
      bodyfile = location['bodyfile']
      bodystart = location['bodystart']
      bodyend = location['bodyend']
      MyLogger.critical(bodyfile)
      MyLogger.critical(bodystart)
      MyLogger.critical(bodyend)
      db.DFAppendRow([compoundname, definition, argsstring, name, bodyfile, bodystart, bodyend])
   db.DFWrite()
#============================================================================================================================================================
@MyLogger.deco
def DraftUML():
   inputbase='./input/'
   outputbase='./output/'
   for index,values in db.GetDict().items():
      compoundname = values['compoundname']
      definition = values['definition']
      argsstring = values['argsstring']
      MyLogger.critical(argsstring)
      argsstring = argsstring.replace(" ","_").replace(":","").replace("&","").replace("<","").replace(">","")
      name = values['name']
      bodyfile = values['bodyfile']
      bodystart = int(values['bodystart'])-1
      bodyend = int(values['bodyend'])
      inputfile = inputbase+bodyfile
      outputfile = outputbase+bodyfile+'/'+name+"_"+argsstring+'.pu'
      if not os.path.exists(os.path.dirname(outputfile)):
         os.makedirs(os.path.dirname(outputfile))
      functionbody = __myopen(inputfile, 'r').readlines()[bodystart:bodyend]
      functionbody = CustomizeFunctionBody(functionbody, compoundname)
      with __myopen(outputfile, 'w', encoding='utf-8') as f:
         f.write("' #######################################\n")
         f.write("@startuml\n")
         f.write("== " + compoundname + ":" + name + " ==\n")
         f.write("activate " + compoundname + "\n")
         f.write("' #######################################\n")
         # f.write("note right " + compoundname + "\n")
         f.write(''.join(functionbody))
         # f.write("end note\n")
         f.write("' #######################################\n")
         f.write("deactivate " + compoundname + "\n")
         f.write("@enduml\n")
         f.write("' #######################################\n")
#============================================================================================================================================================
@MyLogger.deco
def CustomizeFunctionBody(functionbody, compoundname):
   def RemoveEmpty(functionbody, compoundname):
      ret = []
      for line in functionbody:
         line = line.strip(' ')
         line = line.strip('\t')
         ret.append(line)
      return ret
   def Format(functionbody, compoundname):
      ret = []
      buf = ''
      def AppendMatch(ret, buf, result):
         if buf.find('}') != -1:
            ret.append('}\n')
         ret.append(result.group(1).replace("\n", "") + "\n")
         # buf = buf.replace(result.group(1), "")
         buf = ''
         return ret,buf
      for line in functionbody:
         for char in line:
            buf += char
            # 関数宣言マッチャー # ifとかforもマッチするはず
            result = re.fullmatch("(.*\(.*\).*\{).*", buf, re.S)
            if result:
               ret,buf = AppendMatch(ret,buf,result)
            # 一行コメントマッチャー
            result = re.fullmatch(".*(//.*)\n.*", buf, re.S)
            if result:
               ret,buf = AppendMatch(ret,buf,result)
            # 複数行コメントマッチャー
            result = re.fullmatch(".*(\/\*.*\*\/).*", buf, re.S)
            if result:
               ret,buf = AppendMatch(ret,buf,result)
            # 処理マッチャー
            result = re.fullmatch("(.*;)", buf, re.S)
            if result:
               ret,buf = AppendMatch(ret,buf,result)
      buf = buf.replace("\n", "")
      ret.append(buf + "\n")
      return ret
   def RemoveFunctionBlock(functionbody, compoundname):
      return functionbody[1:-1]
   def AddPlantUMLSentence(functionbody, compoundname):
      ret = []
      for line in functionbody:
         # if line.find("}") != -1 and line.find("}") != -1:
         # if line.find("{") != -1:
         ret.append('note right ' + compoundname + ': ' + line)
      return ret
   functionbody = RemoveEmpty(functionbody, compoundname)
   functionbody = Format(functionbody, compoundname)
   functionbody = RemoveFunctionBlock(functionbody, compoundname)
   functionbody = AddPlantUMLSentence(functionbody, compoundname)
   return functionbody
#============================================================================================================================================================
if __name__ == '__main__':
   # main('./input/xml/')
   DraftUML()
#============================================================================================================================================================
