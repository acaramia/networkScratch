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
# wedo extension
#   https://scratch.mit.edu/scratchr2/static/js/scratch_extensions/wedoExtension.js
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

from flask import Flask, request
import logging
import time
import pymysql.cursors

""" 
  global variables
"""
app = Flask("NetworkScratch")
EXTENSION_PORT = 3330
jobs = set()  # jobs keeps the waiting jobs id. blocks type:'w'
variables = {}  # addVariable to return values to scratch (blocks type: 'r')
db=None


def initLogger(app):
    """ initialize logger, app to DEBUG and flask to ERROR """
    from sys import stdout
    app.logger.removeHandler(app.logger.handlers[0])
    loggers = [[app.logger, logging.DEBUG, logging.StreamHandler(stdout)],
               [logging.getLogger('werkzeug'), logging.ERROR, logging.NullHandler()]]
    # handler = logging.FileHandler('"Scratch_Pycraft".log')
    formatter = logging.Formatter('%(asctime)s - %(name)14s - %(levelname)s - %(message)s')
    for logger in loggers:
        handler = logger[2]
        handler.setFormatter(formatter)
        logger[0].addHandler(handler)
        logger[0].setLevel(logger[1])

def log(s):
    app.logger.debug("executing {}".format(s))

def addVariable(varName, varValue):
    global variables
    variables[varName] = str(varValue)

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


@app.route('/write/<int:jobId>/<string:varname>/<string:varvalue>/<string:username>')
def write(jobId,varname,varvalue,username):
    global jobs, variables, db
    jobs.add(jobId)
    log("write")
    addVariable(varname, varvalue)
    db.insert(varname,varvalue,username)
    jobs.remove(jobId)
    return "OK"

@app.route('/valueR/<string:varname>/<string:username>')
def valueR(varname,username):
    global jobs, variables, db
    #jobs.add(jobId)
    value = db.select(varname, username)
    #addVariable("value", value)
    #jobs.remove(jobId)
    return value

@app.route('/read/<int:jobId>/<string:varname>/<string:username>')
def read(jobId,varname,username):
    global jobs, variables, db
    jobs.add(jobId)
    value = db.select(varname, username)
    addVariable("value", value)
    jobs.remove(jobId)
    return "OK"

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

from dbmysql import Db

def main():
    global app, db, EXTENSION_PORT
    initLogger(app)
    print(" * The Scratch helper app is running. Have fun :)")
    print(" * ")
    print(" * Press Control + C to quit.")
    print(" * ")

    db = Db()

    done = False
    while not done:
        try:
            app.run('0.0.0.0', port=EXTENSION_PORT)
        except:
            print("trying again")
            time.sleep(1)
        else:
            print("scratch helper app done")
            done = True
            db.disconnect()

if __name__ == "__main__":
    main()
