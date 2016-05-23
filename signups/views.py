from django.shortcuts import render_to_response, render
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib import auth
from django.core.context_processors import csrf
from forms import MyRegistrationForm
from django.contrib.formtools.wizard.views import SessionWizardView
from django.template import RequestContext

import sys
import MySQLdb
from mysql.connector import FieldType
from pymongo import MongoClient

import os
import subprocess

from django.core.urlresolvers import reverse
from django.utils import simplejson as json

# Create your views here.
# Basic User management operations

def login(request):
    c = {}
    c.update(csrf(request))    
    return render_to_response('login.html', c)

def auth_view(request):
    username = request.POST.get('username', '')
    password = request.POST.get('password', '')
    user = auth.authenticate(username=username, password=password)
    
    if user is not None:
        auth.login(request, user)
        return HttpResponseRedirect('/accounts/loggedin')
    else:
        return HttpResponseRedirect('/accounts/invalid')
    
def loggedin(request):
	return render_to_response('loggedin.html',context_instance=RequestContext(request))

def invalid_login(request):
    c = {}
    c.update(csrf(request))
    return render_to_response('invalid_login.html',c)

def logout(request):
    auth.logout(request)
    c = {}
    c.update(csrf(request))
    return render_to_response('logout.html',c)

def register_user(request):
    if request.method == 'POST':
        form = MyRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/accounts/register_success')
        
    else:
        form = MyRegistrationForm()
    args = {}
    args.update(csrf(request))
    
    args['form'] = form
    
    return render_to_response('register.html', args)

def register_success(request):
    c = {}
    c.update(csrf(request))
    return render_to_response('register_success.html',c)

# Extract data from SQL database and transform it into the target No-SQL (MongoDB)
def convert(request):
    # Mongo datbase connection
    client = MongoClient('localhost', 27017)
    dbname = request.POST['d_name']
    username = request.POST['u_name']
    password = request.POST['password']    
    passer = {}
    passer1 = {}
    ctable = []
    t_name = []
    table = []
    no_row = []
    dtype = []
    # Open database connection
    try:
        # db = MySQLdb.connect("localhost","root","root","test1")
    	mdb = client[dbname]
    	db = MySQLdb.connect("localhost",username,password,dbname )
	    # prepare a cursor object using cursor() method
	cursor = MySQLdb.cursors.SSCursor(db)
	#cursor = db.cursor()
	    # Prepare SQL query to INSERT a record into the database.
	sql = "show tables"
	try:
	       # Execute the SQL command
	       cursor.execute(sql)
	       table_counter = 0 
	       tables = cursor.fetchall()
	       for row in tables:
	       	   table = []
	       	   dtype = []
	           tname = row[0]
	           table_counter = table_counter+1
	           t_name.insert(table_counter,tname)
	           
	           # Prepare SQL query to INSERT a record into the database.
	    	   sql = "SELECT * FROM {}".format(tname)
	    	   collection = mdb[tname]

	    	   # Execute the SQL command
	    	   cursor.execute(sql)
	    	   col=[]
	    	   j=0
	    	   print "**************Schema*************************\n"
	    	   for i in range(len(cursor.description)):
		       print("Column {}:".format(i+1))
		       #--passer['len_{}'.format(tname)]=len(cursor.description)
		       desc = cursor.description[i]
		       col.insert(j,desc[0])
		       dtype.insert(j,FieldType.get_info(desc[1]))
		       j=j+1
	       	       print("  column_name = {}".format(desc[0]))
		       print("  type = {} ({})".format(desc[1], FieldType.get_info(desc[1])))

		   # Fetch all the rows in a list of lists.
		   table.insert(0,col)
		   table.insert(1,dtype)
	           #passer["col_name_{}".format(table_counter)]=col
	           rows = cursor.fetchone()
	           print "**************CONVERTING*************************\n"
	           counter=0
	    	   while rows is not None:
	             # Now print fetched result
	             data = {}
	      	     for c in range(len(cursor.description)):
	      	     	if type(rows[c]) is str:
	      	     		temp = unicode(rows[c], errors='replace')
	      	     		data[col[c]] = temp
	      	     	else:
						data[col[c]] = rows[c]
	             collection.insert(data)
	             counter=counter+1;
	             sys.stdout.write("\r%d / %d CONVERTED" % (counter, len(rows)))
	             no_row.insert(table_counter,counter)
	             sys.stdout.flush()
	             rows = cursor.fetchone()	
	           table.insert(2,counter)
	           ctable.insert(table_counter,table)
	           print " "

	        # disconnect from server
	       db.close()
	       passer1['flag']='true'
	       passer1['data']=ctable
	       passer1['t_name']=t_name
	       passer1['no_tables']=table_counter
	       return HttpResponse(json.dumps(passer1), mimetype='application/javascript') 
	except Exception, e:
		passer1['flag']='table fault'
		print e
		return HttpResponse(json.dumps(passer1), mimetype='application/javascript') 
    except Exception, e:
    	passer1['flag']='database fault'
    	return HttpResponse(json.dumps(passer1), mimetype='application/javascript') 

# Retrieve Tables from the SQL database
def get_tables(request):
	dbname = request.POST['d_name']
	username = request.POST['u_name']
	password = request.POST['password']
	result_table = {}
	try:
		db = MySQLdb.connect("localhost",username,password,dbname )
		cursor = MySQLdb.cursors.SSCursor(db)
		sql = "show tables"
		cursor.execute(sql)
		tables = cursor.fetchall()
		result_table['flag']='true'
		result_table['tables']=tables
		return HttpResponse(json.dumps(result_table), mimetype='application/javascript')
	except Exception, e:
		result_table['flag']='table fault'
		print e
		return HttpResponse(json.dumps(result_table), mimetype='application/javascript')

# Get the schema of tables selected by user
def get_schema(request):
	tables = []
	dbname = request.POST['d_name']
	username = request.POST['u_name']
	password = request.POST['password']
	tables = request.POST.getlist('tables[]')
	result_schema = {}
	data_array = []
	data = []
	# Open database connection
	try:
		db = MySQLdb.connect("localhost",username,password,dbname)
		# db = MySQLdb.connect("localhost",username,password,dbname )
		j = 0
		for row in tables:
			# prepare a cursor object using cursor() method
			cursor = MySQLdb.cursors.SSCursor(db)
			data = []
			# Prepare SQL query to INSERT a record into the database.
			# print "11fsalkhfslkhdflkshdflkhalkhfdlkashlkdh"
			sql = "SELECT * FROM {}".format(row)
			# Execute the SQL command
			cursor.execute(sql)
			# print cursor.description
			for i in range(len(cursor.description)):
				desc = cursor.description[i]
				data.insert(i,desc[0]+'('+FieldType.get_info(desc[1])+')')
				# print data
			# print "data: "
			# print data_array		
			data_array.insert(j,data)
			j = j + 1
		result_schema['schema'] = data_array
		result_schema['flag'] = 'true'
		return HttpResponse(json.dumps(result_schema), mimetype='application/javascript')
	except Exception, e:
		result_schema['flag']='table fault'
		print e
		return HttpResponse(json.dumps(result_schema), mimetype='application/javascript')

# Get certain rows from the SQL database by using the query created by user
def get_data(request):
	dbname = request.POST['d_name']
	username = request.POST['u_name']
	password = request.POST['password']
	query = request.POST['query']
	result_data = {}
	schema_array = []
	data_array = []
	data = []
	# Open database connection
	try:
#		db = MySQLdb.connect("localhost","root","root","test1")
		 db = MySQLdb.connect("localhost",username,password,dbname )
		j = 0
		# prepare a cursor object using cursor() method
		cursor = MySQLdb.cursors.SSCursor(db)
		data = []
		
		# Execute the SQL command
		cursor.execute(query)
		print cursor.description
		for i in range(len(cursor.description)):
			desc = cursor.description[i]
			data.insert(i,desc[0]+'('+FieldType.get_info(desc[1])+')')
			# print data
		print "data: "
		print data		
		schema_array.insert(j,data)
		print "s_data: "
		print schema_array	

		rows = cursor.fetchone()
		counter = 0
		while rows is not None:
			data = []
			for c in range(len(cursor.description)):
				if type(rows[c]) is str:
					temp = unicode(rows[c], errors='replace')
					data.insert(c,temp)
				else:
					data.insert(c,rows[c])					
			data_array.insert(counter,data)
			counter = counter + 1
			rows = cursor.fetchone()

		result_data['data'] = data_array
		result_data['schema'] = schema_array
		result_data['flag'] = 'true'
		return HttpResponse(json.dumps(result_data), mimetype='application/javascript')
	except Exception, e:
		result_data['flag']='table fault'
		print e
		return HttpResponse(json.dumps(result_data), mimetype='application/javascript')

# Convert just the tables selected by user
def tconvert(request):
    # Mongo datbase connection
    client = MongoClient('localhost', 27017)
    dbname = request.POST['d_name']
    username = request.POST['u_name']
    password = request.POST['password']
    sql = request.POST['query']   
    ntable = '' 
    passer = {}
    passer1 = {}
    ctable = []
    t_name = []
    table = []
    no_row = []
    dtype = []
    # Open database connection
    try:
#    	db = MySQLdb.connect("localhost","root","root","test1")
    	mdb = client[dbname]
    	 db = MySQLdb.connect("localhost",username,password,dbname )
    	cursor = MySQLdb.cursors.SSCursor(db)
    	# sql = "SELECT * FROM {}".format(ptable)
    	print sql
    	table_counter = 1 
    	start = sql.lower().find('from') + 5
    	end = sql.lower().find(' ', start)
    	ntable = sql[start:end]
    	while (sql[0] is not ' '):
    		# ntable = ntable + sql[i]
		print ntable
		t_name.insert(table_counter,ntable)
		collection = mdb[ntable]

		# Execute the SQL command
		cursor.execute(sql)
		col=[]
		j=0
		print "**************Schema*************************\n"
		for i in range(len(cursor.description)):
			print("Column {}:".format(i+1))
			desc = cursor.description[i]
			col.insert(j,desc[0])
			dtype.insert(j,FieldType.get_info(desc[1]))
			j=j+1
			print("  column_name = {}".format(desc[0]))
			print("  type = {} ({})".format(desc[1], FieldType.get_info(desc[1])))

		# Fetch all the rows in a list of lists.
		table.insert(0,col)
		table.insert(1,dtype)
		rows = cursor.fetchone()
		print "**************CONVERTING*************************\n"
		counter=0
		while rows is not None:
			data = {}
			for c in range(len(cursor.description)):
				if type(rows[c]) is str:
					temp = unicode(rows[c], errors='replace')
		     		data[col[c]] = temp
		     	else:
		     		data[col[c]] = rows[c]
			collection.insert(data)
			counter=counter+1;
			sys.stdout.write("\r%d / %d CONVERTED" % (counter, len(rows)))
			rows = cursor.fetchone()
			# no_row.insert(table_counter,counter)
			sys.stdout.flush()				
		table.insert(2,counter)
		ctable.insert(table_counter,table)
		print " "

		# disconnect from server
		db.close()
		passer1['flag']='true'
		passer1['data']=ctable
		passer1['t_name']=t_name
		passer1['no_tables']=table_counter
		return HttpResponse(json.dumps(passer1), mimetype='application/javascript')

    except Exception, e:
    	passer1['flag']='database fault'
    	print e
    	return HttpResponse(json.dumps(passer1), mimetype='application/javascript') 

# Provide a ZIP file to user of the data transformed into MongoDB
def send_zipfile(request):
    dbname = request.POST['d_name']
    dbname = 'test1'    
    subprocess.call(['mongodump','-d',dbname,'--dbpath','/home/gaurav/example','-o','/home/gaurav/export_backup/'+dbname+'.json'])
    subprocess.call(['zip','-r','/home/gaurav/x.zip','/home/gaurav/export_backup/'+dbname+'.json/'])
    # (output, err) = p.communicate()
    return response
