from population import Population
import numpy as np
import matplotlib.pyplot as plt

debugging = False

def debugPrint(msg):
    if debugging: print msg
    

def printDebugHouseholds(pop):
    for h in pop.households:
        pcnt = 0
        for p in h:
            if p in pop.people:
                debugPrint(p.printRelationships())
                pcnt += 1
        if pcnt > 0:
            debugPrint("\n")
        

def runSim(simDays, peopleCount, datesEveryXDays, isolateIfSick, isolateIfRoomieSick, initialInfectedPerc, avgRelationships, maxRelationships, avgHouseSize, maxHouseSize):
    # Create pop
    pop = Population(peopleCount, datesEveryXDays, isolateIfSick, isolateIfRoomieSick, initInfectedPerc, avgRelationships, maxRelationships, avgHouseSize, maxHouseSize, debugPrint)
        
    printDebugHouseholds(pop)
        
    print 'Running simulation...'
        
    # Run sim
    pop.runSim(simDays)
            
    # Print output
    totalSimPopInfections = 0
    infectedGenPop = 0
    infectionsFromOutsidePop = 0
    rValues = []
    for p in pop.people:
        if p.immune:
            totalSimPopInfections += 1
            infectedGenPop += p.infectedGenPop
            if p.infectedByGenPop: infectionsFromOutsidePop += 1
            rValues.append(p.rValue)
            
    casesCausedBySimPopTransmission = totalSimPopInfections - infectionsFromOutsidePop
            
    # avgActiveInfectedDaily = round(sum(activeInfectedDaily)/float(len(activeInfectedDaily)), 2)
    avgRValue = round(sum(rValues)/float(len(rValues)), 2)
    
    # print rValues
    print '{0} infections occured after {1} days'.format(totalSimPopInfections + infectedGenPop, simDays)
    print '{0} total sim pop'.format(pop.count)
    print '{0} rValue'.format(avgRValue)
    print '{0} Infections caused by sim pop transmission'.format(casesCausedBySimPopTransmission)
    print '{0} Starter Infections'.format(pop.initialInfected)
    print '{0} Sim pop were infected by gen pop'.format(infectionsFromOutsidePop - pop.initialInfected)
    print '{0} Gen pop were infected by sim Pop'.format(infectedGenPop)
    print '12.5% Infected by day {0}'.format('Never' if pop.firstDay125PercInfected < 0 else pop.firstDay125PercInfected)
    print '25.0% Infected by day {0}'.format('Never' if pop.firstDay25PercInfected < 0 else pop.firstDay25PercInfected)
    print '50.0% Infected by day {0}'.format('Never' if pop.firstDay50PercInfected < 0 else pop.firstDay50PercInfected)
    print ''
    
    return pop


def runMultipleSims(testToRun, simDays, peopleCount, datesEveryXDays, isolateIfSick, isolateIfRoomieSick, initialInfectedPerc, avgRelationships, maxRelationships, avgHouseSize, maxHouseSize):
    pops = []
    for i in range(0, testToRun):
        pops.append( runSim(daysToRun, popSize, datesEveryXDays, isolateIfSick, isolateIfRoomieSick, initialInfectedPerc, avgRelationships, maxRelationships, avgHouseSize, maxHouseSize) )
    return pops
    
    
def plotPops(plot, pops, title):
    activeDailiesAvg = [0 for i in pops[0].activeInfectedDaily]
    totalDailiesAvg = [0 for i in pops[0].totalInfectedDaily]
    
    for pop in pops:
        activeDailyPerc = [round(d/float(pop.count) * 100, 2) for d in pop.activeInfectedDaily]
        totalDailyPerc = [round(d/float(pop.count) * 100, 2) for d in pop.totalInfectedDaily]
        
        for i in range(0, len(activeDailiesAvg)):
            activeDailiesAvg[i] += activeDailyPerc[i]
            totalDailiesAvg[i] += totalDailyPerc[i]
            
        plot.plot(range(0, daysToRun), activeDailyPerc, color='#f10c45', linewidth=1, alpha=0.4)
        plot.fill_between(range(0, daysToRun), totalDailyPerc, color='#047495', alpha = 0.05)
        
    for i in range(0, len(activeDailiesAvg)):
        activeDailiesAvg[i] = activeDailiesAvg[i] / len(pops)
        totalDailiesAvg[i] = totalDailiesAvg[i] / len(pops)
        
    plot.plot(range(0, daysToRun), activeDailiesAvg, color='#f10c45', linewidth=3, alpha=0.7)
    plot.plot(range(0, daysToRun), totalDailiesAvg, color='#047495', linewidth=3, alpha=0.7)
        
    plot.set_title(title, size='small')
    
    
# Settings
avgRelationships = 2
maxRelationships = 4
avgHouseSize = 3
maxHouseSize = 15
testToRun = 20
daysToRun = 100
popSize = 1000
initInfectedPerc = 0.01


# Setup plots
fig, plots = plt.subplots(3, sharex=True, sharey=True)


# Run and Plot Scenario 1
popsNoDates = runMultipleSims(testToRun, daysToRun, popSize, -1, True, True, initInfectedPerc, avgRelationships, maxRelationships, avgHouseSize, maxHouseSize)
plotPops(plots[0], popsNoDates, "No dating/visiting outside the house.")


# Run and Plot Scenario 2
pops7Day = runMultipleSims(testToRun, daysToRun, popSize, (5,9), True, True, initInfectedPerc, avgRelationships, maxRelationships, avgHouseSize, maxHouseSize)
plotPops(plots[1], pops7Day, "Outside date every 5-9 days. Isolate if roommate is symptomatic")


# Run and Plot Scenario 3
popsRangeDay = runMultipleSims(testToRun, daysToRun, popSize, (0,7), True, False, initInfectedPerc, avgRelationships, maxRelationships, avgHouseSize, maxHouseSize)
plotPops(plots[2], popsRangeDay, "No time restrictions, No isolating if roommate is symptomatic")
    

# Format and plots
fig.suptitle("Poly Covid Simulator")

for plot in plots.flat:
    plot.set(xlabel='Days', ylabel='Infected%')
    
for plot in plots.flat:
    plot.label_outer()

fig.show()
    
   
   
   
   