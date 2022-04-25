import gensim
import gensim.models
import os
import sys

myclasses = str(sys.argv[1])
mywindow= int(sys.argv[2])
mysize= int(sys.argv[3])
mincount=int(sys.argv[4])
model =str (sys.argv[5])
pretrain=str (sys.argv[6])
ontology_corpus = str (sys.argv[7])
outfile=str(sys.argv[8])
entities_file = str(sys.argv[9])

entities = [line.strip() for line in open(entities_file).readlines()]

mymodel=gensim.models.Word2Vec.load (pretrain)
mymodel.min_count = mincount
sentences =gensim.models.word2vec.LineSentence(ontology_corpus)
mymodel.build_vocab(sentences, update=True)
mymodel.train (sentences,total_examples=mymodel.corpus_count, epochs=100)

# Store vectors for each given class
word_vectors=mymodel.wv

file= open (outfile, 'w')
file.write('{')
first = False
for ent in entities:
	if ent in word_vectors.vocab:
		if first:
			file.write(", '%s':%s" % (ent, str(mymodel[ent].tolist())))
		else:
			file.write("'%s':%s" % (ent, str(mymodel[ent].tolist())))
			first = True
file.write('}')
file.close()

