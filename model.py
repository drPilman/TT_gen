from types import SimpleNamespace
import json
from dataclasses import dataclass
from random import randint, choice, shuffle, random, uniform
from tabulate import tabulate
import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
from tqdm import tqdm
import wandb
from numpy.random import normal
#history_fitness = []
#fitness_av = [[], [], []]
TIME_IN_DAY = 6
DAYS_IN_WEEK = 12


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

    def copy(self):
        return Chromosoma(self.time, self.room)


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


def gettime_by_id(time):
    return time // TIME_IN_DAY, time % TIME_IN_DAY


def probability(s):  # return true with probability(s)
    return random() <= s


class Timetable(list):

    def __init__(self, mas_inp, TYPE, config, from_list=False):
        self.TYPE = TYPE
        self.config = config
        if from_list:
            super().__init__(mas_inp)
        else:
            super().__init__()
            for inp in mas_inp:
                self.extend([
                    Chromosoma(randint(0, 35), choice(rooms[inp.tip]))
                    for i in range(inp.count)
                ])

    def f1(self):
        result = 0
        cur_rooms = {}  #{(123room,12time):[ChromInfo,count]}
        for chromosoma, info in zip(self, self.TYPE):
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

    def f2(self):
        result = 0
        cur_teacher = {}  #{(teacher, time):room}
        for chromosoma, info in zip(self, self.TYPE):
            if (info.teacher, chromosoma.time) in cur_teacher:
                if cur_teacher[(info.teacher,
                                chromosoma.time)] != chromosoma.room:
                    result += 10
            else:
                cur_teacher[(info.teacher, chromosoma.time)] = chromosoma.room
        return result

    def f3(self):

        tt_for_group = [[[[]
                          for lesson in range(TIME_IN_DAY)]
                         for day in range(DAYS_IN_WEEK)]
                        for i in groups]
        for chromosoma, info in zip(self, self.TYPE):
            tt_for_group[info.group][chromosoma.time //
                                     TIME_IN_DAY][chromosoma.time %
                                                  TIME_IN_DAY] = [
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

    def fitness(self):
        return sum(w * f(self) for f, w in zip(self.fit_func, self.weight))

    def child(self, loser):
        return Timetable([(a if probability(
            self.config.prob_winner_gen_in_child) else b).copy()
                          for a, b in zip(self, loser)],
                         self.TYPE,
                         self.config,
                         from_list=True)

    def view_group(self, group_id):
        timetable_for_group = [['-'] * TIME_IN_DAY for i in range(DAYS_IN_WEEK)]
        for chromo, info in zip(self, self.TYPE):
            if info.group == group_id:
                t = gettime_by_id(chromo.time)
                timetable_for_group[t[0]][
                    t[1]] = f'{info} {rooms_raw[chromo.room][0]}'
        for i, day in enumerate(timetable_for_group):
            print(i, day)

    def view_all(self):
        tt_for_group = [[[[]
                          for lesson in range(TIME_IN_DAY)]
                         for day in range(DAYS_IN_WEEK)]
                        for i in groups]
        for chromosoma, info in zip(self, self.TYPE):
            tt_for_group[info.group][chromosoma.time //
                                     TIME_IN_DAY][chromosoma.time %
                                                  TIME_IN_DAY] = [
                                                      chromosoma.room, info
                                                  ]
        for group in tt_for_group:
            print(f'GROUP: {groups[group]}\n{"="*8}')
            for day in group:
                print(f'DAY: {groups[group]}\n{"-"*8}')
                for room, info in day:
                    print(f'{info} {rooms_raw[room][0]}')


class Population(list):

    def __init__(self, mas_inp: list[Inp], config):
        self.config = config
        self.TYPE = [
            ChromInfo(inp.group, inp.teacher, inp.subject, inp.tip)
            for inp in mas_inp
            for _ in range(inp.count)
        ]
        super().__init__(
            Timetable(mas_inp, self.TYPE, config)
            for i in range(config.start_count))

    def select_cross(self):
        n = self.config.select_n
        shuffle(self)

        ff = [(tt.fitness(), i) for i, tt in enumerate(self)]

        l = len(self)

        winners = []
        for i in range(0, l, n):
            win_i = max(ff[i:min(i + n, l)], key=lambda x: x[0])[1]
            winners.extend([win_i] * min(n, l - i))

        for i, winner in enumerate(winners):
            if i != winner:
                self[i] = self[winner].child(self[i])

    def select_cross2(self):
        self.sort(key=lambda x: x.fitness(), reverse=True)
        n = len(self)
        half = n // 2
        for i in range(half, n):
            loser = winner = min(abs(int(normal(0.0, half / 2))),
                                 half + half // 2)
            while loser == winner:
                loser = min(abs(int(normal(0.0, half / 2))), half + half // 2)
            self[i] = self[winner].child(self[loser])

    def mutation(self):
        s = self.config.prob_mutation_tt
        ss = self.config.prob_mutation_chromasoma
        for timetable in self:
            if probability(s):
                for chromo, info in zip(timetable, timetable.TYPE):
                    if probability(ss):
                        chromo.time = randint(0, 35)

                    if probability(ss):
                        chromo.room = choice(rooms[info.tip])

    def mutation2(self):
        s = self.config.prob_mutation_tt
        ss = self.config.prob_mutation_chromasoma
        for timetable in self[(len(self) // 2):]:
            if probability(s):
                for chromo, info in zip(timetable, timetable.TYPE):
                    if probability(ss):
                        chromo.time = randint(0, 35)

                    if probability(ss):
                        chromo.room = choice(rooms[info.tip])

    def log(self):
        ff = [tt.fitness() for tt in self]
        log_dict = {
            "fitness_max": max(ff),
            "fitness_min": min(ff),
            "fitness_avr": sum(ff) / len(ff)
        }
        if self.config.wandb:
            wandb.log(log_dict)
        if self.config.log:
            return tuple(log_dict.values())


def gna(mas_inp, config):

    fitness_av = [[], [], []]

    population = Population(mas_inp, config)

    for i in tqdm(range(config.max_iter)):
        population.select_cross()

        population.mutation()
        if config.log or config.wandb:
            logs = population.log()

        if config.log:
            fitness_av[0].append(logs[0])
            fitness_av[1].append(logs[1])
            fitness_av[2].append(logs[2])

    population.sort(key=lambda x: x.fitness(), reverse=True)

    return population, fitness_av


config = SimpleNamespace(max_iter=200,
                         start_count=500,
                         wandb=True,
                         log=False,
                         select_n=5,
                         prob_winner_gen_in_child=0.8,
                         prob_mutation_tt=0.1,
                         prob_mutation_chromasoma=0.3)


def simplerun():
    if config.wandb:
        wandb.init(
            project="genetic-algorithm",
            tags=["baseline", "paper1"],
            config=config.__dict__,
        )

        wandb.define_metric("fitness_max", summary="max")
        wandb.define_metric("fitness_min", summary="max")
        wandb.define_metric("fitness_avr", summary="max")
    population, stat = gna(input_json, config)


def tryall(count):
    config = SimpleNamespace(max_iter=200,
                             start_count=500,
                             wandb=False,
                             log=True,
                             select_n=4,
                             prob_winner_gen_in_child=0.8,
                             prob_mutation_tt=0.1,
                             prob_mutation_chromasoma=0.3)

    max_all = (-100000000000000000, "NONE")
    for i in range(count):
        config.prob_winner_gen_in_child = uniform(0.6, 0.9)
        config.prob_mutation_tt = uniform(0.01, 0.9)
        config.prob_mutation_chromasoma = uniform(0.01, 0.9)
        label = f'({i}): {config.prob_winner_gen_in_child} {config.prob_mutation_tt} {config.prob_mutation_chromasoma}'
        print(f'start {label}')
        population, stat = gna(input_json, config)
        max_fitness = (max(stat[0]), i, label)
        max_all = max(max_all, max_fitness)
        print(f'result ({i}) {max_fitness[0]} | allmax:{max_all}')
        fig, ax = plt.subplots()
        fig.suptitle(label)
        ax.plot(range(len(stat[0])), stat[0])
        ax.plot(range(len(stat[1])), stat[1])
        ax.plot(range(len(stat[2])), stat[2])
        plt.savefig(f'save/{i}.png')


simplerun()
"""
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
"""