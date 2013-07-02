#!/usr/bin/env python

##############################################################################
# Welcome to Grok!
#
# In this sample application we'll be creating a model of energy use for a
# local business, in this case a Recreation Center.
#
# Spiking energy use can be a sign of waste for a business. To save energy, and
# money, we need a way to predict what our energy consumption will be like in
# the next hour, so we can take action *now* to prevent wasting power.
#
# In this application we will:
#
# * Create a Model
# * Create a Stream of our energy use data
# * Configure how we want our Model to use our Stream
# * Start a Grok Swarm to optimize our Model for the given Stream
# * Get results from the Swarm
#
# We'll end up with a CSV we can examine to see how well Grok learned and
# predicted the energy use for this business.
#
##############################################################################

import time
import csv
import os
import sys

import grokpy

##############################################################################
# Configuration Settings

API_KEY = 'YOUR_KEY_HERE'
INPUT_CSV = 'data/rec-center-swarm.csv'
OUTPUT_CSV = 'output/SwarmOutput.csv'
SWARM_SIZE = os.environ.get('HELLOGROK_SWARM_SIZE')

##############################################################################
# API KEY NOTE: A more secure method is to store your API key in your
# shell environment.
#
# From the command line:
#  echo "export GROK_API_KEY=YOUR_KEY_HERE" >> ~/.bashrc
#  source ~/.bashrc
#
# After doing so you do not need to pass a key to instantiate a client.
# e.g. grok = grokpy.Client()

def HelloGrok():

  ##############################################################################
  # Setup
  #
  # This is where we will create all the top level objects we'll be working
  # with in this application.
  #
  # grokpy.DEBUG = True # Uncomment this line if you want more verbose output

  # Connect to Grok
  print 'Connecting to Grok ...'
  grok = grokpy.Client(API_KEY)
  now = time.time()

  ##############################################################################
  # Your Stream
  #
  # For Grok to use your data we need a careful specification of that data to
  # work with. The combination of your data and its specification is what
  # we call a 'Stream'.

  # Create our stream specification
  # Note: Until we call createStream(streamSpec) all these operations are local.
  print 'Defining our stream ...'
  streamSpec = grokpy.StreamSpecification()
  streamSpec.setName('Recreation Center Stream ' + str(now))

  # Create a Data Source and specify fields
  local = grokpy.LocalDataSource()
  local.setName('Local CSV Data')

  # Create each of our fields
  timestamp = grokpy.DataSourceField()
  timestamp.setName('timestamp')
  timestamp.setType(grokpy.DataType.DATETIME)
  timestamp.setFlag(grokpy.DataFlag.TIMESTAMP)

  consumption = grokpy.DataSourceField()
  consumption.setName('consumption')
  consumption.setType(grokpy.DataType.SCALAR)

  # Add our fields to our source
  local.addField(timestamp)
  local.addField(consumption)

  # Add our source to the stream specification
  streamSpec.addDataSource(local)

  # Create an empty stream using our streamSpec object
  # Note this makes an actual call to the API
  print 'Creating the stream ...'
  myStream = grok.createStream(streamSpec)

  # Add data to the stream from a csv
  print 'Adding records to stream ...'
  fileHandle = open(INPUT_CSV, 'rU')
  recCenterData = [row for row in csv.reader(fileHandle)]
  fileHandle.close()
  myStream.addRecords(recCenterData)

  ##############################################################################
  # Create and configure your Model
  #
  # Your models can listen to your streams in many different ways. Here we
  # tell the model how to deal with stream data and which field we want to
  # optimize our predictions for.

  print 'Defining a model ...'
  modelSpec = grokpy.ModelSpecification()
  # Give the model a name
  modelSpec.setName("Recreaction Center Model " + str(time.time()))
  # Set which field this model will predict and optimize for
  modelSpec.setPredictedField("consumption")
  # Set which stream this model will listen to
  modelSpec.setStream(myStream.id)

  # We want to get predictions every hour, so we'll set this model to
  # aggregate data for us.
  modelSpec.setAggregationInterval({"hours": 1})

  # Create that model using our specification
  print 'Creating an empty model ...'
  recCenterEnergyModel = grok.createModel(modelSpec)
  print "Done. Your model's Id is: %s" % recCenterEnergyModel.id

  ##############################################################################
  # Start the Swarm
  #
  # Now we have a project, a stream with data, and a model configured for that
  # stream. We can start a Grok Swarm! The Swarm will find the best
  # configuration of our model to predict the data that exist in the stream.

  print 'Starting Grok Swarm'
  recCenterEnergyModel.startSwarm(size=SWARM_SIZE)

  ##############################################################################
  # Monitor Progress
  #
  # To know when our Swarm is complete we will poll for the state of the Swarm

  swarmStarted = False
  while True:
    state = recCenterEnergyModel.getSwarmState()
    jobStatus = state['status']
    results = state['details']
    if 'numRecords' in results:
      recordsSeen = results['numRecords']
    else:
      recordsSeen = 0

    if jobStatus == grokpy.SwarmStatus.COMPLETED:
      # Swarm is done
      bestConfig = results['bestModel']
      print '\nYou win! Your Grok Swarm is complete.'
      print '\tBest Configuration: ' + str(bestConfig)
      print '\tWith an Error of: ' + str(results['bestValue'])
      print ('\tThis model uses the following field(s): '
             + str(results['fieldsUsed']))
      print
      # Exit the loop
      break
    elif jobStatus == grokpy.SwarmStatus.RUNNING and swarmStarted == False:
      # The first time we see that the swarm is running
      swarmStarted = True
      print 'Swarm started.'
    elif jobStatus == grokpy.SwarmStatus.STARTING:
      print 'Swarm is starting up ...'
      time.sleep(2)
    else:
      print ".",
      sys.stdout.flush()
      time.sleep(2)

  ##############################################################################
  # Retrieve Swarm results

  print "Getting full results from Swarm ..."
  headers, resultRows, resultMetadata = recCenterEnergyModel.getModelOutput(limit = 2500)

  # Write results out to a CSV
  if not os.path.exists('output'):
    print 'Output directory not found, creating ...'
    os.mkdir('output')
  print "Saving results to " + OUTPUT_CSV
  fileHandle = open(OUTPUT_CSV, 'w')
  writer = csv.writer(fileHandle)
  writer.writerow(headers)
  writer.writerows(resultRows)
  fileHandle.close()

  ##############################################################################
  # Next steps ...
  #
  # You now have a set of predictions about the energy use of this building!
  # Now would be a good time to explore the results of the Swarm and familiarize
  # yourself with their format. You can find documentation about this here:
  #
  # https://www.groksolutions.com/devs/interpreting_results.html
  #
  # After that, you can take the Model id printed out below and head over
  # to Part Two!

  print """
=====================================================================
On to Part Two!
  Take this, you'll need it:
  MODEL_ID: %s

Please edit HelloGrokPart2.py, adding in the MODEL_ID.
Then run:
  python HelloGrokPart2.py""" % recCenterEnergyModel.id

if __name__ == '__main__':
  HelloGrok()
