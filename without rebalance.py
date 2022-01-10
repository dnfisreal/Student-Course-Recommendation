import pandas as pd 
import sys

'''Read in the data file and eliminate empty columns.'''
def readCSV(fileName):
    fulldataFrame = pd.read_csv(sys.path[0] + "/" + fileName)
    return fulldataFrame.dropna(axis = 1, how = 'all')

dataFrame1 = readCSV("CS student.csv")

'''Read in the student's ID.'''
print("Type the student's ID here and press Enter:")
inputFlag = True
while(inputFlag):
    studentID = int(input())
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

'''Display the courses this student has taken.'''
print("The courses this student has taken are")
if (len(takenCourses) == 1):
    print(takenCourses[0])
else:
    for i in range(len(takenCourses)):
        if (i != len(takenCourses) - 1):
            print(takenCourses[i] + ", ", end = '')
        else:
            print("and " + takenCourses[i] + ".")





def checkPrereq(preReq, courseSet):
    allConditions = preReq.split(";")
    for condition in allConditions:
        flag = False
        allCourses = condition.split("/")
        for oneCourse in allCourses:
            details = oneCourse.split(":")
            course = details[0]
            minGrade = details[1]
            if course in courseSet:
                grade = courseSet[course]
                if (grade <= minGrade):
                    flag = True
                    break
        if not flag:
            return False
    return True


def generateCore(dataFrame, courseSet, unitCount, res, buf):
    coreFrame = dataFrame[dataFrame['Category'] == 'Core']
    coreUnits = 0
    for index, row in coreFrame.iterrows():
        preReq = row['Prerequisite']
        courseNumber = row['Course']
        unit = row['Unit']
        if (preReq == 'None' or checkPrereq(preReq, courseSet)):
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
        

def generateSupple(dataFrame, courseSet, unitCount, res, buf):
    suppleFrame = dataFrame[dataFrame['Category'] == 'Supplementary']
    suppleUnits = 0
    for index, row in suppleFrame.iterrows():
        preReq = row['Prerequisite']
        courseNumber = row['Course']
        unit = row['Unit']
        if (preReq == 'None' or checkPrereq(preReq, courseSet)):
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


def generateGenEd(dataFrame, courseSet, unitCount, res, buf):
    genEdFrame = dataFrame[dataFrame['Category'] == 'General Education']
    genEdUnits = 0
    for index, row in genEdFrame.iterrows():
        preReq = row['Prerequisite']
        courseNumber = row['Course']
        unit = row['Unit']
        if (preReq == 'None' or checkPrereq(preReq, courseSet)):
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
mustTake = dict()

unitCount = generateCore(majorFrame, courseSet, unitCount, coreResult, coreBuffer)
unitCount = generateSupple(majorFrame, courseSet, unitCount, suppleResult, suppleBuffer)
unitCount = generateGenEd(majorFrame, courseSet, unitCount, genEdResult, genEdBuffer)


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
        extendAll(coreRes, suppleRes, genEdRes, res)
        return unitCount

    if (coreLength < 3):
        for (course, unit) in coreBuf:
            if (unitCount + unit <= 54 and totalLength < 5):
                coreRes.append(course)
                unitCount += unit
                totalLength += 1
                if (totalLength == 5):
                    extendAll(coreRes, suppleRes, genEdRes, res)
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
                        extendAll(coreRes, suppleRes, genEdRes, res)
                        return unitCount
    
    extendAll(coreRes, suppleRes, genEdRes, res)
    return unitCount
        
    
finalResult = []
unitCount = balance(unitCount, coreResult, coreBuffer, suppleResult, suppleBuffer, genEdResult, genEdBuffer, finalResult)
print("The recommended courses for this student are:")
print(finalResult)
print("The total units are", unitCount)