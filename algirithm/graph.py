import collections



def BFS(graph, root):
    visited, queue, result = set([root]), collections.deque([root]), collections.deque()
    while queue: 
        v = queue.popleft()
        for neighbour in graph[v]:
            if neighbour not in visited:
                visited.add(neighbour)
                queue.append(neighbour)
                result.append((v, neighbour))
    return result


def DFSUtil(g, node, visited, result): 
    visited[node]= True
    for child in g[node]: 
    	if not (child in visited) or visited[child] == False:
       	    result.append((node, child)) 
            DFSUtil(g, child, visited, result) 
    
def DFS(graph, root): 
        result=collections.deque()
        visited = graph.fromkeys(graph, False)
        DFSUtil(graph, root, visited, result) 
        return result


def TSP(graph, start, end):
    path=TSPUtil(graph, start, end)
    return list(zip(path[:-1], path[1:]))


def TSPUtil(graph, start, end, path=[]):
        path=path+[start]
        if start==end: return path
        if not start in graph: return None
        shortest = None
        for node in graph[start]:
            if node not in path:
                newpath = TSPUtil(graph, node, end, path)
                if newpath:
                    if not shortest or len(newpath) < len(shortest):
                        shortest = newpath
        return shortest

def fromAM2AL(graph):
    return [[ 1 if j in i else 0 for j in graph.keys()] for i in graph.values()]

