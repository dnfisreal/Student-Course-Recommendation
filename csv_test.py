import pandas as pd 
import sys

oridataFrame = pd.read_csv(sys.path[0] + "/CS student.csv")
dataFrame = oridataFrame.dropna(axis = 1, how = 'all')

print("Type the student's ID here and press Enter")
studentID = int(input())
res = dataFrame[dataFrame['ID'] == studentID]
courseString = res.iloc[0]['Courses already taken']
newCS = courseString.split(";")
newCS.sort()

print("The courses this student has taken are")
for i in range(len(newCS)):
    if (i != len(newCS) - 1):
        print(newCS[i] + ", ", end = '')
    else:
        print("and " + newCS[i] + ".")

courseSet = set(newCS)

# print(courseSet)