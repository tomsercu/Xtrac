import simplejson as json

def documentify(subj):
    return ['%s documentary'%subj, '%s national geographic'%subj]

# automatic: subject documentaries
subjects=['airplane','automobile','bird','cat','deer','dog','frog','horse','ship','truck']
q={}
for subj in subjects:
    q[subj]=documentify(subj)
# manual queries
q['airplane'].extend(  ['airplane flight', 'airplane landing', 'airbus','boeing'])
q['automobile'].extend(['racing','top gear', 'bmw','audi', 'chevrolet','mercedes'])
q['bird'].extend(      ['chicken documentary','ducks'])
q['cat'].extend(       ['cat video compilation', 'funny cat', 'cute cat', 'ugly cat'])
q['dog'].extend(       ['dog video compilation', 'funny dog', 'cute dog', 'ugly dog'])
deertypes= ['elk','moose','reindeer']
for deer in deertypes:
    q['deer'].extend(documentify(deer))
q['frog'].extend(documentify('bullfrog'))
q['horse'].extend(    ['horses wildlife'])
q['ship'].extend(     ['sea ships',])
q['truck'].extend(    ['trucks', 'road trucks' ])

print "Dump to cifar10.json"
with open('cifar10.json','w') as fh:
    out=json.dump(q, fh, sort_keys=True, indent=4*' ')

