import traceback
import os

def relPath(resource: str):
    stack = traceback.extract_stack()
    frameIndex = [i for i,s in enumerate(stack) if s.filename == __file__][0]
    callerFile = stack[frameIndex-1].filename
    callerDir = os.path.dirname(callerFile)
    return os.path.join(callerDir, resource)