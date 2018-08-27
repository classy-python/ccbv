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

First you should install some OS libraries required for some packages, this can vary with each OS, but if you're on Ubuntu 14.04, then this should do the trick for you:

    sudo apt-get install python3-dev libmemcached-dev zlib1g-dev libpq-dev

After this, install as you normally would a Django site (requirements.txt provided).

e.g. (inside your virtualenv or whatever)

    pip install -r requirements.txt

Prepare the database (assuming you've got required database)

    python manage.py migrate cbv

Populate the database with fixtures, either all at once:

    python manage.py load_all_django_versions

or one at a time, for example:

    python manage.py loaddata cbv/fixtures/project.json

    python manage.py loaddata cbv/fixtures/1.8.json
    python manage.py loaddata cbv/fixtures/1.9.json

Collect static files (CSS & JS)

    python manage.py collectstatic

Run server and play around

    python manage.py runserver


Updating Requirements
---------------------
Run `pip-compile` and `requirements.txt` will be updated based on the specs in `requirements.in`.

More details can be found on the [pip-tools](https://github.com/nvie/pip-tools) website.


Updating for New Versions of Django
-----------------------------------
The procedure for updating for a new version of Django is as simple as:

1. Update the `requirements.in` file to pin the required version of Django;
2. Use `pip-compile -o requirements.txt requirements.in` to freshen requirements
   for the new version of Django;
3. Use `pip-sync` to update your virtual environment to match the newly compiled
   `requirements.txt` file;
4. Update the project's code to run under the target version of Django, as
   necessary;
5. Use `python manage.py populate_cbv` to introspect the running Django
   and populate the required objects in the database;
6. Use `python manage.py fetch_docs_urls` to update the records in the
   database with the latest links to the Django documentation;
7. Export the new Django version into a fixture with: `python manage.py cbv_dumpversion x.xx > cbv/fixtures/x.xx.json`;


Testing
-------

All you should do is:

    make test


License
--------
License is [BSD-2](http://opensource.org/licenses/BSD-2-Clause).

