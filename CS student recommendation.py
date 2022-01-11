import pandas as pd 
import sys
import math

'''Read in the data file and eliminate empty columns.'''
def readCSV(fileName):
    fulldataFrame = pd.read_csv(sys.path[0] + "/" + fileName)
    return fulldataFrame.dropna(axis = 1, how = 'all')

dataFrame1 = readCSV("CS student.csv")

'''Read in the student's ID.'''
print("Type the student's ID here and press Enter:")
inputFlag = True
while(inputFlag):
    '''Handle the exception when the input is not an integer'''
    try:
        studentID = int(input())
    except ValueError:
        print("The input value is not an integer! Please retype the student's ID here and press Enter:")
        continue

    '''Look up the courses this student has taken.'''
    infoLine = dataFrame1[dataFrame1['ID'] == studentID]
    if (infoLine.size == 0):
        print("The student's ID is invalid! Please retype the student's ID here and press Enter:")
    else:
        inputFlag = False

courseString = infoLine.iloc[0]['Courses already taken']
studentMajor = infoLine.iloc[0]['Major']
takenCourses = courseString.split(";")
takenCourses.sort()

courseSet = dict()
for course in takenCourses:
    details = course.split(":")
    courseSet[details[0]] = details[1]

def printList(L):
    if (len(L) == 1):
        print(L[0] + '.')
    else:
        for i in range(len(L)):
            if (i != len(L) - 1):
                print(L[i] + ", ", end = '')
            else:
                print("and " + L[i] + '.')

'''Display the courses this student has taken.'''
print()
print("The course(s) this student has taken is/are:")
printList(takenCourses)
print()



def checkPrereq(preReq, courseSet, mustTake):
    allConditions = preReq.split(";")
    for condition in allConditions:
        bit = 0
        allCourses = condition.split("/")
        course = ""
        alreadyIn = False
        for oneCourse in allCourses:
            details = oneCourse.split(":")
            course = details[0]
            minGrade = details[1]
            if course in courseSet:
                grade = courseSet[course]
                if grade <= minGrade:
                    bit = 1
                    break
                else:
                    if (course in mustTake):
                        alreadyIn = True
                    bit = 2
        if (bit == 0):
            return False
        elif (bit == 2):
            if (not alreadyIn):
                mustTake.add(course)
            return False
    return True


def generateCore(dataFrame, courseSet, unitCount, res, buf, mustTake):
    coreFrame = dataFrame[dataFrame['Category'] == 'Core']
    coreUnits = 0
    for index, row in coreFrame.iterrows():
        preReq = row['Prerequisite']
        courseNumber = row['Course']
        unit = row['Unit']
        if (preReq == 'None' or checkPrereq(preReq, courseSet, mustTake)):
            if (coreUnits + unit <= 31):
                unitCount += unit
                coreUnits += unit
                res.append(courseNumber)
                if (len(res) == 3):
                    return unitCount
            else:
                buf.append((courseNumber, unit))
                if (len(buf) == 2):
                    return unitCount
    return unitCount
        

def generateSupple(dataFrame, courseSet, unitCount, res, buf, mustTake):
    suppleFrame = dataFrame[dataFrame['Category'] == 'Supplementary']
    suppleUnits = 0
    for index, row in suppleFrame.iterrows():
        preReq = row['Prerequisite']
        courseNumber = row['Course']
        unit = row['Unit']
        if (preReq == 'None' or checkPrereq(preReq, courseSet, mustTake)):
            if (suppleUnits + unit <= 22):
                unitCount += unit
                suppleUnits += unit
                res.append(courseNumber)
                if (len(res) == 3):
                    return unitCount
            else:
                buf.append((courseNumber, unit))
                return unitCount
    return unitCount


def generateGenEd(dataFrame, courseSet, unitCount, res, buf, mustTake):
    genEdFrame = dataFrame[dataFrame['Category'] == 'General Education']
    genEdUnits = 0
    for index, row in genEdFrame.iterrows():
        preReq = row['Prerequisite']
        courseNumber = row['Course']
        unit = row['Unit']
        if (preReq == 'None' or checkPrereq(preReq, courseSet, mustTake)):
            if (unitCount + unit <= 54 and genEdUnits + unit <= 21):
                unitCount += unit
                genEdUnits += unit
                res.append(courseNumber)
            else:
                buf.append((courseNumber, unit))
                if (len(buf) == 3):
                    return unitCount
    return unitCount


dataFrame2 = readCSV("CS catalog.csv")
dataFrame2 = dataFrame2.sort_values(['Department', 'Category', 'Course'])
majorFrame = dataFrame2[(dataFrame2['Department'] == studentMajor) & (~dataFrame2['Course'].isin(courseSet))]

unitCount = 0
coreResult = []
coreBuffer = []
suppleResult = []
suppleBuffer = []
genEdResult = []
genEdBuffer = []
mustTake = set()

unitCount = generateCore(majorFrame, courseSet, unitCount, coreResult, coreBuffer, mustTake)
unitCount = generateSupple(majorFrame, courseSet, unitCount, suppleResult, suppleBuffer, mustTake)
unitCount = generateGenEd(majorFrame, courseSet, unitCount, genEdResult, genEdBuffer, mustTake)


def extendAll(coreRes, suppleRes, genEdRes, res):
    res.extend(coreRes)
    res.extend(suppleRes)
    res.extend(genEdRes)

def balance(unitCount, coreRes, coreBuf, suppleRes, suppleBuf, genEdRes, genEdBuf, res):
    coreLength = len(coreRes)
    suppleLength = len(suppleRes)
    genEdLength = len(genEdRes)
    totalLength = coreLength + suppleLength + genEdLength
    if (totalLength == 5):
        return unitCount

    if (coreLength < 3):
        for (course, unit) in coreBuf:
            if (unitCount + unit <= 54 and totalLength < 5):
                coreRes.append(course)
                unitCount += unit
                totalLength += 1
                if (totalLength == 5):
                    return unitCount
                if (len(coreRes) == 3):
                    break
        
    if (totalLength < 5): 
        if (len(suppleBuf) == 1):
            (course, unit) = suppleBuf[0]
            if (unitCount + unit <= 54 and totalLength < 5):
                suppleRes.append(course)
                unitCount += unit
                totalLength += 1

        if (totalLength <= 4):
            for (course, unit) in genEdBuf:
                if (unitCount + unit <= 54 and totalLength < 5):
                    genEdRes.append(course)
                    unitCount += unit
                    totalLength += 1
                    if (totalLength == 5):
                        return unitCount
    
    return unitCount

def deleteFromCertain(dataFrame, unitCount, res):
    deleteCourse = res[len(res) - 1]
    courseLine = dataFrame[dataFrame['Course'] == deleteCourse]
    unit = courseLine.iloc[0]['Unit']
    unitCount -= unit
    res.remove(deleteCourse)
    return unitCount

def deleteOneCourse(dataFrame, unitCount, firstRes, secondRes, thirdRes):
    if (len(firstRes) != 0):
        unitCount = deleteFromCertain(dataFrame, unitCount, firstRes)
        return unitCount
    
    if (len(secondRes) != 0):
        unitCount = deleteFromCertain(dataFrame, unitCount, secondRes)
        return unitCount

    if (len(thirdRes) != 0):
        unitCount = deleteFromCertain(dataFrame, unitCount, thirdRes)
        return unitCount

def dealCore(dataFrame, unitCount, coreRes, suppleRes, genEdRes, currentUnit, flag):
    if (len(coreRes) != 0):
        newUnit = 0
        for coreCourse in coreRes:
            newCourseLine = dataFrame[dataFrame['Course'] == coreCourse]
            newUnit = newCourseLine.iloc[0]['Unit']
            if (unitCount - newUnit + currentUnit <= 54):
                coreRes.remove(coreCourse)
                unitCount = unitCount - newUnit + currentUnit
                flag = True
                break
        if not flag:
            lastCourse = coreRes[len(coreRes) - 1]
            coreRes.remove(lastCourse)
            unitCount = unitCount - newUnit + currentUnit
            unitCount = deleteOneCourse(dataFrame, unitCount, genEdRes, suppleRes, coreRes)
    else:
        if (unitCount + currentUnit > 54):
            unitCount = deleteOneCourse(dataFrame, unitCount, genEdRes, suppleRes, coreRes)
            if (unitCount + currentUnit > 54):
                unitCount = deleteOneCourse(dataFrame, unitCount, genEdRes, coreRes, suppleRes)
        unitCount += currentUnit
    return unitCount

def dealSupple(dataFrame, unitCount, coreRes, suppleRes, genEdRes, currentUnit, flag):
    if (len(suppleRes) != 0):
        newUnit = 0
        for suppleCourse in suppleRes:
            newCourseLine = dataFrame[dataFrame['Course'] == suppleCourse]
            newUnit = newCourseLine.iloc[0]['Unit']
            if (unitCount - newUnit + currentUnit <= 54):
                suppleRes.remove(suppleCourse)
                unitCount = unitCount - newUnit + currentUnit
                flag = True
                break
        if not flag:
            lastCourse = suppleRes[len(suppleRes) - 1]
            suppleRes.remove(lastCourse)
            unitCount = unitCount - newUnit + currentUnit
            unitCount = deleteOneCourse(dataFrame, unitCount, genEdRes, suppleRes, coreRes)
    else:
        if (unitCount + currentUnit > 54):
            unitCount = deleteOneCourse(dataFrame, unitCount, genEdRes, coreRes, suppleRes)
            if (unitCount + currentUnit > 54):
                unitCount = deleteOneCourse(dataFrame, unitCount, genEdRes, coreRes, suppleRes)
        unitCount += currentUnit
    return unitCount

def dealGenEd(dataFrame, unitCount, coreRes, suppleRes, genEdRes, currentUnit, flag):
    if (len(genEdRes) != 0):
        newUnit = 0
        for genEdCourse in genEdRes:
            newCourseLine = dataFrame[dataFrame['Course'] == genEdCourse]
            newUnit = newCourseLine.iloc[0]['Unit']
            if (unitCount - newUnit + currentUnit <= 54):
                genEdRes.remove(genEdCourse)
                unitCount = unitCount - newUnit + currentUnit
                flag = True
                break
        if not flag:
            lastCourse = genEdRes[len(genEdRes) - 1]
            genEdRes.remove(lastCourse)
            unitCount = unitCount - newUnit + currentUnit
            unitCount = deleteOneCourse(dataFrame, unitCount, genEdRes, suppleRes, coreRes)
    else:
        if (unitCount + currentUnit > 54):
            unitCount = deleteOneCourse(dataFrame, unitCount, suppleRes, coreRes, genEdRes)
            if (unitCount + currentUnit > 54):
                unitCount = deleteOneCourse(dataFrame, unitCount, suppleRes, coreRes, genEdRes)
        unitCount += currentUnit
    return unitCount

def rebalance(dataFrame, unitCount, mustTake, coreRes, suppleRes, genEdRes):
    for course in mustTake:
        courseLine = dataFrame[dataFrame['Course'] == course]
        category = courseLine.iloc[0]['Category']
        currentUnit = courseLine.iloc[0]['Unit']
        flag = False

        if (unitCount + currentUnit <= 54):
            unitCount += currentUnit
            continue

        if (category == "Core"):
            unitCount = dealCore(dataFrame, unitCount, coreRes, suppleRes, genEdRes, currentUnit, flag)
                 
        elif (category == 'Supplementary'):
            unitCount = dealSupple(dataFrame, unitCount, coreRes, suppleRes, genEdRes, currentUnit, flag)

        else:
            unitCount = dealGenEd(dataFrame, unitCount, coreRes, suppleRes, genEdRes, currentUnit, flag)
    
    return unitCount

        
finalResult = []
unitCount = balance(unitCount, coreResult, coreBuffer, suppleResult, suppleBuffer, genEdResult, genEdBuffer, finalResult)

if len(mustTake) > 0:
    newDataFrame = dataFrame2[dataFrame2['Department'] == studentMajor]
    countDataFrame = newDataFrame[newDataFrame['Course'].isin(courseSet)]
    unitCount = rebalance(newDataFrame, unitCount, mustTake, coreResult, suppleResult, genEdResult)
    print("You must retake the following course(s) in order to satisfy prerequisites of other courses:")
    for course in mustTake:
        print(course + " ", end = '')
    print()
    print()
    print("The rest of the recommended course(s) for this student is/are:")

else:
    print("The recommended course(s) for this student is/are:")

extendAll(coreResult, suppleResult, genEdResult, finalResult)
printList(finalResult)
print()
print("The total units are", str(unitCount) + ".")
print()



coreFrame = majorFrame[majorFrame['Category'] == 'Core'] 
suppleFrame = majorFrame[majorFrame['Category'] == 'Supplementary'] 
genEdFrame = majorFrame[majorFrame['Category'] == 'General Education'] 
coreCount = len(coreFrame.index)
suppleCount = len(suppleFrame.index)
genEdCount = len(genEdFrame)
totalCount = coreCount + suppleCount + genEdCount


for course in mustTake:
    courseLine = countDataFrame[countDataFrame['Course'] == course]
    category = courseLine.iloc[0]['Category']
    if (category == 'Core'):
        coreCount += 1
        totalCount += 1
    elif (category == 'Supplementary'):
        suppleCount += 1
        totalCount += 1
    else:
        genEdCount += 1
        totalCount += 1

def estimate(core, supple, genEd, total):
    totalCount = math.ceil(total / 4.5)
    maxLimit = math.ceil(total / 4)
    
    coreCount = math.ceil(core / 2.5)
    coreLeast = math.ceil(core / 3)
    suppleCount = supple
    genEdCount = math.ceil(genEd / 2)

    finalCount = max(coreLeast, min(maxLimit, max(totalCount, coreCount, suppleCount, genEdCount)))
    return finalCount

    
semesterCount = estimate(coreCount, suppleCount, genEdCount, totalCount)
print("It is estimated that this student can graduate in " + str(semesterCount) + " semester(s).")
print()