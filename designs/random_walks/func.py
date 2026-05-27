

def get_iter(rang, prob, seed, data=0):
    

    import random
    random.seed(seed)

    list=[]
    for x in range(0,rang):
        if random.random()>=prob:
            data+=1
        else:
            data-=1
        list +=[data]

    return list
