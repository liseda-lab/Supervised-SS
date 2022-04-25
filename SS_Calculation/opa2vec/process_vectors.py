import os
import sys

input_file= str(sys.argv[1])
entities_file = str(sys.argv[2])
output_file = str(sys.argv[3])

entities = [line.strip() for line in open(entities_file).readlines()]

inf =open(input_file)
data = ""
for line in inf:
    line.strip().replace ('[',"").replace(']',"\n")
    data = data + line.strip().replace('[', "").replace(']', "\n")

lines = data.split('\n')
lines.remove('')

entities, vectors = [], []
for line in lines:
    values = line.split(' ')
    values = ' '.join(values).split()
    if values[0] in entities:
        entities.append(values[0])
        y = [float(i) for i in values[1:]]
        vectors.append(y)

zip_iterator = zip(entities, vectors)
dict_embeddings = dict(zip_iterator)

o = open(output_file, 'w')
o.write(str(dict_embeddings))
o.close()

