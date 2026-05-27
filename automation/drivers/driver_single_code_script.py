import subprocess

#/opt/homebrew/opt/python@3.12/bin/python3.12
python_path = "/opt/homebrew/opt/python@3.12/bin/python3.12"

#Square?
square = input("Square? (true or false):")



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

    #flowers = ['daisy'] #, 'hot', 'accent', 'purples', 'cividis', 'plasma']  # etc.

    #particle_nums = [5, 30, 100]
    #configs = [(9*(10000/512),2), (4*(10000/512),4), (3*(10000/512),2)]
    colormaps = ['plasma', 'Blues', 'binary', 'winter', 'PuBu_r']
    for colormap in colormaps:

        try:

            art_path = '/.../Designs/Releases/Next_release/Heatmap/flowers_v4.py'
            art_cmd_arg = [
                "--flower", "external",
                "--colormap", colormap,
            ]

            art_tot = [art_path] + [art_cmd_arg]
    
            run_command(art_tot)
            print(f"Art generation output for")
        except Exception as e:
            print(f"Error generating art with : {e}")
            break  # Skip to the next colormap if one fails

        # create product info
        try:

            prod_path = "/.../Automation/Printify/Drivers/prod_info_create.py"
            prod_cmd_arg = [
                "--prod_info", "satin poster",
                "--square", square
            ]

            prod_tot = [prod_path] + [prod_cmd_arg]

            run_command(prod_tot)
            print(f"Product Creation output:")
        except Exception as e:
            print(f"Error creating Printify template: {e}")
            continue
        
        # After generating art, create the product template on Printify.
        try:

            printify_path = "/.../Automation/Printify/Satin_Poster/sposter_requests_publish.py"
            printify_cmd_arg = [
                "--prod_info", "satin poster"
            ]
            printify_tot = [printify_path] + [printify_cmd_arg]

            run_command(printify_tot)
            print(f"Printify output: ")
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
