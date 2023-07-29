import os
import logging
from datetime import datetime
import cmd

class File:
    def __init__(self, name, content='', permissions=None, path=''):
        self.name = name
        self.content = content
        self.path = os.path.join(path, name)
        self.permissions = permissions if permissions else {'read': True, 'write': True, 'execute': False}
        self.creation_time = datetime.now()
        self.modified_time = self.creation_time
        with open(self.path, 'w') as f:
            f.write(self.content)

    def update_content(self, new_content):
        self.content = new_content
        with open(self.path, 'w') as f:
            f.write(self.content)

    def delete(self):
        os.remove(self.path)

class Directory:
    def __init__(self, name, path=''):
        self.name = name
        self.path = os.path.join(path, name)
        os.makedirs(self.path, exist_ok=True)
        self.contents = {}

class FileSystem:
    def __init__(self):
        self.root = Directory('root')
        self.current_directory = self.root
    
    def create_directory(self, path, name):
        try:
            directory = self.get_directory(path)
            if name in directory.contents:
                raise FileExistsError(f"Directory '{name}' already exists.")
            directory.contents[name] = Directory(name, directory.path)
        except FileNotFoundError as e:
            logging.error(str(e))
        except FileExistsError as e:
            logging.error(str(e))
        except Exception as e:
            logging.error(f"An unexpected error occurred: {str(e)}")
        logging.info(f"Directory '{name}' created at path '{path}'")

    def create_file(self, path, name, content='', permissions=None):
        if permissions is None:
            permissions = {'read': True, 'write': True, 'execute': False}
        try:
            directory = self.get_directory(path)
            if name in directory.contents:
                raise FileExistsError(f"File '{name}' already exists.")
            directory.contents[name] = File(name, content, permissions, directory.path)
        except FileNotFoundError as e:
            logging.error(str(e))
        except FileExistsError as e:
            logging.error(str(e))
        except Exception as e:
            logging.error(f"An unexpected error occurred: {str(e)}")

    def read_file(self, path, name):
        try:
            file = self.get_file(path, name)
            if file.permissions['read']:
                return file.content
            else:
                raise PermissionError("Read permission denied.")
        except FileNotFoundError as e:
            logging.error(str(e))
        except PermissionError as e:
            logging.error(str(e))
        except Exception as e:
            logging.error(f"An unexpected error occurred: {str(e)}")

    def write_file(self, path, name, content):
        try:
            file = self.get_file(path, name)
            if file.permissions['write']:
                file.update_content(content)
                file.modified_time = datetime.now()
            else:
                raise PermissionError("Write permission denied.")
        except FileNotFoundError as e:
            logging.error(str(e))
        except PermissionError as e:
            logging.error(str(e))
        except Exception as e:
            logging.error(f"An unexpected error occurred: {str(e)}")

    def delete_file(self, path, name):
        try:
            directory = self.get_directory(path)
            if name in directory.contents:
                directory.contents[name].delete()
                del directory.contents[name]
            else:
                raise FileNotFoundError(f"File '{name}' not found.")
        except FileNotFoundError as e:
            logging.error(str(e))
        except Exception as e:
            logging.error(f"An unexpected error occurred: {str(e)}")

    def get_directory(self, path):
        current_directory = self.root
        for directory_name in path:
            if directory_name in current_directory.contents and isinstance(current_directory.contents[directory_name], Directory):
                current_directory = current_directory.contents[directory_name]
            else:
                raise FileNotFoundError("Directory not found.")
        return current_directory

    def get_file(self, path, name):
        directory = self.get_directory(path)
        if name in directory.contents and isinstance(directory.contents[name], File):
            return directory.contents[name]
        else:
            raise FileNotFoundError(f"File '{name}' not found.")

class FileSystemShell(cmd.Cmd):
    intro = '\nWelcome to the FileSystemShell.\n' \
            'Type help or ? to list commands.\n' \
            'Type help <command> to get help on a specific command.\n'
    file = None
    # Define the current_path variable as a list starting with 'root'
    current_path = ['root']

    def precmd(self, line):
        # Update the prompt to reflect the current_path
        self.prompt = '(filesystem ' + ' '.join(self.current_path) + ') '
        return line

    def do_touch(self, arg):
        'Create a new file: touch filename [content]'
        args = arg.split(maxsplit=1)
        name = args[0] 
        content = args[1] if len(args) > 1 else ""
        # Use the current_path instead of calling os.getcwd()
        fs.create_file(self.current_path, name, content)

    def do_cat(self, arg):
        'Read a file: cat filename'
        name = arg
        # Use the current_path instead of calling os.getcwd()
        print(fs.read_file(self.current_path, name))

    def do_mkdir(self, arg):
        'Create a new directory: mkdir directory_name'
        name = arg
        # Use the current_path instead of calling os.getcwd()
        fs.create_directory(self.current_path, name)

    def do_ls(self, arg):
        'List files and directories: ls'
        # Use the current_path instead of calling os.getcwd()
        directory = fs.get_directory(self.current_path)
        for name, item in directory.contents.items():
            print(name)

    def do_cd(self, arg):
        'Change directory: cd directory_name'
        # Update the current_path variable, and use it to check if the directory exists
        self.current_path.append(arg)
        # Use the current_path to get the directory
        directory = fs.get_directory(self.current_path)
        # If the directory exists, the current_path is updated, otherwise revert it
        if directory:
            fs.current_directory = directory
        else:
            self.current_path.pop()

    def do_echo(self, arg):
        'Write to a file: echo filename content'
        args = arg.split(maxsplit=1)
        if len(args) < 2:
            print("You need to provide content to write into the file.")
        else:
            name, content = args
            # Use the current_path instead of calling os.getcwd()
            fs.write_file(self.current_path, name, content)

    def do_rm(self, arg):
        'Delete a file: rm filename'
        name = arg
        # Use the current_path instead of calling os.getcwd()
        fs.delete_file(self.current_path, name)

    def do_exit(self, arg):
        'Exit the shell: EXIT'
        print('Thank you for using the FileSystemShell')
        return True

    def default(self, line):
        print('Command not recognized. Type "help" or "?" for a list of commands.')

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    fs = FileSystem()
    FileSystemShell().cmdloop()