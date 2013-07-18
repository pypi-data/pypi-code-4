from flask import Blueprint
import router
blueprint = router.dispatcher

def getBlueprint():
    return blueprint
