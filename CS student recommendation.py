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
courseSet = set(takenCourses)

'''Display the courses this student has taken.'''
print("The courses this student has taken are")
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
        for course in allCourses:
            if course in courseSet:
                flag = True
                break
        if not flag:
            return False
    return True


def generateCore(dataFrame, courseSet, res):
    coreFrame = dataFrame[dataFrame['Category'] == 'Core']
    count = 0
    for index, row in coreFrame.iterrows():
        preReq = row['Prerequisite']
        courseNumber = row['Course']
        # unit = row['Unit']
        if (preReq == 'None' or checkPrereq(preReq, courseSet)):
            res.append(courseNumber)
            count += 1
            if count == 3:
                return
        

# def generateSupple(dataFrame, res):
#     suppleFrame = dataFrame[dataFrame['Category'] == 'Supplementary']
#     count = 0
#     for index, row in suppleFrame.iterrows():
#         courseNumber = row['Course']
#         if courseNumber not in courseSet:
#             res.append(courseNumber)
#             count += 1
#             if count == 2:
#                 return

    

dataFrame2 = readCSV("CS catalog.csv")
dataFrame2 = dataFrame2.sort_values(['Department', 'Category', 'Course'])
# dataFrame2 = readCSV("catalog.csv")
majorFrame = dataFrame2[(dataFrame2['Department'] == studentMajor) & (~dataFrame2['Course'].isin(takenCourses))]

# print(dataFrame2)
# print(majorFrame)

unitLimit = 54
unitCount = 0
finalResult = []
generateCore(majorFrame, courseSet, finalResult)
# generateSupple(majorFrame, finalResult)
print(finalResult)


