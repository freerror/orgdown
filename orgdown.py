import glob
import sqlite3
import configparser
import os

def get_script_path():
    """
    Returns the path of the script
    """
    return os.path.dirname(os.path.realpath(__file__))

def get_file_name_from_path(path):
    """
    Returns the file name only if given a full path
    """
    return os.path.basename(path)

def init_db(cur):
    """
    Sets the database
    """
    sql_create_matched_items_table = ''' Create Table matched_items (
                                            line_number TEXT,
                                            pattern_name TEXT,
                                            description TEXT,
                                            type TEXT
                                        )'''

    sql_create_patterns_table = '''Create Table patterns (
                                        name TEXT,
                                        representation TEXT,
                                        pattern TEXT,
                                        type TEXT
                                    )'''

    sql_create_relationships_table = '''Create Table relationships (
                                        line_number TEXT,
                                        related_line_number INTEGER
                                    )'''

    cur.execute(sql_create_patterns_table)
    cur.execute(sql_create_matched_items_table)
    cur.execute(sql_create_relationships_table)

def populate_patterns(cur, config):
    """
    Pupulates the patterns table
    """
    sql = ''' INSERT INTO patterns(
        name,representation,pattern,type)
        VALUES(?,?,?,?) '''
    for section in config.sections():
        pattern_data = (config[section]['Name'].replace("'", ""), 
                        config[section]['Representation'].replace("'", ""), 
                        config[section]['Pattern'].replace("'", ""),
                        config[section]['Type'].replace("'", ""))
        cur.execute(sql, pattern_data)
    

def populate_matched(md_file, cur):
    """
    Populates the matched_items table
    """
    file_name = get_file_name_from_path(md_file)
    with open(md_file, 'r') as f:
        read_data = f.read()
        line_num = 1
        for line in read_data.split("\n"):
            cur.execute('SELECT * FROM patterns')
            patterns_table = cur.fetchall()
            for row in patterns_table:
                pattern_name = row[0]
                pattern = row[2]
                pattern_type = row[3]
                # Look for pattern on line
                found_pattern = line.find(pattern)
                sql = ''' INSERT INTO matched_items(
                        line_number,pattern_name,description,type
                    )
                    VALUES(?,?,?,?) '''
                while True:
                    # determine where the description should start...
                    start_pos = found_pattern + len(pattern)
                    # ...and store it...
                    item_desc = line[start_pos:]
                    if found_pattern != -1:
                        # see if the line has more instances of pattern
                        found_pattern = line.find(pattern, start_pos)
                        file_line = '{0}:{1}'.format(file_name, line_num)
                        if found_pattern != -1:
                            # if found, then use the location...
                            item_desc = line[start_pos:found_pattern - 1]
                            # ...to delimit and print 
                            match_data = (file_line, pattern_name, item_desc, pattern_type)
                            cur.execute(sql, match_data)
                        else:
                            match_data = (file_line, pattern_name, item_desc, pattern_type)
                            cur.execute(sql, match_data)
                            # if not then to the end of the line
                    # if no (more) patterns found, then exit the while
                    else:
                        break
            line_num += 1


def relate_matches(cur):
    """
    Finds all the related matched_items and stores them in the relationships table 
    """
    sql = ''' INSERT INTO relationships(
            line_number,related_line_number
        )
        VALUES(?,?) '''
    cur.execute('SELECT * FROM matched_items WHERE type="todo_variant"')
    table_todos = cur.fetchall()
    line_numbers_todo = []
    cur.execute('SELECT * FROM matched_items WHERE type="todo_attribute"')
    table_attributes = cur.fetchall()
    line_numbers_attribute = []
    for row in table_todos:
        line_numbers_todo.append(row[0])
    for row in table_attributes:
        line_numbers_attribute.append(row[0])
    for line_num in line_numbers_todo:
        line_num_split = line_num.split(':')
        next_line = '{0}:{1}'.format(line_num_split[0],(int(line_num_split[1]) + 1))
        if next_line in line_numbers_attribute:
            cur.execute(sql, (line_num, next_line))
        else:
            nothing = 0
            cur.execute(sql, (line_num, nothing))

def display_relationship(cur):
    """
    Prints contents of relationships table row by row
    """
    cur.execute('SELECT * FROM relationships')
    relationships_table = cur.fetchall()
    for row in relationships_table:
        print(row[0],row[1])

def display_matches(cur):
    """
    Prints contents of matched_items table row by row
    """
    cur.execute('SELECT * FROM matched_items')
    matches_table = cur.fetchall()
    for row in matches_table:
        print(row[0], row[1], row[2], row[3])

def display_with_attributes(cur):
    """
    Prints all the related items from the relationships table and the matching data
    """
    welcome = 'Orgdown Todo Finder'
    file_row_max_width = -15
    print('\n{:=^50}\n'.format(welcome))
    cur.execute('SELECT * FROM relationships')
    relationships_table = cur.fetchall()
    print('{0:<20} {1} {2: ^30}'.format('L#', 'state', 'description'))
    print('{:-^50}'.format(''))
    # TODO fix weaknesses, should 
    for row in relationships_table:
        cur.execute('SELECT * FROM matched_items WHERE line_number=?', (row[0],))
        type_todo = cur.fetchone()
        cur.execute('SELECT representation FROM patterns WHERE name=?', (type_todo[1],))
        pattern_repr_type_todo = cur.fetchone()[0]
        truncated_prefix = ''
        if len(row[0])> 15:
            truncated_prefix = '...'
        try:
            cur.execute('SELECT * FROM matched_items WHERE line_number=?', (row[1],))
            type_attribute = cur.fetchone()
            cur.execute('SELECT representation FROM patterns WHERE name=?', (type_attribute[1],))
            pattern_repr_type_attribute = cur.fetchone()[0]
        except:
            type_attribute = 0
            pattern_repr_type_attribute = ''
        print('{0:<20} {1} {2}'.format('{0}{1}'.format(truncated_prefix, row[0][file_row_max_width:]), pattern_repr_type_todo, type_todo[2]))
        if type_attribute != 0:
            print('{0:<20}       {1} {2}'.format('', pattern_repr_type_attribute, type_attribute[2]))
            
    print()
    
def display_matches_only(cur):
    """
    Prints all the matched_items
    """
    welcome = 'Orgdown Todo Finder'
    print('\n{:=^50}\n'.format(welcome))
    cur.execute('SELECT * FROM matched_items')
    matches_table = cur.fetchall()
    print('{0:<20} {1} {2: ^30}'.format('line #', 'state', 'description'))
    print('{:-^50}'.format(''))
    for row in matches_table:
        cur.execute('SELECT representation FROM patterns WHERE name=?', (row[1],))
        pattern_repr = cur.fetchone()[0]
        print('{0:<20} {1} {2}'.format(row[3], pattern_repr, row[2]))
    print('\n')

def main():
    # TODO Order by type so todos are at the top/bottom. This might require
    # relating the relationship and matched_item tables or changing the
    # function slightly


    # Import prefs
    program_path = get_script_path()
    prefs_config = configparser.ConfigParser()
    pattern_config = configparser.ConfigParser()
    # These could be changed to XDG config path
    pattern_config.read('{0}/patterns.ini'.format(program_path))
    prefs_config.read('{0}/preferences.ini'.format(program_path))
    filepaths = prefs_config['Setup']['dir_patterns'].split(',')

    # Setup DB
    db = sqlite3.connect(':memory:')
    cur = db.cursor()
    init_db(cur)

    # Populate DB tables
    populate_patterns(cur, pattern_config)

    for file in filepaths:
        for md_file in glob.glob(file):
            populate_matched(md_file, cur)

    relate_matches(cur)

    # Program CLI Output
    display_with_attributes(cur)
    # display_matches_only(cur)
    # display_relationship(cur)
    # display_matches(cur)
    # The reason it's not working as expected
    # the line numbers are not a unique ID
    # perhaps filename:line?
    
if __name__ == '__main__':
    main()