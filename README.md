# How to build a local copy

This website uses Nikola Static Site generator

To build a local version you need Python 3.5.3 or newer. 

    $ python3 -V
    Python 3.6.4

Clone or download a copy of this repository:

    # Either clone with git
    $ git clone https://github.com/lugfl/website.git LUGFL-Website
    
    # or download a zip
    $ curl -O https://github.com/lugfl/website/archive/master.zip
    $ unzip master.zip -d LUGFL-Website
  
Then follow these steps to get a development environment going: 
   
    $ cd LUGFL-Website
    $ python3 -m venv venv
    $ source ./venv/bin/activate
    $ pip install -r requirements.txt
    $ cd website
    $ nikola auto -b

To add new pages, just call

    $ nikola new_page

Or to create a news entry

    $ nikola new_post
    Creating New Post
    -----------------
    
    Title: Neue Webseite der LUGFL erblickt das Licht der Welt
    Scanning posts........done!
    [2018-09-30T08:33:02Z] INFO: new_post: Your post's text is at: posts/neue-webseite-der-lugfl-erblickt-das-licht-der-welt.rst


# How to update dependencies

The requirements.txt file lists the exact versions of all python-packages and
and there dependencies.

The requirements-dev.txt file lists only "wanted" python-packages. Dependencies
of this packages are automaticly installed by pip.

To Update the requirements.txt file create a clean virtualenv and install Nikola with:

    $ pip install -r requirements-dev.txt

If everything is working well, recreate the requirements.txt file with:

    $ pip freeze > requirements.txt

Commit both files into the repository.

Our automatic Build-Script will use requirements.txt only.


