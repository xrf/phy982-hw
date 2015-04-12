#!/usr/bin/env python
from common import *
from hw2_data import *

def plot_rdcs(name, data, charge_product):
    import subprocess
    from pandas import DataFrame
    data = DataFrame(data)
    data["rdcs_min"] = data["rdcs"] - data["rdcs_err"]
    data["rdcs_max"] = data["rdcs"] + data["rdcs_err"]
    try:
        check_call_with_input(("Rscript", "-"), plot_template.format(
            data=data.to_csv(sep=" ", na_rep="nan", index=False),
            units="(mb/sr)" if charge_product == 0 else "Rutherford",
            outname=name,
        ).encode("utf-8"))
    except subprocess.CalledProcessError:
        import sys
        sys.exit(1)

def run_fresco(name, fresco_input, remote=REMOTE):
    from shutil import rmtree
    work_dir = "dist/" + name
    remote_dir = "tmp/fresco/" + name

    # get a clean working directory
    rmtree(work_dir, ignore_errors=True)
    mkdirs(work_dir)

    # prepare the inputs
    write_file(work_dir + "/fresco.in",  fresco_input)

    # calculate
    output = ssh(remote, ("mkdir -p " + sh_escape(remote_dir) +
                          " && cd " + sh_escape(remote_dir) +
                          " && /user/nunes/bin/x86_64/fresco",),
                 input=fresco_input.encode("utf-8"))
    scp((remote + ":" + remote_dir + "/*", work_dir))
    ssh(remote, ("rm -r " + sh_escape(remote_dir),))
    write_file(work_dir + "/fresco.out", output.decode("utf-8"))

def run_sfresco(name, fresco_input, search_input, remote=REMOTE):
    from shutil import rmtree
    work_dir = "dist/" + name
    remote_dir = "tmp/sfresco/" + name
    sfresco_input = sfresco_template

    # get a clean working directory
    rmtree(work_dir, ignore_errors=True)
    mkdirs(work_dir)

    # prepare the inputs
    write_file(work_dir + "/search.in",  search_input)
    write_file(work_dir + "/fresco.in",  fresco_input)
    write_file(work_dir + "/sfresco.in", sfresco_input)

    # calculate
    ssh(remote, ("mkdir -p " + sh_escape(remote_dir),))
    scp((work_dir + "/search.in", work_dir + "/fresco.in",
         remote + ":" + remote_dir))
    output = ssh(remote, ("cd " + sh_escape(remote_dir) +
                          " && /user/nunes/bin/x86_64/sfresco",),
                 input=sfresco_input.encode("utf-8"))
    scp((remote + ":" + remote_dir + "/*", work_dir))
    ssh(remote, ("rm -r " + sh_escape(remote_dir),))
    write_file(work_dir + "/sfresco.out", output.decode("utf-8"))

def make_potential_terms(A_p, A_t, r_c, Vras,
                         radius_factor=1, enable_imag=True,
                         overrides={}):
    terms = {0: {"ap": A_p, "at": A_t, "rc": r_c * radius_factor}}

    # place the parameters in the correct positions
    term_type = 1
    for i, (V, r, a) in enumerate(zip(*(Vras[i::3] for i in range(3)))):
        real = i % 2 == 0
        if V != 0 and (real or enable_imag):
            if term_type in terms:
                term = terms[term_type]
            else:
                term = {}
                terms[term_type] = term
            offset = 3 * (not real)
            term[offset]     = V
            term[offset + 1] = r * radius_factor
            term[offset + 2] = a
        if not real:
            term_type += 1

    for name, value in overrides.items():
        i, j = parameter_indices[name]
        terms[i - 1][j - 1] = value

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

def make_fresco_input(energy, projectile,
                      radius_factor=1, enable_imag=True, overrides={}):
    projectile_charge = CHARGE[projectile]

    p    = params[(params.projectile == projectile) &
                  (params.energy == energy)].iloc[0][2:]
    Vras = p[:-1]
    r_c  = p[-1]

    terms = make_potential_terms(
        projectile_mass,
        target_mass,
        r_c,
        Vras,
        radius_factor=radius_factor,
        enable_imag=True,
        overrides=overrides,
    )
    pot_str = "\n".join(" &POT {0} /".format(format_pairs(term))
                        for term in terms)

    return fresco_template.format(
        R_match=R_match,
        J_max=J_max,
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
    )

def parse_fresco_output(fn):
    '''Str -> {"angle": Float, "rdcs": Float}'''
    from re import MULTILINE, search
    from pandas import DataFrame
    data = []
    with open(fn, "rt") as f:
        for line in f:
            if (line.startswith("#") or
                line.startswith("@") or
                line.strip() == "END"):
                continue
            data.append(tuple(map(float, line.split())))
    data = DataFrame(data, columns=("angle", "rdcs"))
    return data

def parse_fit_case(projectile, energy, case):
    '''(Str, Float, {
        [-]"parameters": [{
            "name":    Str,
            "initial": Float,
            "step":    Float,
            ...
        }],
        ...
    })'''
    parameters = case.pop("parameters")
    parameters = list(parameters)       # make copy
    for i, parameter in enumerate(parameters):
        parameter = dict(parameter) # make copy
        parameters[i] = parameter
        name    = parameter["name"]
        initial = parameter.pop("initial")
        parameter["pline"], parameter["col"] = \
            parameter_indices[name]
        parameter["kp"]   = parameter.get("kp", 1)
        parameter["kind"] = parameter.get("kind", 1)
        parameter["potential"] = initial
    params_str = "\n".join(" &variable {0} /".format(format_pairs(parameter))
                           for parameter in parameters)
    expt = expt_data[(expt_data.projectile == projectile) &
                     (expt_data.energy == energy)]
    return search_template.format(
        num_parameters=len(parameters),
        num_expt_dataset=1,
        parameters=params_str,
        expt_data=expt[["angle", "dcs", "dcs_err"]]
                  .to_csv(sep=" ", na_rep="nan", index=False, header=False),
    )

def parse_sfresco_output(fn):
    import pandas as pd
    stage = 0
    expt_data = []
    theory_data = []
    with open(fn) as f:
        for line in f:
            if (line.startswith("#") or
                line.startswith("@") or
                line.strip() == ""):
                continue
            if line.strip() == "&":
                stage += 1
                continue
            if stage == 0:
                expt_data.append(tuple(map(float, line.split())))
            elif stage == 1:
                row = tuple(map(float, line.split()))
                if row[0] != 0:
                    theory_data.append(row)
            else:
                assert False
    expt_data   = pd.DataFrame(expt_data, columns=("angle", "dcs", "dcs_err"))
    theory_data = pd.DataFrame(theory_data, columns=("angle", "dcs"))
    expt_data["origin"]   = "expt"
    theory_data["origin"] = "theory"
    return pd.concat((expt_data, theory_data))

def do_fit_cases(name_template):
    for case in fit_cases:
        case = dict(case)               # make a copy
        name       = case.pop("name")
        projectile = case.pop("projectile")
        energy     = case.pop("energy")
        charge_product = target_charge * CHARGE[projectile]
        search_input = parse_fit_case(projectile, energy, case)
        fresco_input = make_fresco_input(energy, projectile, **case)
        name = name_template.format(target=target, name=name,
                                    projectile=projectile)
        run_sfresco(name, fresco_input, search_input)
        work_dir = "dist/" + name
        data = parse_sfresco_output(work_dir + "/search.plot")
        data["energy"]            = energy
        data["target_charge"]     = target_charge
        data["projectile_charge"] = CHARGE[projectile]
        maybe_divide_rutherford(data)
        plot_rdcs(name, data, charge_product)

def do_fresco_cases(name_template):
    from pandas import concat
    for case in fresco_cases:
        case = dict(case)               # make a copy
        name       = case.pop("name")
        projectile = case.pop("projectile")
        energy     = case.pop("energy")
        charge_product = target_charge * CHARGE[projectile]
        fresco_input = make_fresco_input(energy, projectile, **case)
        name = name_template.format(target=target, name=name,
                                    projectile=projectile)
        run_fresco(name, fresco_input)
        work_dir = "dist/" + name
        data = parse_fresco_output(work_dir + "/fort.16")
        data["origin"]        = "theory"
        data["energy"]        = energy
        data["target_charge"] = target_charge
        expt = expt_data[(expt_data.projectile == projectile) &
                         (expt_data.energy     == energy)]
        plot_rdcs(name, concat((data, expt)), charge_product)

def do_fresco_quad_cases(name_template, group_template):
    from pandas import concat
    for group, quad in fresco_quad_cases.items():
        datasets = []
        for case in quad:
            case = dict(case)
            name       = case.pop("name") + "-" + group
            energy     = case.pop("energy")
            projectile = case.pop("projectile")
            charge_product = target_charge * CHARGE[projectile]
            fresco_input = make_fresco_input(energy, projectile, **case)
            name = name_template.format(target=target, name=name,
                                        projectile=projectile)
            run_fresco(name, fresco_input)
            work_dir = "dist/" + name
            data = parse_fresco_output(work_dir + "/fort.16")
            datasets.append(data)
            data["origin"]     = "theory"
            data["projectile"] = projectile
            data["energy"]     = energy
            datasets.extend((
                data,
                expt_data[(expt_data.projectile == projectile) &
                          (expt_data.energy     == energy)],
            ))
        data = concat(datasets)
        write_table(group_template.format(group=group) + ".dat",
                    data[["origin", "projectile", "energy",
                          "angle", "angle_err", "rdcs", "rdcs_err"]])

fresco_template = """
Fresco;
NAMELIST
 &FRESCO hcm=0.1 rmatch={R_match}
         jtmin=0.0 jtmax={J_max}  absend=0.001
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
"""[1:]

sfresco_template = """
search.in
min
migrad
end
plot
"""[1:]

search_template = """
'fresco.in' 'fresco.out'
{num_parameters} {num_expt_dataset}
{parameters}
&data iscale=2 idir=0 lab=F abserr=T/
{expt_data}
&
"""[1:]

plot_template = """
source("common.r")

data <- read.table(textConnection("{data}"), header=TRUE)

(ggplot(subset(data, origin == "expt"), aes(x=angle, y=rdcs, color=origin))
 + geom_point(size=1)
 + geom_line(aes(x=angle, y=rdcs), subset(data, origin == "theory"))
 + geom_errorbar(aes(x=angle, ymin=rdcs_min, ymax=rdcs_max))
 + scale_y_log10()
 + annotation_logticks(sides="l")
 + xlab("angle /deg")
 + ylab(paste0("differential cross section /{units}]"))
 + mytheme
 + save("{outname}.svg"))
"""

fresco_quad_cases = dict(({1.0: "1", 1.5: "1-large-radius"}[radius_factor], (
    {
        "name": "low",
        "projectile": "p",
        "energy": 8.2,
        "radius_factor": radius_factor,
    },
    {
        "name": "high",
        "projectile": "p",
        "energy": 55.0,
        "radius_factor": radius_factor,
    },
    {
        "name": "low",
        "projectile": "n",
        "energy": 5.0,
        "radius_factor": radius_factor,
    },
    {
        "name": "high",
        "projectile": "n",
        "energy": 24.0,
        "radius_factor": radius_factor,
    },
)) for radius_factor in (1.0, 1.5))

fresco_cases = (
    # {
    #     "name": "low-vol-re-sens-V",
    #     "projectile": "p",
    #     "energy": 8.2,
    #     "overrides": {
    #         "Vvr": 53.5 * 1.1,
    #     },
    # },
)

fit_cases = (
    {
        "name": "low-vol-re",
        "projectile": "p",
        "energy": 8.2,
        "overrides": {"Vor": 0, "ror": 0, "aor": 0},
        "parameters": (
            {
                "name": "Vvr",
                "initial": 53.5,
                "step": 0.1,
            },
            {
                "name": "rvr",
                "initial": 1.25,
                "step": 0.01,
            },
            {
                "name": "avr",
                "initial": 0.65,
                "step": 0.01,
            },
        ),
    },
    {
        "name": "low-nofit",
        "projectile": "p",
        "energy": 8.2,
        "parameters": (),
    },
    {
        "name": "low-surf-im",
        "projectile": "p",
        "energy": 8.2,
        "overrides": {"Vor": 0, "ror": 0, "aor": 0},
        "parameters": (
            {
                "name": "Wsi",
                "initial": 13.5,
                "step": 0.1,
            },
            {
                "name": "rsi",
                "initial": 1.25,
                "step": 0.01,
            },
            {
                "name": "asi",
                "initial": 0.47 * 1.1,
                "step": 0.01,
            },
        ),
    },
    {
        "name": "low-both",
        "projectile": "p",
        "energy": 8.2,
        "overrides": {"Vor": 0, "ror": 0, "aor": 0},
        "parameters": (
            {
                "name": "Vvr",
                "initial": 84.6,
                "step": 0.1,
            },
            {
                "name": "rvr",
                "initial": 1.03,
                "step": 0.01,
            },
            {
                "name": "avr",
                "initial": 0.59,
                "step": 0.01,
            },
            {
                "name": "Wsi",
                "initial": 22.7,
                "step": 0.1,
            },
            {
                "name": "rsi",
                "initial": 1.3,
                "step": 0.01,
            },
            {
                "name": "asi",
                "initial": 0.55,
                "step": 0.01,
            },
        ),
    },
    {
        "name": "low-spinorb",
        "projectile": "p",
        "energy": 8.2,
        "parameters": (
            {
                "name": "Vvr",
                "initial": 89,
                "step": 0.1,
            },
            {
                "name": "rvr",
                "initial": 1.05,
                "step": 0.01,
            },
            {
                "name": "avr",
                "initial": 0.57,
                "step": 0.01,
            },
            {
                "name": "Wsi",
                "initial": 25,
                "step": 0.1,
            },
            {
                "name": "rsi",
                "initial": 1.2,
                "step": 0.01,
            },
            {
                "name": "asi",
                "initial": 0.25,
                "step": 0.01,
            },
            {
                "name": "Vor",
                "initial": 7.5,
                "step": 0.1,
            },
            {
                "name": "ror",
                "initial": 1.25,
                "step": 0.01,
            },
            {
                "name": "aor",
                "initial": 0.47,
                "step": 0.01,
                "valmin": 0.2,
            },
        ),
    },
)

parameter_indices = {
    "ap":  (1, 1),
    "at":  (1, 2),
    "rc":  (1, 3),
    "Vvr": (2, 1),
    "rvr": (2, 2),
    "avr": (2, 3),
    "Wvi": (2, 4),
    "rvi": (2, 5),
    "avi": (2, 6),
    "Vsr": (3, 1),
    "rsr": (3, 2),
    "asr": (3, 3),
    "Wsi": (3, 4),
    "rsi": (3, 5),
    "asi": (3, 6),
    "Vor": (4, 1),
    "ror": (4, 2),
    "aor": (4, 3),
    "Woi": (4, 4),
    "roi": (4, 5),
    "aoi": (4, 6),
}

# ============================================================================

if __name__ == "__main__":
    name_template  = "hw2-{target}-{projectile}-elastic-{name}"
    group_template = "hw2-{group}"
    do_fresco_quad_cases(name_template, group_template)
    do_fresco_cases(name_template)
    do_fit_cases(name_template)
