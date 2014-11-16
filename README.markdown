Django Class Based Views Inspector
==================================

Use the [Django Class Based Views Inspector](http://ccbv.co.uk/)

What's a class based view anyway?
---------------------------------

Django 1.3 came with class based generic views. These are really awesome, and
very powerfully coded with mixins and base classes all over the shop. This
means they're much more than just a couple of generic shortcuts, they also
provide utilities which can be mixed in the much more complex views that you
write yourself.

Great! So what's the point of the inspector?
--------------------------------------------

All of this power comes at the expense of simplicity. Trying to work out
exactly which method you need to customise on your `UpdateView` can feel a
little like wading through spaghetti - it has 8 separate ancestors (plus
`object`) spread across 3 different files. So working out that you wanted to
tweak `UpdateView.get_initial` and what it's keyword arguments are is a bit of
a faff.

That's where this comes in! Here's the manifesto:

> Provide an easy interface to learning the awesomeness of class based views.
> It should offer at least the ability to view the MRO of a generic view, all
> of the methods which are available on a particular class (including all
> inherited methods) complete with signature and docstrings. Ideally you should
> then be able to see where that method has come from, and any `super` calls
> it's making should be identified. Wrap this all up in a shiny front end!

Tools to consider
-----------------

* Python's built in [inspect](http://docs.python.org/library/inspect.html)
  module to work out what's going on and put it in the database
* [JQuery](http://jquery.com) for shinyness
* [Backbone](http://documentcloud.github.com/backbone/) for JS structure
* [Piston](https://bitbucket.org/jespern/django-piston/wiki/Home) for API
* [SASS](http://sass-lang.com/)/LESS and/or
  [Bootstrap](http://twitter.github.com/bootstrap/) to make CSS less painful

Installation
------------

Install as you normally would a Django site (requirements provided).

e.g. (inside your virtualenv or whatever)

    pip install -r requirements/local.txt

Sync the database (assuming you've got required database)

    python manage.py syncdb

Run the migrations

    python manage.py migrate cbv

Populate the database with fixtures

    python manage.py loaddata cbv/fixtures/project.json

    python manage.py loaddata cbv/fixtures/1.3.json
    python manage.py loaddata cbv/fixtures/1.4.json
    python manage.py loaddata cbv/fixtures/1.5.json
    python manage.py loaddata cbv/fixtures/1.6.json
    python manage.py loaddata cbv/fixtures/1.7.json

Run server and play around

    python manage.py runserver


Testing
-------

First of all, use another virtualenv, and install the requirements for the tests:

    pip install -r requirements/test.txt

Run the tests:

    make test


License
--------
License is [BSD-2](http://opensource.org/licenses/BSD-2-Clause).

