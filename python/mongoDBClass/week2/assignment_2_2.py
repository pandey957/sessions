import pymongo
import datetime
import sys
connection = pymongo.MongoClient("mongodb://localhost")
db=connection.students
grades = db.grades
student_id = None	
test =  grades.find(filter= {'type':'homework'},sort=[('student_id',1),('score',1)])
for scores in test:
	if student_id == scores['student_id']: pass
	else: 
		student_id = scores['student_id']
		grades.delete_one({'_id':scores['_id']})
