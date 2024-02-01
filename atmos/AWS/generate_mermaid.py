import os

def generate_mermaid_map(startpath, file_types=None):
    if file_types is None:
        file_types = []
    mermaid_graph = ["graph TD;"]
    node_relations = []

    for root, dirs, files in os.walk(startpath):
        path = root.split(os.sep)
        root_node = root.replace(os.sep, '_').replace('.', '_')
        relevant_files = [file for file in files if any(file.endswith(ft) for ft in file_types)] if file_types else files

        if len(path) > 1 or relevant_files:
            # Create node for directory
            mermaid_graph.append(f"    {root_node}[\"{os.path.basename(root)}\"];")
            # Create relation from parent to current directory
            if len(path) > 1:
                parent_path = os.sep.join(path[:-1]).replace(os.sep, '_').replace('.', '_')
                node_relations.append(f"    {parent_path} --> {root_node};")

        for file in relevant_files:
            # Create node for file
            file_node = f"{root_node}_{file.replace('.', '_')}"
            mermaid_graph.append(f"    {file_node}[\"{file}\"];")
            # Create relation from directory to file
            node_relations.append(f"    {root_node} --> {file_node};")

    return "\n".join(mermaid_graph + node_relations)

# Specify the top level directory here
start_path = 'stacks'  # replace with your directory path
# Specify the file types you want to include in the mermaid map
file_types = ['.yaml', '.md']  # Add or remove file types as needed
mermaid_output = generate_mermaid_map(start_path, file_types=file_types)

# Specify the output file names
output_mmd_file_name = 'directory_structure.mmd'
output_md_file_name = 'directory_structure.md'

# Write the Mermaid diagram code to a .mmd file
with open(output_mmd_file_name, 'w') as file:
    file.write(mermaid_output)

# Write the Mermaid diagram code to a Markdown (.md) file with Mermaid code fences
with open(output_md_file_name, 'w') as file:
    file.write(f"```mermaid\n{mermaid_output}\n```")

print(f"Mermaid diagram saved to {output_mmd_file_name} and {output_md_file_name}")