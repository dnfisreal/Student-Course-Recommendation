# Student-Course-Recommendation
A student management system that can provide course recommendations for students

Given a csv of students’ data, including students’ IDs, names, majors, 
and taken courses, and a csv of course catalog, including courses’ numbers, 
units, departments, categories, and prerequisites, when you type in 
a valid student ID, this system can output the courses that this student 
has already taken, the recommended courses, the total number of units, 
and roughly how soon this student can graduate.

To store data, the system uses DataFrame and Series data structures 
from Pandas library. 

Since there are three categories: Core, Supplementary, and General Education, 
in order for the taken courses to be balanced, the system finds out 
recommended courses for each category and then do necessary adjustments. 
Specifically, the system uses a necessary and an optional course list 
for each category. After generating those two lists for every category, 
the system will first combine all the necessary lists. If there are 
still available units, the system then loops through each optional 
course list to add more courses. As a result, it doesn’t need to do a search 
in the catalog again. 

To find a suitable recommended course, the system first checks if 
its prerequisites have been satisfied. If the student doesn’t meet 
one prerequisite due to grade, the system is guaranteed to output this course 
in the recommended courses and will tell this student to retake this course. 
Note that in all cases, the system will ensure that the total unit 
of the recommended courses is under the maximum unit limit. 

Last, the system will give an approximate estimation on 
how many semesters this student can graduate in.  
