import rand_utils


# Infection Settings
daysUntilSymptomaticLow = 2
daysUntilSymptomaticMid = 5
daysUntilSymptomaticHigh = 10
infectiousStartDayLow = 2
infectiousStartDayMid = 3
infectiousStartDayHigh = 5
infectiousEndDayLow = 10
infectiousEndDayMid = 12
infectiousEndDayHigh = 15
infectionLengthLow = 12
infectionLengthMid = 15
infectionLengthHigh = 17
chanceOfShowingSymptoms = 0.5

oRelDatesEveryXDays = 7
chanceOfTransmissionOnDate = 0.9
chanceOfTransmissionFromDatesRoommates = 0.1 # Assumes social distancing
chanceOfTransmissionToDatesRoommates = 0.1 # Assumes social distancing
chanceOfTransmissionToDatesNesting = 0.2 # Assumes social distancing

chanceOfAsymRoomieToInfect = 0.5
chanceOfSymRoomieToInfect = 0.25
chanceOfAsymNestToInfect = 0.9
chanceOfSymNestToInfect = 0.45
chanceOfOutsideExposure = 9000 / 40000000 #Based on est. 9000 new cases per day per 40 million people (Roughly estimated rate in CA)
changeOfTransmittingToGenPopAsym = 0.02 #0.02
changeOfTransmittingToGenPopSym = 0.01 #0.01



class InfectionManager:

    def __init__(self, debugPrint):
        self.debugPrint = debugPrint
        
        self.infected = False
        self.symptomatic = False
        self.infectious = False
        self.immune = False
        
        self.infectedDay = 0
        self.rValue = 0
        self.infectedGenPop = 0
        self.infectedByGenPop = False
        
        self.symptomaticDay = rand_utils.expCurveIntRange(daysUntilSymptomaticLow, daysUntilSymptomaticMid, daysUntilSymptomaticHigh)
        self.infectiousStartDay = rand_utils.expCurveIntRange(infectiousStartDayLow, infectiousStartDayMid, infectiousStartDayHigh)
        self.infectiousEndDay = rand_utils.expCurveIntRange(infectiousEndDayLow, infectiousEndDayMid, infectiousEndDayHigh)
        self.infectionLength = rand_utils.expCurveIntRange(infectionLengthLow, infectionLengthMid, infectionLengthHigh)
        self.willShowSymptoms = rand_utils.chance(chanceOfShowingSymptoms)
        
        
    def infectedBy(self, source):
        if self.immune == False:
            self.infected = True
            self.immune = True
            self.infectedDay = 0
            
            if source is not None:
                source.rValue += 1
            else:
                self.infectedByGenPop = True
            
            return True
        else:
            return False
            
    
    def infectGenPop(self):
        self.rValue += 1
        self.infectedGenPop += 1
        
        
    def updateDay(self, day, person):
        if self.infected:
            self.infectedDay += 1
            self.infectious = self.infectedDay >= self.infectiousStartDay and self.infectedDay <= self.infectiousEndDay
            
            prevSym = self.symptomatic
            
            self.symptomatic = self.willShowSymptoms and self.infectedDay >= self.symptomaticDay
            
            if not prevSym and self.symptomatic:
                self.debugPrint('{0} is infected and started showing symptoms'.format(person))
            
            if self.infectedDay >= self.infectionLength:
                self.infected = False
                self.infectious = False
                self.symptomatic = False
                
                if prevSym:
                    self.debugPrint('{0} was symptomatic but has now gotten over the virus'.format(person))
        


class Person:
    def __init__(self, datesEveryXDays, isolateIfSick, isolateIfRoomieSick, debugPrint):
        
        self.debugPrint = debugPrint
        
        self.name = rand_utils.name()
        
        self.isolateIfSick = isolateIfSick
        self.isolateIfRoomieSick = isolateIfRoomieSick
        self.roommates = []
        self.nesting = []
        self.relationships = []
        self.housed = False
        
        self.infection = InfectionManager(debugPrint)
        
        if isinstance(datesEveryXDays, list) or isinstance(datesEveryXDays, tuple):
            self.datesEveryXDaysMin = datesEveryXDays[0]
            self.datesEveryXDaysMax = datesEveryXDays[1]
        else:
            self.datesEveryXDaysMin = datesEveryXDays
            self.datesEveryXDaysMax = datesEveryXDays
            
        if self.datesEveryXDaysMax >= 0:
            self.nextORelDate = rand_utils.intRange(0, self.datesEveryXDaysMax)
        else:
            self.nextORelDate = 100000
            
        self.nextORelToDateIndex = 0
        
        
    def __str__(self):
        return '{0}({1})'.format(self.name, self.printInfectionCode())
        
        
    def printRelationshipsAndLiving(self):
        rm_names = [x.name for x in self.roommates]
        n_names = [x.name for x in self.nesting]
        r_names = [x.name for x in self.relationships]
        return '{0}:\n  Roommates: {1}\n  Nesting: {2}\n  Relationships: {3}'.format(self.name, rm_names, n_names, r_names)
        
        
    def printInfectionCode(self):
        code = ""
        if self.infected: code += "I"
        if self.symptomatic: code += "S"
        return code
        
    def printRelationships(self):
        n_names = [x.name for x in self.nesting]        
        r_names = [x.name for x in self.relationships]
        return '{0}({1}): {2}, [{3}]'.format( self.name
                                       , self.printInfectionCode()
                                       , ', '.join(r_names)
                                       , ', '.join(n_names))
        
        
    def setupLivingTogether(self, person):
        if self.liveTogether(person) == False:
            if (self.inRelationship(person)):
                self.nesting.append(person)
                person.nesting.append(self)
                
                self.relationships.remove(person)
                person.relationships.remove(self)
            else:
                self.roommates.append(person)
                person.roommates.append(self)
            return 2
        else:
            return 0
        
        
    def setupRelationship(self, person):
        if self.inRelationship(person) == False:
            self.relationships.append(person)
            person.relationships.append(self)
            return 2
        else:
            return 0
        
        
    def inRelationship(self, person):
        return person in self.relationships or person in self.nesting
        
        
    def liveTogether(self, person):
        return person in self.roommates or person in self.nesting
        
        
    def countOutsideRelationships(self):
        return len(self.relationships)
        
        
    def countRelationships(self):
        return len(self.relationships) + len(self.nesting)
        
        
    def countRoomieAndNests(self):
        return len(self.roommates) + len(self.nesting)
            
    @property
    def rValue(self):
        return self.infection.rValue
            
    @property    
    def infectedGenPop(self):
        return self.infection.infectedGenPop
            
    @property    
    def infectedByGenPop(self):
        return self.infection.infectedByGenPop
            
    @property    
    def infected(self):
        return self.infection.infected
            
    @property    
    def infectious(self):
        return self.infection.infectious
            
    @property    
    def immune(self):
        return self.infection.immune
            
    @property    
    def symptomatic(self):
        return self.infection.symptomatic
            
            
    def countInfectiousHousemates(self):
        roomiesAndNests = self.roommates + self.nesting
        count = 0
        for p in roomiesAndNests:
            if p.infectious:
                count += 1
        return count
        
        
    def infectedBy(self, source):
        return self.infection.infectedBy(source)
            
            
    def infectGenPop(self):
        return self.infection.infectGenPop()
            
            
    def goOnDate(self, person):
        if self.infectious and not person.immune:
            if rand_utils.chance(chanceOfTransmissionOnDate):
                person.infectedBy(self)
                self.debugPrint('{0} infected {1} on their date'.format(self, person))
                
        elif person.infectious and not self.immune:
            if rand_utils.chance(chanceOfTransmissionOnDate):
                self.infectedBy(person)
                self.debugPrint('{0} infected {1} on their date'.format(person, self))
        
        outcome = rand_utils.fromList([0,1,2])
        if outcome == 0:
            # Date at house
            self.__maybeAffectHousematesOnDate(person, self)
        elif outcome == 1:
            # Date at partners house
            self.__maybeAffectHousematesOnDate(self, person)
        else:
            # Date outside of the house
            None
                
                
    def __maybeAffectHousematesOnDate(self, visitor, resident):
        if not visitor.immune:
            for housemate in (resident.roommates + resident.nesting):
                if housemate.infectious and rand_utils.chance(chanceOfTransmissionFromDatesRoommates):
                    visitor.infectedBy(housemate)
                    self.debugPrint('{0} was infected a housemate of {1} on their date ({2})'.format(visitor, resident, housemate))
        if visitor.infectious:
            for housemate in resident.roommates:
                if rand_utils.chance(chanceOfTransmissionToDatesRoommates):
                    housemate.infectedBy(visitor)
                    self.debugPrint('{0} infected a housemate of {1} on their date ({2})'.format(visitor, resident, housemate))
            for np in resident.nesting:
                if rand_utils.chance(chanceOfTransmissionToDatesRoommates):
                    np.infectedBy(visitor)
                    self.debugPrint('{0} infected a nesting partner of {1} on their date ({2})'.format(visitor, resident, np))
        
    def canGoOnDate(self):
        if (self.symptomatic and self.isolateIfSick) or self.datesEveryXDaysMax < 0:
            return False
        elif self.isolateIfRoomieSick:
            roomiesAndNests = self.roommates + self.nesting
            for p in roomiesAndNests:
                if p.symptomatic:
                    return False
            return True
        else:
            return True
                
                
    def getIndexOfPartnerThatCanDate(self, day):
        for i in range(0, len(self.relationships)):
            index = (i + self.nextORelToDateIndex) % len(self.relationships)
            partner = self.relationships[index]
            if partner.nextORelDate <= day and partner.canGoOnDate():
                return index
        return -1
            
            
    def updateDay(self, day):
        self.infection.updateDay(day, self)
        
        if self.countOutsideRelationships() > 0:
            if self.nextORelDate <= day and self.canGoOnDate():
                pId = self.getIndexOfPartnerThatCanDate(day)
                
                if pId >= 0:
                    partner = self.relationships[pId]
                    self.nextORelToDateIndex = (pId + 1) % len(self.relationships)
                
                    self.goOnDate(partner)
                    
                    self.nextORelDate = day + rand_utils.intRange(self.datesEveryXDaysMin, self.datesEveryXDaysMax)
                    partner.nextORelDate = day + rand_utils.intRange(partner.datesEveryXDaysMin, partner.datesEveryXDaysMax)
        
        if not self.immune:
            # Maybe infected by nesting partner
            for p in self.nesting:
                 if p.infectious:
                    if p.symptomatic and rand_utils.chance(chanceOfSymNestToInfect):
                        self.infectedBy(p)
                        self.debugPrint('{0} was infected by a symptomatic nesting partner ({1})'.format(self, p))
                    elif not p.symptomatic and rand_utils.chance(chanceOfAsymNestToInfect):
                        self.infectedBy(p)
                        self.debugPrint('{0} was infected by an asymptomatic nesting partner ({1})'.format(self, p))
            
            # Maybe infected by roommate
            for p in self.roommates:
                 if p.infectious:
                    if p.symptomatic and rand_utils.chance(chanceOfSymRoomieToInfect):
                        self.infectedBy(p)
                        self.debugPrint('{0} was infected by a symptomatic roommate ({1})'.format(self, p))
                    elif not p.symptomatic and rand_utils.chance(chanceOfAsymRoomieToInfect):
                        self.infectedBy(p)
                        self.debugPrint('{0} was infected by an asymptomatic roommate ({1})'.format(self, p))
            
            # Maybe infected randomly
            if rand_utils.chance(chanceOfOutsideExposure):
                self.infectedBy(None)
                self.debugPrint('{0} was infected by someone in the general population'.format(self))
                
        if self.infectious:
            if self.symptomatic and rand_utils.chance(changeOfTransmittingToGenPopSym):
                self.debugPrint('{0} was symptomatic and infected someone in the general pop'.format(self))
                self.infectGenPop()
            if not self.symptomatic and rand_utils.chance(changeOfTransmittingToGenPopAsym):
                self.debugPrint('{0} was asymptomatic and infected someone in the general pop'.format(self))
                self.infectGenPop()