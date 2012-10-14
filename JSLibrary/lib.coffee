
root = this
prefIt = root.LIB

LIB = (obj) ->
  if obj instanceof LIB
    return obj
  if not (this instanceof LIB)
    return new LIB(obj)

if typeof exports isnt 'undefined'
  LIB = exports
else
  LIB = root.LIB = {}

LIB.VERSION = '0.01'

helloWorld = LIB.helloWorld = () ->
  return "Hello World!"

