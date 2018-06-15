Instructions to run program:

1) Prerequisites required
    a) Clone https://github.com/udacity/fullstack-nanodegree-vm.git
    b) Set item_catalog under UdacityPythonFiles/fullstack-nanodegree-vm/vagrant
    c) In terminal, run python vagrant up followed by vagrant ssh
    d) Once vagrant is up cd /vagrant
    e) Go inside item_catalog folder and run 'python database_setup.py'
    f) Go inside item_catalog folder and run 'python initialData.py'
    g) Go inside item_catalog folder and run 'python application.py'


Structure of the code:
    Templates
      - Inside the folder there are the html page template to my views

    application.py
      - The controller and views communicate here with its appropriate methods

    database_setup.py
      - This is where models are stored and setup
      - The database is setup as sqlite:///catalogitems.db

    initialData.py
      - This is dummy data for each model
      - Once ran, database will have initial data

    client_secrets.py
      - googleapi's credentials and client's information will be stored here
      - This will be accessed for login purposes
      - Put in your own secret_key and client for googleapi


Future Work:
    - Create header html that applies css to all html pages
    - Delete redundant html public pages and use 1 page for (non) login user
    - Add css page using boothstrap


Potential bugs:
    - When one user does not logout and another log in, the user can go back
      and have the same authorization rights
