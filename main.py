from wsgiref.validate import validator

from flask import Flask, render_template, url_for, redirect, flash
from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap5
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Boolean, DateTime
from datetime import datetime
from flask_wtf import FlaskForm
from wtforms.fields.choices import SelectField
from wtforms.fields import DateField
from wtforms.fields.simple import StringField, BooleanField, SubmitField
from wtforms.validators import DataRequired, InputRequired

app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
bootstrap = Bootstrap5(app)

class Base(DeclarativeBase):
    pass

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tasks.db'
db = SQLAlchemy(model_class=Base)
db.init_app(app)

class Task(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    task: Mapped[str] = mapped_column(String(250), nullable=False)
    status: Mapped[bool] = mapped_column(Boolean, default=False)
    priority: Mapped[str] = mapped_column(String(10), default='Medium')  #low, medium, high
    due_date: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    category: Mapped[str] = mapped_column(String(50), nullable=True)    #work, personal

with app.app_context():
    db.create_all()


class TodoForm(FlaskForm):
    task = StringField('Task', validators=[DataRequired()])
    status = BooleanField('Status', validators=[InputRequired()], default=False)
    priority = SelectField('Priority', choices=[('Low','Low'), ('Medium', 'Medium'),('High', 'High')])
    due_date = DateField('Due Date', format='%Y-%m-%d')
    category = StringField('Category', validators=[DataRequired()])
    submit = SubmitField('Add Todo')


@app.route('/')
def home():
    tasks = Task.query.all()
    return render_template('index.html', tasks=tasks)

@app.route('/add', methods=['GET', 'POST'])
def add_todo():
    form = TodoForm()
    if form.validate_on_submit():
        new_todo = Task(
            task = form.task.data,
            status = form.status.data,
            priority = form.priority.data,
            due_date = form.due_date.data,
            category = form.category.data
        )
        db.session.add(new_todo)
        db.session.commit()
        return redirect(url_for('home'))
    return render_template('add.html', form=form)


@app.route('/delete/<int:task_id>', methods=['GET', 'POST'])
def delete_todo(task_id):
    # task_to_delete = db.session.get(Task, task_id) #or we can to like this also see down
    task_to_delete = Task.query.get_or_404(task_id)   #this will automatically returns 404 error if task is not found.
    if task_to_delete:
        db.session.delete(task_to_delete)
        db.session.commit()
        flash('Task deleted successfully!', 'success')
    return redirect(url_for('home'))




if __name__ == '__main__':
    app.run(debug=True)