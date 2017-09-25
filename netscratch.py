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
#

from flask import Flask, request
import logging
import time

""" 
  global variables
"""
app = Flask("NetworkScratch")
EXTENSION_PORT = 3330
jobs = set()  # jobs keeps the waiting jobs id. blocks type:'w'
variables = {}  # addVariable to return values to scratch (blocks type: 'r')

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
    variables = {}
    return "OK"

@app.route('/crossdomain.xml')
def cross_domain_check():
    return '<cross-domain-policy><allow-access-from domain="*" to-ports="'+EXTENSION_PORT+'"/></cross-domain-policy>'

# PYCRAFT FUNCTIONS:

def log(s):
    app.logger.debug("executing {}".format(s))

def addVariable(varName, varValue):
    global variables
    variables[varName] = str(varValue)

@app.route('/penup/<int:jobId>')
def penup(jobId):
    global myturtle, jobs, variables
    jobs.add(jobId)
    log("penup")
    myturtle.penup()
    jobs.remove(jobId)
    return "OK"

@app.route('/pendown/<int:jobId>')
def pendown(jobId):
    global myturtle, jobs, variables
    jobs.add(jobId)
    log("pendown")
    myturtle.pendown()
    jobs.remove(jobId)
    return "OK"

@app.route('/up/<int:jobId>/<int:angle>')
def up(jobId,angle):
    global myturtle, jobs, variables
    jobs.add(jobId)
    log("up {}".format(angle))
    myturtle.up(angle)
    jobs.remove(jobId)
    return "OK"

@app.route('/down/<int:jobId>/<int:angle>')
def down(jobId, angle):
    global myturtle, jobs, variables
    jobs.add(jobId)
    log("down {}".format(angle))
    myturtle.down(angle)
    jobs.remove(jobId)
    return "OK"

@app.route('/forward/<int:jobId>/<int:steps>')
def forward(jobId, steps):
    global myturtle, jobs, variables
    jobs.add(jobId)
    log("forward {}".format(steps))
    myturtle.forward(steps)
    jobs.remove(jobId)
    return "OK"

@app.route('/left/<int:jobId>/<int:degrees>')
def left(jobId, degrees):
    global myturtle, jobs, variables
    jobs.add(jobId)
    log("left {}".format(degrees))
    myturtle.left(degrees)
    jobs.remove(jobId)
    return "OK"

@app.route('/right/<int:jobId>/<int:degrees>')
def right(jobId, degrees):
    global myturtle, jobs, variables
    jobs.add(jobId)
    log("right {}".format(degrees))
    myturtle.right(degrees)
    jobs.remove(jobId)
    return "OK"

@app.route('/goto/<int:jobId>/<int:x>/<int:y>/<int:z>')
def goto(jobId, x, y, z):
    global myturtle, jobs, variables
    jobs.add(jobId)
    log("goto x {} y {} z {}".format(x, y, z))
    myturtle.goto(x, y, z)
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

def main():
    global app, myturtle, EXTENSION_PORT
    initLogger(app)
    print(" * The Scratch helper app is running. Have fun :)")
    print(" * ")
    print(" * Press Control + C to quit.")
    print(" * ")

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

if __name__ == "__main__":
    main()
