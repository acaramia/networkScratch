#! /usr/bin/python

# Scratch Helper app
# ------------------
# template based on work of Chris Proctor, Project homepage: http://mrproctor.net/scratch
#   https://github.com/cproctor/scratch_hue
#
# main document
#   https://wiki.scratch.mit.edu/w/images/ExtensionsDoc.HTTP-9-11.pdf
# Scratch Extension Protocol Discussion
#   https://wiki.scratch.mit.edu/wiki/Scratch_Extension
#   https://scratch.mit.edu/discuss/topic/18117/
# scratchx extension
#   https://github.com/LLK/scratchx/wiki
# hat blocks
#   https://scratch.mit.edu/discuss/topic/49736/
# wedo2 extension
#   https://scratch.mit.edu/scratchr2/static/js/scratch_extensions/wedo2Extension.js
# framework scratch/snap
#   https://github.com/blockext/blockext/tree/master/blockext
# flask objects
#   http://flask.pocoo.org/docs/0.12/api/
# scratch editor source code
#   https://github.com/LLK/scratch-flash
#   trovati R e r e -
#   https://scratch.mit.edu/discuss/topic/127898/?page=1#post-1141794
#
#   https://github.com/LLK/scratch-flash/blob/develop/src/extensions/ScratchExtension.as
# block modding from source
#    https://scratch.mit.edu/discuss/topic/38970/?page=1
# probabilmente, l'estensione con url funziona solo sui domini concessi (github.io e code.me). da provare

from flask import Flask, request
import logging
import time
import requests

""" 
  global variables
"""
app = Flask("NetworkScratchHttp")
EXTENSION_PORT = 3333
TIMEOUT = 1
jobs = set()  # jobs keeps the waiting jobs id. blocks type:'w'
variables = {}  # addVariable to return values to scratch (blocks type: 'r')


def initLogger(app):
    """ initialize logger, app to DEBUG and flask to ERROR """
    from sys import stdout
    app.logger.removeHandler(app.logger.handlers[0])
    loggers = [[app.logger, logging.ERROR, logging.StreamHandler(stdout)],
               [logging.getLogger('werkzeug'), logging.ERROR, logging.NullHandler()]]
    # handler = logging.FileHandler('"Scratch_Pycraft".log')
    formatter = logging.Formatter('%(asctime)s - %(name)14s - %(levelname)s - %(message)s')
    for logger in loggers:
        handler = logger[2]
        handler.setFormatter(formatter)
        logger[0].addHandler(handler)
        logger[0].setLevel(logger[1])


def log(s):
    app.logger.debug(s)


def add_variable(name, value):
    global variables
    variables[name] = str(value)
    return name


def read_variable(name):
    if name in variables:
        value = variables[name]
    else:
        value = "{} not found".format(name)
    return value


@app.errorhandler(Exception)
def exceptions(e):
    app.logger.debug(e)


@app.before_request
def after_request():
    if request.path != "/poll": # to avoid not necessary logs
        app.logger.debug("received {}".format(request.full_path))


# scratch protocol path
@app.route('/poll')
def poll():
    global jobs, variables
    s = "\n".join(["_busy {}".format(job) for job in jobs])
    s = s + "\n".join(["{} {}".format(var, variables[var]) for var in variables.keys()])
    #b = s
    #if b.strip() != "":
    #    print(b)
    return s


@app.route('/reset_all')
def reset_all():
    global jobs, variables
    jobs = set()
    return "OK"


@app.route('/crossdomain.xml')
def cross_domain_check():
    return '<cross-domain-policy><allow-access-from domain="*" to-ports="'+EXTENSION_PORT+'"/></cross-domain-policy>'


@app.route('/get_my_ip')
def get_my_ip():
    global jobs, variables
    from socket import gethostname, gethostbyname
    my_ip = gethostbyname(gethostname())  # get our IP. Be careful if you have multiple network interfaces or IPs
    value = my_ip
    return value


@app.route('/set_remote/<int:jobId>/<string:remote_name>/<string:remote_ip>/<string:value>')
def set_remote(jobId, remote_name, remote_ip, value):
    global jobs, variables
    jobs.add(jobId)
    #payload = {'name': remote_name, 'value': value}
    url = "http://{}:{}/set_variable/{}/{}".format(remote_ip, EXTENSION_PORT, remote_name, value)
    log("calling {}".format(url))
    status = ""
    try:
        r = requests.get(url, timeout=TIMEOUT)
        status = r.status_code
        if r.status_code == requests.codes.ok:
            response = r.text
            if response.startswith("OK"):
                status = response
            else:
                status = "KO {} {}".format(r.status_code, response)
    except requests.exceptions.RequestException as e:
        status = "KO "+str(e)
    add_variable("status", status)
    log("status {}".format(status))
    jobs.remove(jobId)
    return "OK"


@app.route('/get_remote/<string:remote_name>/<string:remote_ip>')
def get_remote(remote_name, remote_ip):
    global jobs, variables
    url = "http://{}:{}/get_variable/{}".format(remote_ip, EXTENSION_PORT, remote_name)
    log("calling {}".format(url))
    value = ""
    status = ""
    try:
        r = requests.get(url, timeout=TIMEOUT)
        status = r.status_code
        if r.status_code == requests.codes.ok:
            response = r.text
            value = response
    except requests.exceptions.RequestException as e:
        status = "KO "+str(e)
    add_variable("status", status)
    log("status {}".format(status))
    return value


@app.route('/set_local/<int:jobId>/<string:name>/<string:value>')
def set_local(jobId, name, value):
    global jobs
    jobs.add(jobId)
    add_variable(name, value)
    jobs.remove(jobId)
    return "OK"


@app.route('/get_local/<string:name>')
def get_local(name):
    return read_variable(name)


"""  called from remote app, not from Scracth """


@app.route('/get_variable/<string:name>')
def get_variable(name):
    return read_variable(name)


@app.route('/set_variable/<string:name>/<string:value>')
def set_variable(name, value):
    add_variable(name, value)
    return "OK [{} = {}]".format(name, value)

"""
@app.route('/cube/<int:jobId>/<string:block>/<int:side>/<int:x>/<int:y>/<int:z>')
def cube(jobId, block, side, x, y, z):
    global myturtle, jobs, variables
    jobs.add(jobId)
    print(block, side, x, y, z)
    pcmt.cube(pcmt.getblock(block), side, x, y, z)
    jobs.remove(jobId)
    return "OK"
"""


def main():
    global app, EXTENSION_PORT
    initLogger(app)
    print(" **************************************************")
    print(" * The Scratch helper app is running. Have fun :) *")
    print(" *                                                *")
    print(" * Press Control + C to quit.                     *")
    print(" **************************************************")

    done = False
    while not done:
        try:
            app.run('0.0.0.0', port=EXTENSION_PORT, threaded=True)
        except:
            print("trying again")
            time.sleep(1)
        else:
            print("scratch helper app done")
            done = True


if __name__ == "__main__":
    main()
