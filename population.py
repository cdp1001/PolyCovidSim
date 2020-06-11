import random
import rand_utils
from person import Person

class Population:
    def __init__(self, peopleCount, datesEveryXDays, isolateIfSick, isolateIfRoomieSick, initialInfectedPerc, avgRelationships, maxRelationships, avgHouseSize, maxHouseSize, debugPrint):
        self.people = []
        self.households = []
        self.initialInfected = 0
        self.count = peopleCount
        self.debugPrint = debugPrint
        self.firstDay125PercInfected = -1
        self.firstDay25PercInfected = -1
        self.firstDay50PercInfected = -1
        self.activeInfectedDaily = []
        self.totalInfectedDaily = []
    
        # Create people
        self.people = self.__createPeople(self.count, datesEveryXDays, isolateIfSick, isolateIfRoomieSick)

        print 'Setting up relationships...'
        
        # Setup Relationships
        self.__setupRelationships(self.people, avgRelationships * self.count, maxRelationships)

        print 'Done setting up relationships, setting up housing...'
                
        # Setup Roommates/Nesting
        self.households = self.__setupHousing(self.people, avgHouseSize, maxHouseSize)
        
        print 'Done setting up housing, looking for random networked group...'
        
        filterTries = 100
        minGroupSize = int(self.count * 0.25)
        self.people = self.__filterNetworkedOnly(self.people, minGroupSize, filterTries)
        self.count = len(self.people)
        
        if self.count < minGroupSize:
            print 'Could not find sufficiently large networked group ({0}) after {1} tries.  Aborting test...'.format(minGroupSize, filterTries) 
            return -1
        
        
        print 'Done finding networked group, new sim pop count is {0}, seeding initial infected...'.format(self.count)
        
        
        self.initialInfected = int(round(self.count * initialInfectedPerc))
        if self.initialInfected < 1: self.initialInfected = 1
              
        for i in range(0, self.initialInfected):
            self.people[i].infectedBy(None)
            
            
        print 'Done seeding initial infected ({0})'.format(self.initialInfected)
        
        
    def runSim(self, totalDays):
        for d in range(0, totalDays):
            activeInfections = 0
            totalInfections = 0
            
            for p in self.people:
                if p.infected:
                    activeInfections += 1
                if p.immune:
                    totalInfections += 1

            self.activeInfectedDaily.append(activeInfections)
            self.totalInfectedDaily.append(totalInfections)
            self.debugPrint('\n--------Day {0} (Active Infections: {1}, Total: {2})---------'.format(d, activeInfections, totalInfections))
            
            if self.firstDay125PercInfected < 0 and totalInfections >= self.count * 0.125:
                self.firstDay125PercInfected = d
            if self.firstDay25PercInfected < 0 and totalInfections >= self.count * 0.25:
                self.firstDay25PercInfected = d
            if self.firstDay50PercInfected < 0 and totalInfections >= self.count * 0.5:
                self.firstDay50PercInfected = d
            
            for p in self.people:
                p.updateDay(d)
        
        
    def __createPeople(self, amount, datesEveryXDays, isolateIfSick, isolateIfRoomieSick):
        people = []
        for x in range(0, amount):
            people.append(Person(datesEveryXDays, isolateIfSick, isolateIfRoomieSick, self.debugPrint))
        return people
        
        
    def __setupRelationships(self, people, totalRelationships, maxRelationshipPerPerson):
        r = 0
        
        while r < totalRelationships:
            p1 = rand_utils.fromList(people)
            p2 = rand_utils.fromList(people)
            
            relPossible = p1.countRelationships() < maxRelationshipPerPerson and p2.countRelationships() < maxRelationshipPerPerson
            
            if p1 != p2 and relPossible:
                r += p1.setupRelationship(p2)
                
                
    def __setupHousing(self, people, avgHouseSize, maxHouseSize):
        r = 0
        totalRoommates = avgHouseSize * len(people)
        households = []
        unhoused = people[:]
        random.shuffle(unhoused)

        while r < totalRoommates and len(unhoused) > 0:
            housesize = rand_utils.expCurveIntRange(1, avgHouseSize, maxHouseSize)
            house = []
            
            for i in range(0, housesize):
                maybeNest = None
                for p in house:
                    for partner in p.relationships:
                        if partner.housed is False:
                            maybeNest = partner
                            break
                    if maybeNest is not None:
                        break
                            
                if maybeNest is not None and rand_utils.chance(0.5):
                    unhoused.remove(maybeNest)
                    maybeNest.housed = True
                    house.append(maybeNest)
                elif len(unhoused) > 0:
                    p = unhoused.pop(0)
                    p.housed = True
                    house.append(p)
                else:
                    break
                    
            for i in range(0, len(house) - 1):
                for j in range(i + 1, len(house)):
                    p1 = house[i]
                    p2 = house[j]
                    r += p1.setupLivingTogether(p2)
                        
            households.append(house)
            
        for p in unhoused:
            households.append([p])
            
        return households
        

    def __filterNetworkedOnly(self, people, minGroupSize, triesBeforeFail):
        networkedGroup = []
        tries = triesBeforeFail
        
        while len(networkedGroup) < minGroupSize: # int(peopleCount * 0.25):
            tries -= 1
            if tries < 0:
                return []
        
            networkedGroup = [rand_utils.fromList(people)]
            
            def filterNetworked(p):
                for p2 in p.relationships + p.nesting + p.roommates:
                    if p2 not in networkedGroup:
                        networkedGroup.append(p2)
                        filterNetworked(p2)
            
            filterNetworked(networkedGroup[0])
            
        return networkedGroup