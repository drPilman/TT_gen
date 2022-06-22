import json
from dataclasses import dataclass
from random import randint, choice, shuffle, random
from tabulate import tabulate
import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
from tqdm import tqdm

history_fitness = []
fitness_av = [[], [], []]
TIME_IN_DAY = 6
DAYS_IN_WEEK = 6


@dataclass
class Inp:
    group: int
    teacher: int
    subject: int
    tip: int
    count: int


@dataclass
class ChromInfo:
    group: int
    teacher: int
    subject: int
    tip: int

    def __str__(self) -> str:
        return f'{teachers[self.teacher]} {subjects[self.subject]} {tips[self.tip]}'


@dataclass
class Chromosoma:
    time: int
    room: int


TYPE = []

with open('input.json') as f:
    data = json.load(f)
    teachers = data["teachers"]
    subjects = data["subjects"]
    groups = data["groups"]

    tips = data["tips"]

    rooms_raw = data["rooms"]
    rooms = [[] for i in tips]
    capaсity = [[] for i in rooms_raw]
    for i, (name, cap, ts) in enumerate(rooms_raw):
        capaсity[i] = cap
        for t in ts:
            rooms[t].append(i)
    input_json = [Inp(**inp) for inp in data["inputs"]]


def init_timetable(mas_inp):
    # first lect
    timetable = []
    for inp in mas_inp:
        timetable.extend([
            Chromosoma(randint(0, 35), choice(rooms[inp.tip]))
            for i in range(inp.count)
        ])
    return timetable


def init_population(mas_inp, start_count):
    for inp in mas_inp:
        TYPE.extend([
            ChromInfo(inp.group, inp.teacher, inp.subject, inp.tip)
            for i in range(inp.count)
        ])

    population = [init_timetable(mas_inp) for i in range(start_count)]

    return population


def f1(timetable):
    result = 0
    cur_rooms = {}  #{(123room,12time):[ChromInfo,count]}
    for chromosoma, info in zip(timetable, TYPE):
        if (chromosoma.room, chromosoma.time) in cur_rooms:
            a = cur_rooms[chromosoma.room, chromosoma.time]
            if (a[0].tip == info.tip and a[0].teacher == info.teacher and
                    a[0].subject == info.subject):
                a[1] += 1
                if a[1] > capaсity[chromosoma.room]:
                    result += 8
            else:
                result += 10
        else:
            cur_rooms[chromosoma.room, chromosoma.time] = [info, 1]
    return result


def f2(timetable):
    result = 0
    cur_teacher = {}  #{(teacher, time):room}
    for chromosoma, info in zip(timetable, TYPE):
        if (info.teacher, chromosoma.time) in cur_teacher:
            if cur_teacher[(info.teacher, chromosoma.time)] != chromosoma.room:
                result += 10
        else:
            cur_teacher[(info.teacher, chromosoma.time)] = chromosoma.room
    return result


def f3(timetable):

    tt_for_group = [[[[]
                      for lesson in range(TIME_IN_DAY)]
                     for day in range(DAYS_IN_WEEK)]
                    for i in groups]
    for chromosoma, info in zip(timetable, TYPE):
        tt_for_group[info.group][chromosoma.time //
                                 TIME_IN_DAY][chromosoma.time % TIME_IN_DAY] = [
                                     chromosoma.room, info
                                 ]
    # окна у групп
    window = 0
    for group in tt_for_group:
        for day in group:
            z = -1
            for lesson in day:
                if lesson:
                    if z == -1:
                        z = 0
                    elif z != 0:
                        window += z
                        z = 0
                else:
                    if z != -1:
                        z += 1
    return window


fit_func = [f1, f2, f3]
weight = [-50, -50, -1]


def fitness(timetable):
    return sum(w * f(timetable) for f, w in zip(fit_func, weight))


def select(population, n=3):
    shuffle(population)
    l = len(population)
    result = [population[i:min(i + n, l)] for i in range(0, l, n)]
    for group in result:
        group.sort(key=fitness, reverse=True)

    return result


def probability(s):  # return true with probability(s)
    return random() <= s


def child(winer, loser, s=0.7):
    return [a if probability(s) else b for a, b in zip(winer, loser)]


def cross(population):
    result = []
    for group in population:
        result.append(group[0])
        for loser in group[1:]:
            result.append(child(group[0], loser))
    return result


def mutation(population, s=0.1, ss=0.3):

    for timetable in population:
        if probability(s):
            for chromo, info in zip(timetable, TYPE):
                if probability(ss):
                    chromo.time = randint(0, 35)

                if probability(ss):
                    chromo.room = choice(rooms[info.tip])

    return population


def gna(mas_inp, max_iter=200, start_count=500):

    population = init_population(mas_inp, start_count)

    for i in tqdm(range(max_iter)):
        population = select(population)

        population = cross(population)

        population = mutation(population)
        ff = [fitness(tt) for tt in population]
        history_fitness.append(ff)
        fitness_av[0].append(max(ff))
        fitness_av[1].append(min(ff))
        fitness_av[2].append(sum(ff) / len(ff))

    population.sort(key=fitness, reverse=True)

    return population


def gettime_by_id(time):
    return time // TIME_IN_DAY, time % TIME_IN_DAY


def view(group_id, timetable):
    timetable_for_group = [['-'] * TIME_IN_DAY for i in range(DAYS_IN_WEEK)]
    for chromo, info in zip(timetable, TYPE):
        if info.group == group_id:
            t = gettime_by_id(chromo.time)
            timetable_for_group[t[0]][
                t[1]] = f'{info} {rooms_raw[chromo.room][0]}'
    for i, day in enumerate(timetable_for_group):
        print(i, day)


population = gna(input_json)
for i, group in enumerate(groups):
    print(group)
    view(i, population[0])

#plt.style.use('_mpl-gallery')

x = range(len(history_fitness))

# plot:
fig, ax = plt.subplots()

ax.eventplot(history_fitness,
             orientation="vertical",
             lineoffsets=x,
             linewidth=0.5)

#ax.set(xlim=(0, 8), xticks=np.arange(1, 8), ylim=(0, 8), yticks=np.arange(1, 8))

#fig, ax = plt.subplots()  # Create a figure containing a single axes.
ax.plot(range(len(fitness_av[0])), fitness_av[0])
ax.plot(range(len(fitness_av[1])), fitness_av[1])
ax.plot(range(len(fitness_av[2])), fitness_av[2])
# Plot some data on the axes.
plt.show()