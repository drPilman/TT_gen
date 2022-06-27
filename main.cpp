#include <iostream>
#include <fstream>
#include <iomanip>
#include <gna.h>

int main()
{
    setlocale(LC_ALL, "");
    /*
        json j =
            {
                {"pi", 3.141},
                {"Привет", true},
                {"name", "Niels"},
                {"nothing", nullptr},
                {"answer", {{"everything", 42}}},
                {"list", {1, 0, 2}},
                {"object", {{"currency", "USD"}, {"value", 42.99}}}};

        // add new values
        j["new"]["key"]["value"] = {"another", "list"};

        // count elements
        auto s = j.size();
        j["size"] = s;
        auto w = j["object"];
        // pretty print with indent of 4 spaces
        std::cout << std::setw(4) << j << '\n';
        * /
            /*
                InputData data = {1,
                                  1,
                                  1,
                                  1,
                                  1};*/

    ifstream file("input.json");
    json j;
    file >> j;
    Config cfg = {500, 200};
    Population p(j, cfg);
    cout << p.teachers[0] << endl;
}