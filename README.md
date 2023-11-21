# Project Description

This repository serves the purpose of creating a personalized bot for a company based on the provided documentation.

## Project Setup Instructions

To set up the project, the following steps should be followed:

1. **Repository Cloning**
   - Begin by cloning the repository to your local machine by executing the following command:
     ```bash
     git clone <repository_url>
     ```

2. **Document Preparation**
   - The necessary documents should be placed within the `data/raw` directory inside the repository. Supported file formats include TXT, HTML, and MD.

3. **Global Line Regex Configuration**
   - If your documents are extensive, the regex pattern utilized for paragraph segmentation in the global configuration file can be modified. However, for shorter files where processing as a whole is preferred, set the `always_get_full_files` parameter in the global configuration to 'True'.

4. **Prompt Customization**
   - Adjust the prompt within `config/chatgpt_config` to align with your specific requirements. A sample configuration is provided for a fictional company. Furthermore, ensure to set your API Key for Open AI.

5. **API or Telegram Bot Integration Selection**
   - In the `config/global_config` file, set the `enable_api` and `enable_telegram` parameters in accordance with your needs.

6. **Telegram Bot Configuration**

     In the `telegram_config` file, there are several parameters available for customization:
   - **token**: Your token for the Telegram bot
   - **bot_username**: The name of your bot on Telegram
   - **allow_only_whitelist**: Only individuals on the whitelist will be permitted to interact with the bot
   - **send_source_text_as_file**: The bot sends files containing the part of the documentation from which the answer was derived
   - **whitelist**: Two lists containing IDs that the bot will accept

8. **Docker Container Building**
   - Generate the Docker containers using the subsequent command:
     ```bash
     docker-compose build
     ```

9. **Application Launch**
   - Start the application by running Docker Compose:
     ```bash
     docker-compose up
     ```

The project is now configured and ready for utilization.
