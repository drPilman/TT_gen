#include <iostream>
#include <string>
#include <random>
#include <json.hpp>

using json = nlohmann::json;
using namespace std;

extern const size_t TIME_IN_DAY, DAYS_IN_WEEK, TIME_MAX;

class Config
{
public:
    size_t populationSize;
    size_t populationIters;
};

class Random
{
public:
    mt19937 engine;
    uniform_int_distribution<size_t> timegenerator;
    uniform_int_distribution<size_t> roomgenerator;
    Random();
    size_t genTime();
    size_t gen(size_t b);
};

extern Random randomGenerator;

class Chromasoma_info
{
public:
    size_t group;
    size_t teacher;
    size_t subject;
    size_t tip;
};

class Chromasoma
{
public:
    size_t time;
    size_t room;
    Chromasoma();
};

class Timetable
{
public:
    vector<Chromasoma_info> *chromasomas_type;
    vector<Chromasoma> chromasomas;
    Timetable(vector<Chromasoma_info> &type);
};

class Population
{
public:
    Config config;
    vector<string> tips, teachers, subjects, groups, rooms;
    vector<int_fast16_t> rooms_capasity;
    vector<vector<size_t>> rooms_by_tip;
    vector<Chromasoma_info> chromasomas_type;
    vector<Timetable> individuals;
    Population(json &inputs, Config &cfg);
};