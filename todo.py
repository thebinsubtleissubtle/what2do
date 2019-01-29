#!/usr/bin/python3
#!/usr/bin/env python3

import os
import datetime
import enum
from bottle import Bottle, route, run, template, TEMPLATE_PATH, error, redirect, request, static_file
from sqlalchemy import create_engine, Column, Integer, String, Boolean, Sequence, text, DateTime, Enum, __version__
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import pymysql

# globals

app = Bottle()
ENGINE = create_engine("mysql+pymysql://root:1234@localhost/todoapp")
BASE = declarative_base()
ABS_APP_DIR_PATH = os.path.dirname(os.path.realpath(__file__))
ABS_STATIC_FILES_PATH = os.path.join(ABS_APP_DIR_PATH, "static")
if not os.path.exists(ABS_STATIC_FILES_PATH):
	os.makedirs(ABS_STATIC_FILES_PATH)

# sqlalchemy requires 
if __version__ < "0.6.5":
	raise NotImplementedError("Version 0.6.5 or higher of SQLAlchemy is required.")



# database classes

class PriorityEnum(enum.Enum):
	low    = "Low"
	medium = "Medium"
	high   = "High"


class Todo(BASE):
	__tablename__ = "todo"
	id = Column(Integer, primary_key = True)
	task = Column(String(100), nullable = False)
	status = Column(Boolean, nullable = False)
	priority = Column(Enum(PriorityEnum), nullable = False)
	created_at = Column(DateTime, nullable = False)
	updated_at = Column(DateTime, nullable = False)

	def __repr__(self):
		return "TODO id = %s, task = '%s', status = %s, priority = %s" % (self.id, self.task, self.status, self.priority)

BASE.metadata.create_all(ENGINE)
SESSION = sessionmaker(bind = ENGINE)
session = SESSION()
# web interface

@app.route("/")
def root():
	try:
		rows = session.query(Todo.id, Todo.task, Todo.status, str(Todo.priority)).all()
		try:
			return template("index.html", rows = rows, year = datetime.datetime.now().year)
		except:
			redirect("/new")
	except Exception as e:
		session.rollback()
		self.root()


# static files

@app.route("<filename:path>.css")
def load_css(filename):
	return static_file("{}.css".format(filename), root = "static")

@app.route("<filename:path>.js")
def load_js(filename):
	return static_file("{}.js".format(filename), root = "static")

@app.route("<filename:path>.png")
def load_png(filename):
	return static_file("{}.png".format(filename), root = "static")

@app.route("<filename:path>.jpg")
def load_jpg(filename):
	return static_file("{}.jpg".format(filename), root = "static")


# search function
@app.post("/search")
def get_search_results():
	search_task = request.forms.get("search")
	rows = session.query(Todo.id, Todo.task, Todo.status, str(Todo.priority)).filter(Todo.task.like("%" + search_task + "%")).all()
	return template("index.html", rows = rows, year = datetime.datetime.now().year)


# for finished button in table
@app.route("/finished/<id:int>")
def finished_task(id):
	session.query(Todo).filter(Todo.id == id, Todo.status == 0).update({"status": 1, "updated_at": datetime.datetime.now()})
	session.commit()
	redirect("/")

# new task
@app.route("/new")
def new_task():
	return template("new.html", year = datetime.datetime.now().year)

@app.route("/new", method = "POST")
def post_new_task():
	task = request.forms.get("task")
	status = int(request.forms.get("status"))
	priority = request.forms.get("priority")
	print(priority)
	
	new_task = Todo(task = task, status = status, priority = priority, created_at = datetime.datetime.now(), updated_at = datetime.datetime.now())
	session.add(new_task)
	session.commit()
	redirect("/")

# TODO: view tasks
@app.route("/view/<id:int>")
def view_task(id):
	data = session.query(Todo.id, Todo.task, Todo.status, Todo.priority, Todo.created_at, Todo.updated_at).filter(Todo.id == id).one()
	return template("view.html", year = datetime.datetime.now().year)


# edit tasks
@app.route("/edit/<id:int>", method = "GET")
def edit_task(id):
	data = session.query(Todo.id, Todo.task, Todo.status, Todo.priority).filter(Todo.id == id).one()
	return template("edit.html", data = data, year = datetime.datetime.now().year)

@app.route("/edit/<id:int>", method = "POST")
def save_edited_task(id):
	id = request.forms.get("id")
	form_task = request.forms.get("task")
	form_status = int(request.forms.get("status"))
	form_priority = request.forms.get("priority")

	session.query(Todo).filter(Todo.id == id).update({"task": form_task, "status": form_status, "priority": form_priority, "updated_at": datetime.datetime.now()})
	session.commit()
	redirect("/")

# delete tasks
@app.route("/delete/<id:int>")
def delete_data(id):
	to_delete = session.query(Todo).filter(Todo.id == id).one()

	session.delete(to_delete)
	session.commit()
	redirect("/")


@app.error(404)
def error404(error):
	return template("404.html", error = error)

if __name__ == "__main__":
	run(app = app, host = "localhost", port = 6969, debug = True, reloader = True)
