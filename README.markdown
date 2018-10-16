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


Installation
------------
Make sure you have a local python environment set up and run:

    make setup

This will install the project and all its dependencies in your local python
environment giving you the `ccbv` command.


## Usage

  make build

This will create a `versions` directory with a `virtualenv` for each version of
Django listed in `config.json`.
Then it will run the `ccbv generate` command for each version of Django
configured.


### View HTML

    make serve

This will serve the `output` directory at `http://localhost:8000`.


### Helper Commands
Various typical workflows have been been wrapped up in the Makefile and can
be viewed by running:

    make help


License
--------
License is [BSD-2](http://opensource.org/licenses/BSD-2-Clause).

