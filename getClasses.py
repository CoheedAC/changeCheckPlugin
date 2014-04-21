from kelp.octopi import OctopiPlugin
from optparse import OptionParser
import kurt
import sys
import os

def main():
    parser = OptionParser(usage = "getClasses.py [DIRECTORY]") #Reads all scratch files in a directory and generates an import list for them
    opt, argv = parser.parse_args()
    writeList = []
    importList = []
    spriteCostumes = {}
    if len(argv) == 0:
        print("Usage: getClasses.py [Directory or File]")
        return 1
    for scratchfile in os.listdir(argv[0]):
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
                spriteList[sprite.name] = ([],[])
                spriteCostumes[sprite.name] = costumeCount
                if len(sprite.scripts) != 0:
                    for script in sprite.scripts:
                        if not isinstance(script, kurt.Comment):
                            spriteList[sprite.name][0].append(repr(script.stringify()))
            for name, lister in spriteList.items():
                writeList.append('"'+name+'":[[')
                writeList.append(',\n    '.join((lister[0])))
                writeList.append(']')
                writeList.append(',' +str(spriteCostumes[name])+'],\n    ')
            writeList.append('}')
            writeList[-2]= writeList[-2][0:-6]
            if (name == "AnimalRace" or "DanceParty"):
                writeList.append('\n    addOkay=True')
            else:
                writeList.append('\n    addOkay=False')
    if not os.path.exists('projectClasses.py'):
        with open ('projectClasses.py', "w") as fp: #prints out classes
            fp.write(''.join(writeList))
    with open (argv[0]+'import.txt', "w") as fp: #prints a list of classes to be added to the "classes" dict
        fp.write('{' + ','.join(importList)+'}')
        
if __name__ == "__main__":
    main()