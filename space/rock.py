# -*- coding: iso-8859-1 -*-
"""Functions to aid in constructing moons, asteroids and other clutter.

$Id: rock.py,v 1.3 2005-03-13 19:09:59 eddy Exp $
"""

from basEddy.units import tophat, mega, day, km, metre, kg, litre
from space.body import Planetoid, Planet
from space.common import Spheroid, Orbit, Spin

# Packaging data taken from NASA atlas, mostly pp 325--327
def NASAshell(major, minor=None, minim=None, Sp=Spheroid, u=km):
    major =  major * u
    if minor is not None: minor = minor * u
    if minim is not None: minim = minim * u
    return Sp(major, minor, minim) # should really be a Surface ...

def NASAorbit(planet, sma, per, tilt = 90 * (.5 + tophat),
              u=day, centi=.01*tophat, Mm=mega*metre, O=Orbit, S=Spin, **what):
    # no eccentricities supplied ... but they are all bound orbits ...
    # no tilt supplied, aside from retrograde or not ...
    if per < 0: tilt, per = tilt + 90, -per
    # no error bars supplied, but all periods gave two decimal places
    # sma is really radius / (1 - eccentricity), but endure it and let per's error-bar infect it
    return apply(O, (planet, sma * Mm, S(u * (per + centi), tilt)), what)

def NASAdata(what, found, mass, rho, skin, shell, m=kg, d=kg/litre):
    what['discovery'] = found
    if mass is not None: what['mass'] = mass * 1e20 * m
    if rho  is not None: what['density'] = rho * d
    if skin is not None: shell.also(material=skin)

def NASAtrojan(name, found, boss, phase, shell, skin=None, mass=None, rho=None, P=Planet, **what):
    NASAdata(what, found, mass, rho, skin, shell)
    what.update({ 'boss': boss })

    # there may be a better way to encode this ...
    ans = apply(P, (name, shell, boss.orbit), what)
    boss.Lagrange[phase].append(ans)
    return ans

def NASAmoon(name, planet, found, sma, per, shell, skin=None, mass=None, rho=None, P=Planet, **what):
    NASAdata(what, found, mass, rho, skin, shell)
    return apply(P, (name, shell, NASAorbit(planet, sma, per)), what)

def NamedOrbit(name, planet, sma, per, P=Planetoid, **what):
    # No data bon the bodies themselves, but good data on name and discovery
    what['orbit'] = NASAorbit(planet, sma, per, name=name)
    return apply(P, (name,), what)

def SAOmoon(planet, found, nom, sma, per, name=None, P=Planetoid):
    # Names are catalogue numbers and we have no data on the bodies themselves ...
    assert planet.name[0] == nom[0] # the rest of nom is a number, with maybe a trailing #
    if name is None: name = 'S/%d %s' % (found.year, nom)
    return P(name, orbit=NASAorbit(planet, sma, per, name=name), discovery=found)

del Planetoid, Planet, Spheroid, Orbit, Spin, tophat, mega, day, km, metre, kg, litre

_rcs_log = """
$Log: rock.py,v $
Revision 1.3  2005-03-13 19:09:59  eddy
Clean up import/export.

Revision 1.2  2005/03/12 17:57:42  eddy
typo-fix: appply

Initial Revision 1.1  2005/03/12 15:33:57  eddy
"""