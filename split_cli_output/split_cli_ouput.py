import os
import re


def get_files_in_path(root_dir, only_ext="log"):
    """returns a list with all files from the given directory"""
    files = [os.path.join(dirpath, file)
             for (dirpath, dirnames, filenames) in os.walk(root_dir)
             for file in filenames]

    if only_ext:
        ends_with = only_ext if only_ext[0] == "." else "." + only_ext
        return [file for file in files if file.endswith(ends_with)]

    else:
        return files


def split_config_file(raw_data):
    """splits multiple outputs from a single configuration file"""
    split_config = re.split("\n\S+#", raw_data)

    commands = dict()
    if len(split_config) > 0:
        # ignore the first element if it doesn't start with the prompt
        if not re.match("^\S+#", split_config[0], re.MULTILINE):
            split_config = split_config[1:]

        for single_command in split_config:
            lines = single_command.splitlines()

            # skip the command if no output is given
            if len(lines) > 1:
                # ensure that only the command is used as key
                if re.match("^\S+#", lines[0]):
                    cmd = lines[0].split("#")[1]
                else:
                    cmd = lines[0]

                commands[cmd] = "\n".join(lines[1:])

    return commands


if __name__ == "__main__":
    INPUT_DIRECTORY = "_input"
    OUTPUT_DIRECTORY = "_output"

    files = get_files_in_path(INPUT_DIRECTORY, only_ext="log")

    for file_path in files:
        if not os.path.isfile(file_path):
            print("File not found or no file: %s -- skip it" % file_path)

        else:
            with open(file_path) as f:
                raw_data = f.read()

            # the file name contains only the hostname following an extension
            hostname = os.path.basename(file_path)[:-len(".log")]

            # split the file in a <command>: <content> dictionary
            result = split_config_file(raw_data)

            # write results to the directory
            root_dir = os.path.join(OUTPUT_DIRECTORY, hostname)
            os.makedirs(root_dir, exist_ok=True)
            for command in result:
                with open(os.path.join(root_dir, "%s.txt" % command.strip()), "w+") as f:
                    f.write(result[command])
