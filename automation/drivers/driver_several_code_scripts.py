import subprocess


#/opt/homebrew/opt/python@3.12/bin/python3.12
python_path = "/opt/homebrew/opt/python@3.12/bin/python3.12"


def run_command(command):
    if len(command) == 1:
        result = subprocess.run([python_path, command[0]])
    else:
        result = subprocess.run(['/opt/homebrew/opt/python@3.12/bin/python3.12', command[0]] + command[1])    
    """Run a python command and return its output; raise an exception if it fails."""
    print(f"Running command: {command}")
    
    if result.returncode != 0:
        # You can also log the error details here.
        raise RuntimeError(f"Command failed with error: {result.stderr}")
    return result.stdout

def main():
    # Define your different commands.
    # For instance, suppose you have a script to generate art that takes a colormap parameter:
    colormaps = ['ocean', 'gist_earth', 'gist_stern', 'brg', 'spring', 'winter', 'afmhot', 'cool', 'Pastel2', 'seismic', 'plasma', 'binary']
    good_files = ['/.../Designs/Releases/June_2024/Lines/Code/Pink_Lines/Lines.py', '/.../Designs/Releases/June_2024/Lines/Code/Sunset/even.py', '/.../Designs/Releases/June_2024/Lines/Code/Sunset/odd.py', '/.../Designs/Releases/June_2024/Lines/Code/USA/pattern1.py', '/.../Designs/Releases/June_2024/Lines/Code/USA/pattern2.py', '/.../Designs/Releases/June_2024/Lines/Code/USA/pattern3.py', '/.../Designs/Releases/June_2024/Lines/Code/USA/pattern4.py']

    vers = [True, False]
    
    for color in colormaps:
        for py_file in good_files:
            for ver in vers:

                art_path = py_file
                art_cmd_arg = [
                     "--color", f"{colormaps[color]}",
                     "--verity", f"{ver}",

                ]
                art_tot = [art_path] + [art_cmd_arg]
                
                try:
                    run_command(art_tot)
                    print(f"Art generation output for {colormaps[color]}")
                except Exception as e:
                    print(f"Error generating art with {colormaps[color]}: {e}")
                    break  # Skip to the next colormap if one fails

                # create product info
                try:
                    prod_path = "/.../Automation/Printify/Drivers/prod_info_create.py"
                    prod_cmd_arg = [
                        "--prod_info", "satin-poster"
                    ]

                    prod_tot = [prod_path] + [prod_cmd_arg]

                    run_command(prod_tot)
                    print(f"Product Creation output: {color}, {ver}")
                except Exception as e:
                    print(f"Error creating Printify template: {e}")
                    continue
                
                # After generating art, create the product template on Printify.
                try:
                    printify_path = "/.../Automation/Printify/Satin_Poster/sposter_requests.py"
                    printify_cmd_arg = [
                        "--prod_info", "satin-poster"
                    ]
                    printify_tot = [printify_path] + [printify_cmd_arg]

                    run_command(printify_tot)
                    print(f"Printify output: {color}, {ver}")
                except Exception as e:
                    print(f"Error creating Printify template: {e}")
                    continue
                
                # Then post to Facebook.
                try:
                    ig_fb_cmd = ["/.../Automation/Instagram Posts/ig_fb_post.py"]
                    facebook_output = run_command(ig_fb_cmd)
                    print(f"Facebook output: {facebook_output}")
                except Exception as e:
                    print(f"Error posting on Facebook: {e}")
                    continue
            

if __name__ == '__main__':
    main()
