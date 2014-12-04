Using Docker and Fig
--------------------

If you prefer, you can use our docker containers to get your local development environment working really fast.

So first you'll need to [Install Docker](https://docs.docker.com/installation/) in you machine.

After that you should [install Fig](http://www.fig.sh/install.html) in your machine, this will allow you to run the Django linked with the DB containers more easily.

After you have both tools installed, I'll need to ensure you have the dockers build files in your project.
To do this, run the following commands:

    git submodule init
    git submodule update


Now all you have to do is run the command:

    fig up -d

This will:

* Build the DB (PostgreSQL) and the Django app container;
* Start the DB container;
* Start the Django app container;

To follow what's going on you can check the logs, by running:

    fig logs

When you see the line: *"Starting Django..."* it's because you're ready to go.

Just open a browser on the address http://localhost:8000 you should see everything running locally.

To stop the containers just run:

    fig stop

To start again the containers you can do it with:

    fig start


**OBS**: By default, the Django app container will create a Django admin super-user with:

* User: admin2
* Email: admin2@example.com
* Pass: pass2
