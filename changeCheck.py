from kelp.octopi import OctopiPlugin
import kurt
import sys
import os
from optparse import OptionParser
import projectClasses #imports classfile that contains all required classes


classes = {"AnimalRace":projectClasses.AnimalRace,"CAGeography":projectClasses.CAGeography,
            "CAGeographyBroadcast":projectClasses.CAGeographyBroadcast,"DanceParty":projectClasses.DanceParty,"EgyptGame":projectClasses.EgyptGame,
            "GoldRush":projectClasses.GoldRush,"IntroGame":projectClasses.IntroGame,"MammalsGame":projectClasses.MammalsGame,"Missions":projectClasses.Missions,
            "MissionsBroadcast":projectClasses.MissionsBroadcast,"Planets":projectClasses.Planets,"PlanetsBroadcast":projectClasses.PlanetsBroadcast,
            "PlantGrowing":projectClasses.PlantGrowing,"RaceGame":projectClasses.RaceGame,"ThanksgivingGame":projectClasses.ThanksgivingGame} #lengthy list of classes
def main():
    parser = OptionParser(usage = "changeCheck.py Module [Filepath]")
    parser.add_option('-s', '--student-dir', action="store", type="string", dest="student", default=False,
                      help=('Analyze a directory of a projects of the same type.'))
    opt, argv = parser.parse_args()
    if len(argv) == 2: #analyze a single scratch file
        if os.path.exists(os.path.abspath(os.path.dirname(argv[1]))+'\\results\\output.html'):
            print("\nPlease remove the output.html file or rename it before running the check again")
            return 1
        if not os.path.exists(argv[1]):
            print("\nError: File not found")
            return 1
        module = argv[0]
        for key , objs in classes.items():
            if key == module:
                targetPath = argv[1]
                analyzeSingleFile(module, targetPath)
                return 0 
        print("\nError: Module not found.")
        return 1
    if opt.student: #analyze multiple scratch files (directory)
        if os.path.exists(os.path.abspath(os.path.dirname(argv[1]))+'\\results\\output.html'):
            print("\nPlease remove the output.html file or rename it before running the check again")
            return 1
        module = argv[0]
        targetPath = opt.student
        analyzeMultipleSnaps(module, targetPath)
    elif len(argv) < 2:
        print("usage: changeCheck.py Module (options) [Filepath]")
        return 1
    
def analyze(module, targetPath): #takes module argument and path to a scratch file
    oct = kurt.Project.load(os.path.abspath(targetPath))
    l = classes[module]() #creates a class of the appropriate type based on project
    results = []
    if (len(oct.sprites)< l.spriteCount): #checks for sprite addition/deletion
        results.append(str(l.spriteCount-len(oct.sprites))+" sprite(s) deleted")
    if (len(oct.sprites) == l.spriteCount):
        results.append("Correct amount of sprites")
    if (len(oct.sprites) > l.spriteCount):
        results.append(str(len(oct.sprites)-l.spriteCount)+" extra sprite(s)")
    for spriteName, spriteTuple in l.sprites.items(): #checks all scripts against originals
        count = 0
        scriptText = spriteTuple[0]
        numCostumes = spriteTuple[1]
        for sprite in oct.sprites:
            if spriteName == sprite.name: #start checking scripts to ensure accuracy
                for script in sprite.scripts:
                    for stuff in scriptText: # for each script belonging to the sprite
                        if stuff in script.stringify(): #loop that checks for each original script
                            count += 1
                            if stuff == script.stringify():
                                results.append (spriteName + ": Script " +str(count)+" unchanged")
                            else:
                                if (l.addOkay == False):
                                    results.append (spriteName +":Script " +str(count)+" Additions Made")
                            if (len (l.sprites[spriteName][0])!=0):
                                l.sprites[spriteName][0].remove(stuff)
                if (len(sprite.costumes) < numCostumes): #checks to see if costumes are created or deleted
                    results.append(spriteName +":Costumes Deleted")
                #if (len(sprite.costumes)  == numCostumes):
                    #results.append(spriteName+":Same number of costumes")
                if (len(sprite.costumes) > numCostumes):
                    results.append(spriteName +"Costumes Added")
    c = classes[module]()
    for sprite, script in l.sprites.items():
        if(len(script[0]) != 0 and (len(c.sprites[sprite][0]) != 0)):
            results.append(sprite + ":Script deletions made or script removed")
    return results    
def analyzeSingleFile(module, targetFile):
    resultsDict = {}
    if targetFile.endswith(".oct"):
        resultsDict[targetFile] = analyze(module, targetFile)
    else: 
        return
    html_out(resultsDict, os.path.dirname(os.path.abspath(targetFile)))
def analyzeMultipleSnaps(module, targetDirectory): #runs check against all files in a directory (snapshot)
    resultsDict = {}
    for scratchFile in os.listdir(targetDirectory):
        if scratchFile.endswith(".oct"):
            resultsDict[scratchFile] = analyze(module, targetDirectory+'\\'+scratchFile)
    html_out(resultsDict, os.path.abspath(targetDirectory))
def html_out(resultsDict, outpath):
    if not os.path.exists(outpath+'\\results'):
        os.mkdir(outpath+'\\results')
    html = []
    if not os.path.exists(outpath+'\\results/output.html'): #don't print anything if the path already exists 
        for project, list in resultsDict.items():
            html.append("<h2>" + project + "</h2>")
            for item in list:
                html.append("<p>"+item +"<p>")
        with open(outpath+'\\results/output.html', 'w') as fp:
            fp.write(''.join(html))
    #write out all results to a single page. 


if __name__ == "__main__":
    main()