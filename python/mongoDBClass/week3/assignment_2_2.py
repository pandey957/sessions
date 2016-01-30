import pymongo
import datetime
import sys
connection = pymongo.MongoClient("mongodb://localhost")
db=connection.school
student = db.student
student_id = None	
#test =  grades.find(filter= {'type':'homework'},sort=[('student_id',1),('score',1)])
student_c = student.find()
for current_student in student_c:
  current_score = current_student['scores']
  new_score = current_score[:2]
  new_score.append(sorted(current_score[2:])[-1])
  current_student['scores'] = new_score[:]
  print current_student['_id']
  student.find_one_and_update({'_id': current_student['_id']},{'$set': {'scores': new_score}})
  
