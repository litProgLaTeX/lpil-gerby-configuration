
import argparse
import os
import yaml

# List the known Gerby Constants so that IF they are in the TOML file
# they will be used to over-ride the computed values
gerbyConsts = [
  "COMMENTS",
  "DATABASE",
  "UNIT",
  "DEPTH",
  "PATH",
  "PAUX",
  "TAGS",
  "PDF"
]

class ConfigManager(object) :

  def __init__(self, requireBaseDir=False) :
    self.data = {}

    # setup the command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument(
      'configPath',
      help="The path to a YAML file describing how to configure this Gerby-website instance."
    )
    if requireBaseDir :
      parser.add_argument(
        'baseDir',
        help="The base directory associated with this configuration."
      )
    else:
      parser.add_argument(
        'baseDir', nargs='?',
        help="The base directory associated with this configuration."
      )
    parser.add_argument(
      '-v', '--verbose', action='store_true', default=False,
      help="Be verbose [False]"
    )
    parser.add_argument(
      '-q', '--quiet', action='store_true', default=False,
      help="Be quiet [False]"
    )
    self.parser = parser
    self.cmdArgs = None
    self.baseDir = None

  def parseCmdArgs(self) :
    self.cmdArgs = vars(self.parser.parse_args())

    self.baseDir = self.cmdArgs['baseDir']
    if self.baseDir and self.baseDir.startswith('~') :
      self.baseDir = os.path.abspath(
        os.path.expanduser(self.baseDir)
      )

    self.configPath = self.cmdArgs['configPath']
    if self.configPath and self.configPath.startswith('~') :
      self.configPath = os.path.abspath(
        os.path.expanduser(self.configPath)
      )

  def checkInterface(self, keyList) :
    for theKey, theDef in keyList.items() :
      origKey = theKey
      thePath = theKey
      theDict = self.data
      while '.' in thePath :
        key, thePath = thePath.split('.', maxsplit=1)
        if '*' == key :
          keys = list(theDict.keys())
        else :
          keys = [ key ]
        origDict = theDict
        for aKey in keys :
          theDict = origDict
          if aKey not in theDict :
            if 'msg' in theDef :
              raise KeyError(
                f"Could not find key [{theKey.replace('*',aKey)}]: {theDef['msg']} (a)"
              )
            theDict[aKey] = {}
          theDict = theDict[aKey]
      if thePath not in theDict :
        if 'default' in aDef : theDict[thePath] = theDef['default']
        elif 'msg' in aDef   : raise KeyError(
          f"Could not find key [{theKey}]: {theDef['msg']} (b)"
        )
        else : raise KeyError(f"Could not find [{theKey}]")

  def __getitem__(self, key, default=None) :
    if isinstance(key, (list, tuple)) : key = '.'.join(key)
    origKey = key
    thePath = key
    theDict = self.data
    while '.' in thePath :
      key, thePath = thePath.split('.', maxsplit=1)
      if key not in theDict :
        return default
      theDict = theDict[key]
    theValue = theDict[thePath]
    if isinstance(theValue, str) :
      if self.baseDir and '$baseDir' in theValue :
        theValue = theValue.replace('$baseDir', self.baseDir)
    return theValue

  def __setitem__(self, key, value) :
    if isinstance(key, (list, tuple)) : key = '.'.join(key)
    thePath = key
    theDict = self.data
    while '.' in thePath :
      key, thePath = thePath.split('.', maxsplit=1)
      if key not in theDict :
        theDict[key] = {}
      theDict = theDict[key]

    theDict[thePath] = value

  def showConfig(self) :
    print(yaml.dump(self.data))

  def loadConfig(self) :
    if not self.cmdArgs :
      self.parseCmdArgs()

    yamlConfig = {}
    try:
      with open(self.configPath, 'rb') as yamlFile :
        yamlConfig = yaml.safe_load(yamlFile.read())
    except Exception as err :
      print(f"Could not load configuration from [{configPath}]")
      print(repr(err))

    if yamlConfig : self.data = yamlConfig

    if self.cmdArgs['verbose'] :
      self.data['verbose'] = self.cmdArgs['verbose']

    self.data['configPath'] = self.configPath
    self.data['baseDir']    = self.baseDir

    # report the configuration if verbose
    if self.data['verbose'] :
      print(f"Loaded config from: [{self.configPath}]\n")
      print("----- command line arguments -----")
      print(yaml.dump(self.cmdArgs))
      print("---------- configuration ---------")
      print(yaml.dump(self.data))

"""
def getDefaultConfig() :
  # default config
  config = {
    'gerbyConsts' : gerbyConsts,
    'working_dir' : '.',
    'document' : 'document',
    'port' : 5000,
    'host' : "127.0.0.1",
    'github_url' : "https://github.com/stacks/stacks-project",
    'verbose' : cmdArgs['verbose'],
    'quiet' : cmdArgs['quiet']
  }
"""