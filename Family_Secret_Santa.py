import random
from collections import defaultdict
from openpyxl import Workbook

# --------------------------------------------------------
# Penalty Parameters
# --------------------------------------------------------
MAX_CADEAUX_IDEAL = 2                 # ideally 1 adult + 1 child
PENALITE_PARENTS_ENFANTS = 25          # strong penalty
PENALITE_GRANDPARENTS_PETITENFANT = 25 # strong penalty
PENALITE_MEMES_GRANDS_PARENTS = 20     # strong penalty (e.g., cousins)
PENALITE_GP_TO_GP = 15                 # moderate penalty for GP↔GP
PENALITE_TROP_CADEAUX = 40             # if a giver offers to more than 2 people
BONUS_INIT = -5                        # encourage those who haven’t given yet
PENALITE_2_ADULTES = 100               # avoid 2 adults from the same giver
PENALITE_2_ENFANTS = 10                # avoid 2 children from the same giver
BONUS_MIXTE = -5                       # encourage adult + child mix

# --------------------------------------------------------
# Family Definitions
# --------------------------------------------------------
familles = [
    {"parents": ["Lea"], "enfants": ["Arie","Mila"], "grands_parents": ["Dov", "Michèle"]},
    {"parents": ["Nanette","Ofir"], "enfants": ["Emma","Avigael"], "grands_parents": ["Dov", "Michèle"]},
    {"parents": ["Jérémie"], "grands_parents": ["Dov", "Michèle"]},
    {"parents": ["Benjamin L","Jade"], "enfants": ["Ora","Hersh"], "grands_parents": ["Dov", "Michèle"]},
    {"parents": ["Jonathan","Laura"], "enfants": ["Joseph","Noah","Mina"], "grands_parents": ["Nicole"]},
    {"parents": ["Sarah","JD"], "enfants": ["Elsie","Ethan","Ariel"], "grands_parents": ["Nicole"]},
    {"parents": ["Samuel","Anaelle"], "enfants": ["Isaac","Amos","Adèle","Ida"], "grands_parents": ["Nicole"]},
    {"parents": ["Jonas","Solenne"], "grands_parents": ["Roland","Valérie"]},
    {"parents": ["Julia"], "grands_parents": ["Roland","Valérie"]},
    {"parents": ["Gabriel"], "grands_parents": ["Roland","Valérie"]},
    {"parents": ["Nina","Benjamin M"], "enfants": ["Saul","Jules"], "grands_parents": ["Judith","Fabrice"]},
    {"parents": ["Noémie","JB"], "enfants": ["Yael","Abigail"], "grands_parents": ["Judith","Fabrice"]},
    {"parents": ["Romain","Eva"], "enfants": ["Anya"], "grands_parents": ["Judith","Fabrice"]},
    {"parents": ["Meredith"], "grands_parents": ["Judith","Fabrice"]},
]

# --------------------------------------------------------
# Prepare participant sets
# --------------------------------------------------------
participants = set()
enfants = set()
adults = set()
grands_parents = set()
famille_of = {}                     # person → family ID
grands_parents_of_person = defaultdict(set)  # person → grandparents set
parents_of_person = defaultdict(set)         # child → parents

for fid, f in enumerate(familles):
    gps = f.get("grands_parents", [])
    parents = f.get("parents", [])
    kids = f.get("enfants", [])

    for gp in gps:
        participants.add(gp)
        adults.add(gp)
        grands_parents.add(gp)
        grands_parents_of_person[gp].add(gp)  # a GP is their own ancestor GP

    for p in parents:
        participants.add(p)
        adults.add(p)
        famille_of[p] = fid
        for gp in gps:
            grands_parents_of_person[p].add(gp)

    for e in kids:
        participants.add(e)
        enfants.add(e)
        famille_of[e] = fid
        for gp in gps:
            grands_parents_of_person[e].add(gp)
        for p in parents:
            parents_of_person[e].add(p)

participants = list(participants)
donneurs_possibles = [p for p in participants if p not in enfants]  # children don’t give gifts

# --------------------------------------------------------
# Backtracking Algorithm
# --------------------------------------------------------
def secret_santa():
    attribution = {}
    cadeaux_par_donneur = defaultdict(int)

    def backtrack(i):
        if i >= len(participants):
            return True

        receveur = participants[i]
        candidats = [d for d in donneurs_possibles if d != receveur]
        scored = []

        for d in candidats:
            score = 0

            # 1) parent ↔ child penalty
            if (d in parents_of_person[receveur]) or (receveur in parents_of_person[d]):
                score += PENALITE_PARENTS_ENFANTS

            # 2) grandparent ↔ grandchild penalty
            if len(grands_parents_of_person[d] & grands_parents_of_person[receveur]) > 0:
                if d in grands_parents and receveur in enfants:
                    score += PENALITE_GRANDPARENTS_PETITENFANT
                elif d in enfants and receveur in grands_parents:
                    score += PENALITE_GRANDPARENTS_PETITENFANT
                else:
                    score += PENALITE_MEMES_GRANDS_PARENTS

            # 3) grandparent ↔ grandparent penalty
            if d in grands_parents and receveur in grands_parents:
                score += PENALITE_GP_TO_GP

            # 4) giver already gives too many gifts
            if cadeaux_par_donneur[d] >= MAX_CADEAUX_IDEAL:
                score += PENALITE_TROP_CADEAUX

            # 5) encourage new givers
            if cadeaux_par_donneur[d] == 0:
                score += BONUS_INIT

            # 6) encourage adult + child mix
            if cadeaux_par_donneur[d] == 1:
                previous = [r for r, g in attribution.items() if g == d][0]
                if previous in adults and receveur in adults:
                    score += PENALITE_2_ADULTES
                if previous in enfants and receveur in enfants:
                    score += PENALITE_2_ENFANTS
                if (previous in adults and receveur in enfants) or (previous in enfants and receveur in adults):
                    score += BONUS_MIXTE

            scored.append((score, d))

        scored.sort(key=lambda x: x[0])

        for _, d in scored:
            attribution[receveur] = d
            cadeaux_par_donneur[d] += 1

            if backtrack(i + 1):
                return True

            # rollback
            cadeaux_par_donneur[d] -= 1
            del attribution[receveur]

        return False

    if not backtrack(0):
        raise RuntimeError("No valid solution found.")
    return attribution

# --------------------------------------------------------
# Execution
# --------------------------------------------------------
random.seed(42)
attribution = secret_santa()

# Organize results
offre_par = defaultdict(list)
recoit_de = defaultdict(str)
for r, d in attribution.items():
    offre_par[d].append(r)
    recoit_de[r] = d

# --------------------------------------------------------
# Console Output
# --------------------------------------------------------
print("---- Who gives to whom ----")
for d in sorted(offre_par):
    enfants_list = [x for x in offre_par[d] if x in enfants]
    adultes_list = [x for x in offre_par[d] if x in adults]
    ligne = f"{d} gives"
    if enfants_list:
        ligne += " to child " + ", ".join(enfants_list)
    if adultes_list:
        if enfants_list:
            ligne += " and"
        ligne += " to adult " + ", ".join(adultes_list)
    print(ligne)

print("\n---- Who receives from whom ----")
for r in sorted(recoit_de):
    print(f"{r} receives from {recoit_de[r]}")

# --------------------------------------------------------
# Export Excel
# --------------------------------------------------------
wb = Workbook()

# Sheet "Gives To"
ws1 = wb.active
ws1.title = "Gives To"
ws1.append(["This person gives", "to this child", "to this adult"])

for d in sorted(offre_par):
    enfants_list = [x for x in offre_par[d] if x in enfants]
    adultes_list = [x for x in offre_par[d] if x in adults]
    ws1.append([
        d,
        ", ".join(enfants_list) if enfants_list else "",
        ", ".join(adultes_list) if adultes_list else "",
    ])

# Sheet "Receives From"
ws2 = wb.create_sheet(title="Receives From")
ws2.append(["This person receives from"])
for r in sorted(recoit_de):
    ws2.append([f"{r} receives from {recoit_de[r]}"])

wb.save("Secret_Santa_Result.xlsx")
print("\nResults exported to Secret_Santa_Result.xlsx")
