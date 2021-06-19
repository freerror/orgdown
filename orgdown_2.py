import glob
import configparser
import os

class TextFile():
    def __init__(self, filepath):
        self.filepath = filepath
        self.filename = os.path.basename(self.filepath)

class OrgdownFile(TextFile):
    def __init__(self, mdfile):
        super().__init__(mdfile)
        self.tracked_status = True
        self.org_entries = []
    
    def find_entries(self, pattern_data):
        with open(self.filepath, 'r') as f:
            read_data = f.read()
            line_num = 1
            for line in read_data.split("\n"):
                # for each pattern we try to find it in the current line
                for pattern_entry in pattern_data:
                    pattern = pattern_entry[2]
                    found_pos = line.find(pattern)
                    if found_pos != -1:
                        description_pos = found_pos + len(pattern)
                        self.org_entries.append(OrgEntry(f"{self.filepath}:{line_num}", line[description_pos:], pattern_entry[0]))
                line_num += 1
        return self.org_entries

class OrgEntry():
    def __init__(self, location, description, entry_type, priority=None):
        self.location = location
        self.description = description
        self.entry_type = entry_type
        self.priority = priority
        self.todo_attributes = []
    
    def relate_entries():
        # find entries in related positions
        print("relating matches")
    

class OrgdownSession():
    def __init__(self, session_type):
        self.session_type = session_type
        self.program_path = os.path.dirname(os.path.realpath(__file__))
        # session configs
        self.prefs_config = configparser.ConfigParser()
        self.pattern_config = configparser.ConfigParser()
        self.pattern_config.read('{0}/patterns.ini'.format(self.program_path))
        self.prefs_config.read('{0}/preferences.ini'.format(self.program_path))
        # get the filepaths
        self.filepaths = self.prefs_config['Setup']['dir_patterns'].split(',')
        self.excluded_files = self.prefs_config['Setup']['excluded_files'].split(',')
        # get all the pattern data
        self.pattern_data = []
        self.patterns = []
        for section in self.pattern_config.sections():
            # Just get all pattern sections?
            self.pattern_data.append((self.pattern_config[section]['Name'].replace("'", ""), 
                            self.pattern_config[section]['Representation'].replace("'", ""), 
                            self.pattern_config[section]['Pattern'].replace("'", ""),
                            self.pattern_config[section]['Type'].replace("'", "")))
            # Not elegant to get just the pattern data?
            self.patterns.append(self.pattern_config[section]['Pattern'].replace("'", ""),)
        self.org_entries = []


    def parse_files(self):
        file_list = []
        
        for filepath in self.filepaths:
            for mdfile in glob.glob(filepath):
                if mdfile not in self.excluded_files:
                    # create OrgdownFile instances
                    file_list.append(OrgdownFile(mdfile))
        
        for file in file_list:
            returned_entries = file.find_entries(self.pattern_data)
            self.org_entries = self.org_entries + returned_entries
    
    def fetch_representation(self, entry_type):
        representation = 'UNDEFINED'
        for data in self.pattern_data:
            if entry_type == data[0]:
                representation = data[1]
        return representation
        

    
    def print_entries(self, search_type=1):
        if search_type == 1:
            type_selection = 'Ready TODO'
        elif search_type == 2:
            type_selection = 'Waiting TODO'
        elif search_type == 3:
            type_selection = 'Completed TODO'
        elif search_type == 4:
            type_selection = 'Killed TODO'
        print(f"\n\nShowing type: {type_selection}")
        print("========================================")
        last_entry_selected = False
        for entry in self.org_entries:
            if entry.entry_type == type_selection:
                last_entry_selected = True
                print("     -----------------------------------")
                print(f"{self.fetch_representation(entry.entry_type)} {entry.description}")
                print(f"     {entry.location}")
            elif entry.entry_type.find('Indicator') != -1:
                if last_entry_selected:
                    print(f"     ({self.fetch_representation(entry.entry_type)}:{entry.description})")
            else:
                last_entry_selected = False
        print("========================================\n\n\n")





def main():
    # Start new session
    s = OrgdownSession('CLI')
    s.parse_files()
    try:
        s.print_entries(int(input('What type of entry? [1 TODO, 2 WAIT, 3 DONE, 4 KILL]: ')))
    except:
        print("Unexpected or nil input, printing with default type (TODO)")
        s.print_entries()


if __name__ == '__main__':
    main()