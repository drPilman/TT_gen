#include <gna.h>
#include <iterator>

const size_t TIME_IN_DAY = 6;
const size_t DAYS_IN_WEEK = 12;
const size_t TIME_MAX = TIME_IN_DAY * DAYS_IN_WEEK - 1;

Random::Random()
{
    random_device device;
    engine.seed(device());
    timegenerator = uniform_int_distribution<size_t>(0, TIME_MAX);
}
size_t Random::genTime()
{
    return timegenerator(engine);
}
size_t Random::gen(size_t b)
{
    uniform_int_distribution<size_t> distribution(0, b - 1);
    return distribution(engine);
}

Random randomGenerator = Random();

Timetable::Timetable(vector<Chromasoma_info> &type)
{
    chromasomas_type = &type;
    chromasomas.resize(type.size());
}
Chromasoma::Chromasoma()
{
    time = randomGenerator.genTime();
}

Population::Population(json &inputs, Config &cfg)
{
    config = cfg;
    tips = inputs["tips"];
    teachers = inputs["teachers"];
    subjects = inputs["subjects"];
    groups = inputs["groups"];
    size_t lessons_count = 0;
    for (auto &lesson : inputs["lessons"])
    {
        lessons_count += lesson["count"].get<size_t>();
    }
    chromasomas_type.resize(lessons_count);

    vector<Chromasoma_info>::iterator info_iter = chromasomas_type.begin();

    for (auto &lesson : inputs["lessons"])
    {
        Chromasoma_info info;
        info.group = lesson["group"].get<size_t>();
        info.teacher = lesson["teacher"].get<size_t>();
        info.subject = lesson["subject"].get<size_t>();
        info.tip = lesson["tip"].get<size_t>();
        size_t count = lesson["count"].get<size_t>();
        for (size_t i = 0; i < count; ++i)
        {
            *(info_iter++) = info;
        }
    }
    individuals.resize(config.populationSize);
    for (Timetable &timetable : individuals)
    {
        timetable = Timetable(chromasomas_type);
        timetable.randomInit();
    }
}
