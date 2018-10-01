"""
This application is a tkinter windowed-app for Neuroshima game-masters. It
provides a repository for player-sharacters and NPC statsheets with all skills
and statistics and easy-to-use dice-testing functionality which could be used
straight from the character-statsheet.

Character statistics are stored in the python dict, and displayed in tkinter
window.

Another functionality is a repository of game-locations with a short text-de-
scriptions and links to the google-maps geolocations. One click opens a new tab
in the default browser with the g-maps address.
"""

import shelve
from functools import partial
import webbrowser
from random import *
from tkinter import *
from tkinter import filedialog


class Statistic:
    """
    This class contains definitions for typical Neuroshima character statstics
    and basic methods of making operations on them.
    """

    Statistics = ["Budowa", "Zręczność", "Percepcja", "Spryt", "Charakter",
                  "Szczęście"]

    def __init__(self, name: str, value: int):
        """
        Creates a new Statistic of NS-rpg mechanics. Possible Statistics are:
        Budowa, Zręczność, Percepcja, Spryt, Charakter, Szczęście.

        :param name: str name of a Statistic
        :param value: int value of a Statistic (in range: 8-20)
        """
        self.type = "Statistic"
        self.name = name
        self.value = value


class Skill:
    """
    This class contains definitions for typical Neuroshima character skills and
    basic methods of making operations on them.
    """

    Statistics = {"Karabiny": "Zręczność", "Pływanie": "Budowa",
                  "Samochód": "Zręczność", "Wspinaczka": "Zręczność",
                  "Kondycja": "Budowa", "Bijatyka": "Budowa",
                  "Broń biała": "Budowa", "Pistolety": "Zręczność",
                  "Skradanie": "Zręczność", "Ukrywanie": "Percepcja",
                  "Maskowanie": "Percepcja", "Czujność": "Percepcja",
                  "Persfazja": "Charakter", "Blef": "Spryt",
                  "Wyczucie emocji": "Percepcja", "OnB": "Charakter",
                  "Tropienie": "Percepcja", "Łowiectwo": "Spryt",
                  "Zdobywanie wody": "Spryt", "Ciężarówka":"Zręczność",
                  "Motocykl": "Zręczność", "Mechanika": "Spryt",
                  "Elektronika": "Spryt", "Komputery": "Spryt",
                  "Dowodzenie": "Charakter", "Niezłomność": "Charakter",
                  "Morale": "Charakter", "Zastraszanie": "Charakter",
                  "Pierwsza pomoc": "Spryt", "Wiedza medyczna": "Spryt",
                  "Chirurgia": "Zręczność"}

    def __init__(self, name: str, value: int, sliders: int=0, statistic=None):
        """
        Creates a newe Skill of NS-rpg mechanics.

        :param name: str name of a Skill
        :param value: value of a Skill (in range: 1-8)
        :param sliders: amount of sliders gained (each makes tests 1-level easier)
        :param statistic: a Statistic which is tested along with this Skill
        """
        self.type = "Skill"
        self.name = name
        self.value = value
        self.sliders = sliders
        self.statistic = statistic


class Trick:
    """This class represents a Neuroshima Tricks attributes."""

    def __init__(self, name: str, description: str, statistic: str=None,
                 slider: int=0, repeat: bool=False,
                 modifier: int=0):
        """
        Creates a new NS-rpg mechanics special trait.

        :param name: str name of a trick.trait.
        :param description: str description od trait.
        :param statistic: str, which Skill/Statistic it concerns.
        :param slider: bool, if trck provides additional sliders in tests.
        :param repeat: bool, if trait provides a re-roll of an tests.
        :param modifier: int, if trait provides a test-modifier.
        """
        self.name = name
        self.statistic = statistic
        self.description = description
        self.slider = slider
        self.repeat = repeat
        self.modifier = modifier


class Person:
    """Class for a player-character or an NPC character-sheet."""

    def __init__(self, name: str):
        """
        Creates a new player-character or NPC.

        :param name: str, name of the character.
        """
        self.name = name
        self.statistics = {}
        self.tricks = {}

    def set_statistic(self, name: str, value: int):
        if name not in self.statistics:
            self.statistics[name] = Statistic(name, value)
        else:
            self.statistics[name].value = value

    def set_skill(self, name: str, slider: int, value: int):
        if name not in self.statistics:
            self.statistics[name] = Skill(name, slider, value)
        else:
            self.statistics[name].value = value

    def set_trick(self, name: str, description: str, statistic: str = None,
                  slider: int = 0, repeat: bool = False,
                  modifier: int = 0):
        if name not in self.tricks:
            self.tricks[name] = Trick(name, description, statistic, slider,
                                      repeat, modifier)
        else:
            self.tricks[name].name = name
            self.tricks[name].description = description
            self.tricks[name].statistic = statistic
            self.tricks[name].slider = slider
            self.tricks[name].repeat = repeat
            self.tricks[name].modifier = modifier


class Location():
    """Class for an geo-locations links for in-game places."""

    def __init__(self, name: str, address: str, description: str = None):
        """
        Creates a new g-maps location.

        :param name: str, name of the place.
        :param address: str, http address to the g-maps geo-location of place.
        :param description: str, description of the place.
        """
        self.name = name
        self.address = address
        self.description = description


class Application:
    """Actual tkinter window-app."""

    def __init__(self, master):
        self.mainframe = master
        self.mainframe.title("Neuroshima Test Simulator")
        self.mainframe.protocol('WM_DELETE_WINDOW', self.close_application)
        # Buttons:
        self.main_buttons_frame = Frame(self.mainframe)
        self.main_buttons_frame.pack(side=TOP, expand=YES, fill=BOTH)
        self.main_window = Frame(self.mainframe).pack(side=TOP, expand=YES,
                                                      fill=BOTH)
        self.message_label = Label(self.mainframe)
        self.message_label.pack(side=BOTTOM, fill=BOTH, expand=YES)
        self.show_persons_button = Button(self.main_buttons_frame, text="Postaci")
        self.show_persons_button.pack(side=LEFT)

        self.show_locations_button = Button(self.main_buttons_frame, text="Miejsca")
        self.show_locations_button.pack(side=LEFT)

        self.search_entry = self.entry = Entry(self.main_buttons_frame)
        self.search_entry.pack(side=LEFT)
        self.search_entry.bind("<FocusIn>", self.bind_keys)
        self.search_button = Button(self.main_buttons_frame, text="Szukaj",
                                    command= self.find_person).pack(side=LEFT)

        self.display_frame = Frame(self.main_window)
        self.display_frame.pack(side=LEFT, expand=YES, fill=BOTH)

        self.test_frame = Frame(self.main_window)
        self.test_frame.pack(side=LEFT, expand=YES, fill=BOTH)


        self.required_statistics = 6

        self.load()
        self.persons["Type"] = Person
        self.locations["Type"] = Location
        self.show_persons_button.configure(
            command=partial(self.show_elements, self.persons))
        self.show_locations_button.configure(
            command=partial(self.show_elements, self.locations))

    def open_file(self):
        file = filedialog.askopenfilename()
        print(file)

    def show_elements(self, dictOfElements: dict):
        """
        Display in the window all elements of a dictionary.

        :param dictOfElements: dict, dicitionary of elements.
        :return: None
        """
        self.clear(self.display_frame, self.test_frame)
        for element in dictOfElements:
            self.display_new_element(dictOfElements[element])

        if dictOfElements["Type"] == Person:
            Button(self.display_frame.winfo_children()[-1], text="Nowa postać",
                 bg="wheat", command=self.create_person).pack(side=TOP, fill=X,
                                                                pady=11)
        elif dictOfElements["Type"] == Location:
            Button(self.display_frame.winfo_children()[-1], text="Nowa lokacja",
                   bg="wheat", command=self.create_location).pack(side=TOP,
                                                                fill=X,
                                                                pady=11)

        self.message_label.configure(text="")

    def display_new_element(self, element):
        """
        Display one element of an dict.

        :param element: element of an dicitionary.
        :return: None
        """
        if len(self.display_frame.winfo_children()) == 0 or \
            len(self.display_frame.winfo_children()[-1].winfo_children()) > 15:
            self.new_row(self.display_frame)

        if isinstance(element, Person):
            self.display_new_person(element)
        elif isinstance(element, Location):
            self.display_new_location(element)

    def clear(self, *cleared):
        """
        Clear the window of it's children-widgets preparing it to display new
        content.

        :param cleared: a tkinter widget to be cleared of it's children
        :return: None
        """
        self.message_label.configure(text="", bg="white")
        for widget in cleared:
            for child in widget.winfo_children():
                child.destroy()

    def new_row(self, where):
        """
        Add a new row to the displayed Character list.

        :param where: a widget inside which a new child will be created
        :return: None
        """
        new_row = Frame(where)
        new_row.pack(side=LEFT, expand=YES, fill=BOTH)

    def display_new_person(self, person: Person):
        """
        Add one Character to the window.

        :param person: an instance of a Person class.
        :return: None
        """
        lf = LabelFrame(self.display_frame.winfo_children()[-1], text=person.name)
        lf.pack()

        Button(lf, text="Wyświetl statystyki", bg="grey80",
               command=partial(self.show_statistics, person)).pack(side=LEFT)
        Button(lf,
               text="Usuń", bg="red",
               command=partial(self.delete_element, self.persons, person)).pack(side=LEFT)
        if check_required(person):
            Label(lf, text="OK",
                  fg="green").pack(side=LEFT)
        else:
            Label(lf, text="X",
                  fg="red").pack(side=LEFT)

    def display_new_location(self, location: Location):
        """
        Add one Location to the window.

        :param location: an instance of the Location class.
        :return: None
        """
        lf = LabelFrame(self.display_frame.winfo_children()[-1],
                        text=location.name)
        lf.pack()

        Button(lf, text="Pokaż na mapie", bg="grey80",
               command=partial(self.show_on_map, location.address)).pack(side=LEFT)
        Button(lf, text="Edytuj", bg="grey80",
               command=partial(self.create_location, location)).pack(side=LEFT)
        Button(lf, text="Usuń", bg="red", command=partial(self.delete_element,
                self.locations, location)).pack(side=LEFT)

    def delete_element(self, dictOfElements: dict, element):
        """
        Delete an element from the provided dict

        :param dictOfElements: dict, dicitionary to process.
        :param element: an instance of spcified class to be deleted.
        :return: None
        """
        del dictOfElements[element.name]
        self.show_elements(dictOfElements)

    def show_on_map(self, addres: str):
        """
        Open webbrowser with a new tab and displays a location on gmaps.

        :param addres: str, a http address of the geolocation in gmaps.
        :return: None
        """
        webbrowser.open(addres, autoraise=True)

    def find_person(self):
        """
        Find a particular Person in self.persons dict. The instance is querried
        from an entry in the main window.

        :return: None
        """
        name = self.search_entry.get()
        if name is None:
            if name in self.persons.keys():
                self.show_statistics(self.persons[name])
                self.message_label.configure(text="", bg="white")
        else:
            self.message_label.configure(text="Nie znaleziono.", bg="red")

    def bind_keys(self, event):
        """
        Bind keyboard-press to the self.autocompletion method.

        :param event: key-press in entry field.
        :return: None
        """
        self.search_entry.bind("<Key>", self.autocomplete)

    def autocomplete(self, event):
        """
        Change an user-input from search field to the searching result.

        :param event: key-press in the entry-field.
        :return: None
        """
        self.clear(self.display_frame)
        entry_input = self.search_entry.get()

        for person in self.persons:
            if entry_input is not None and person != "Type":
                if entry_input in self.persons[person].name:
                    self.display_new_element(self.persons[person])

        for location in self.locations:
            if entry_input is not None and location != "Type":
                if entry_input in self.locations[location].name:
                    self.display_new_element(self.locations[location])

    def show_statistics(self, person: Person):
        """
        Display all the stats of a particular character.

        :param person: an instance of Person class.
        :return: None
        """
        self.clear(self.display_frame)
        Frame(self.display_frame).pack(side=TOP)
        Label(self.display_frame.winfo_children()[-1], text=person.name).pack()
        Button(self.display_frame.winfo_children()[-1],
               text="Sztuczki i Cechy", bg="wheat",
               command=partial(self.show_tricks, person)).pack(side=TOP, fill=X)

        for statistic in person.statistics:
            self.display_statistic(person, statistic)

        Button(self.display_frame.winfo_children()[-1], text="Dodaj Współczynnik", bg="wheat",
               command=partial(self.add_new_statistic, person, None)).pack(side=TOP, fill=X)
        Button(self.display_frame.winfo_children()[-1], text="Dodaj Umiejętność", bg="wheat",
               command=partial(self.add_new_skill, person, None)).pack(side=TOP, fill=X)

        if not check_required(person):
            self.message_label.configure(text="Ustaw wartości Współczynników głównych!", bg="red")

    def display_statistic(self, person: Person, statistic: Statistic):
        """
        Display a one Statistic at the end of current-frame.

        :param person: an instance of the Person class.
        :param statistic: an instance of the Statistic class.
        :return: None
        """
        if len(self.display_frame.winfo_children()) == 1 or \
                len(self.display_frame.winfo_children()[
                        -1].winfo_children()) > 20:
            self.new_row(self.display_frame)
        last_col = self.display_frame.winfo_children()[-1]

        Frame(last_col).pack(side=TOP, expand=NO, fill=X)
        self.display_frame.winfo_children()[-1].pack()
        Label(last_col.winfo_children()[-1],
              text=person.statistics[statistic].name).pack(side=LEFT,
                                                           expand=YES,
                                                           fill=X)
        Label(last_col.winfo_children()[-1], bg="white",
              text=person.statistics[statistic].value).pack(side=LEFT,
                                                            expand=YES,
                                                            fill=X)
        Button(last_col.winfo_children()[-1],
               text="Wykonaj test", command=partial(self.run_test,
                                                    person, person.statistics[
                                                        statistic])).pack(
            side=LEFT,
            expand=YES,
            fill=X)
        if isinstance(person.statistics[statistic], Statistic):
            Button(last_col.winfo_children()[-1], text="Edytuj",
                   bg="lightgreen", command=partial(
                    self.add_new_statistic, person, statistic)).pack(
                side=LEFT,
                expand=YES,
                fill=X)
        else:
            Button(last_col.winfo_children()[-1], text="Edytuj",
                   bg="lightgreen", command=partial(
                    self.add_new_skill, person, statistic)).pack(side=LEFT,
                                                                 expand=YES,
                                                                 fill=X)
        Button(last_col.winfo_children()[-1], text="Usuń",
               bg="red", command=partial(self.delete_stat, person,
                                         statistic)).pack(side=LEFT,
                                                          expand=YES,
                                                          fill=X)

    def show_tricks(self, person: Person):
        """
        Display all Tricks and Traits of a person.

        :param person: an instance of the Person class
        :return: None
        """
        self.clear(self.display_frame)

        Label(self.display_frame, text="Sztuczki i Cechy:").pack(side=TOP)

        for trick in person.tricks:
            self.display_trick(person, trick)

        Button(self.display_frame.winfo_children()[-1],
               text="Dodaj Sztuczkę/Cechę", bg="wheat",
               command=partial(self.add_trick, person)).pack(side=TOP, fill=X)

    def display_trick(self, person, trick):
        """
        Add one Trick or Trait from person.trick dict to the window.

        :param person: an instance of the Person class.
        :param trick: an instanmce of the Trick class.
        :return: None
        """

        if len(self.display_frame.winfo_children()) == 1 or \
                len(self.display_frame.winfo_children()[
                        -1].winfo_children()) > 20:
            self.new_row(self.display_frame)
        last_col = self.display_frame.winfo_children()[-1]

        Frame(last_col).pack(side=TOP, expand=NO, fill=X)
        self.display_frame.winfo_children()[-1].pack()
        Label(last_col.winfo_children()[-1],
              text=person.tricks[trick].name).pack(side=LEFT, expand=YES, fill=X)
        Button(last_col.winfo_children()[-1],
               text="Edytuj", bg="wheat",
               command=partial(self.add_trick, person, trick)).pack(side=LEFT,
                                                                    fill=X)
        b = Button(last_col.winfo_children()[-1], text="Usuń",
               bg="red",command=partial(self.delete_trick, person, trick))
        b.pack(side=LEFT, expand=YES, fill=X)

    def delete_stat(self, person, statistic):
        """
        Delete a Skill of Statistic from person's statistics dict.

        :param person: an instance of the Person class.
        :param statistic: an instanmce of the Statistic class.
        :return: None
        """
        del person.statistics[statistic]
        self.show_statistics(person)

    def delete_trick(self, person, trick):
        """
        Delete a Trick or Trait from person's tricks dict.

        :param person: an instance of the Person class.
        :param trick: an instance of the Trick class.
        :return: None
        """
        del person.tricks[trick]
        self.show_tricks(person)

    def dice_roll(cls, faces: int):
        """
        Generate result in range of 1–[number of faces] and returns it.

        :param faces: int, number of dice-faces.
        :return: int, result of the dice-roll.
        """
        return randint(1, faces)

    def convert_sliders(self, slider_value: int):
        """
        Convert sliders/test difficulty to the actual modifier.

        :param slider_value: int, number of sliders.
        :return: int, modifier to the test.
        """
        values = {-5: -15, -4: -11, -3: -8, -2: -5, -1: -2, 0: 0, 1: 2, 2: 5,
                  3: 8, 4: 11, 5: 15, 6: 20, 7: 24}
        return values[slider_value]

    def run_test(self, person: Person, statistic: Statistic or Skill):
        """
        Simulate a 3d20 test of a particular Skill or Statistic.

        :param person: an instance of the Person class.
        :param statistic: an instance of the Statistic or Skill class.
        :return: None
        """

        def difficulty_text(event):
            names = {-2: "Bardzo łatwy", -1: "Łatwy", 0: "Przeciętny",
                     1: "Problematyczny", 2: "Trudny", 3: "Bardzo trudny",
                     4: "Cholernie trudny", 5: "Farciarski", 6: "Mistrzowski",
                     7: "Arcymistrzowski"}
            self.diff_name.configure(text=names[self.diff_scale.get()])

        def apply_tricks():
            for trick in person.tricks:
                if person.tricks[trick].statistic == statistic:
                    Label(self.trick_frame, text=person.tricks[trick].name).pack(side=TOP)
                    if person.tricks[trick].slider > slider:
                        slider = person.tricks[trick].slider
                    if person.tricks[trick].modifier > modifier:
                        modifier = person.tricks[trick].modifier

        def display_result(result):
            self.clear(self.test_frame)

            txt = "ZDANY" if result[0] else "PORAŻKA"
            color = "green" if result[0] else "red"

            Label(self.test_frame, text=txt, bg=color, font=20)
            self.test_frame.winfo_children()[-1].pack(side=TOP, expand=YES,
                                                         fill=BOTH)

            LabelFrame(self.test_frame, text="Trudność testu:")
            self.test_frame.winfo_children()[-1].pack(side=TOP, expand=YES,
                                                         fill=BOTH)
            Label(self.test_frame.winfo_children()[-1],
                  text=result[4]).pack(side=LEFT, expand=YES, fill=BOTH)

            LabelFrame(self.test_frame, text="Wyniki na kościach:")
            self.test_frame.winfo_children()[-1].pack(side=TOP)
            Label(self.test_frame.winfo_children()[-1],
                  text=result[1][0]).pack(side=LEFT, expand=YES, fill=BOTH)
            Label(self.test_frame.winfo_children()[-1],
                  text=result[1][1]).pack(side=LEFT, expand=YES, fill=BOTH)
            Label(self.test_frame.winfo_children()[-1],
                  text=result[1][2]).pack(side=LEFT, expand=YES, fill=BOTH)

            if len(result) == 6:
                LabelFrame(self.test_frame, text="Dwie najlepsze kości:")
                self.test_frame.winfo_children()[-1].pack(side=TOP, fill=BOTH)
                Label(self.test_frame.winfo_children()[-1],
                      text=result[5][0]).pack(side=LEFT, expand=YES, fill=BOTH)
                Label(self.test_frame.winfo_children()[-1],
                      text=result[5][1]).pack(side=LEFT, expand=YES, fill=BOTH)

            LabelFrame(self.test_frame, text="Po odjęciu Umiejętności:")
            self.test_frame.winfo_children()[-1].pack(side=TOP, fill=BOTH)
            Label(self.test_frame.winfo_children()[-1],
                  text=result[2][0]).pack(side=LEFT, expand=YES, fill=BOTH)
            Label(self.test_frame.winfo_children()[-1],
                  text=result[2][1]).pack(side=LEFT, expand=YES, fill=BOTH)

            LabelFrame(self.test_frame, text="Punkty sukcesu/porażki:")
            self.test_frame.winfo_children()[-1].pack(side=TOP, expand=YES,
                                                         fill=BOTH)
            Label(self.test_frame.winfo_children()[-1], text=str(result[3]),
                  bg=color, font=20).pack(side=LEFT, expand=YES, fill=BOTH)

        def roll_for_skill(statistic):

            skill_points = statistic.value
            sliders = (slider + int(skill_points / 4))

            base_difficulty = int(self.diff_scale.get()) - sliders
            real_difficulty = self.convert_sliders(base_difficulty)

            roll_result = []

            for i in range(0, 3):
                roll_result.append(self.dice_roll(20))
            original_roll_result = roll_result.copy()

            for result in roll_result:
                if result == 1:
                    real_difficulty -= 3
                elif result == 20:
                    real_difficulty += 3
            testedValue = statistic.statistic - real_difficulty

            worst_result = max(roll_result)
            roll_result.remove(worst_result)
            unmodified = roll_result.copy()

            while skill_points > 0:
                skill_points -= 1
                for i in range(0, 2):
                    if roll_result[i] == max(roll_result) and roll_result[i] > 1:
                        roll_result[i] -= 1
                        break

            if max(roll_result) > testedValue:
                fail_points = max(roll_result) - testedValue
                display_result([False, original_roll_result, roll_result,
                                fail_points, testedValue, unmodified])
            else:
                succes_points = abs(max(roll_result) - testedValue)
                display_result([True, original_roll_result, roll_result,
                                succes_points, testedValue, unmodified])

        def roll_for_stat(statistic):

            difficulty = int(self.diff_scale.get())
            real_difficulty = self.convert_sliders(difficulty)
            roll_result = []

            for i in range(0, 3):
                roll_result.append(self.dice_roll(20))
            original_roll_result = roll_result.copy()

            for result in roll_result:
                if result == 1:
                    real_difficulty -= 3
                elif result == 20:
                    real_difficulty += 3
            tested_value = statistic.value - real_difficulty

            worst_result = max(roll_result)
            roll_result.remove(worst_result)

            for result in roll_result:
                if result > tested_value:
                    fail_points = max(roll_result) - tested_value
                    display_result([False, original_roll_result, roll_result,
                                    fail_points, tested_value])
                    return
                else:
                    succes_points = abs(max(roll_result) - tested_value)
                    display_result([True, original_roll_result, roll_result,
                                    succes_points, tested_value])

        self.clear(self.display_frame)
        Label(self.display_frame,
            text="Testowany współczynnik: "+ statistic.name)
        self.display_frame.winfo_children()[-1].pack()

        self.difficulty = LabelFrame(self.display_frame, text="Trudność testu:")
        self.difficulty.pack(side=TOP)
        self.diff_scale = Scale(self.difficulty, from_=-2, to=7,
                                orient=HORIZONTAL, showvalue=0,
                                command=difficulty_text)
        self.diff_scale.set(0)
        self.diff_scale.pack()
        self.diff_name = Label(self.difficulty, text="Przeciętny")
        self.diff_name.pack()

        self.trick_frame = LabelFrame(self.display_frame, text="Sztuczki:")
        self.trick_frame.pack(side=TOP)

        slider = 0
        modifier = 0
        apply_tricks()

        if isinstance(statistic, Skill):
            Button(self.display_frame, text="Rzuć!",
                   command=partial(roll_for_skill, statistic)).pack(side=TOP)
        else:
            Button(self.display_frame, text="Rzuć!",
                   command=partial(roll_for_stat, statistic)).pack(side=TOP)

        Button(self.display_frame, text="Powrót", command=partial(
            self.show_statistics, person)).pack(side=TOP)

    def add_new_skill(self, person: Person, skill_name: str):
        """
        Register new Skill to the Person's dict and display new list of this
        Character's skills.

        :param person: an instance of the Person class.
        :param skill_name: str, name of the skill.
        :return: None
        """

        def add_skill(person):
            name = skill_name if skill_name is not None else self.entry.get()
            value = int(self.entry2.get())
            sliders = int(self.entry4.get())
            if self.entry3.get() != "":
                statistic = person.statistics[self.entry3.get()].value
            else:
                statistic = person.statistics[Skill.Statistics[name.title()]].value

            person.statistics[name] = Skill(name, value, sliders, statistic)

            self.show_statistics(person)

        self.clear(self.display_frame)
        LabelFrame(self.display_frame, text="Nazwa:")
        self.display_frame.winfo_children()[-1].pack()
        self.entry = Entry(self.display_frame.winfo_children()[-1])
        if skill_name is not None:
            self.entry.insert(END, skill_name)
            self.entry.configure(state=DISABLED)
        self.entry.pack()

        LabelFrame(self.display_frame, text="Poziom:")
        self.display_frame.winfo_children()[-1].pack()
        self.entry2 = Entry(self.display_frame.winfo_children()[-1])
        self.entry2.pack()

        LabelFrame(self.display_frame, text="Przypisana Cecha:")
        self.display_frame.winfo_children()[-1].pack()
        self.entry3 = Entry(self.display_frame.winfo_children()[-1])
        self.entry3.pack()

        LabelFrame(self.display_frame, text="Dodatkowe suwaki:")
        self.display_frame.winfo_children()[-1].pack()
        self.entry4 = Entry(self.display_frame.winfo_children()[-1])
        self.entry4.insert(END, 0)
        self.entry4.pack()

        Button(self.display_frame, text="Dodaj Umiejętność!",
               command=partial(add_skill, person)).pack(side=TOP)

    def add_new_statistic(self, person: Person, stat_name=None):
        """
        Register new Statistic to the Person's dict and display new list of
        this Character's skills.

        :param person: an instance of the Person class.
        :param stat_name: str, name of statistic.
        :return: None
        """

        def add_statistic(person):
            name = stat_name if stat_name is not None else self.entry.get()
            value = int(self.entry2.get())

            person.statistics[name] = Statistic(name, value)

            self.show_statistics(person)

        self.clear(self.display_frame)
        LabelFrame(self.display_frame, text="Nazwa:")
        self.display_frame.winfo_children()[-1].pack()
        self.entry = Entry(self.display_frame.winfo_children()[-1])
        if stat_name is not None:
            self.entry.insert(END, stat_name)
            self.entry.configure(state=DISABLED)
        self.entry.pack()

        LabelFrame(self.display_frame, text="Poziom:")
        self.display_frame.winfo_children()[-1].pack()
        self.entry2 = Entry(self.display_frame.winfo_children()[-1])
        self.entry2.pack()

        LabelFrame(self.display_frame, text="Dodatkowe suwaki:")
        self.display_frame.winfo_children()[-1].pack()
        self.entry3 = Entry(self.display_frame.winfo_children()[-1])
        self.entry3.pack()

        Button(self.display_frame, text="Dodaj Cechę!",
               command=partial(add_statistic, person)).pack(side=TOP)

    def add_trick(self, person: Person, trick_name=None):
        """
        Add a new special-trait/trick to the person.

        :param person: person: an instance of the Person class.
        :param trick_name: str, special trait name.
        :return: None
        """
        def new_trick(person):
            trick_name = self.name_entry.get()
            description = self.work_entry.get()
            stat_name = self.stat_entry.get()
            slider = self.scale.get()
            modifier = self.mod_entry.get()
            repeat = self.reroll_box.getboolean(repeat_roll)
            mod = 0
            person.tricks[trick_name] = Trick(trick_name, description,
                                              stat_name, slider, repeat,
                                              modifier)
            self.show_statistics(person)

        name = "" if trick_name is None else person.tricks[trick_name].name
        stat = "" if trick_name is None else person.tricks[trick_name].statistic
        repeat_roll = False if trick_name is None else person.tricks[trick_name].repeat
        slider = 0 if trick_name is None else person.tricks[trick_name].slider
        modifier = 0 if trick_name is None else person.tricks[trick_name].modifier
        description = "" if trick_name is None else person.tricks[trick_name].description

        self.clear(self.display_frame)
        LabelFrame(self.display_frame, text="Nazwa:")
        self.display_frame.winfo_children()[-1].pack()
        self.name_entry = Entry(self.display_frame.winfo_children()[-1])
        self.name_entry.insert(END, name)
        self.name_entry.pack()

        LabelFrame(self.display_frame, text="Dotyczy Współczynnika:")
        self.display_frame.winfo_children()[-1].pack()
        self.stat_entry = Entry(self.display_frame.winfo_children()[-1])
        self.stat_entry.insert(END, stat)
        self.stat_entry.pack(side=LEFT)

        LabelFrame(self.display_frame, text="Ułatwia test?:")
        self.display_frame.winfo_children()[-1].pack()
        self.mod_entry = Entry(self.display_frame.winfo_children()[-1],
                                      variable=repeat_roll)
        self.mod_entry.insert(END, modifier)
        self.reroll_box.pack(side=LEFT)

        LabelFrame(self.display_frame, text="Zapewnia przerzut?:")
        self.display_frame.winfo_children()[-1].pack()
        self.reroll_box = Checkbutton(self.display_frame.winfo_children()[-1],
                                      variable=repeat_roll)
        self.reroll_box.getboolean(repeat_roll)
        self.reroll_box.pack(side=LEFT)

        LabelFrame(self.display_frame, text="Zapewnia Suwak?:")
        self.display_frame.winfo_children()[-1].pack()
        self.scale = Scale(self.display_frame.winfo_children()[-1], from_=0,
                           to=2, orient=HORIZONTAL)
        self.scale.set(slider)
        self.scale.pack(side=LEFT)

        LabelFrame(self.display_frame, text="Działanie:")
        self.display_frame.winfo_children()[-1].pack()
        self.work_entry = Entry(self.display_frame.winfo_children()[-1])
        self.work_entry.insert(END, description)
        self.work_entry.pack()
        self.scale.pack(side=LEFT)

        Button(self.display_frame, text="Dodaj Cechę/Sztuczkę!",
               command=partial(new_trick, person)).pack(side=TOP)

    def create_person(self):
        """
        Display form for adding new Characters to self.persons dict.

        :return: None
        """
        self.clear(self.display_frame)

        lf = LabelFrame(self.display_frame, text="Imię:")
        self.display_frame.winfo_children()[-1].pack()
        self.name_entry = Entry(lf)
        self.name_entry.pack()

        Button(self.display_frame, text="Dodaj!",
               command=self.new_person).pack(side=TOP)

    def new_person(self):
        """
        Add a new Character to the character's dict. It is only a raw data
        which is later used to display records in the window.

        :return: None
        """
        name = self.name_entry.get()
        if name != "":
            self.persons[name] = Person(name)

            for statistic in Statistic.Statistics:
                self.persons[name].set_statistic(statistic, 0)

            for skill in Skill.Statistics:
                self.persons[name].set_skill(skill, 0, 0)

            self.show_statistics(self.persons[name])
        else:
            self.message_label.configure(text="Wpisz imię!", bg="red")

    def create_location(self, location: Location=None):
        """
        Fulfill data fields for a new Location to be added.

        :param location: an instance of the Location class.
        :return: None
        """
        self.clear(self.display_frame)

        lfn = LabelFrame(self.display_frame, text="Nazwa:")
        self.display_frame.winfo_children()[-1].pack()
        self.name_entry = Entry(lfn)
        self.name_entry.pack()
        if location is not None:
            self.name_entry.insert(END, self.locations[location].name)

        lfa = LabelFrame(self.display_frame, text="Adres:")
        self.display_frame.winfo_children()[-1].pack()
        self.address_entry = Entry(lfa)
        self.address_entry.pack()
        if location is not None:
            self.address_entry.insert(END, str(self.locations[location].address))

        lfd = LabelFrame(self.display_frame, text="Opis:")
        self.display_frame.winfo_children()[-1].pack()
        self.desc_entry = Entry(lfd)
        self.desc_entry.pack()
        if location is not None:
            self.desc_entry.insert(END,
                                      str(self.locations[location].description))

        Button(self.display_frame, text="Zapisz!", command=self.new_location).pack(side=TOP)

    def new_location(self):
        """
        Add a new Location to the self.locations dict.

        :return: None
        """
        name = self.name_entry.get()
        address = self.address_entry.get()
        desc = self.desc_entry.get()

        self.locations[name] = Location(name, address, desc)

    def save(self):
        """
        Saves self.persons dict to the file. Called automatically when the
        application is closed.

        :return: None
        """
        shelfFile = shelve.open("saved_data")
        shelfFile['persons'] = self.persons
        shelfFile['locations'] = self.locations
        shelfFile.close()

    def load(self):
        """
        Retrieve a self.persons dict from the file. Called automatically on
        the start of application.

        :return: None
        """
        shelfFile = shelve.open("saved_data")
        self.persons = shelfFile['persons']
        self.locations = shelfFile['locations']
        shelfFile.close()
        self.message_label.configure(
            text=str(len(self.persons)-1)+" characters, and " +
                 str(len(self.locations)-1) + " locations loaded successfully.")

    def close_application(self):
        """
        Replace a default application closing mechanism.

        :return: None
        """
        self.save()
        self.mainframe.destroy()


def check_required(person: Person):
    """
    Check if a Person has all required Statistics. Returns boolean.

    :param person: an instance of the Person class.
    :return: bool, if there is enough Statistics created.
    """
    stats_count = 0
    for stat in person.statistics:
        if isinstance(person.statistics[stat], Statistic):
            if person.statistics[stat].value > 0:
                stats_count += 1
    return stats_count == 6


if __name__ == '__main__':
    root = Tk()
    app = Application(root)
    root.mainloop()
