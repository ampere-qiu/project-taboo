# Project-Taboo : Taboo Game App

The Taboo Game App is an interactive Python application designed to facilitate the popular party game "Taboo" using voice input and AI assistance. Built with Tkinter for the graphical user interface, the app allows players to engage in the game where one player must describe a word without using specific "taboo" words or phrases to help the agent guess the keyword. 

Please note that, this project is experimental and a work in progress. The design and functionality are subject to change and further development.

## Features

- **Interactive UI**: Utilizes Tkinter for a user-friendly interface with navigation buttons and a dynamic display of game cards.
- **Voice Recording**: Integrates PyAudio for recording player descriptions using a microphone.
- **AI Assistance**: Leverages OpenAI's GPT-4 model to assist players by generating clues based on recorded descriptions.
- **Data Management**: Reads game cards and taboo words from a JSON file, allowing for easy customization and expansion of game content.

## Dependencies
- Python (>=3.6)
- Pillow
- PyAudio
- openai==0.11.0

## Contributing
Feel free to fork this repository, contribute improvements, or report issues. Contributions are welcome!


