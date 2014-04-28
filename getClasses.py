from kelp.octopi import OctopiPlugin
from optparse import OptionParser
import kurt
import sys
import os
from kurt import Image

def main():
    parser = OptionParser(usage = "getClasses.py [-a] DIRECTORY") #Reads all scratch files in a directory and generates an import list for them
    parser.add_option('-a', '--append', action = "store", type = "string", dest = "directory")
    opt, argv = parser.parse_args()  
    if len(argv) == 0:
        if len(opt.directory) == 0:
            print("Usage: getClasses.py [-a(ppend)] Directory")
            return 1
        if len(opt.directory) != 0:
            directoryPath = opt.directory
            results = parseProjects(directoryPath)
            append = True 
    if len(argv) == 1:
        directoryPath = argv[0]
        results = parseProjects(directoryPath)
        append = False
    writeList = results[0]
    inputList = results[1]
    writeClassFile(directoryPath, writeList, inputList, append);
    
    
def parseProjects(directoryPath):
    writeList = []
    importList = []
    spriteCostumes = {}
    for scratchfile in os.listdir(directoryPath):
        if(scratchfile.endswith(".oct")):
            spriteList = {}
            spriteCount = 0
            oct = kurt.Project.load(os.path.abspath(scratchfile))
            spriteCount = len(oct.sprites)
            writeList.append("\nclass " + scratchfile[0:-4] +"():\n")
            importList.append('"'+scratchfile[0:-4]+'":projectClasses.'+scratchfile[0:-4])
            writeList.append('    spriteCount='+str(spriteCount)+'\n')
            writeList.append('    sprites={')
            spriteCount = len(oct.sprites)
            for sprite in oct.sprites: #iterates through each sprite
                costumeCount = len(sprite.costumes) #gets # of costumes
                image = sprite.name
                #print(list(sprite.costumes[0].image._pil_image.getdata()))
                spriteList[image] = ([],[]) #we use the sprite name because it is more unique than the first costume (lots of things named "costume1")
                spriteCostumes[image] = costumeCount
                if len(sprite.scripts) != 0:
                    for script in sprite.scripts:
                        if not isinstance(script, kurt.Comment):
                            spriteList[image][0].append(repr(script.stringify()))
            for name, lister in spriteList.items():
                writeList.append('"'+name+'":[[')
                writeList.append(',\n    '.join((lister[0])))
                writeList.append(']')
                writeList.append(',' +str(spriteCostumes[name])+'],\n    ')
            writeList.append('}')
            writeList[-2]= writeList[-2][0:-6]
            if (scratchfile == "AnimalRace.oct" or scratchfile == "DanceParty.oct"): #files in which it is acceptable to add to scripts
                writeList.append('\n    addOkay=True')
            else:
                writeList.append('\n    addOkay=False')
    return writeList, importList
def writeClassFile(directoryPath, writeList, importList, append):
        if not os.path.exists('projectClasses.py'):
            with open ('projectClasses.py', "w") as fp: #prints out classes
                fp.write(''.join(writeList))
        elif (append == True):
            with open ('projectClasses.py', "a") as fp:
                fp.write(''.join(writeList))
        if not os.path.exists('import.txt'):
            with open (directoryPath+'import.txt', "w") as fp: #prints a list of classes to be added to the "classes" dict
                fp.write('{' + ','.join(importList)+'}')
if __name__ == "__main__":
    main()