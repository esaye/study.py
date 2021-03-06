"""Multinomials - polynomials in several free variables.

c.f. polynomial, using only one free variable.
See study.LICENSE for copyright and license information.
"""
from study.snake.lazy import Lazy
from polynomial import unNaturalPower

class Multinomial (Lazy):
    def __init__(self, bok):
        for k, v in bok.items():
            if v:
                v * .4 + v * .6 # raise error if no arithmetic
                for it in k: # raise error if k not a sequence of naturals
                    if it != long(it) or it < 0: raise unNaturalPower

                if k and k[-1] == 0:
                    q = k[:-1]
                    while q and q[-1] == 0: q = q[:-1]
                    del bok[k]
                    bok[q] = v

            else: del bok[k]

        # canonical form for keys: last entry non-zero
        self.__coefs = bok # dictionary { (int, ...): scalars }

    def __add__(self, whom):
        try: tot = whom.__coefs.copy()
        except AttributeError: tot = {(): whom}

        zero = self._zero
        for k, v in self.__coefs.items():
            tot[k] = tot.get(k, zero) + v

        return Multinomial(tot)

    __radd__ = __add__

    def __sub__(self, whom):
        tot, zero = self.__coefs.copy(), self._zero

        try: bok = whom.__coefs
        except AttributeError: tot[()] = tot.get((), zero) - whom
        else:
            for k, v in bok.items():
                tot[k] = tot.get(k, zero) - v

        return Multinomial(tot)

    def __rsub__(self, whom):
        try: tot = whom.__coefs.copy()
        except AttributeError: tot = {(): whom}

        zero = self._zero
        for k, v in self.__coefs.items():
            tot[k] = tot.get(k, zero) - v

        return Multinomial(tot)

    def addboks(key, cle): # tool func for __mul__
        tot = [0] * max(len(key), len(cle))

        i = len(key)
        while i > 0:
            i = i - 1
            tot[i] = key[i]

        i = len(cle)
        while i > 0:
            i = i - 1
            tot[i] = tot[i] + cle[i]

        while tot and tot[-1] == 0: tot = tot[:-1]
        return tuple(tot)

    def __mul__(self, whom, add=addboks):
        term = {}
        try: bok = whom.__coefs
        except AttributeError:
            for key, val in self.__coefs.items():
                term[key] = val * whom
        else:
            zero = self._zero * whom._zero
            for key, val in self.__coefs.items():
                for cle, lue in bok.items():
                    tot = add(key, cle)
                    term[tot] = term.get(tot, zero) + val * lue

        return Multinomial(term)

    del addboks
    __rmul__ = __mul__

    def __pow__(self, n, mod=None):
        result = 1
        if mod is None:
            x = self
            def step(b, x, r):
                if b: r *= x
                return x * x, r
        else:
            x = self % mod
            def step(b, x, r, m=mod):
                if b: r = (r * x) % m
                return (x * x) % m, r

        while n >= 1:
            n, b = divmod(n, 2)
            x, r = step(b, x, r)

        return result

    def __divmod__(self, whom):
        # solve self = q * whom + r with r `suitably less than (?)' whom
        raise NotImplementedError

    def subboks(this, that): # tool func for derivative (and divmod ?)
        row, scale = [0] * max(len(this), len(that)), 1

        i = len(this)
        while i > 0:
            i = i - 1
            row[i] = this[i]

        i = len(that)
        while i > 0:
            i = i - 1
            if that[i] > 0:
                v = row[i] - that[i]
                if v < 0: return None, 1
                scale = reduce(lambda x, y: x * y, range(row[i], v, -1), scale)
                row[i] = v

        while row and row[-1] == 0: row = row[:-1]
        return tuple(row), scale

    def derivative(self, key, sub=subboks):
        """Differentiate; key says how often in which variables. """
        bok = {}
        while key and key[-1] == 0: key = key[:-1]

        for k, v in self.__coefs.items():
            q, s = subboks(k, key)
            if q is not None: bok[q] = s * v

        return Multinomial(bok)

    del subboks

    def __call__(self, *args):
        if len(args) != len(self.profile):
            raise TypeError('Multinomial in n variables needs n values', len(self.profile))

        result = self._zero
        for key in self._powers:
            val, i = self.__coefs[key], len(args)
            while i > 0:
                i = i - 1
                try: p = key[i]
                except IndexError: pass
                else: val = val * args[i]**p

            result = result + val

        return result

    def __nonzero__(self): return self.rank >= 0
    def __eq__(self, whom): return (self - whom).rank < 0
    def __neg__(self): return 0 - self

    def __repr__(self): return self._repr
    variablenames = 'zyxwvutsrqpnmlkhgfdcba' # skip o,i,j,e [0, sqrt(-1), exp(1)]

    def _lazy_get_rank_(self, ig):
        if any(self.__coefs.values()):
            return max(self._ranks)
        return -1

    def _lazy_get_uniform_(self, ig): # a.k.a. homogeneous
        return all(x == self.rank for x in self._ranks)

    def _lazy_get_profile_(self, ig, top=lambda *x: max([0] + [e for e in x if e])):
        # For each variable, the highest power of it in any term of self:
        return tuple(map(top, *self.__coefs.keys()))
    # NB: need map(), to pad short keys with None instead of zip()'s truncation;
    # top() takes out the None entries for us.

    # support ...

    def _lazy_get__zero_(self, ig):
        try: return self.__coefs.values()[0] * 0
        except IndexError: return 0

    def format(num):
        # it might be nice to also cope with non-scalar coefficients ...
        try:
            if num.imag == 0:
                num = num.real
                raise AttributeError
        except AttributeError:
            if num == int(num): num = int(num)

        ans = str(num)
        if ans[0] != '-': return ' +' + ans
        else: return ' ' + ans

    def powname(seq, noms):
        i, row = len(seq), []
        while i > 0:
            i = i - 1
            if seq[i] == 1: row.append(noms[i])
            elif seq[i]: row.append('%s**%d' % (noms[i], seq[i]))

        return '*'.join(row)

    def _lazy_get__repr_(self, ig, fmt=format, nom=powname):
        result, names, keys = '', self.variablenames, self._powers

        for key in keys:
            val = self.__coefs[key]
            if key:
                if val == 1: result = result + ' +'
                elif val == -1: result = result + ' -'
                else: result = result + fmt(val) + '*'
                result = result + nom(key, names)

            else: result = result + fmt(val)

        lamb = 'lambda ' + ', '.join(names[:len(self.profile)]) + ':'
        if not result: return lamb + ' 0'
        if result[:2] == ' +': return lamb + ' ' + result[2:]
        return lamb + result

    del format, powname

    def _lazy_get__ranks_(self, ign):
        return tuple(sum(k) for k in self.__coefs.keys())

    def keyorder(that, this):
        sign = cmp(sum(this), sum(that)) or cmp(len(this), len(that))
        if sign: return sign

        i = len(this) # == len(that)
        while i > 0:
            i = i - 1
            sign = cmp(this[i], that[i])
            if sign: return sign

        return 0

    def _lazy_get__powers_(self, id, order=keyorder):
        row = self.__coefs.keys()
        row.sort(order)
        return tuple(row)

    del keyorder
