import csv
from re import S

groups = [
    "БВТ2101", "БВТ2102", "БВТ2103", "БВТ2104", "БВТ2105", "БВТ2106", "БВТ2107",
    "БВТ2108"
]

groups_id = {x: i for i, x in enumerate(groups)}
subjs = {}
s_max = 0
teachers = {}
t_max = 0
rooms = {}
rooms_t = {}
r_max = 0
tips = {'лек': 0, 'лаб': 1, 'пр': 2}
tips_m = ['лек', 'лаб', 'пр']
result = {}
with open('table.csv') as f:
    reader = csv.DictReader(f)
    day = -1
    time = -1
    parity = 0
    for row in reader:
        if row['day']:
            day += 1
            time = -1
        if row['id']:
            time += 1
        for group in groups:
            s = row[group]
            tip = ''
            if s:
                s = s.split('\n')
                l = len(s)
                if l == 0:
                    continue
                if l != 3 and l != 4 and l != 2:
                    raise ValueError(l, s)
                if l == 2:
                    subj, s = s
                    s = s.strip().split('  ')
                    if len(s) == 2:
                        teacher, tip = s
                        room = '1009'
                    elif len(s) == 1:
                        teacher, tip = s[0], 'пр'
                    else:
                        teacher, room, tip = s

                elif l == 3:
                    subj, teacher, room = s
                elif l == 4:
                    subj, teacher, _, room = s
                subj, teacher, room = map(lambda x: x.strip(),
                                          (subj, teacher, room))

                if subj not in subjs:
                    subjs[subj] = s_max
                    s_max += 1
                s = teacher.split('  ')
                if len(s) == 1:
                    ss = s[0].split()
                    if len(ss) == 2:
                        teacher = s[0]
                    elif len(ss) == 3:
                        teacher = ' '.join(ss[:2])
                        tip = ss[2]
                    elif len(ss) == 4:
                        teacher = ' '.join(ss[:2])
                        room = ss[2]
                        tip = ss[3]
                    else:
                        raise ValueError(s)
                elif len(s) == 3:
                    teacher, room, tip = s
                elif len(s) == 2:
                    ss = s[1].strip().split()
                    if len(ss) == 1:
                        teacher, tip = s
                    elif len(ss) == 2:
                        teacher, room, tip = s[0], ss[0], ss[1]
                    else:
                        raise ValueError(s)
                if teacher not in teachers:
                    teachers[teacher] = t_max
                    t_max += 1

                s = room.split(')')
                if len(s) == 2:
                    room = s[1].strip()
                room = room.lower().replace('ауд', '').replace('.', '').replace(
                    'авиамоторная', '').strip()
                if not tip:
                    raise ValueError('not tip' + row[group])
                tip = tip.lower().strip()
                if room:
                    if room not in rooms:
                        rooms[room] = r_max
                        rooms_t[room] = set()
                        r_max += 1
                    rooms_t[room].add(tips[tip])
                f = (groups_id[group], subjs[subj], teachers[teacher],
                     tips[tip])
                if f in result:
                    result[f] += 1
                else:
                    result[f] = 1

        parity ^= 1

print(result)

subjs_m = [''] * len(subjs)
for i in subjs:
    subjs_m[subjs[i]] = i

teachers_m = [''] * len(teachers)
for i in teachers:
    teachers_m[teachers[i]] = i

rooms_m = [''] * len(rooms)
for i in rooms:
    rooms_m[rooms[i]] = i
ss = {i: set() for i in range(len(groups))}

res_m = []
for group, subj, teacher, tip in result:
    ss[group].add(
        f'{subjs_m[subj]}, {tips_m[tip]}, {result[group, subj, teacher, tip]}')
    res_m.append({
        "group": group,
        "teacher": teacher,
        "subject": subj,
        "tip": tip,
        "count": result[group, subj, teacher, tip]
    })
w = ss[0]
for i in ss:
    w = w & ss[i]
for i in ss:
    print(i, ss[i].difference(w))

rooms_res = []
for i, room in enumerate(rooms_m):
    t = list(rooms_t[room])
    rooms_res.append([room, 4 if 0 in t else 1, t])

data = {
    "teachers": teachers_m,
    "subjects": subjs_m,
    "groups": groups,
    "tips": tips_m,
    "rooms": rooms_res,
    "inputs": res_m
}

import json
with open('input.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False)
