from app import app
import mongoengine.errors
from flask import render_template, flash, redirect, url_for
from flask_login import current_user
from app.classes.data import Puzzle, Comment
from app.classes.forms import PuzzleForm, CommentForm
from flask_login import login_required
import datetime as dt

@app.route('/puzzle/new', methods=['GET', 'POST'])
# This means the user must be logged in to see this page
@login_required
# This is a function that is run when the user requests this route.
def puzzleNew():
    # This gets the form object from the form.py classes that can be displayed on the template.
    form = PuzzleForm()

    # This is a conditional that evaluates to 'True' if the user submitted the form successfully.
    # validate_on_submit() is a method of the form object. 
    if form.validate_on_submit():

        # This stores all the values that the user entered into the new blog form. 
        # Blog() is a mongoengine method for creating a new blog. 'newBlog' is the variable 
        # that stores the object that is the result of the Blog() method.  
        newPuzzle = Puzzle(
            # the left side is the name of the field from the data table
            # the right side is the data the user entered which is held in the form object.
            name = form.name.data,
            question = form.question.data,
            tag = form.tag.data,
            author = current_user.id,
            # This sets the modifydate to the current datetime.
            modify_date = dt.datetime.utcnow
        )
        # This is a method that saves the data to the mongoDB database.
        newPuzzle.save()

        # Once the new blog is saved, this sends the user to that blog using redirect.
        # and url_for. Redirect is used to redirect a user to different route so that 
        # routes code can be run. In this case the user just created a blog so we want 
        # to send them to that blog. url_for takes as its argument the function name
        # for that route (the part after the def key word). You also need to send any
        # other values that are needed by the route you are redirecting to.
        return redirect(url_for('puzzle',puzzleID=newPuzzle.id))

    # if form.validate_on_submit() is false then the user either has not yet filled out
    # the form or the form had an error and the user is sent to a blank form. Form errors are 
    # stored in the form object and are displayed on the form. take a look at blogform.html to 
    # see how that works.
    return render_template('puzzleform.html',form=form)


@app.route('/puzzle/<puzzleID>')
# This route will only run if the user is logged in.
@login_required
def puzzle(puzzleID):
    # retrieve the blog using the blogID
    thisPuzzle = Puzzle.objects.get(id=puzzleID)
    # If there are no comments the 'comments' object will have the value 'None'. Comments are 
    # related to blogs meaning that every comment contains a reference to a blog. In this case
    # there is a field on the comment collection called 'blog' that is a reference the Blog
    # document it is related to.  You can use the blogID to get the blog and then you can use
    # the blog object (thisBlog in this case) to get all the comments.
    theseComments = Comment.objects(puzzle=thisPuzzle)
    # Send the blog object and the comments object to the 'blog.html' template.
    return render_template('puzzle.html',puzzle=thisPuzzle,comments=theseComments)


@app.route('/puzzle/list')
@app.route('/puzzles')
# This means the user must be logged in to see this page
@login_required
def puzzleList():
    # This retrieves all of the 'blogs' that are stored in MongoDB and places them in a
    # mongoengine object as a list of dictionaries name 'blogs'.
    puzzles = Puzzle.objects()
    # This renders (shows to the user) the blogs.html template. it also sends the blogs object 
    # to the template as a variable named blogs.  The template uses a for loop to display
    # each blog.
    return render_template('puzzles.html',puzzles=puzzles)


@app.route('/puzzle/edit/<puzzleID>', methods=['GET', 'POST'])
@login_required
def puzzleEdit(puzzleID):
    editPuzzle = Puzzle.objects.get(id=puzzleID)
    # if the user that requested to edit this blog is not the author then deny them and
    # send them back to the blog. If True, this will exit the route completely and none
    # of the rest of the route will be run.
    if current_user != editPuzzle.author:
        flash("You can't edit a blog you don't own.")
        return redirect(url_for('puzzle',puzzleID=puzzleID))
    # get the form object
    form = PuzzleForm()
    # If the user has submitted the form then update the blog.
    if form.validate_on_submit():
        # update() is mongoengine method for updating an existing document with new data.
        editPuzzle.update(
            name = form.name.data,
            question = form.question.data,
            tag = form.tag.data,
            modify_date = dt.datetime.utcnow
        )
        # After updating the document, send the user to the updated blog using a redirect.
        return redirect(url_for('blog',puzzleID=puzzleID))

    # if the form has NOT been submitted then take the data from the editBlog object
    # and place it in the form object so it will be displayed to the user on the template.
    form.name.data = editPuzzle.name
    form.question.data = editPuzzle.question
    form.tag.data = editPuzzle.tag


    # Send the user to the blog form that is now filled out with the current information
    # from the form.
    return render_template('puzzleform.html',form=form)


@app.route('/puzzle/delete/<puzzleID>')
# Only run this route if the user is logged in.
@login_required
def puzzleDelete(puzzleID):
    # retrieve the blog to be deleted using the blogID
    deletePuzzle = Puzzle.objects.get(id=puzzleID)
    # check to see if the user that is making this request is the author of the blog.
    # current_user is a variable provided by the 'flask_login' library.
    if current_user == deletePuzzle.author:
        # delete the blog using the delete() method from Mongoengine
        deletePuzzle.delete()
        # send a message to the user that the blog was deleted.
        flash('The Puzzle was deleted.')
    else:
        # if the user is not the author tell them they were denied.
        flash("You can't delete a blog you don't own.")
    # Retrieve all of the remaining blogs so that they can be listed.
    puzzles = Puzzle.objects()  
    # Send the user to the list of remaining blogs.
    return render_template('puzzles.html',puzzles=puzzles)