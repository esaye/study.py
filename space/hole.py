"""Description of black holes.

$Id: hole.py,v 1.2 2005-04-09 10:20:09 eddy Exp $
"""

from const import Vacuum, Quantum, Cosmos, Thermal, pi, Object, Quantity

class BlackHole (Object):
    # Pass at least one of mass, radius, (surface) gravity, temperature to constructor.
    """A simple Schwarzschild black hole.

Unlike other species of particle, black holes can have pretty much any mass.
Their mass, radius, apparent temperature and surface gravity are all simply
related to one another.  Any one of these four quantities suffices for our
initializer.  See the documentation of Thermal.Hawking and Cosmos.Schwarzschild
for details; and http://casa.colorado.edu/~ajsh/hawk.html
"""

    def _lazy_get_mass_(self, ig, tm=Thermal.Hawking):
        return tm / self.temperature

    def _lazy_get_radius_(self, ig, mr=Cosmos.Schwarzschild):
        return mr * self.mass

    def _lazy_get_gravity_(self, ig, rg=Vacuum.c**2 * .5):
        return rg / self.radius

    def _lazy_get_temperature_(self, ig, gt=Quantum.hbar * .5 / pi / Vacuum.c / Thermal.k):
        return gt * self.gravity

    def _lazy_get_tidal_(self, ig):
        return 2 * self.gravity / self.radius

    def _lazy_get_diameter_(self, ignored):
        return 2 * self.radius

    def _lazy_get_circumference_(self, ignored, tp=2 * pi):
        return tp * self.radius

    def _lazy_get_area_(self, ignored, fp=4*pi):
        return fp *  self.radius ** 2

    def _lazy_get_volume_(self, ignored, ftp=pi/.75):
        return ftp *  self.radius ** 3

    def _lazy_get_luminosity_(self, ig, q=Quantum.h / 30, k=Cosmos.kappa):
        """Rate of energy loss due to Hawking radiation.

The power output of the thermal radiation - the Hawking luminosity - is given by
the usual Stefan-Boltzmann law,

        L = A sigma T**4

where A is the surface area, 4 pi r**2, and sigma is the Stefan-Boltzmann
constant.  These yield

        L = 4 pi sigma (hbar c / 4 / pi / k)**4 / r**2
          = 4 pi**3 / 60 / c**2 / hbar**3 (hbar c / 4 / pi)**4 (c**2 / 2 / G / m)**2
          = hbar c**6 / 15 / pi / 1024 / G**2 / m**2
          = h / 480 / kappa**2 / m**2

However, L rises by a factor N/2 where N is the number of particle types having
mass less than k.T, counting two helicity types of photons separately so that N
is at least 2 for any positive T.  (But presumably this is actually true for the
Stefan-Boltzmann law generally.)  Note that k.T/c/c = hbar.c/8/pi/G/m is the
mass limit for particle types; the constant this divides by m is a mass squared
and the mass in question is just the Planck mass divided by 4.pi.

Neutrinos are the least massive particles type, so should provide the lowest
temperature deviation from the above; which, once observed, would give us a
datum on the mass of neutrinos.  Since the Stefan-Boltzmann law has presumably
been confirmed with reasonable precision, and I suppose we don't yet have a
datum from this on the neutrino mass, I guess this gives us a lower bound on the
neutrino mass.  The known upper bound of 82e-36 kg (see below) implies a
temperature of around half a million Kelvin below which we should notice
neutrinos complicating this law.  Provided the same modification applies to
normal thermal radiation, we might even be able to detect this ...
"""
        return q / (k * 4 * self.mass)**2

    MassCubedRate = Quantity(-.1, Quantum.h / (4 * Vacuum.c * Cosmos.kappa)**2,
                             """Rate of decrease of the cube of a black hole's mass.

  ... the evaporation time is shorter for smaller black holes (evaporation time
  t is proportional to M**3), and black holes with masses less than about 1e11
  kg (the mass of a small mountain) can evaporate in less than the age of the
  Universe.

Observe that dm/dt = -L/c/c with N = 2 unchanging would give
        d(m**3)/dt = 3 m**2 dm/dt = -h / 160 / c**2 / kappa**2
constant, confirming that time to evaporate is proportional to cube of mass:
cube of mass decreases at a constant rate, 11.897 peta kg**3 / s.  This (a dozen
cubic tonnes per microsecond) also deserves to be imortalized as someone's
constant ;^)

The above-mentioned 1e11 kg black hole that would evaporate within the present
age of the universe has an initial temperature of over a tera Kelvin.  Which is
at least tiny compared to the Planck temperature ... to evaporate within a
century, a black hole would need to have mass at most a third of a million
tonnes; with a radius less than half an atto-metre, this would be a very good
approximation to a point mass.
""")
    VolumeRate = Quantity(-.1 / 768 / pi**2, Quantum.h * Cosmos.kappa * Vacuum.c,
                          """Rate of decrease of volume of a black hole.

Given that r = 2.G.m/c/c is proportional to m, we can infer (from MassCubedRate,
q.v.) that r**3 also decreases at the constant rate h kappa c / 10240 / pi**3,
or about 39e-66 cubic metres per second, whence the nominal volume of the black
hole decreases at 4.pi/3 times this, i.e. h kappa c / 7680 / pi**2 or about
0.16e-63 cubic metres per second.  With k.T inversely proportional to mass, we
can infer that (k.T)**-3 decreases at the fixed rate pi**3 kappa / (h c)**2 /
20, so 1/T**3 decreases at 6.433e-54 / second / Kelvin**3.  Note that the a
black hole hot enough to boil Osmium at its surface (i.e. above 5300 Kelvin)
would have radius about 32 nano metres, mass 23 peta tonnes (about 3e-4 of the
Moon's mass) yet would still take over 28e33 years to boil away ...

Of course, all these evaporation times are over-estimates; they ignore the fact
that N increases as T grows.  At half a peta Kelvin k.T/c/c exceeds the mass of
the heaviest quark, Truth; at 2.6 peta Kelvin it exceeds the mass of a Uranium
atom.  If N only counts fundamental particle types, it's at least 14 at the
first of these and I can't say for sure that it ever gets above that; othewise,
it's functionally infinite (every isotope, including all the unstable ones, of
every known element; plus quite a lot of stranger things) by around the second,
which is only five times as big.  A half peta Kelvin black hole has mass just
over a quarter of a million tonnes and radius under 0.4e-18 metres; with N=14
this will take about 7 years to evaporate.

It seems reasonable to guess that nothing but the neutrinos has less mass than
the electron.  On that assumption, N is at most 5 for temperatures below 5.9
giga Kelvin, radii above 31 femto metres (of order the size of nuclei), masses
above 21 giga tonne.  Even if we (conservatively) suppose N jumps to infinity at
this threshold, we only eliminate the last 23 peta years of the time a black
hole takes to evaporate; and at least 40% of the remainder survives the
N-scaling; for just the age of the universe to remain requires only 22 million
tonnes of extra mass, about one part in a thousand.  Thus any black hole bigger
or colder than the threshold just described will last essentially for ever; and
even an asteroid a couple of kilometres across has more mass than that.
""")

_rcs_log = """
$Log: hole.py,v $
Revision 1.2  2005-04-09 10:20:09  eddy
Widened the N<6 region up to the electron mass.

Revision 1.1  2005/04/09 10:05:15  eddy
Initial revision
"""