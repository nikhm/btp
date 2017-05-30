# Dynamic Programming implementation of LCS problem
def lcs(X , Y):
    # find the length of the strings
    m = len(X)
    n = len(Y)

    # declaring the array for storing the dp values
    L = [[None]*(n+1) for i in xrange(m+1)]

    """Following steps build L[m+1][n+1] in bottom up fashion
    Note: L[i][j] contains length of LCS of X[0..i-1]
    and Y[0..j-1]"""
    for i in range(m+1):
        for j in range(n+1):
            if i == 0 or j == 0 :
                L[i][j] = 0
            elif X[i-1] == Y[j-1]:
                L[i][j] = L[i-1][j-1]+1
            else:
                L[i][j] = max(L[i-1][j] , L[i][j-1])

    # L[m][n] contains the length of LCS of X[0..n-1] & Y[0..m-1]
    return L[m][n]
#end of function lcs


# Driver program to test the above function
def main(X,Y):
    common = lcs(X,Y)
    denom = len(X)
    print "Percent correct: " + str(float(common)/max(len(X),len(Y)))

import sys

if __name__ == "__main__":
    x,y = '',''
    n,m = sys.argv[1], sys.argv[2]
    f1 = open(n)
    for line in f1:
        x += line
    f1.close()
    f1 = open(m)
    for line in f1:
        y += line
    f1.close()
    xl,yl = len(x), len(y)
    print 'x length: ' + str(xl)
    print 'y length: ' + str(yl)
    if (xl*yl > 100000000):
        exit()
    else:
        main(x,y)
