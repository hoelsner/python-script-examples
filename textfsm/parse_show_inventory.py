import textfsm
# Load the input file to a variable
input_file = open("show_inventory.txt", encoding='utf-8')
raw_text_data = input_file.read()
input_file.close()

# Run the text through the FSM. 
# The argument 'template' is a file handle and 'raw_text_data' is a 
# string with the content from the show_inventory.txt file
template = open("show_inventory_multiple.textfsm")
re_table = textfsm.TextFSM(template)
fsm_results = re_table.ParseText(raw_text_data)

# the results are written to a CSV file
outfile_name = open("outfile.csv", "w+")
outfile = outfile_name

# Display result as CSV and write it to the output file
# First the column headers...
print(re_table.header)
for s in re_table.header:
    outfile.write("%s;" % s)
outfile.write("\n")

# ...now all row's which were parsed by TextFSM
counter = 0
for row in fsm_results:
    print(row)
    for s in row:
        outfile.write("%s;" % s)
    outfile.write("\n")
    counter += 1
print("Write %d records" % counter)
