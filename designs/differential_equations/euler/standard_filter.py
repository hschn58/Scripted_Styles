
def upper_bound_filter(data):
    standard = data[-1]
    filtered_data = []
    
    for dat in data:

        remove_flag = False

        #all the solutions could exist for different lengths, take the minimum length so no error 
        
        length=min(len(dat[0]),len(standard[0]))

        for point in range(length):
            if dat[1][point] > standard[1][point]:
                remove_flag = True
                break
        if not remove_flag:
            filtered_data.append(dat)
    
    return filtered_data




# #xmethod-wrong data structure 
# def upper_bound_filter(data):
#     standard =data[-1]

#     stand_max=max([point[1] for point in standard])

#     for dat in data:
#         xmax=max([point[0] for point in dat])
#         if xmax>stand_max:
#             data.remove(dat)


#     return data
