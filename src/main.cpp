#include <fstream>
#include <iostream>
#include <string>
#include <vector>
// #include "../nlohmann/json.hpp"

using namespace std;
// using json = nlohmann::json;

int main() {
    string str;
    fstream fin;
    fin.open("../data/items.json");
    cout << "==== Read Start ====" << endl;
    // json items = json::parse(fin);
    // for (auto it = items.begin(); it != items.end(); it++)
    //     string netName = it.key();
    vector<vector<string> > data;
    vector<string> temp;
    int count = 0;
    while (fin >> str) {
        cout << str << endl;
        if (str == "\"id\":")
            data.push_back(temp);
        cout<<++count<<endl;
    }
    return 0;
}