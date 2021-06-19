import csv
import datetime

def main():
    todo_files = 'todo vf.md'
    patterns = ('- DONE ', '  - CLOSED: ', '  - STARTED: ', '  - CUSTOMER: ')
    output_data = []

    line_relevant = lambda x: any(s == x[:len(s)] for s in patterns)
    data_complete = lambda x: all(s in x for s in patterns[-1:])

    with open(todo_files, 'r') as f:
        content = f.read()
    
    raw_relevant_data = '\n'.join([l for l in list(filter(line_relevant, content.split('\n')))])

    complete_data = list(filter(data_complete, raw_relevant_data.split('- DONE ')))

    for item in complete_data:
        item_list = item.split('\n')
        start_time_string = f'{item_list[3][len(patterns[2]):-10]} {item_list[3][-5:]}'
        start_time_date = datetime.datetime.strptime(start_time_string, '%Y-%m-%d %H:%M')
        end_time_string = f'{item_list[1][len(patterns[1]):-10]} {item_list[1][-5:]}'
        end_time_date = datetime.datetime.strptime(end_time_string, '%Y-%m-%d %H:%M')
        duration = round((end_time_date - start_time_date).total_seconds() / 60)
        company = item_list[2][len(patterns[3]):]
        notes = item_list[0]
        output_data.append([start_time_string, end_time_string, duration, company, notes])
    
    [print(l) for l in output_data]
    
    csv_fields = "Start Time", "End Time", "Duration (minutes)", "Company", "Notes"
    
    with open('output.csv', 'w') as f:
        writer = csv.writer(f)
        writer.writerow(csv_fields)
        writer.writerow(("", "", "", "", ""))
        [writer.writerow(r) for r in output_data]

if __name__ == '__main__':
    main()