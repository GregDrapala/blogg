from flask import render_template, request, session, flash, redirect, url_for
from blog import app
from blog.models import Entry, db
from blog.forms import EntryForm, LoginForm
import functools

def login_required(view_func):
   @functools.wraps(view_func)
   def check_permissions(*args, **kwargs):
       if session.get('logged_in'):
           return view_func(*args, **kwargs)
       return redirect(url_for('login', next=request.path))
   return check_permissions


def create_or_edit_entry(entry_id, entry, form):
    errors = None
    if request.method == 'POST':
        if form.validate_on_submit() and entry_id:
            form.populate_obj(entry)
            db.session.commit()
            return redirect(url_for("homepage"))
        elif form.validate_on_submit():
            db.session.add(entry)
            db.session.commit()
        else:
            errors = form.errors
    return render_template("entry_form.html", form=form, errors=errors, entry_id=entry_id)


@app.route("/")
def homepage():
   all_posts = Entry.query.filter_by(is_published=True).order_by(Entry.pub_date.desc())
   return render_template("homepage.html", all_posts=all_posts)


@app.route("/create/", methods=['GET', 'POST'])
@login_required
def create_entry():
    form = EntryForm()
    entry_id = None
    entry = Entry(
        title=form.title.data,
        body=form.body.data,
        is_published=form.is_published.data
        )
    return create_or_edit_entry(entry_id, entry, form)


@app.route("/edit_entry/<int:entry_id>", methods=['GET', 'POST'])
@login_required
def edit_entry(entry_id):
    entry = Entry.query.filter_by(id=entry_id).first_or_404()
    form = EntryForm(obj=entry)
    return create_or_edit_entry(entry_id, entry, form)

@app.route("/login/", methods=['GET', 'POST'])
def login():
   form = LoginForm()
   errors = None
   next_url = request.args.get('next')
   if request.method == 'POST':
       if form.validate_on_submit():
           session['logged_in'] = True
           session.permanent = True  # Use cookie to store session.
           flash('You are now logged in.', 'success')
           return redirect(next_url or url_for('homepage'))
       else:
           errors = form.errors
   return render_template("login_form.html", form=form, errors=errors)


@app.route('/logout/', methods=['GET', 'POST'])
def logout():
   if request.method == 'POST':
       session.clear()
       flash('You are now logged out.', 'success')
   return redirect(url_for('homepage'))    

@app.route("/drafts/", methods=['GET'])
@login_required
def list_drafts():
   drafts = Entry.query.filter_by(is_published=False).order_by(Entry.pub_date.desc())
   return render_template("drafts.html", drafts=drafts)



@app.route("/delete_entry/<int:entry_id>", methods=['POST'])
@login_required
def delete_entry(entry_id):
    if request.method == 'POST':
        entry = Entry.query.filter_by(id=entry_id).first_or_404()
        db.session.delete(entry)
        db.session.commit()
        flash(f'Usuni??to post {entry.title} na blogu.')
    return redirect(url_for("homepage"))