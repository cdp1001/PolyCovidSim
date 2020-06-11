import random

def expCurveRange(min, mean, max):
    r = 16 * ((random.random()-0.5) ** 5) + 0.5
    if r < 0.5:
        return ((mean - min) * (r * 2)) + min
    else:
        return ((max - mean) * ((r-0.5) * 2)) + mean

        
def expCurveIntRange(min, mean, max):
    return int(round(expCurveRange(min, mean, max)))
    
    
def intRange(min, max):
    return random.randint(min, max)
    
    
def chance(percChance):
    return random.random() < percChance
    

def fromList(list):
    return list[random.randint(0, len(list) - 1)]
    
    
def name():
    const = 'bcdfghjklmnpqrstvwxyz'
    vowel = 'aeiou'
    name = ""
    name += const[random.randint(0, len(const)-1)].upper()
    name += vowel[random.randint(0, len(vowel)-1)]
    name += const[random.randint(0, len(const)-1)]
    name += vowel[random.randint(0, len(vowel)-1)]
    name += const[random.randint(0, len(const)-1)]
    return name