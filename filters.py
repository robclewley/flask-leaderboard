from app import app
from models import User, Task, Entry, Upvote, Downvote

@app.template_filter('get_user_name')
def get_user_name(id):
	return User.query.filter(User.id == id).first().name

@app.template_filter('get_task_title')
def get_task_title(id):
	return Task.query.filter(Task.id == id).first().title
	
@app.template_filter('get_score')
def get_score(id):
	score = 0
	entries = Entry.query.filter(Entry.receiver == id)
	for entry in entries:
		upvotes = entry.upvotes.count()
		downvotes = entry.downvotes.count()
		if upvotes > downvotes:
			score += get_task_value(entry.task)
	return score
	
@app.template_filter('format_datetime')
def format_datetime(timestamp):
	return timestamp.strftime('%Y-%m-%d @ %H:%M')
	
def allowed_file(filename):
		return '.' in filename and filename.rsplit('.', 1)[1] in app.config['ALLOWED_EXTENSIONS']

def user_has_voted(user, entry):
	has_upvotes = Upvote.query.filter(Upvote.user_id == user, Upvote.entry_id == entry).first()
	has_downvotes = Downvote.query.filter(Downvote.user_id == user, Downvote.entry_id == entry).first()
	if has_upvotes != None or has_downvotes != None:
		return True
	else:
		return False

def get_task_value(id):
	score = Task.query.filter(Task.id == id).first().value
	return score