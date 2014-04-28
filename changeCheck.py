from kelp.octopi import OctopiPlugin
import kurt
import sys
import os
from optparse import OptionParser
import projectClasses #imports classfile that contains all required classes
import copy


classes = {"AnimalRace":projectClasses.AnimalRace,"CAGeography":projectClasses.CAGeography,
            "CAGeographyBroadcast":projectClasses.CAGeographyBroadcast,"DanceParty":projectClasses.DanceParty,"EgyptGame":projectClasses.EgyptGame,
            "GoldRush":projectClasses.GoldRush,"IntroGame":projectClasses.IntroGame,"MammalsGame":projectClasses.MammalsGame,"Missions":projectClasses.Missions,
            "MissionsBroadcast":projectClasses.MissionsBroadcast,"Planets":projectClasses.Planets,"PlanetsBroadcast":projectClasses.PlanetsBroadcast,
            "PlantGrowing":projectClasses.PlantGrowing,"RaceGame":projectClasses.RaceGame,"ThanksgivingGame":projectClasses.ThanksgivingGame} #lengthy list of classes
def main():
    parser = OptionParser(usage = "changeCheck.py Module [Filepath]")
    parser.add_option('-s', '--student-dir', action="store", type="string", dest="student", default=False,
                      help=('Analyze a directory of a projects of the same type.'))
    parser.add_option('-d', '--directory', action ="store", type="string", dest="dir", default = False)
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
        if os.path.exists(os.path.abspath(os.path.dirname(opt.student))+'\\results\\output.html'):
            print("\nPlease remove the output.html file or rename it before running the check again")
            return 1
        module = argv[0]
        targetPath = opt.student
        results = analyzeMultipleSnaps(module, targetPath)
        html_out(results, targetPath)
    if opt.dir:
        module = argv[0]
        targetPath = opt.dir
        analyzeDirectoryOfStudentProjects(module, targetPath)
    elif len(argv) < 2:
        #print("usage: changeCheck.py Module (options) [Filepath]")
        #return 1
        analyzeSingleFile("AnimalRace", "test.oct")
    
def analyze(module, targetPath): #takes module argument and path to a scratch file
    oct = kurt.Project.load(os.path.abspath(targetPath))
    j = classes[module]()
    l = copy.deepcopy(j) #creates a class of the appropriate type based on project
    results = {}
    results["DeletedSprites"] = l.spriteCount - len(oct.sprites)
    for spriteName, spriteTuple in l.sprites.items(): #for all sprites and their information in the original project files  
        exists = False
        for sprite in oct.sprites:
            if (spriteName == sprite.name):
                exists = True
        if exists == True:
            count = 0
            scriptText = spriteTuple[0]
            numCostumes = spriteTuple[1]
            results[spriteName] = {}
            results[spriteName]['unchangedScripts'] = 0
            additions = 0
            unchanged = 0
            for sprite in oct.sprites: #for all sprites in the student's project
                if spriteName == sprite.name: #if this sprite is one of the ones in the original project file
                    results[spriteName]['scriptDeletions'] = 0
                    for script in sprite.scripts: #check each script in the files
                        if not isinstance(script, kurt.Comment):
                            for stuff in scriptText: # for each script belonging to the original project
                                if stuff in script.stringify(): #if they match
                                    count += 1
                                    if stuff == script.stringify(): #If an exact match
                                        unchanged += 1
                                    else:
                                        if (l.addOkay == False): # if some content added
                                            additions += 1
                                    #if (len (l.sprites[spriteName][0])!=0): #remove the script from the pool to check against
                                        #l.sprites[spriteName][0].remove(stuff)
                        else:
                            sprite.scripts.remove(script)
                    results[spriteName]['scriptDeletions'] = len(l.sprites[spriteName][0]) - len(sprite.scripts)
                    results[spriteName].update({'unchangedScripts': unchanged}) #writes out # of unchanged scripts
                    results[spriteName]['scriptsWithAdditions'] = additions #writes out # of scripts with additions
                    results[spriteName]['deletedCostumes'] = numCostumes - len(sprite.costumes) #writes out the number of deleted costumes
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
    return resultsDict
    #html_out(resultsDict, os.path.abspath(targetDirectory))
def analyzeDirectoryOfStudentProjects(module, targetDirectory):
    results = {}
    madeChanges = 0
    added = 0
    deletedCostume = 0
    deletedScript = 0
    deletedSprite = 0
    numStudents = 0
    for directory in os.listdir(targetDirectory):
        results[directory] = analyzeMultipleSnaps(module, targetDirectory+'\\'+directory)
    for student, data in results.items():
        numStudents += 1
        changes = False
        delCostume = False
        addScript  = False
        delScript = False
        delSprite = False
        for filename, projectResults in data.items():
            if projectResults['DeletedSprites'] != 0: 
                    delSprite = True
            del projectResults['DeletedSprites']
            for sprite, dictionary in projectResults.items():
                if dictionary['unchangedScripts'] != 0:
                    changes = True
                if dictionary['deletedCostumes'] != 0:
                    delCostume = True
                if dictionary['scriptsWithAdditions'] != 0:
                    addScript = True
                if dictionary['scriptDeletions'] != 0:
                    delScript = True
        if changes == True:
            madeChanges+=1 
        if delCostume == True:
            deletedCostume +=1
        if addScript == True:
            added +=1 
        if delScript == True:
            deletedScript +=1
        if delSprite == True:
            deletedSprite +=1
    resultsDict = {'added':added, 'costumeDeleted':deletedCostume, 'scriptDeleted':deletedScript, 'spritesDeleted':deletedSprite, 'nochanges':(numStudents-madeChanges),
                   'numstudents': numStudents}
    stats_out(resultsDict, targetDirectory)
def html_out(resultsDict, outpath):
    if not os.path.exists(outpath+'\\results'):
        os.mkdir(outpath+'\\results')
    html = []
    if not os.path.exists(outpath+'\\results/output.html'): #don't print anything if the path already exists 
        for project, list in resultsDict.items():
            html.append("<h2>" + project + "</h2>")
            html.append("Deleted Sprites:" + str(list['DeletedSprites']))
            del list['DeletedSprites']
            for key, pair in list.items():
                html.append("<h3><p>"+key + ":</p></h3>")
                for name, value in pair.items():
                    html.append("<p>    "+ name + ":" + str(value) +"</p>")
        with open(outpath+'\\results/output.html', 'w') as fp:
            fp.write(''.join(html))
    #write out all results to a single page. 
def stats_out(resultsDict, outpath):
    if not os.path.exists(outpath+'\\results'):
        os.mkdir(outpath+'\\results')
    with open(outpath+'\\results/data.txt', 'w') as fp:
            fp.write("#students who made no changes to starting scripts: " + str(resultsDict['nochanges'])+ "\n")
            fp.write("#students who added to starting scripts: " + str(resultsDict['added'])+ "\n")
            fp.write("#students who deleted a costume: " + str(resultsDict['costumeDeleted'])+ "\n")
            fp.write("#students who deleted a script: "  + str(resultsDict['scriptDeleted'])+ "\n")
            fp.write("#students who deleted a sprite: " + str(resultsDict['spritesDeleted'])+ "\n")
            fp.write("#students total: " + str(resultsDict['numstudents']))
    #writes out the stats 
if __name__ == "__main__":
    main()