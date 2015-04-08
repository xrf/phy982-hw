#!/usr/bin/env python
from common import *

# hbar * c /(MeV fm)
HBAR_C = 197.326972

# fine structure constant
ALPHA = 7.29735257e-3

CHARGES = {
    "n": 0,
    "p": 1,
}

def rutherford_dcs(angle, E, z=1, Z=1):
    '''(deg, MeV, 1, 1) -> (mb/sr)'''
    from numpy import sin, pi
    return 10. / 16. * (ALPHA * z * Z * HBAR_C /
                        (E * sin(angle / 360. * pi) ** 2)) ** 2

def maybe_rutherford_dcs(angle, E, z=1, Z=1):
    '''(deg, MeV, 1, 1) -> (mb/sr OR unitless i)'''
    from numpy import where
    return where(z * Z != 0, rutherford_dcs(angle, E, z, Z), 1.)

template = """
Fresco;
NAMELIST
 &FRESCO hcm=0.1 rmatch={matching_radius}
	 jtmin=0.0 jtmax=50.0  absend=0.001
	 thmin=0.0 thmax=180.0 thinc=1.0
 	 chans=1 smats=2 xstabl=1
	 elab(1:1)={energy} /
 &PARTITION namep='{projectile}' massp={projectile_mass} zp={projectile_charge}
 	    namet='{target}' masst={target_mass} zt={target_charge}
            qval=0 nex=1  /
 &STATES jp={projectile_j} bandp={projectile_parity} ep=0.0
         jt={target_j} bandt={target_parity} et=0.0
         cpot=1 /
 &partition /
{potentials}
 &pot /
 &overlap /
 &coupling /
"""[1:-1]

#https://www-nds.iaea.org/cgi-bin/ripl_om_param.pl?Z=28&A=60&ID=4100&E1=8.2&E2=8.2
#https://www-nds.iaea.org/cgi-bin/ripl_om_param.pl?Z=28&A=60&ID=4102&E1=55&E2=55
#https://www-nds.iaea.org/cgi-bin/ripl_om_param.pl?Z=28&A=60&ID=401&E1=5&E2=5
#https://www-nds.iaea.org/cgi-bin/ripl_om_param.pl?Z=28&A=60&ID=100&E1=24&E2=24
params = """
   8.2   53.5  1.25  0.65    0.0  0.00  0.00    0.0  0.00  0.00   13.5  1.25  0.47    7.5  1.25  0.47    0.0  0.00  0.00   1.25
  55.0   42.4  1.16  0.75    6.2  1.37  0.37    0.0  0.00  0.00    2.5  1.37  0.37    6.0  1.06  0.78    0.0  0.00  0.00   1.25
   5.0   45.6  1.29  0.66    0.0  0.00  0.00    0.0  0.00  0.00    9.3  1.25  0.48    7.0  1.29  0.66    0.0  0.00  0.00   0.00
  24.0   47.0  1.17  0.75    3.7  1.26  0.58    0.0  0.00  0.00    6.2  1.26  0.58    6.2  1.01  0.75    0.0  0.00  0.00   0.00
"""[1:-1].split("\n")

cases =  tuple(map(record_to_dict, parse_table("""
projectile energy_type energy
p low   8.2
p high 55.0
n low   5.0
n high 24.0
""").to_records()))

name_template = "hw2-{target}-{projectile}-elastic-{energy_type}.in"

# Mass number of projectile and target
projectile_mass   = 1
projectile_j      = 1/2.
projectile_parity = +1
target        = "Ni60"
target_mass   = 60
target_charge = 28
target_j      = 0
target_parity = +1

def make_potential_terms(A_p, A_t, r_c, Vras):
    terms = {}

    # add Coulomb term if needed
    if r_c:
        terms[0] = {"ap": A_p, "at": A_t, "rc": r_c}

    # place the parameters in the correct positions
    term_type = 1
    real = True
    for V, r, a in zip(*(Vras[i::3] for i in range(3))):
        if V != 0:
            if term_type in terms:
                term = terms[term_type]
            else:
                term = {}
                terms[term_type] = term
            offset = 3 * (not real)
            term[offset]     = V
            term[offset + 1] = r
            term[offset + 2] = a
        if not real:
            term_type += 1
        real = not real

    # process one more time to fix the parameter names
    # and add supplementary parameters
    terms2 = []
    for term_type, term in terms.items():
        if term_type:
            term = dict(
                ("p{0}".format(param_index + 1) , param)
                for param_index, param in term.items()
            )
        term.update({"kp": 1, "type": str(term_type)})
        terms2.append(term)
    return terms2

def generate_inputs():
    for case in cases:

        index       = case["index"]
        energy      = case["energy"]
        energy_type = case["energy_type"]
        projectile  = case["projectile"]

        assert projectile in ("p", "n")
        projectile_charge = (projectile == "p") * 1

        p      = tuple(map(float, params[index].split()))
        assert energy == p[0]
        Vras   = p[1:-1]
        r_c    = p[-1]

        terms = make_potential_terms(projectile_mass, target_mass, r_c, Vras)
        pot_str = "\n".join(" &POT {0} /".format(format_pairs(term))
                            for term in terms)

        name = name_template.format(target=target, **case)

        write_file(name, template.format(
            matching_radius=60,
            energy=energy,
            projectile=projectile,
            projectile_mass=projectile_mass,
            projectile_charge=projectile_charge,
            projectile_j=projectile_j,
            projectile_parity=projectile_parity,
            target=target,
            target_mass=target_mass,
            target_charge=target_charge,
            target_j=target_j,
            target_parity=target_parity,
            potentials=pot_str,
        ))

def extract_rdcr(fn, fn_out):
    from re import MULTILINE, search
    from pandas import DataFrame
    data = []
    comments = []
    with open(fn, "rt") as f:
        for line in f:
            if line.startswith("#"):
                comments.append(line)
            elif not (line.startswith("#") or
                      line.startswith("@") or
                      line.strip() == "END"):
                data.append(tuple(map(float, line.split())))
    data = DataFrame(data, columns=("angle", "rdcs"))
    # the way projectile and energy are obtained here are quite hacky D:
    matched = search('^#legend string *0 "Lab energy *= *([.0-9eE+-]+)"',
                     "".join(comments), flags=MULTILINE)
    assert matched
    data["projectile"] = "p" if search("-p-", fn) else "n"
    assert search("-p-", fn) or search("-n-", fn)
    data["energy"]     = float(matched.group(1))
    data["angle_err"]  = None
    data["rdcs_err"]   = None
    write_table(fn_out, data)

if __name__ == "__main__":
    run_with_argv((
        generate_inputs,
        extract_rdcr,
    ))
