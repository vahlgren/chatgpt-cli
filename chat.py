from datetime import datetime
import json
import os
import readline
import sys
from typing import Dict, Tuple, List

import openai
import yaml
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich import print

welcome_msg = """
# Welcome to ChatGPT CLI!

Greetings! Thank you for choosing this CLI tool. This tool is generally developed for personal use purpose.

We use OpenAI's official API to interact with the ChatGPT, which would be more stable than the web interface.

This tool is still under development, and we are working on improving the user experience. 

If you have any suggestions, please feel free to open an issue on our [GitHub](https://github.com/efJerryYang/chatgpt-cli/issues)

Here are some useful commands you may frequently use:

- `!help`: show this message
- `!save`: save the conversation to a `JSON` file
- `!load`: load a conversation from a `JSON` file
- `!new`: start a new conversation
- `!regen`: regenerate the last response
- `!edit`: select a prompt message to edit (default: the last message)
- `!drop`: select a prompt message to drop (default: the last message)
- `!exit` or `!quit`: exit the program

You can enter these commands at any time when you are prompted to give your input.

For more detailed documentation, please visit <link_to_wiki> or <link_to_docs>

Enjoy your chat!
"""

# set up path to config.yaml
workdir = os.path.dirname(os.path.abspath(__file__))
config_path = os.path.join(workdir, "config.yaml")

# check if config file exists
first_launch_msg = """
# Welcome to ChatGPT CLI!

It looks like this is the first time you're using this tool.

To use the ChatGPT API you need to provide your OpenAI API key in the `config.yaml` file.

To get started, please follow these steps:

1. Copy the `config.yaml.example` file to `config.yaml` in the same directory.
2. Open `config.yaml` using a text editor an replace `<YOUR_API_KEY>` with your actual OpenAI API key.
3. Optionally, you can also set a default prompt to use for generating your GPT output.

If you don't have an OpenAI API key, you can get one at https://platform.openai.com/account/api-keys/.

Once you've configured your `config.yaml` file, you can start this tool again.

Thank you for using ChatGPT CLI!
"""
if not os.path.exists(config_path):
    print(
        Panel(
            Markdown(first_launch_msg),
            title="ChatGPT CLI Setup",
            border_style="red",
            width=120,
        )
    )
    exit(1)

# load configurations from config.yaml
with open(config_path, "r") as f:
    try:
        config = yaml.safe_load(f)
    except yaml.YAMLError:
        print("Error in configuration file:", config_path)
        exit(1)

# set up openai API key and system prompt
openai.api_key = config["openai"]["api_key"]
# set proxy if defined
if "proxy" in config:
    os.environ["http_proxy"] = config["proxy"].get("http_proxy", "")
    os.environ["https_proxy"] = config["proxy"].get("https_proxy", "")


def execute_command(user_input:str):
    if user_input == "!help":
        printmd(welcome_msg)
    elif user_input == "!save":
        save_data(prompt, filename)
    elif user_input == "!load":
        filename, prompt = load_data(prompt)
    elif user_input == "!new":
        filename = ""
        prompt = default_prompt
    elif user_input == "!regen":
        prompt = prompt[:-1]
        prompt.append(prompt[-1])
        printmd(prompt[-1]["text"])
    elif user_input == "!edit":
        prompt = edit_prompt(prompt)
    elif user_input == "!drop":
        prompt = drop_prompt(prompt)
    elif user_input == "!exit" or user_input == "!quit":
        print("Bye!")
        exit(0)
    elif user_input.startswith("!"):
        print("Invalid command, please try again")
    else:
        return False


def save_data(data: List[Dict[str, str]], filename: str) -> None:
    # save list of dict to JSON file
    currdir = os.path.dirname(os.path.abspath(__file__))
    print("Current: ", currdir)
    datadir = os.path.join(currdir, "data")
    if not os.path.exists(datadir):
        os.mkdir(datadir)
    # if filename end with json
    if filename.endswith(".json"):
        filepath = os.path.join(datadir, filename)
    else:
        filepath = os.path.join(datadir, filename + ".json")
    with open(filepath, "w") as f:
        json.dump(data, f, indent=4)
    print(f"Data saved to {filepath}")


def load_data(default_prompt: List[Dict[str, str]]) -> Tuple[str, List[Dict[str, str]]]:
    currdir = os.path.dirname(os.path.abspath(__file__))
    print("Current: ", currdir)
    datadir = os.path.join(currdir, "data")
    if not os.path.exists(datadir):
        os.mkdir(datadir)
    # list all JSON files in the 'data' directory
    files = [f for f in os.listdir(datadir) if f.endswith(".json")]
    if not files:
        print("No data files found in 'data' directory")
        return "", default_prompt
    # prompt user to select a file to load
    print("Available data files:")
    for i, f in enumerate(files):
        print(f"{i+1}. {f}")
    selected_file = input(
        f"Enter file number to load (1-{len(files)}), or Enter to start a fresh one: "
    )
    if not selected_file:
        return "", default_prompt
    # validate user input and load the selected file
    try:
        index = int(selected_file) - 1
        if not 0 <= index < len(files):
            raise ValueError()
        filepath = os.path.join(datadir, files[index])
        with open(filepath, "r") as f:
            data = json.load(f)
        print(f"Data loaded from {filepath}")
        return filepath, data
    except (ValueError, IndexError):
        print("Invalid input, please try again")
        return load_data(default_prompt)


console = Console()


def printmd(msg: str) -> None:
    console.print(Markdown(msg))


def user_input() -> str:
    """
    Get user input with support for multiple lines without submitting the message.
    """
    # Use readline to handle user input
    prompt = "\nUser: "
    lines = []
    while True:
        line = input(prompt)
        if line.strip() == "":
            break
        lines.append(line)
        # Update the prompt using readline
        prompt = "\r" + " " * len(prompt) + "\r" + " .... " + readline.get_line_buffer()
    # clear_input()
    # Print a message indicating that the input has been submitted
    msg = "\n".join(lines)
    user_output(msg + "\n**[Input Submitted]**")
    print()
    return msg


def user_output(msg: str) -> None:
    printmd("**User:** {}".format(msg))


def assistant_output(msg: str) -> None:
    printmd("**ChatGPT:** {}".format(msg))


def system_output(msg: str) -> None:
    printmd("**System:** {}".format(msg))


panel = Panel(
    Markdown(welcome_msg),
    title="ChatGPT CLI",
    border_style="green",
    expand=False,
    width=120,
)
print(panel)

default_prompt = config.get("openai", {}).get("default_prompt", None)
if default_prompt is None:
    default_prompt = []
    # Warnning: the default prompt is empty
    print(
        Panel(
            "Warning: the `default prompt` is empty in `config.yaml`",
            title="ChatGPT CLI Setup",
            border_style="red",
            width=120,
        )
    )
    exit(1)

filepath, messages = load_data(default_prompt)
print()
for msg in messages:
    if msg["role"] == "user":
        # printmd("**User:** {}".format(msg["content"]))
        user_output(msg["content"])
    elif msg["role"] == "assistant":
        # console.print(Markdown("**ChatGPT:** {}".format(msg["content"])))
        assistant_output(msg["content"])
    else:  # system
        # console.print(Markdown("**System:** {}".format(msg["content"])))
        system_output(msg["content"])
    # newline
    console.print()
# select to response to the conversation or start a new one
response = input(
    "Continue the conversation? You can also ask a follow up question. (y[es]/a[sk]/n[o]/q[uit]): "
)
if response.lower() in ["n", "no"]:
    messages = default_prompt
    print("Starting a new conversation...")
elif response.lower() in ["a", "ask"]:
    print("Ask a follow up question...")
    user_message = user_input()
    if user_message in ["q", "quit"]:
        print("Exiting...")
        exit()
    messages.append({"role": "user", "content": user_message})
elif response.lower() in ["q", "quit"]:
    print("Exiting...")
    exit()
else:
    print("Continuing the conversation...")
while True:
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  # or gpt-3.5-turbo-0301
            messages=messages,
        )
        assistant_message = response["choices"][0]["message"]["content"]
        messages.append({"role": "assistant", "content": assistant_message})
        # printmd("**ChatGPT:** {}".format(assistant_message))
        assistant_output(assistant_message)
        user_message = user_input()
    except openai.error.APIConnectionError as api_err:
        print(api_err)
        user_message = input(
            "Oops, something went wrong. Do you want to retry? (y/n): "
        )
        if user_message.lower() in ["n", "no"]:
            user_message = "quit"
        else:
            continue
    except openai.error.InvalidRequestError as invalid_err:
        print(invalid_err)
        user_message = input(
            "Oops, something went wrong. Do you want to select a message to drop and retry? (y/n): "
        )
        if user_message.lower() in ["n", "no"]:
            user_message = "quit"
        else:
            index_to_remove = []
            print(
                f"There are {len(messages)-1} messages in the conversation (exclude the system message):"
            )
            for i, msg in enumerate(messages):
                if i == 0:
                    # The system message should not be dropped
                    continue
                print(f"{i}. {msg['role']}: {msg['content']}\n")
                drop_msg = input(f"Drop this message? (y/n): ")
                if drop_msg.lower() in ["y", "yes"]:
                    index_to_remove.append(i)
                    print(f"Message {i} dropped")
            # remove the selected messages
            for i in sorted(index_to_remove, reverse=True):
                messages.pop(i)
            continue
    if user_message in ["quit", "exit", "q"]:
        t = f"{datetime.now():%Y-%m-%d_%H:%M:%S}"
        # Do you want to save the conversation?
        save = input(f"Do you want to save the conversation? (y[es]/n[o]): ")
        if save.lower() in ["n", "no"]:
            print("Exiting...")
            break
        if not filepath:
            filename = input(f"Enter a filename to save to (default to '{t}.json'): ")
            filename = t if not filename.strip() else filename.strip()
            save_data(messages, filename)
            break
        # filepath is not empty, ask if user wants to save to the same file
        save = input(f"Save to the same file? (y[es]/n[o]): ")
        if save.lower() in ["n", "no"]:
            filename = input(
                f"Enter a filename to save to (default to '{t}.json'), or Enter 'exit' to exit: "
            )
            filename = t if not filename.strip() else filename.strip()
            save_data(messages, filename)
            break
        filename = os.path.basename(filepath)
        save_data(messages, filename)
        break
    messages.append({"role": "user", "content": user_message})

# Todo:
# 1. Support starting a new conversation with command `!new`
# 2. Support markdown enable or disable with command `!md-on` or `!md-off`
# 3. Support saving the conversation to a file with command `!save`
# 4. Markdown support even the user input.
# 5. Support loading a conversation from a file with command `!load`
# 6. Allow user to regenerate last message with command `!regen`
# 7. Allow user to drop a message with command `!drop`
# 8. Allow user to edit a message with command `!edit`
# 9. Allow user to change the model with command `!model`
# add reference to the hint i got from
# https://github.com/acheong08/ChatGPT
# https://github.com/mmabrouk/chatgpt-wrapper
# !help to start a new terminal with help info but the previous one shoule not be overriden
# Avoid [Ctrl]+[C] to interupt the input and prompt the user with a confirmation
