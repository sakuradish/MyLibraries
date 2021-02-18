#============================================================================================================================================================
import sys
sys.path.append('../MyLogger/')
sys.path.append('../MyDataBase/')
from MyLogger import MyLogger
MyLogger = MyLogger.GetInstance()
from MyDataBase import MyDataBase
db_functions = MyDataBase.GetInstance('plantuml_functions.xlsx')
db_functions.DFAppendColumn(['compoundname', 'definition', 'argsstring', 'name', 'samenamecnt', 'bodyfile', 'bodystart', 'bodyend'])
# db_defines = MyDataBase.GetInstance('plantuml_defines.xlsx')
# db_defines.DFAppendColumn(['compoundname', 'name', 'params', 'initializer', 'bodyfile', 'bodystart', 'bodyend']) #仮
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
def AnalyzeDoxygen(doxygenpath):
   files = [file for file in glob.glob(doxygenpath+'/**/*', recursive=True) if file.find('class_') != -1]
   # files = [file for file in glob.glob(doxygenpath+'/**/*', recursive=True) if file.find('.xml') != -1]
   MyLogger.SetFraction(len(files))
   for file in files:
      MyLogger.SetNumerator(files.index(file))
      ParseFunctions(file)
   db_functions.DFWrite()
#============================================================================================================================================================
@MyLogger.deco
def ParseFunctions(xmlpath):
   xml = ''.join(__myopen(xmlpath, 'r').readlines())
   soup = BeautifulSoup(xml, 'lxml')
   componddef = soup.find('compounddef')
   if not componddef:
      MyLogger.warning('not found compoundname in ', xmlpath)
      return
   compoundname = componddef.find('compoundname').text
   compoundname = compoundname[compoundname.rfind(":")+1:]
   functions = componddef.find_all('memberdef', {'kind':'function'})
   samenamecnt = {}
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
      if not name in samenamecnt:
         samenamecnt[name] = 1
      else:
         samenamecnt[name] += 1
      MyLogger.sakura(name,"[",samenamecnt[name],"]")
      db_functions.DFAppendRow([compoundname, definition, argsstring, name, samenamecnt[name], bodyfile, bodystart, bodyend])
#============================================================================================================================================================
# @MyLogger.deco
# def ParseDefines(xmlpath):
#    xml = ''.join(__myopen(xmlpath, 'r').readlines())
#    soup = BeautifulSoup(xml, 'lxml')
#    componddef = soup.find('compounddef')
#    if not componddef:
#       MyLogger.warning('not found compoundname in ', xmlpath)
#       return
#    compoundname = componddef.find('compoundname').text
#    defines = componddef.find_all('memberdef', {'kind':'define'})
#    for define in defines:
#       name = define.find('name').text
#       params = define.find_all('param')
#       initializer = define.find('initializer').text
#       if not location.has_attr('bodyfile'):
#          MyLogger.warning('not found bodyfile of ', definition)
#          continue
#       bodyfile = location['bodyfile']
#       bodystart = location['bodystart']
#       bodyend = location['bodyend']
#       db_defines.DFAppendRow([compoundname, name, params, initializer, bodyfile, bodystart, bodyend])
#============================================================================================================================================================
@MyLogger.deco
def DraftUML():
   inputbase='./input/'
   outputbase='./output/'
   MyLogger.SetFraction(len(db_functions.GetDict().items()))
   for index,values in db_functions.GetDict().items():
      MyLogger.SetNumerator(index)
      compoundname = values['compoundname']
      definition = values['definition']
      argsstring = values['argsstring']
      name = values['name'][values['name'].rfind(":")+1:]
      samenamecnt = str(values['samenamecnt'])
      bodyfile = values['bodyfile']
      bodystart = int(values['bodystart'])-1
      bodyend = int(values['bodyend'])
      inputfile = inputbase+bodyfile
      outputfile = outputbase+bodyfile+'/'+name+"_"+samenamecnt+'.pu'
      if not os.path.exists(os.path.dirname(outputfile)):
         os.makedirs(os.path.dirname(outputfile))
      if bodyend != -1:
         functionbody = __myopen(inputfile, 'r').readlines()[bodystart:bodyend]
      else:
         functionbody = __myopen(inputfile, 'r').readlines()[bodystart]
      functionbody = CustomizeFunctionBody(functionbody, compoundname)
      with __myopen(outputfile, 'w', encoding='utf-8') as f:
         f.write("' #######################################\n")
         f.write("' definition="+definition+"\n")
         f.write("' bodyfile="+bodyfile+"\n")
         f.write("' bodystart="+str(bodystart)+"\n")
         f.write("' bodyend="+str(bodyend)+"\n")
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
      ret = ['']
      for line in functionbody:
         line = line.strip(' ')
         line = line.strip('\t')
         ret.append(line)
      return ret
   def FirstFormat(functionbody, compoundname):
      ret = ['']
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
         # switch文caseマッチャー
         elif (result := re.fullmatch("(case.*:\n)", buf, re.S)):
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
      ret = ['']
      blockcnt = 0
      for line in functionbody:
         blockcnt -= len(re.findall("}", line))
         if blockcnt > 0:
            ret.append(line)
         blockcnt += len(re.findall("{", line))
      return ret
   def AddCallDependency(functionbody, compoundname):
      ret = ['']
      for line in functionbody:
         if (results := re.findall("\w+\(", line, re.S)):
            # MyLogger.sakura(results)
            # MyLogger.sakura(line.replace("\n",""))
            for result in results:
               # MyLogger.sakura(type(result))
               result = result[:result.find("(")]
               db_functions.DFRead()
               db_functions.DFFilter('name', result, mode='fullmatch')
               MyLogger.sakura(result)
               functions = db_functions.GetDict().values()
               if len(functions) == 1:
                  # 要素一個のときのdict_valueのアクセスの仕方後で調べる
                  for function in functions:
                     ret.append("' MyPlantUML["+compoundname+"->"+function['compoundname']+":"+result+"]\n")
               else:
                  ret.append("' MyPlantUML["+compoundname+"->]\n")
         ret.append(line)
      return ret
   def AddPlantUMLSentence(functionbody, compoundname):
      ret = ['']
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
         elif re.fullmatch("(case.*:\n)", line, re.S):
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
         # plantuml comment
         elif re.fullmatch("('.*\n)", line, re.S):
            ret.append(line)
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
      ret = ['']
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
   functionbody = AddCallDependency(functionbody, compoundname)
   functionbody = AddPlantUMLSentence(functionbody, compoundname)
   # functionbody = SecondFormat(functionbody, compoundname)
   return functionbody
#============================================================================================================================================================
if __name__ == '__main__':
   # AnalyzeDoxygen('./docs/xml/')
   DraftUML()
#============================================================================================================================================================
