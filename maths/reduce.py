"""Solving linear equations in integer coefficients.

This is desirable for unit-related calculations, when inferring how a set of
values, of known kinds, imply units for values of assorted other kinds.  For
this use, the addition and integer scaling of our linear system correspond to
multiplication and taking powers of the kinds of value.  Each available vector
describes the kind of one of the given values by the powers of the 'base kinds'
that make up the value's kind.  The standard base units (i.e. canonical basis)
may then be inferred from the values by using the linear system's inverse.

See study.LICENSE for copyright and license information.
"""

import natural, permute
from study.snake.lazy import Lazy

class System (Lazy):
    """Analyzer for integer-valued linear systems.

    The system is described by a canonical basis and a set of available vectors
    expressed in terms of this basis.  The object representing the system does
    what it can to express the canonical basis in terms of the available
    vectors.  Where the available vectors' span coincides with that of some
    subset of the canonical basis, the object expresses this subset of the
    canonical basis in terms of it, via the .inverse attribute.  Otherwise,
    attempting to access .inverse shall get you a value error and the object
    does the best it can, via other attributes (to be invented).

    Each matrix attribute is encoded as a tuple of rows; each row is itself a
    tuple giving co-ordinates of the row with respect to either the canonical
    basis or the available vectors.  In matrix attributes marked as
    '(rational)', each row's last entry is an implicit denominator for all
    earlier entries; others are simple integer sequences, with no extra entry on
    each row.  Aside from .problem, all attributes are lazily-evaluated.

    Public attributes:

      problem -- cleaned-up form of the constructor's input (rational)

      inverse -- 'inverse' of .problem (rational), where available; each row,
                 .inverse[i], specifies a linear combination of available
                 vectors which yields the canonical basis member with index i,
                 where that is accessible; otherwise, inaccessibility is
                 signalled by a denominator of 0 and the rest of the row is
                 taken from kernel or, if those run out, is all zero.  Where two
                 canonical basis members are inseparable, you'll get a
                 ValueError (there's only so much I'm willing to kludge).

      available -- each row is a vector, in terms of the canonical basis,
                   which can be expressed in terms of the available vectors

      recipe -- each row specifies the linear comibination of the available
                vectors that yields the matching row of .available

      kernel -- each row is a linear dependency among the available vectors

      solution -- tuple, (.available, .recipe, .kernel), describing what can be
                  achieved.

    The rows of .available and of .recipe are linearly independent, as are those
    of .inverse with non-zero denominator, when available.  Note that .kernel is
    not guaranteed to be exhaustive, or linearly independent, but it's quite
    likely to be both.

    Although dealing notionally with integer-valued data, this class actually
    (via the implicit denominator mechanism) supports rational values; general
    integer-valued problems can perfectly readilly imply solutions involving
    rationals, so it makes sense to support the converse case. The crucial thing
    is that all arithmetic is approached from an exact integer perspective,
    rather than using floating-point approximations.\n"""

    def __init__(self, n, *rows):
        """Prepare to analyze an integer-valued linear system.

        First input, n, is the dimension of a linear space; each subsequent
        input is a sequence of integers, denoting a vector in that linear space.
        Any [n] entry of such a sequence denotes a denominator by which the [:n]
        entries are implicitly divided.  Any sequence shorter than n is
        implicitly padded with zero entries to length n, and given an [n] entry
        of 1.  The sequences are not modified.  The new object retains copies of
        them, so subsequent modifications to them shall not affect the new
        object.\n"""
        # TODO: cope with the case where span(rows) has dimension < n

        self.__ca = n, len(rows) # numbers of vectors: in canonical basis; and available
        self.problem = self.__ingest(n, rows)

    def contract(self, row):
        """Weighted sum of available values.

        Single argument is a sequence of coefficients for the available vectors
        supplied to the constructor; each entry is multiplied by the matching
        available vector, the results are summed and a rational vector
        (i.e. final entry is an implied denominator for the earlier ones)
        relative to the canonical basis is returned.  If the given sequence has
        fewer entries than there are available values, (a copy of) it is padded
        with zeros; otherwise, it may have one extra value, indicating an
        implied denominator for all the others.\n"""

        n = self.__ca[1]
        if len(row) > 1 + n:
            raise ValueError('too many entries', row, n)
        elif len(row) < n:
            row = list(row)
            while len(row) < n: row.append(0)

        if len(row) > n: row, scale = row[:n], row[n]
        else: scale = 1

        return self.__lincomb(row, scale)

    def obtain(self, row, scale=1):
        """Find how to combine availables to yield a given member of our linear space.

        Required argument, row, is a member of the linear space; returns a
        sequence of coefficients which, if fed to .contract(), would yield this
        row as output.\n"""

        n = self.__ca[0]
        if len(row) > 1 + n:
            raise ValueError('too many entries', row, n)
        elif len(row) < n:
            row = list(row)
            while len(row) < n: row.append(0)

        if len(row) > n: row, scale = row[:n], row[n]
        else: scale = 1

        return self.__obtain(row, scale)

    def check(self):
        """Compute solution and test for correctness.

        The test is done via assertions, so only works if debug is enabled !\n"""

        dim, ava = self.__ca
        try: inv = self.inverse
        except ValueError: pass
        else:
            assert ava >= dim == len(inv)
            i = dim
            while i > 0:
                i -= 1
                self.__check(i, inv[i])

        av, re, ker = self.solution # re * problem == av
        i = len(re)
        while i > 0:
            i -= 1
            self.__confirm(re[i], av[i])

        i, nul = len(ker), ( 0, ) * dim
        while i > 0:
            i -= 1
            self.__confirm(ker[i], nul)

        if len(re) + len(ker) != len(self.problem):
            print "It surprises me that kernel", len(ker), "and rank", len(re), \
                  "don't add up to system size", len(self.problem)
            # but this isn't an error

    def _lazy_get_available_(self, ig): return self.solution[0]
    def _lazy_get_recipe_(self,    ig): return self.solution[1]
    def _lazy_get_kernel_(self,    ig): return self.solution[2]
    def _lazy_get_solution_(self,  ig):
        self.__setup()
        self.__upper()
        self.__diag()
        return self.__tidy()

    def freeze(row): return tuple(tuple(r) for r in row) # local function, del'd later

    def _lazy_get_inverse_(self, ig, gcd=natural.hcf, safe=freeze):
        can, how, ker = self.solution
        how = [list(h) for h in how] # deep copy; it'll be our result
        # Conveniently, .__tidy() is sure to have left this diagonal if invertible.

        dim, ava = self.__ca
        i, j, k, co = 0, 0, 0, []
        while i < dim and j < len(can):
            row = can[j]
            if row[i]:
                j += 1
                how[i].append(row[i])
                f = gcd(*how[i])
                if f and how[i][-1] < 0: f = -f
                if f > 1 or f < 0:
                    k = len(how[i])
                    while k > 0:
                        k -= 1
                        how[i][k] /= f

                if any(row[:i]) or any(row[1+i:]):
                    co.append(j)

            elif k < len(ker):
                how.insert(i, ker[k] + (0,))
                k += 1
            else:
                how.insert(i, (0,) * (ava + 1))

            i += 1

        if co:
            raise ValueError('Irreducible composites', co)

        return safe(how)

    def __ingest(self, n, rows, gcd=natural.hcf, safe=freeze):
        ans = []
        for row in rows:
            if len(row) > 1 + n:
                raise ValueError('over-long row', row)

            r = list(row)
            while len(r) < n: r.append(0)

            if len(r) == n: r.append(1)
            elif not r[n]:
                raise ValueError('zero denominator on row', row)
            else:
                # The two prior cases make f be 0 or 1, so don't need this:
                f = gcd(*r)
                if r[n] < 0: f = -f
                if f > 1 or f < 0:
                    i = len(r)
                    while i > 0:
                        i -= 1
                        r[i] /= f

            ans.append(r)

        return safe(ans)

    def __confirm(self, left, out):
        # left times column j of problem should yield out[j]
        j = self.__ca[0]
        assert j == len(out)
        while j > 0:
            j -= 1
            tot, den = self.__contract(j, left)
            assert tot == out[j] * den

    def __check(self, i, row):
        # row i of inverse times column j of problem should yield 0, or 1 when i == j
        # Final entry in each row of each matrix is a denominator for that row.
        row, scale = row[:-1], row[-1]
        j = self.__ca[0]
        while j > 0:
            j -= 1
            tot, den = self.__contract(j, row) # sum of product entry, implicitly as tot/den

            if j == i:
                assert tot == den * scale, ("Non-unit diagonal entry", i, tot, den, scale)
            else:
                assert tot == 0, ("Non-zero off-diagonal entry", i, j, tot, den, scale)

    def dragwith(matrix, j, row, gcd=natural.gcd):
        k, tot, den = len(row), 0, 1
        assert k == len(matrix)
        assert j < len(matrix[0])

        while k > 0:
            k -= 1
            right = matrix[k]
            v, s = row[k] * right[j], right[-1]
            tot = tot * s + v * den
            den *= s
            f = gcd(tot, den)
            if f > 1: tot, den = tot / f, den / f

        return tot, den

    def denominate(pairs, scale, lcm=natural.lcm, gcd=natural.hcf):
        den = lcm(*[d for n, d in pairs])
        ans = [n * den / d for n, d in pairs] + [ den * scale ]

        f = gcd(*ans)
        if ans[-1] < 0: f = -f
        if f > 1 or f < 0:
            i = len(ans)
            while i > 0:
                i -= 1
                ans[i] /= f

        return tuple(ans)

    def __contract(self, j, row, dot=dragwith):
        """Contract column j of matrix with given row."""
        return dot(self.problem, j, row)

    def __lincomb(self, row, scale, comb=denominate):
        """As for .contract(), but with row of correct length and scale separate."""
        return comb([self.__contract(j, row)
                     for j in range(self.__ca[0])], scale)

    def __obtain(self, row, scale=1, comb=denominate, dot=dragwith):
        """As for .obtain(), but with row of correct length and scale separate."""
        # Unfortunately, inadequate to the case where the span of our system
        # isn't the whole space, even though row is within it.
        return comb([dot(self.inverse, j, row)
                     for j in range(len(self.inverse[0]))], scale)

    del dragwith, denominate

    # The actual analysis of the problem:

    def __tidy(self, order=permute.order, shuffle=permute.permute, safe=freeze):
        """Tidy-up after attempted diagonalization.

        We have .__matrix as near as we can hope for to diagonal form, albeit as
        seen through the distorting lens of .__column; we need to extract from
        it, and from the accompanying .__result, the information we were looking
        for.\n"""

        avail, recip, degen = self.__matrix, self.__result, []
        del self.__matrix, self.__result, self.__column

        # Purge any zero rows:
        i = len(avail)
        assert i == len(recip)
        while i > 0:
            i -= 1
            # avail[i] != zero implies recip[i] != zero
            if any(avail[i]): assert any(recip[i])
            else:
                if any(recip[i]): degen.append(recip[i])
                del avail[i], recip[i]

        self.kernel = safe(degen)

        # Order rows by increasing length of initial sequence of zeros:
        indent, i = [], 0
        while i < len(avail):
            j, row = 0, avail[i]
            while not row[j]: j += 1 # we know row has at least one non-zero entry.
            indent.append(j)
            i += 1

        perm = order(indent)
        assert len(avail) == len(perm) == len(recip)
        self.available = safe(shuffle(avail, perm))
        self.recipe    = safe(shuffle(recip, perm))

        return self.available, self.recipe, self.kernel

    del freeze

    def scaling(row):
        nul, ans, i = ( 0, ) * len(row), [], 0
        while i < len(row):
            it = list(nul)
            it[i] = row[i]
            ans.append(it)
            i += 1

        return ans

    def __setup(self, diag=scaling):
        """Prepare for analysis of our linear system.

        Uses .problem's denominators as diagonal entries for (otherwise zero)
        .__result and the rest of .problem as .__matrix; sets up __column as the
        identity permutation.

        When computation is trying to make it be upper triangular and, later,
        diagonal, .__matrix only appears so (in so far as we succeed) when
        viewed via the permutation of its columns encoded in .__column; this
        view of .__matrix is what .__entry() implements.

        If we multiply .__matrix on its right by a column whose entries are the
        members of our canonical basis, the result is a column of vectors.  If
        we multiply .__result on its right by a column whose entries are our
        initial available vectors, we get the same column of vectors.  This
        column is initially just the available vectors, scaled if necessary to
        have integer components.  Note that it is this column of vectors that is
        permuted by .__swap(), not the basis or availables.\n"""

        self.__matrix = [list(r[:-1]) for r in self.problem]
        self.__result = diag([r[-1] for r in self.problem])
        self.__column = range(self.__ca[0])

    del scaling

    def __entry(self, i, j): return self.__matrix[i][self.__column[j]]

    def __diag(self):
        """Reduce .__matrix from upper triangular form to diagonal form."""

        i, ava = self.__ca
        if i > ava: i = ava
        while i > 0:
            i -= 1
            num = self.__entry(i, i)
            if not num: continue # can't change anything usefully

            j = ava
            while j > 0:
                j -= 1
                if j == i: continue # leave that row itself alone !

                n = self.__entry(j, i)
                if n:
                    assert j > self.__ca[0] or j < i, ('expected zeros', i)
                    self.__take(i, n, j, num)

    def __upper(self):
        """Reduce .__matrix to upper triangular form."""
        dim, ava = self.__ca
        if dim > ava: dim = ava
        i = 0
        while i < dim:
            self.__select(i)
            key = self.__entry(i, i)
            if not key:
                break # Remainder of .__matrix is zero, so upper triangular already

            # Use .__matrix[i] to clear .__entry(j, i) for all j > i:
            j = i + 1
            while j < ava:
                q = self.__entry(j, i)
                if q: # else: nothing to do
                    self.__take(i, q, j, key)
                    assert not self.__entry(j, i), ('Bad arithmetic', i, self.__entry(j, i))

                j += 1
            i += 1

    # TODO: study choices for peak; natural.lcm, number of non-zero entries ...
    def __select(self, i, peak=lambda rs: max(abs(r) for r in rs)):
        """Find a good candidate for self.__entry(i, i).

        This prefers a row with low, but non-zero, peak entry; and selects a
        smallest non-zero entry in this row to be the nominal i-th entry on the
        diagonal of __matrix.\n"""

        dim, ava = self.__ca

        # Find row with smallest peak, swap it into row i:
        j, k, m = i+1, i, peak(self.__matrix[i])
        while j < ava and m != 1:
            n = peak(self.__matrix[j])
            if n and (not m or n < m):
                k, m = j, n
            j += 1

        if not m: return # all remaining entries are zero !
        if k != i: self.__swap(i, k)

        # Find smallest non-zero entry in row, swap it into virtual column i
        j, k, m = i+1, i, abs(self.__entry(i, i))
        while j < dim and m != 1:
            n = abs(self.__entry(i, j))
            if n and (not m or n < m):
                k, m = j, n
            j += 1

        assert m, 'How did we find a non-zero lcm of this row, to like ?'
        if k != i:
            col = self.__column
            col[k], col[i] = col[i], col[k]

    def __swap(self, i, j):
        """Swap rows i and j of the system."""
        for seq in self.__matrix, self.__result:
            seq[i], seq[j] = seq[j], seq[i]

    def __take(self, i, ni, j, nj, gcd=natural.hcf):
        """Replace row j of system by a linear combination with row i."""

        for seq in self.__matrix, self.__result:
            top, row = seq[i], seq[j]
            k = len(row)
            while k > 0:
                k -= 1
                row[k] = row[k] * nj - top[k] * ni

        f = gcd(* self.__matrix[j] + self.__result[j])
        r = [i for i in self.__matrix[j] if i]
        if r and r[0] < 0: f = -f
        if f > 1 or f < 0:
            mat, row = self.__matrix[j], self.__result[j]
            k = len(row)
            while k > 0:
                k -= 1
                row[k] /= f
                mat[k] /= f

del Lazy, permute, natural
