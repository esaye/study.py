"""Solving the `eight queens' problem.

Given are an 8 X 8 chessboard and 8 queens which are hostile to each other.
Find a position for each queen (a configuration) such that no queen may be taken
by any other queen (i.e. such that every row, column, and diagonal contains at
most one queen).

Consequently, each row contains exactly one queen, as does each column; so the
mapping from rows to columns is a permutation.  There are twelve essentially
distinct solutions (once one takes accounts of the symmetries of a chess board,
allowing black and white squares to swap), one of which is symmetric under a
half turn of the board: [2, 4, 1, 7, 0, 6, 3, 5].

$Id: queens.py,v 1.2 2002-03-13 02:07:51 eddy Exp $
"""

import permute

class Iterator (permute.Iterator):
    """Iterates over all solutions to the `eight queens' problem.

    They are explored in lexical order.  Same API as permute.Iterator (q.v.),
    providing a picture as repr(). """

    __init = permute.Iterator.__init__
    def __init__(self):
	self.__init(8)
	while self.live and self.__bad(): self.__step()

    __step = permute.Iterator.step
    def step(self):
	self.__step()
	while self.live and self.__bad(): self.__step()

    def __bad(self):
	i, p = 7, self.permutation
	while i:
	    j, n = i, p[i]
	    while j:
		j = j-1
		if p[j] - n in (j-i, i-j): # same diagonal
		    return 1

	    i = i-1

	return None

    def __repr__(self): return show(self.permutation)

def show(it):
    return '\n'.join(map(lambda n: ' ' * n + '#' + ' ' * (7-n), it))

def all():
    q, a = Iterator(), []
    while q.live:
	a.append(q.permutation)
	q.step()

    global all
    def all(r=a): return r
    return a

def unique():
    def entwist(r, seq):
	s = map(lambda i: 7-i, r)
	if s not in seq: seq.append(s[:]) # copy before reversing !
	s.reverse()
	if s not in seq:
	    seq.append(s)
	    s = map(lambda i: 7-i, s)
	    if s not in seq: seq.append(s)

    u, a = [], []
    for r in map(list, all()):
	if r not in a:
	    u.append(tuple(r))
	    new = [ r ]
	    entwist(r, new)

	    r = list(permute.invert(r))
	    if r not in new:
		new.append(r)
		entwist(r, new)

	    a = a + new

    global unique
    def unique(r=u): return r
    return u

_rcs_log = """
 $Log: queens.py,v $
 Revision 1.2  2002-03-13 02:07:51  eddy
 Fixed bugs in unique's isometries, tweaked show() and docs.

 Revision 1.1  2002/03/13 00:44:35  eddy
 Initial revision
"""