#include <stdio.h>

// Define hierarchy
struct {
    char districts[11]; // 10 + NULL
} State;

struct {
    char name;
    State states[11]; // 10 states per country
} Country;

struct {
    char name;
    Country countries[11]; // 10 countries per continent
} Continent;


Continent continents[] = {
    {
        "Asia",
        {
            {
                "India",
                {
                    {"Maharashtra", {"Mumbai", "Pune", "Nagpur", "Nashik", "Aurangabad", "Kolhapur", "Solapur", "Thane", "Satara", "Sangli", NULL}},
                    {"Karnataka", {"Bangalore", "Mysore", "Mangalore", "Hubli", "Belgaum", "Davangere", "Tumkur", "Shivamogga", "Ballari", "Udupi", NULL}},
                    {"Rajasthan", {"Jaipur", "Udaipur", "Jodhpur", "Ajmer", "Kota", "Bikaner", "Alwar", "Sikar", "Chittorgarh", "Bhilwara", NULL}},
                    {NULL} // sentinel
                }
            },
            {"China", {{"Guangdong", {"Guangzhou", "Shenzhen", "Dongguan", NULL}}, {NULL}}},
            {"Japan", {{"Tokyo Prefecture", {"Shinjuku", "Shibuya", "Minato", NULL}}, {NULL}}},
            {NULL} // sentinel
        }
    },
    {"Europe", {{"Germany", {{"Bavaria", {"Munich", "Nuremberg", NULL}}, {NULL}}}, {NULL}}},
    {NULL} // sentinel
};

// Generic display
void showOptions(char *options[]) {
    for (int i = 0; options[i] != NULL; i++) {
        printf("%d. %s\n", i+1, options[i]);
    }
}

int main() {
    int choice;

    // Step 1: Continents
    printf("Choose a continent:\n");
    for (int i = 0; continents[i].name != NULL; i++) {
        printf("%d. %s\n", i+1, continents[i].name);
    }
    scanf("%d", &choice);

    Continent selectedContinent = continents[choice-1];

    // Step 2: Countries
    printf("\nChoose a country in %s:\n", selectedContinent.name);
    for (int i = 0; selectedContinent.countries[i].name != NULL; i++) {
        printf("%d. %s\n", i+1, selectedContinent.countries[i].name);
    }
    scanf("%d", &choice);

    Country selectedCountry = selectedContinent.countries[choice-1];

    // Step 3: States
    printf("\nChoose a state in %s:\n", selectedCountry.name);
    for (int i = 0; selectedCountry.states[i].name != NULL; i++) {
        printf("%d. %s\n", i+1, selectedCountry.states[i].name);
    }
    scanf("%d", &choice);

    State selectedState = selectedCountry.states[choice-1];

    // Step 4: Districts
    printf("\nChoose a district in %s:\n", selectedState.districts[0]); // state name
    showOptions(selectedState.districts);
    scanf("%d", &choice);

    printf("\nYou selected district: %s\n", selectedState.districts[choice-1]);

    return 0;
}
