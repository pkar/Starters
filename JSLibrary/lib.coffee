
root = this
prefIt = root.LIB # For no-conflict

# Reference to LIB
LIB = (obj) ->
  if obj instanceof LIB
    return obj
  if not (this instanceof LIB)
    return new LIB(obj)
  this._wrapped = obj

# Export for Node.js
if typeof exports isnt 'undefined'
  if typeof module isnt 'undefined' and module.exports
    exports = module.exports = LIB
  exports.LIB = LIB
else
  root.LIB = LIB

LIB.VERSION = '0.01'

helloWorld = LIB.helloWorld = () ->
  return "Hello World!"

