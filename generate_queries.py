import simplejson as json
q={}
q['airplane'] = ['airplane flight', 'airplane landing', 'airbus','boeing']
q['automobile']=['racing','top gear', 'bmw','audi', 'chevrolet','mercedes']
q['bird']      =['chicken documentary', 'birds documentary', 'birds national geographic']
q['cat']       =['cat video compilation', 'funny cat', 'cute cat', 'ugly cat','cat documentary']
q['dog']       =['dog video compilation', 'funny dog', 'cute dog', 'ugly dog','dog documentary']
deertypes=['deer','elk','moose','reindeer','fallow deer','chital']
q['deer']      =['%s documentary'%deer for deer in deertypes]
q['deer'].extend(['%s national geographic'%deer for deer in deertypes])
q['frog']     =['frog documentary', 'frog national geographic', 'bullfrog']
q['horse']    =['horse wildlife', 'horses documentary', 'horses national geographic']
q['ship']     =['ships documentary', 'sea ships',]
q['truck']    =['trucks', 'road trucks' ]

print "Dump to cifar10.json"
with open('cifar10.json','wb') as fh:
    out=json.dump(q, fh, sort_keys=True, indent=4*' ')
