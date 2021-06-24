#include <iostream>
using namespace std;

class TextFile {
    private:
        // ? Is there a better type?
        string filepath;
        string filename;
        
    public:
        TextFile(string fp) {
            filepath = fp;
            filename = "TODO";
        };
};

class  OrgdownFile: public TextFile {
    private:
        bool tracked_status;
        string org_entries[];
    public:
        OrgdownFile(string fp) : TextFile(fp) {  // member initialization list
            tracked_status = true;
        }

        string* find_entries(string pattern_data) {
            // use pattern_data to find files
            return org_entries;
        }
        

};

class OrgEntry {
    private:
        string location;
        string description;
        string entry_type;
        int priority;
        string todo_attributes;
    public:
        OrgEntry(string loc,
                 string desc,
                 string e_type,
                 int pri,
                 string todo_attrib) {
            location = loc;
            description = desc;
            entry_type = e_type;
            priority = pri;
            todo_attributes = todo_attrib;
        }
        
        bool relateEntries() {
           std::cout << "TODO Relating Matches" << endl;
        }
};

class OrgdownSession {
    private:
        string session_type;
        string program_path;
    public:
        OrgdownSession(string s_type, string s_path) {
            session_type = s_type;
            program_path = s_path;
        }

        string sessionType() {
            return session_type;
        }
        // etc
};

int main () {
    string session_type = "CLI";
    OrgdownSession s {session_type, "//fake//path"};
    cout << s.sessionType() << endl;
    return 0;
}