import csv
import re
import nltk
import gensim
import random
import collections

"""Get the text from the dataset"""
def get_text(dataset):
    words = set(nltk.corpus.words.words())
    rawtext = []
    rawtextph = []
    #Reading the text from the dataset csv file
    with open(dataset+'.csv', 'r', encoding='utf-8') as read_obj:
        reader = csv.reader(read_obj)
        next(reader, None)
        #Extracting the information we need and putting it into arrays
        for row in reader:
            if row[7] != "[]":
                title = row[0]
                title = " ".join(w for w in nltk.wordpunct_tokenize(title) if w.lower() in words or not w.isalpha())
                title = re.sub('[^A-Za-z0-9]+', ' ', title)
                rawtextph.append(title)
                func = row[2]
                func = " ".join(w for w in nltk.wordpunct_tokenize(func) if w.lower() in words or not w.isalpha())
                func = re.sub('[^A-Za-z0-9]+',' ',func)
                revs = row[7]
                revs = " ".join(w for w in nltk.wordpunct_tokenize(revs) if w.lower() in words or not w.isalpha())
                revs = re.sub('[^A-Za-z0-9]+', ' ', revs)
                combined = func + revs
                rawtextph.append(combined)
                rawtext.append(rawtextph)
                rawtextph = []
    return rawtext

"""Read and tokenize the raw text"""
def read_corpus(fname, tokens_only=False):
    corpora = []
    for row in fname:
        corpora.append(row[1])
    for i, line in enumerate(corpora):
        tokens = gensim.utils.simple_preprocess(line)
        if tokens_only:
            yield tokens
        else:
            # For training data, add tags
            yield gensim.models.doc2vec.TaggedDocument(tokens, [i])

"""Get Corpus"""
rawtext = get_text('datasetnorating')
corpus = list(read_corpus(rawtext[0:40]))

"""Get samples from corpus"""
sampled = []
for x in corpus:
    for y in range(0,20):
        randomsample = random.sample(x[0],7)
        sampled.append(gensim.models.doc2vec.TaggedDocument(randomsample, x[1]))

"""Define Train Dataset and Test Dataset"""
trainlen = round(0.8*len(sampled))
testlen = round(0.2*len(sampled))
trainset = random.sample(sampled,trainlen)
testset = random.sample(sampled,testlen)

"""Model building and training"""
model = gensim.models.doc2vec.Doc2Vec(vector_size=125, min_count=2, epochs=200)
model.build_vocab(trainset)
model.train(trainset, total_examples=model.corpus_count, epochs=model.epochs)
print(model)

# MODEL COUNTER PART
ranks = []
second_ranks = []

for x in range(0,testlen):
    inferred_vector = model.infer_vector(testset[x].words)
    id = str(testset[x][1])
    id = int(id[1:len(id) - 1])
    sims = model.dv.most_similar([inferred_vector], topn=len(model.dv))
    rank = [docid for docid, sim in sims].index(id)
    ranks.append(rank)
    second_ranks.append(sims[1])
    print(len(ranks))

counter = collections.Counter(ranks)
print(counter)
print("Precision : {}%".format(counter[0]/testlen*100))

# # MODEL TESTING PART (Uncomment to use)
# # Pick a random document from the test corpus and infer a vector from the model
# doc_id = random.randint(0, len(corpus) - 1)
# inferred_vector = model.infer_vector(corpus[doc_id][0])
# sims = model.dv.most_similar([inferred_vector], topn=len(model.dv))
#
# # Compare and print the most/median/least similar documents from the train corpus
# print('Test Document ({}): «{}»\n'.format(doc_id, ' '.join(corpus[doc_id][0])))
# print(u'SIMILAR/DISSIMILAR DOCS PER MODEL %s:\n' % model)
# for label, index in [('MOST', 0), ('MEDIAN', len(sims)//2), ('LEAST', len(sims) - 1)]:
#     print(u'%s %s: «%s»\n' % (label, sims[index], ' '.join(trainset[sims[index][0]].words)))

# # SEARCH ENGINE PART (Uncomment to use)
# squery = input("Search Query : ")
# sqtokens = gensim.utils.simple_preprocess(squery)
# sq_vector = model.infer_vector(sqtokens)
# sims = model.dv.most_similar([sq_vector], topn=len(model.dv))
# print(sims)
# mostsim = sims[0]
#
# print('Search Query : «{}»\n'.format(' '.join(sqtokens)))
# sim_id = mostsim[0]
# print('Similar Document : «{}»\n'.format(' '.join(train_corpus[sim_id].words)))
# print('Printer Name : ')
# id = int(sim_id)
# print(rawtext[id][0])
# sigma = 0
# for x in sims:
#     sigma += x[1]
#     avgcg = sigma/len(sims)
# print(avgcg)

