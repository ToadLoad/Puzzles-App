from app import app
import mongoengine.errors
from flask import render_template, flash, redirect, url_for
from flask_login import current_user
from app.classes.data import Response, Comment
from app.classes.forms import ResponseForm, CommentForm
from flask_login import login_required
import datetime as dt
from random import sample

questions = [{"q":"1+1?","a":["2","two"]},
             {"q":"1+2?","a":["3","three"]},
             {"q":"1+3?","a":["4","four"]},
             {"q":"What has a lot of water and starts with an O?","a":["Ocean","ocean","OCEAN"]},
             {"q":"Rearrange these letters to create a word: L F O R E W","a":["FLOWER","flower"]}]

@app.route('/response/new', methods=['GET', 'POST'])
# This means the user must be logged in to see this page
@login_required
# This is a function that is run when the user requests this route.
def responseNew():
    # This gets the form object from the form.py classes that can be displayed on the template.
    form = ResponseForm()

    # This is a conditional that evaluates to 'True' if the user submitted the form successfully.
    # validate_on_submit() is a method of the form object. 
    if form.validate_on_submit():

        # This stores all the values that the user entered into the new blog form. 
        # Blog() is a mongoengine method for creating a new blog. 'newBlog' is the variable 
        # that stores the object that is the result of the Blog() method.  

        newResponse = Response(
            # the left side is the name of the field from the data table
            # the right side is the data the user entered which is held in the form object.

            q1 = form.q1.data,
            q2 = form.q2.data,
            q3 = form.q3.data,
            a1 = form.a1.data,
            a2 = form.a2.data,
            a3 = form.a3.data,
            score = (1 if form.a1.data in form.ca1.data.split(", ") else 0)
            + (1 if form.a2.data in form.ca2.data.split(", ") else 0)
            + (1 if form.a3.data in form.ca3.data.split(", ") else 0),    
            author = current_user.id

        )
        # This is a method that saves the data to the mongoDB database.
        newResponse.save()

        # Once the new blog is saved, this sends the user to that blog using redirect.
        # and url_for. Redirect is used to redirect a user to different route so that 
        # routes code can be run. In this case the user just created a blog so we want 
        # to send them to that blog. url_for takes as its argument the function name
        # for that route (the part after the def key word). You also need to send any
        # other values that are needed by the route you are redirecting to.
        return redirect(url_for('response',responseID=newResponse.id))
    else:
        form.chosenQuestions = sample(questions,k=3)
        form.q1.data = form.chosenQuestions[0]["q"]
        form.q2.data = form.chosenQuestions[1]["q"]
        form.q3.data = form.chosenQuestions[2]["q"]
        form.a1.label = form.chosenQuestions[0]["q"]
        form.a2.label = form.chosenQuestions[1]["q"]
        form.a3.label = form.chosenQuestions[2]["q"]
        form.ca1.data = ", ".join(form.chosenQuestions[0]["a"])
        form.ca2.data = ", ".join(form.chosenQuestions[1]["a"])
        form.ca3.data = ", ".join(form.chosenQuestions[2]["a"])

    # if form.validate_on_submit() is false then the user either has not yet filled out
    # the form or the form had an error and the user is sent to a blank form. Form errors are 
    # stored in the form object and are displayed on the form. take a look at blogform.html to 
    # see how that works.
    return render_template('responseform.html',form=form)


@app.route('/response/<responseID>')
# This route will only run if the user is logged in.
@login_required
def response(responseID):
    # retrieve the blog using the blogID
    thisResponse = Response.objects.get(id=responseID)
    # If there are no comments the 'comments' object will have the value 'None'. Comments are 
    # related to blogs meaning that every comment contains a reference to a blog. In this case
    # there is a field on the comment collection called 'blog' that is a reference the Blog
    # document it is related to.  You can use the blogID to get the blog and then you can use
    # the blog object (thisBlog in this case) to get all the comments.
    theseComments = Comment.objects(response=thisResponse)
    # Send the blog object and the comments object to the 'blog.html' template.
    return render_template('response.html',response=thisResponse,comments=theseComments)


@app.route('/puzzles/list')
@app.route('/puzzles')
# This means the user must be logged in to see this page
@login_required
def responseList():
    # This retrieves all of the 'blogs' that are stored in MongoDB and places them in a
    # mongoengine object as a list of dictionaries name 'blogs'.
    responses = Response.objects()
    # This renders (shows to the user) the blogs.html template. it also sends the blogs object 
    # to the template as a variable named blogs.  The template uses a for loop to display
    # each blog.
    return render_template('responses.html',responses=responses)


@app.route('/response/delete/<responseID>')
# Only run this route if the user is logged in.
@login_required
def responseDelete(responseID):
    # retrieve the blog to be deleted using the blogID
    deleteResponse = Response.objects.get(id=responseID)
    # check to see if the user that is making this request is the author of the blog.
    # current_user is a variable provided by the 'flask_login' library.
    if current_user == deleteResponse.author:
        # delete the blog using the delete() method from Mongoengine
        deleteResponse.delete()
        # send a message to the user that the blog was deleted.
        flash('The Response was deleted.')
    else:
        # if the user is not the author tell them they were denied.
        flash("You can't delete a blog you don't own.")
    # Retrieve all of the remaining blogs so that they can be listed.
    responses = Response.objects()  
    # Send the user to the list of remaining blogs.
    return render_template('responses.html',responses=responses)




