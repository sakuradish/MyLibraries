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
@MyLogger.deco
def main(doxygenpath):
   files = [file for file in glob.glob(doxygenpath+'/**/*', recursive=True) if file.find('class_') != -1]
   # files = [file for file in glob.glob(doxygenpath+'/**/*', recursive=True) if file.find('.xml') != -1]
   MyLogger.SetFraction(len(files))
   for file in files:
      MyLogger.SetNumerator(files.index(file))
      analyzeXML(file)
   db.DFWrite()
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
      MyLogger.sakura(bodyfile)
      MyLogger.sakura(bodystart)
      MyLogger.sakura(bodyend)
      db.DFAppendRow([compoundname, definition, argsstring, name, bodyfile, bodystart, bodyend])
#============================================================================================================================================================
@MyLogger.deco
def DraftUML():
   inputbase='./input/'
   outputbase='./output/'
   MyLogger.SetFraction(len(db.GetDict().items()))
   for index,values in db.GetDict().items():
      MyLogger.SetNumerator(index)
      compoundname = values['compoundname']
      compoundname = compoundname[compoundname.rfind(":")+1:]
      definition = values['definition']
      argsstring = values['argsstring']
      # argsstring = argsstring.replace(" ","_").replace(":","").replace("&","").replace("<","").replace(">","")
      name = values['name']
      bodyfile = values['bodyfile']
      bodystart = int(values['bodystart'])-1
      bodyend = int(values['bodyend'])
      inputfile = inputbase+bodyfile
      # outputfile = outputbase+bodyfile+'/'+name+"_"+argsstring+'.pu'
      outputfile = outputbase+bodyfile+'/'+name+'.pu'
      if not os.path.exists(os.path.dirname(outputfile)):
         os.makedirs(os.path.dirname(outputfile))
      functionbody = __myopen(inputfile, 'r').readlines()[bodystart:bodyend]
      functionbody = CustomizeFunctionBody(functionbody, compoundname)
      with __myopen(outputfile, 'w', encoding='utf-8') as f:
         f.write("' #######################################\n")
         f.write("@startuml\n")
         f.write("== " + compoundname + ":" + name + argsstring + " ==\n")
         f.write("activate " + compoundname + "\n")
         f.write("' #######################################\n")
         f.write(''.join(functionbody))
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
   def FirstFormat(functionbody, compoundname):
      ret = []
      buf = ''
      for char in ''.join(functionbody):
         buf += char
         # bufは必ず空白文字以外で始まるようにする
         buf = buf.lstrip()
         if buf == "":
            continue
         # ラムダ式で引っ掛からないようにする
         elif len(re.findall("\(", buf))-len(re.findall("\)", buf)) != 0:
            continue
         # 関数宣言マッチャー # ifとかforもマッチするはず
         elif (result := re.fullmatch("(.*\(.*\).*\{)", buf, re.S)):
            ret.append(result.group(1).replace("\n", "") + "\n")
            buf = ''
         # 処理マッチャー
         elif (result := re.fullmatch("(.*;)", buf, re.S)):
            ret.append(result.group(1).replace("\n", "") + "\n")
            buf = ''
         # 一行コメントマッチャー
         elif (result := re.fullmatch("(//.*\n)", buf, re.S)):
            ret.append(result.group(1).replace("\n", "") + "\n")
            buf = ''
         # 複数行コメントマッチャー
         elif (result := re.fullmatch("(\/\*.*\*\/)", buf, re.S)):
            ret.append(result.group(1).replace("\n", "") + "\n")
            buf = ''
         # ブロック終端マッチャー
         elif (result := re.fullmatch("(})", buf, re.S)):
            ret.append(result.group(1).replace("\n", "") + "\n")
            buf = ''
         # プリプロセッサーマッチャー
         elif (result := re.fullmatch("(#.*\n)", buf, re.S)):
            ret.append(result.group(1).replace("\n", "") + "\n")
            buf = ''
         # elseマッチャー
         elif (result := re.fullmatch("(else.*{)", buf, re.S)):
            ret[-1] = ret[-1].replace("\n","") + " " + result.group(1).replace("\n", "") + "\n"
            buf = ''
      return ret
   def RemoveFunctionBlock(functionbody, compoundname):
      return functionbody[1:-1]
   def AddPlantUMLSentence(functionbody, compoundname):
      ret = []
      for line in functionbody:
         # プリプロセッサ系
         if re.fullmatch("(#if.*\n)", line, re.S):
            ret.append("alt "+line)
         elif re.fullmatch("(#else.*\n)", line, re.S):
            ret.append("else "+line)
         elif re.fullmatch("(#endif.*\n)", line, re.S):
            ret.append("end "+line)
         # ブロック系
         elif re.fullmatch("(.*\(.*\).*\{\n)", line, re.S):
            ret.append("alt "+line)
         elif re.fullmatch("(}.*else.*\{\n)", line, re.S):
            ret.append("else "+line)
         elif re.fullmatch("(}\n)", line, re.S):
            ret.append("end "+line)
         # コメント
         elif re.fullmatch("(//.*\n)", line, re.S):
            ret.append("note right "+compoundname+": "+line)
         elif re.fullmatch("(\/\*.*\*\/\n)", line, re.S):
            ret.append("note right "+compoundname+": "+line)
         # return
         elif re.fullmatch("(return.*;\n)", line, re.S):
            ret.append(compoundname+"-->entrypoint: "+line)
         # その他
         else:
            ret.append("note right "+compoundname+"#00ffff: "+line)
      return ret
   def SecondFormat(functionbody, compoundname):
      def Nest(nest):
         return ("  "*nest)
      def AlignRight(text):
         maxlen = len("note right "+compoundname+"#00ffff: ")
         return (((" "*maxlen)+text)[-maxlen:])
      ret = []
      nest = 0
      for line in functionbody:
         if (result := re.fullmatch("(alt )(.*\n)", line, re.S)) != None:
            ret.append(AlignRight(result.group(1))+Nest(nest)+result.group(2))
            nest += 1
         elif (result := re.fullmatch("(else )(.*\n)", line, re.S)) != None:
            ret.append(AlignRight(result.group(1))+Nest(nest-1)+result.group(2))
         elif (result := re.fullmatch("(end )(.*\n)", line, re.S)) != None:
            nest -= 1
            ret.append(AlignRight(result.group(1))+Nest(nest)+result.group(2))
         elif (result := re.fullmatch("([^:]*: )(.*\n)", line, re.S)) != None:
            ret.append(AlignRight(result.group(1))+Nest(nest)+result.group(2))
      return ret
   functionbody = RemoveEmpty(functionbody, compoundname)
   functionbody = FirstFormat(functionbody, compoundname)
   functionbody = RemoveFunctionBlock(functionbody, compoundname)
   functionbody = AddPlantUMLSentence(functionbody, compoundname)
   functionbody = SecondFormat(functionbody, compoundname)
   return functionbody
#============================================================================================================================================================
if __name__ == '__main__':
   main('./input/xml/')
   DraftUML()
#============================================================================================================================================================
