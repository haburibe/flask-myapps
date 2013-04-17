# -*- coding: utf-8 -*-
from contextlib import closing
import datetime
import sqlite3
from flask import Flask, request, session, g, redirect, url_for, abort
from flask import render_template, flash

# configuration
DATABASE = '/tmp/flask-myapps.sqlite3'
DEBUG = True
SECRET_KEY = 'development key'

# create application
app = Flask(__name__)
app.config.from_object(__name__)


# database initialization
def init_db():
    with closing(connect_db()) as db:
        with app.open_resource('schema.sql') as f:
            db.cursor().executescript(f.read())
        db.commit()


# database connection/disconnection
def connect_db():
    return sqlite3.connect(app.config['DATABASE'])


@app.before_request
def before_request():
    g.db = connect_db()


@app.teardown_request
def teardown_request(exception):
    g.db.close()


# url routing
@app.route('/')
def index():
    cur = g.db.execute('''
        SELECT id, title, closed
        FROM todos_todo
        ORDER BY closed, pub_date DESC''')
    todos = [
        {'id': row[0], 'title': row[1], 'closed': row[2]}
        for row in cur.fetchall()
    ]
    return render_template('index.html', todos=todos)


@app.route('/add', methods=['POST'])
def add():
    try:
        with g.db:
            g.db.execute(
                '''
                INSERT INTO todos_todo (title, pub_date, closed)
                VALUES (:title, :pub_date, :closed)
                ''',
                {
                    'title': request.form.get('title'),
                    'pub_date': datetime.datetime.now(),
                    'closed': False
                }
            )
            flash(u'新しいTodoが追加されました')
    except sqlite3.IntegrityError:
        flash(u'Titleを入力する必要があります')
    return redirect(url_for('index'))


@app.route('/<int:todo_id>/edit')
def edit(todo_id):
    cur = g.db.execute(
        '''
        SELECT id, title, closed
        FROM todos_todo
        WHERE id=:todo_id
        ''',
        {'todo_id': todo_id})
    row = cur.fetchone()
    if not row:
        abort(404)
    todo = {'id': row[0], 'title': row[1], 'closed': row[2]}
    return render_template('edit.html', todo=todo)


@app.route('/<int:todo_id>/update', methods=['POST'])
def update(todo_id):
    try:
        with g.db:
            g.db.execute(
                '''
                UPDATE todos_todo
                SET title=:title, closed=:closed
                WHERE id=:todo_id
                ''',
                {
                    'title': request.form.get('title'),
                    'closed': True if request.form.get('closed') else False,
                    'todo_id': todo_id
                }
            )
            flash(u'Todoが更新されました')
    except sqlite.IntegrityError:
        flash(u'Titleを入力する必要があります')
    return redirect(url_for('index'))


@app.route('/<int:todo_id>/close')
def close(todo_id):
    g.db.execute('''
        UPDATE todos_todo
        SET closed=:closed
        WHERE id=:todo_id
        ''', {'closed': True, 'todo_id': todo_id})
    g.db.commit()
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run()
