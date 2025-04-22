# Contributing
We maintain tags on [our issues](https://github.com/classy-python/ccbv/issues/) to make it easy to find ones that might suit newcomers to the project.
The [Low-hanging fruit tag](https://github.com/classy-python/ccbv/issues?q=is%3Aissue%20state%3Aopen%20label%3A%22Low-hanging%20fruit%22) is a good place to start if you're unfamiliar with the project.

> [!NOTE]
> TLDR: The project is currently undergoing an overhaul behind the scenes with the goal of removing the need to use Django to serve pages.
> Check that your changes are still relevant with that in mind!
>
> CCBV runs as a Django site, pulling data from a database.
> This made it very fast to get up and running, and easy to maintain for the Django-using developers, but it has been a thorn in the side of the project for years.
> The dataset is entirely fixed.
> Any changes to Django's generic class based views (GCBVs) only happen when Django makes a new release.
> We do not need to dynamically construct templates from the data on every request.
> We can write out some HTML and never touch it again (unless we feel like changing the site's styles!)
> The inspection code is tightly coupled to Django's GCBVs.
> There have been sites for other Django-specific class hierarchies using forks of CCBV for years.
> Other class hierarchies exist in Python.
> Work has been ongoing to reduce the coupling of the site to Django, with the goal of eventually completely removing it.
> This will help both this project and any related ones to more quickly update after Django or library releases, and also open up opportunities for other projects to grow.

## Installation
Set up a virtualenv and run:

    make build

This will install the requirements, collect static files, migrate the database, and finally load all the existing fixtures into your database.

## Updating requirements
Add or remove the dependency from either `requirements.prod.in` or `requirements.dev.in` as appropriate.

Run `make compile` and appropriate txt file will be updated.

## Add data for new versions of Django
1. Update the `requirements.prod.in` file to pin the new version of Django, eg `django==5.1`
1. Run `make compile` to compile this change to `requirements.prod.txt`
1. Run `python manage.py populate_cbv` to introspect the installed Django and populate the required objects in the database
1. Run `python manage.py fetch_docs_urls` to update the records in the database with the latest links to the Django documentation, this will fail at 1.9, this is expected
1. Export the new Django version into a fixture with `python manage.py cbv_dumpversion x.xx > cbv/fixtures/x.xx.json`
1. Remove the empty Generic module from the generated JSON
1. Add the fixture to git with `git add cbv/fixtures/<version>.git`
1. Restore the requirements files with `git restore requirements.*`
1. Commit and push your changes, they will be deployed once your PR is merged to main

## Testing
Run `make test` to run the full test suite with coverage.
