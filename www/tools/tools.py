def cutList1(orList, forindex):

    newList = []  # 空列表

    n = 0    # 每次切片的起点
    for k in range(len(orList)):
        if orList[k][forindex] == orList[-1][forindex]:  
            # 由于排过序，则当orList[k]等于列表最后一个元素值时，可以切片后退出循环
            newList.append(orList[n:])  # 从orList[k]取到最后
            break   # 退出循环
        if orList[k][forindex] != orList[k+1][forindex]:  
            # 由于排过序，相邻元素不等时，就表示切子列表的时候到了
            subList = orList[n:k+1]   # 切片
            newList.append(subList)
            n = k+1   # n用于储存每次切片的起点
    return newList
    