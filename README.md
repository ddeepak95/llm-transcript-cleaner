Simple script to clean the `.txt` transcript output obtained from [https://github.com/ddeepak95/whisper-transcript-w-diarization/blob/main/whisper-diarization.ipynb](https://github.com/ddeepak95/whisper-transcript-w-diarization/blob/main/whisper-diarization.ipynb). The script uses OpenAI's API to clean the transcript.

## Usage

- Install the required packages from the requirement file
- Add OpenAI API key to a `.env` file as `OPENAI_API_KEY`
- Run the scripts in `app.ipynb` to clean the transcript

## Note

The `system_message` can be updated to determine the level of cleaning. Experiment with the `system_message` to get the desired output.
