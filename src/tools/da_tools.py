import os
import subprocess

from .logger import Logger
from .markdown_code import display_markdown_message


class DACodeInterpreter:
    def __init__(self):
        self.logger = Logger.initialize_logger("logs/da-code-interpreter.log")

    def _check_compilers(self, language):
        try:
            language = language.lower().strip()

            compilers = {
                "python": ["python", "--version"],
            }

            if language not in compilers:
                self.logger.error("Invalid language selected.")
                return False

            compiler = subprocess.run(
                compilers[language], capture_output=True, text=True
            )
            if compiler.returncode != 0:
                self.logger.error(f"{language.capitalize()} compiler not found.")
                return False

            return True
        except Exception as exception:
            self.logger.error(f"Error occurred while checking compilers: {exception}")
            raise Exception(f"Error occurred while checking compilers: {exception}")

    def extract_code(
        self,
        code: str,
        start_sep="```",
        end_sep="```",
        skip_first_line=True,
        code_mode=True,
    ):
        """
        Extracts the code from the provided string.
        If the string contains the start and end separators, it extracts the code between them.
        Otherwise, it returns the original string.
        """
        try:
            has_newline = False
            is_code = False
            if start_sep in code and end_sep in code:
                # start = code.find(start_sep) + len(start_sep)
                start = code.find(start_sep)
                # Skip the newline character after the start separator
                if code[start] == "\n":
                    start += 1
                    has_newline = True

                end = code.find(end_sep, start + 3)
                if end != -1:
                    if skip_first_line and code_mode and not has_newline:
                        # Skip the first line after the start separator
                        start = code.find("\n", start) + 1

                    code = code[start:end]
                    # Remove extra words for commands present.
                    if not code_mode and "bash" in code:
                        code = code.replace("bash", "")

                    is_code = True
                    self.logger.info("Code extracted successfully.")
                else:
                    is_code = False
            else:
                self.logger.info(
                    "No special characters found in the code. Returning the original code."
                )
                is_code = False
            return code, is_code
        except Exception as exception:
            self.logger.error(f"Error occurred while extracting code: {exception}")
            raise Exception(f"Error occurred while extracting code: {exception}")

    def save_code(self, filename="output/code_generated.py", code=None):
        """
        Saves the provided code to a file.
        The default filename is 'code_generated.py'.
        """
        try:
            # Check if the directory exists, if not create it
            directory = os.path.dirname(filename)
            if not os.path.exists(directory):
                os.makedirs(directory)

            if not code:
                self.logger.error("Code not provided.")
                display_markdown_message("Error **Code not provided to save.**")
                return
            else:
                with open(filename, "w") as file:
                    file.write(code)
                    self.logger.info(f"Code saved successfully to {filename}.")
        except Exception as exception:
            self.logger.error(f"Error occurred while saving code to file: {exception}")
            raise Exception(f"Error occurred while saving code to file: {exception}")

    def execute_code(
        self,
        code: str,
        language: str,
        env: str = "chatbot_writing",
        path_conda: str = "/data/dodx/anaconda3/bin/activate",
    ):
        """
        This method is used to execute the provided code in the specified language.

        Parameters:
        code (str): The code to be executed.
        language (str): The programming language in which the code is written.

        Returns:
        str: The output of the executed code.
        """
        try:
            language = language.lower()
            self.logger.info(f"Running code: {code[:100]} in language: {language}")

            # Check for code and language validity
            if not code or len(code.strip()) == 0:
                return "Code is empty. Cannot execute an empty code."

            # Check for compilers on the system
            compilers_status = self._check_compilers(language)
            if not compilers_status:
                raise Exception(
                    "Compilers not found. Please install compilers on your system."
                )

            if language == "python":
                command = f'bash -c "source {path_conda} && conda activate {env} && python {code}"'
                process = subprocess.Popen(
                    command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
                )
                stdout, stderr = process.communicate()
                stdout_output = stdout.decode("utf-8")
                stderr_output = stderr.decode("utf-8")
                self.logger.info(
                    f"Python Output execution: {stdout_output}, Errors: {stderr_output}"
                )
                return stdout_output, stderr_output

            else:
                self.logger.info("Unsupported language.")
                raise Exception("Unsupported language.")

        except Exception as exception:
            self.logger.error(f"Exception in running code: {str(exception)}")
            raise exception
