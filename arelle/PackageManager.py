'''
Separated on Jul 28, 2013 from DialogOpenArchive.py

@author: Mark V Systems Limited
(c) Copyright 2010 Mark V Systems Limited, All rights reserved.
'''
import sys, os, io, time, json, logging
from fnmatch import fnmatch
from lxml import etree
if sys.version[0] >= '3':
    from urllib.parse import urljoin
else:
    from urlparse import urljoin
openFileSource = None
from arelle import Locale
from arelle.UrlUtil import isHttpUrl
ArchiveFileIOError = None
try:
    from collections import OrderedDict
except ImportError:
    OrderedDict = dict # python 3.0 lacks OrderedDict, json file will be in weird order 

EMPTYDICT = {}

def baseForElement(element):
    base = ""
    baseElt = element
    while baseElt is not None:
        baseAttr = baseElt.get("{http://www.w3.org/XML/1998/namespace}base")
        if baseAttr:
            if baseAttr.startswith("/"):
                base = baseAttr
            else:
                base = baseAttr + base
        baseElt = baseElt.getparent()
    return base
        

def parsePackage(cntlr, filesource, metadataFile, fileBase):
    global ArchiveFileIOError
    if ArchiveFileIOError is None:
        from arelle.FileSource import ArchiveFileIOError

    unNamedCounter = 1
    
    txmyPkgNSes = ("http://www.corefiling.com/xbrl/taxonomypackage/v1",
                   "http://xbrl.org/PWD/2014-01-15/taxonomy-package",
                   "http://xbrl.org/PWD/2015-01-14/taxonomy-package")
    catalogNSes = ("urn:oasis:names:tc:entity:xmlns:xml:catalog",)
    
    pkg = {}

    currentLang = Locale.getLanguageCode()
    if filesource.isZip:
        _file = filesource.file(metadataFile)[0] # URL in zip
    else:
        _file = metadataFile # URL not in zip
    tree = etree.parse(_file)
    root = tree.getroot()
    ns = root.tag.partition("}")[0][1:]
    nsPrefix = "{{{}}}".format(ns)
    
    if ns in  txmyPkgNSes:  # package file
        for eltName in ("name", "description", "version"):
            pkg[eltName] = ''
            for m in root.iterchildren(tag=nsPrefix + eltName):
                pkg[eltName] = m.text.strip()
                break # take first entry if several
    else: # oasis catalog, use dirname as the package name
        # metadataFile may be a File object (with name) or string filename 
        fileName = getattr(metadataFile, 'fileName',      # for FileSource named objects 
                           getattr(metadataFile, 'name',  # for io.file named objects
                                   metadataFile))         # for string
        pkg["name"] = os.path.basename(os.path.dirname(fileName))
        pkg["description"] = "oasis catalog"
        pkg["version"] = "(none)"

    remappings = {}
    rewriteTree = tree
    catalogFile = metadataFile
    if ns in ("http://xbrl.org/PWD/2015-01-14/taxonomy-package",) and filesource.isZip:
        catalogFile = metadataFile.replace('taxonomyPackage.xml','catalog.xml')
        try:
            rewriteTree = etree.parse(filesource.file(catalogFile)[0])
        except ArchiveFileIOError:
            pass
    for tag, prefixAttr, replaceAttr in (
         (nsPrefix + "remapping", "prefix", "replaceWith"), # taxonomy package
         ("{urn:oasis:names:tc:entity:xmlns:xml:catalog}rewriteSystem", "systemIdStartString", "rewritePrefix"),
         ("{urn:oasis:names:tc:entity:xmlns:xml:catalog}rewriteURI", "uriStartString", "rewritePrefix")): # oasis catalog
        for m in rewriteTree.iter(tag=tag):
            prefixValue = m.get(prefixAttr)
            replaceValue = m.get(replaceAttr)
            if prefixValue and replaceValue is not None:
                if prefixValue not in remappings:
                    base = baseForElement(m)
                    if base:
                        replaceValue = os.path.join(base, replaceValue)
                    if replaceValue: # neither None nor ''
                        if not replaceValue.startswith('http://'):
                                if not os.path.isabs(replaceValue):
                                    replaceValue = fileBase + replaceValue
                                replaceValue = replaceValue.replace("/", os.sep)
                    _normedValue = os.path.normpath(replaceValue)
                    if replaceValue.endswith(os.sep) and not _normedValue.endswith(os.sep):
                        _normedValue += os.sep
                    remappings[prefixValue] = _normedValue
                else:
                    cntlr.addToLog(_("Package catalog duplicate rewrite start string %(rewriteStartString)s"),
                                   messageArgs={"rewriteStartString": prefixValue},
                                   messageCode="arelle.catalogDuplicateRewrite",
                                   file=os.path.basename(catalogFile),
                                   level=logging.ERROR)


    pkg["remappings"] = remappings

    nameToUrls = {}
    pkg["nameToUrls"] = nameToUrls

    for entryPointSpec in tree.iter(tag=nsPrefix + "entryPoint"):
        name = None
        
        # find closest match name node given xml:lang match to current language or no xml:lang
        for nameNode in entryPointSpec.iter(tag=nsPrefix + "name"):
            xmlLang = nameNode.get('{http://www.w3.org/XML/1998/namespace}lang')
            if name is None or not xmlLang or currentLang == xmlLang:
                name = nameNode.text
                if currentLang == xmlLang: # most prefer one with the current locale's language
                    break

        if not name:
            name = _("<unnamed {0}>").format(unNamedCounter)
            unNamedCounter += 1

        epDocCount = 0
        for epDoc in entryPointSpec.iterchildren(nsPrefix + "entryPointDocument"):
            epUrl = epDoc.get('href')
            base = epDoc.get('{http://www.w3.org/XML/1998/namespace}base') # cope with xml:base
            if base:
                resolvedUrl = urljoin(base, epUrl)
            else:
                resolvedUrl = epUrl
            if epDocCount:
                cntlr.addToLog(_("Skipping multiple-document entry point (not supported) %(href)s"),
                               messageArgs={"href": epUrl},
                               messageCode="arelle.packageMultipleDocumentEntryPoints",
                               file=os.path.basename(metadataFile),
                               level=logging.WARNING)
                continue
            epDocCount += 1
    
            #perform prefix remappings
            remappedUrl = resolvedUrl
            longestPrefix = 0
            for mapFrom, mapTo in remappings.items():
                if remappedUrl.startswith(mapFrom):
                    prefixLength = len(mapFrom)
                    if prefixLength > longestPrefix:
                        _remappedUrl = remappedUrl[prefixLength:]
                        if not (_remappedUrl[0] in (os.sep, '/') or mapTo[-1] in (os.sep, '/')):
                            _remappedUrl = mapTo + os.sep + _remappedUrl
                        else:
                            _remappedUrl = mapTo + _remappedUrl
                        longestPrefix = prefixLength
            if longestPrefix:
                remappedUrl = _remappedUrl.replace(os.sep, "/")  # always used as FileSource select
            nameToUrls[name] = (remappedUrl, resolvedUrl)

    return pkg

# taxonomy package manager
# plugin control is static to correspond to statically loaded modules
packagesJsonFile = None
packagesConfig = None
packagesConfigChanged = False
packagesMappings = {}
_cntlr = None

def init(cntlr):
    global packagesJsonFile, packagesConfig, packagesMappings, _cntlr
    try:
        packagesJsonFile = cntlr.userAppDir + os.sep + "taxonomyPackages.json"
        with io.open(packagesJsonFile, 'rt', encoding='utf-8') as f:
            packagesConfig = json.load(f)
        packagesConfigChanged = False
    except Exception:
        # on GAE no userAppDir, will always come here
        packagesConfig = {  # savable/reloadable plug in configuration
            "packages": [], # list taxonomy packages loaded and their remappings
            "remappings": {}  # dict by prefix of remappings in effect
        }
        packagesConfigChanged = False # don't save until something is added to pluginConfig
    pluginMethodsForClasses = {} # dict by class of list of ordered callable function objects
    _cntlr = cntlr
    
def reset():  # force reloading modules and plugin infos
    packagesConfig.clear()  # dict of loaded module pluginInfo objects by module names
    packagesMappings.clear() # dict by class of list of ordered callable function objects
    
def orderedPackagesConfig():
    return OrderedDict(
        (('packages', [OrderedDict(sorted(_packageInfo.items(), 
                                          key=lambda k: {'name': '01',
                                                         'status': '02',
                                                         'version': '03',
                                                         'fileDate': '04',
                                                         'URL': '05',
                                                         'description': '06',
                                                         'remappings': '07'}.get(k[0],k[0])))
                       for _packageInfo in packagesConfig['packages']]),
         ('remappings',OrderedDict(sorted(packagesConfig['remappings'].items())))))
    
def save(cntlr):
    global packagesConfigChanged
    if packagesConfigChanged and cntlr.hasFileSystem:
        with io.open(packagesJsonFile, 'wt', encoding='utf-8') as f:
            jsonStr = _STR_UNICODE(json.dumps(orderedPackagesConfig(), ensure_ascii=False, indent=2)) # might not be unicode in 2.7
            f.write(jsonStr)
        packagesConfigChanged = False
    
def close():  # close all loaded methods
    packagesConfig.clear()
    packagesMappings.clear()
    global webCache
    webCache = None
    
''' packagesConfig structure

{
 'packages':  [list of package dicts in order of application],
 'remappings': dict of prefix:url remappings
}

package dict
{
    'name': package name
    'status': enabled | disabled
    'version': version (such as 2009)
    'fileDate': 2001-01-01
    'url': web http (before caching) or local file location
    'description': text
    'remappings': dict of prefix:url of each remapping
}

'''

def packageNamesWithNewerFileDates():
    names = set()
    for package in packagesConfig["packages"]:
        freshenedFilename = _cntlr.webCache.getfilename(package["URL"], checkModifiedTime=True, normalize=True)
        try:
            if package["fileDate"] < time.strftime('%Y-%m-%dT%H:%M:%S UTC', time.gmtime(os.path.getmtime(freshenedFilename))):
                names.add(package["name"])
        except Exception:
            pass
    return names

def packageInfo(cntlr, URL, reload=False, packageManifestName=None):
    #TODO several directories, eg User Application Data
    packageFilename = _cntlr.webCache.getfilename(URL, reload=reload, normalize=True)
    if packageFilename:
        from arelle.FileSource import TAXONOMY_PACKAGE_FILE_NAMES
        filesource = None
        try:
            global openFileSource
            if openFileSource is None:
                from arelle.FileSource import openFileSource
            filesource = openFileSource(packageFilename, _cntlr)
            # allow multiple manifests [[metadata, prefix]...] for multiple catalogs
            packages = []
            if filesource.isZip:
                _dir = filesource.dir
                _metaInf = '{}/META-INF/'.format(
                            os.path.splitext(os.path.basename(packageFilename))[0])
                if packageManifestName:
                    packageFiles = [fileName
                                    for fileName in filesource.dir
                                    if fnmatch(fileName, packageManifestName)]
                elif _metaInf + 'taxonomyPackage.xml' in _dir:
                    # PWD taxonomy packages
                    packageFiles = [_metaInf + 'taxonomyPackage.xml']
                else:
                    # early generation taxonomy packages
                    packageFiles = filesource.taxonomyPackageMetadataFiles
                if len(packageFiles) < 1:
                    raise IOError(_("Taxonomy package contained no metadata file: {0}.")
                                  .format(', '.join(packageFiles)))
                # if current package files found, remove any nonconforming package files
                if any(pf.startswith(_metaInf) for pf in packageFiles) and any(not pf.startswith(_metaInf) for pf in packageFiles):
                    packageFiles = [pf for pf in packageFiles if pf.startswith(_metaInf)]
                    
                for packageFile in packageFiles:
                    packageFileUrl = filesource.url + os.sep + packageFile
                    packageFilePrefix = os.sep.join(os.path.split(packageFile)[:-1])
                    if packageFilePrefix:
                        packageFilePrefix += os.sep
                    packageFilePrefix = filesource.baseurl + os.sep +  packageFilePrefix
                    packages.append([packageFileUrl, packageFilePrefix, packageFile])
            elif os.path.basename(filesource.url) in TAXONOMY_PACKAGE_FILE_NAMES: # individual manifest file
                packageFile = packageFileUrl = filesource.url
                packageFilePrefix = os.sep.join(os.path.split(packageFile)[:-1])
                if packageFilePrefix:
                    packageFilePrefix += os.sep
                packages.append([packageFileUrl, packageFilePrefix, ""])
            else:
                raise IOError(_("File must be a taxonomy package (zip file), catalog file, or manifest (): {0}.")
                              .format(packageFilename, ', '.join(TAXONOMY_PACKAGE_FILE_NAMES)))
            remappings = {}
            packageNames = []
            descriptions = []
            for packageFileUrl, packageFilePrefix, packageFile in packages:
                parsedPackage = parsePackage(_cntlr, filesource, packageFileUrl, packageFilePrefix)
                packageNames.append(parsedPackage['name'])
                if parsedPackage.get('description'):
                    descriptions.append(parsedPackage['description'])
                for prefix, remapping in parsedPackage["remappings"].items():
                    if prefix not in remappings:
                        remappings[prefix] = remapping
                    else:
                        cntlr.addToLog("Package mapping duplicate rewrite start string %(rewriteStartString)s",
                                       messageArgs={"rewriteStartString": prefix},
                                       messageCode="arelle.packageDuplicateMapping",
                                       file=os.path.basename(URL),
                                       level=logging.ERROR)
            package = {'name': ", ".join(packageNames),
                       'status': 'enabled',
                       'version': parsedPackage['version'],
                       'fileDate': time.strftime('%Y-%m-%dT%H:%M:%S UTC', time.gmtime(os.path.getmtime(packageFilename))),
                       'URL': URL,
                       'manifestName': packageManifestName,
                       'description': "; ".join(descriptions),
                       'remappings': remappings,
                       }
            filesource.close()
            return package
        except EnvironmentError:
            pass
        if filesource:
            filesource.close()
    return None

def rebuildRemappings(cntlr):
    remappings = packagesConfig["remappings"]
    remappings.clear()
    remapOverlapUrls = [] # (prefix, packageURL, rewriteString)
    for _packageInfo in packagesConfig["packages"]:
        _packageInfoURL = _packageInfo['URL']
        if _packageInfo['status'] == 'enabled':
            for prefix, remapping in _packageInfo['remappings'].items():
                remappings[prefix] = remapping
                remapOverlapUrls.append( (prefix, _packageInfoURL, remapping) )
    remapOverlapUrls.sort()
    for i, _remap in enumerate(remapOverlapUrls):
        _prefix, _packageURL, _rewrite = _remap
        for j in range(i-1, -1, -1):
            _prefix2, _packageURL2, _rewrite2 = remapOverlapUrls[j]
            if (_packageURL != _packageURL2 and _prefix and _prefix2 and 
                (_prefix.startswith(_prefix2) or _prefix2.startswith(_prefix))):
                _url1 = os.path.basename(_packageURL)
                _url2 = os.path.basename(_packageURL2)
                if _url1 == _url2: # use full file names
                    _url1 = _packageURL
                    _url2 = _packageURL2
                cntlr.addToLog(_("Packages overlap the same rewrite start string %(rewriteStartString)s")
                               if _prefix == _prefix2 else
                               _("Packages overlap rewrite start strings %(rewriteStartString)s and %(rewriteStartString2)s"),
                               messageArgs={"rewriteStartString": _prefix, "rewriteStartString2": _prefix2},
                               messageCode="arelle.packageRewriteOverlap",
                               file=(_url1, _url2),
                               level=logging.WARNING)
    

def isMappedUrl(url):
    return (packagesConfig is not None and 
            any(url.startswith(mapFrom) 
                for mapFrom in packagesConfig.get('remappings', EMPTYDICT).keys()))

def mappedUrl(url):
    if packagesConfig is not None:
        longestPrefix = 0
        for mapFrom, mapTo in packagesConfig.get('remappings', EMPTYDICT).items():
            if url.startswith(mapFrom):
                prefixLength = len(mapFrom)
                if prefixLength > longestPrefix:
                    mappedUrl = mapTo + url[prefixLength:]
                    longestPrefix = prefixLength
        if longestPrefix:
            return mappedUrl
    return url

def addPackage(cntlr, url, packageManifestName=None):
    newPackageInfo = packageInfo(cntlr, url, packageManifestName=packageManifestName)
    if newPackageInfo and newPackageInfo.get("name"):
        name = newPackageInfo.get("name")
        version = newPackageInfo.get("version")
        j = -1
        packagesList = packagesConfig["packages"]
        for i, _packageInfo in enumerate(packagesList):
            if _packageInfo['name'] == name and _packageInfo['version'] == version:
                j = i
                break
        if 0 <= j < len(packagesList): # replace entry
            packagesList[j] = newPackageInfo
        else:
            packagesList.append(newPackageInfo)
        global packagesConfigChanged
        packagesConfigChanged = True
        return newPackageInfo
    return None

def reloadPackageModule(cntlr, name):
    packageUrls = []
    packagesList = packagesConfig["packages"]
    for _packageInfo in packagesList:
        if _packageInfo['name'] == name:
            packageUrls.append(_packageInfo['URL'])
    result = False
    for url in packageUrls:
        addPackage(cntlr, url)
        result = True
    return result

def removePackageModule(cntlr, name):
    packageIndices = []
    packagesList = packagesConfig["packages"]
    for i, _packageInfo in enumerate(packagesList):
        if _packageInfo['name'] == name:
            packageIndices.insert(0, i) # must remove in reverse index order
    result = False
    for i in packageIndices:
        del packagesList[i]
        result = True
    if result:
        global packagesConfigChanged
        packagesConfigChanged = True
    return result
