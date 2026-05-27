import subprocess
import pandas as pd


#/opt/homebrew/opt/python@3.12/bin/python3.12
python_path = "/opt/homebrew/opt/python@3.12/bin/python3.12"
prod_info = '/.../Automation/Printify/Data/product_information.csv' # contains desired image-to-publish PATH


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
    file = 'IMG_0866.JPG'
    df = pd.read_csv(prod_info)
    df['local_path'] = file
    df.to_csv(prod_info, index=False)


    # create product info
    #add to product_Info
    try:
        prod_path = "/.../Automation/Printify/Drivers/prod_info_create.py" #prod_info_create opens product_information.csv
        prod_cmd_arg = [
            "--prod_info", "satin-poster"
        ]

        prod_tot = [prod_path] + [prod_cmd_arg]

        run_command(prod_tot)
        print(f"Product Creation output:")

    except Exception as e:
        print(f"Error creating Printify template: {e}")
        
    
    # After generating art, create the product template on Printify.
    try:
        printify_path = "/.../Automation/Printify/Satin_Poster/sposter_requests.py"
        printify_cmd_arg = [
            "--prod_info", "satin-poster"
        ]
        printify_tot = [printify_path] + [printify_cmd_arg]

        run_command(printify_tot)
        print(f"Printify output")
    except Exception as e:
        print(f"Error creating Printify template: {e}")

    try:
        ig_fb_cmd = ["/.../Automation/Instagram Posts/ig_fb_post.py"]
        facebook_output = run_command(ig_fb_cmd)
        print(f"Facebook output: {facebook_output}")
    except Exception as e:
        print(f"Error posting on Facebook: {e}")
        
            
        

if __name__ == '__main__':
    main()
