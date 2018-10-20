colors=('unknown','black','blue','green','yellow','red','white','brown')

def evaluate(sensor):
  color = colors[sensor.value()]
  if color != 'white':
    return 0
  return 100
