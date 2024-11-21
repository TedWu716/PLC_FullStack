import time
import google.generativeai as genai
import os

# Important files - All paths converted to Linux style
KEYCHAIN = os.path.expanduser('~/Capstone_Project_Work/Temp_Keychain.txt')
LOG_FILE = os.path.expanduser('~/Capstone_Project_Work/Feedback.txt')
ST_FILE = '/home/james/OpenPLC_v3/webserver/st_files/program_to_check.st'
FIRST_PROMPT_FILE = os.path.expanduser('~/Capstone_Project_Work/First_Prompt_V4.txt')
GEMINI_OUTPUT_FILE = os.path.expanduser('~/Capstone_Project_Work/Gemini_API_Raw_Output_V3.txt')
EXTRACTED_CODE_FILE = os.path.expanduser('~/Capstone_Project_Work/Extracted_Code.st')

def main_control_sequence(Chat_session):
    Loop = 0
    ErrorFlag = 1
    NoCodeFlag = 0
    MaxIterations = 5
    
    while Loop <= MaxIterations and ErrorFlag == 1:
        print("\n\n\n *********************************************************************")
        print(f"While Loop iteration number {Loop+1}\n")

        # PHASE 1 -- EXTRACT STRUCTURED TEXT FROM CHATGPT OUTPUT 
        NoCodeFlag = Extract_ST_Code(GEMINI_OUTPUT_FILE, EXTRACTED_CODE_FILE)

        time.sleep(1)

        if NoCodeFlag:
            print("Attempting to reprompt model for code (WIP)")
            RepromptModel(Chat_session)            
            continue

        # PHASE 2 -- COPY FILE TO OPENPLC DIRECTORY
        os.system(f'cp {EXTRACTED_CODE_FILE} {ST_FILE}')

        # PHASE 3 -- COMPILE ST FILE USING OPENPLC RUNTIME  
        print("Running compiler")
        compile_cmd = 'cd /home/james/OpenPLC_v3/webserver/scripts/ && ./compile_program.sh program_to_check.st'
        compile_result = os.system(compile_cmd)

        # PHASE 4 -- RECORD ERROR MESSAGES AND SEND THEM TO MODEL
        print("Writing compiler feedback to file")
        if compile_result != 0:
            print("Compilation failed, sending to error function")
            with open('/home/james/log.txt', 'r') as log_file:
                error_msg = log_file.read()
            ClassifyErrorAndFeedback(error_msg, Chat_session)
            ErrorFlag = 1
        else:
            print("Successful Compilation, Moving to Next Step")
            Reply = Chat_session.send_message("Thank you").text
            print(Reply)
            ErrorFlag = 0

        Loop += 1

    if Loop > MaxIterations:
        Reply = Chat_session.send_message("Thank you").text
        print("Sends final feedback to LLM")
        print(Reply)

def ClassifyErrorAndFeedback(Error, Chat_Session):
    try:
        with open(EXTRACTED_CODE_FILE, 'r') as file:
            code = file.read()
    except FileNotFoundError:
        print("File not found error, aborting...")
        exit(1)

    if "mv: cannot stat" in Error:
        ModelFeedback = "Can you please reformat how the structured text response is enclosed in the response?"
    elif "Parsing failed because of too many consecutive syntax errors" in Error:
        ModelFeedback = "OpenPLC is saying that parsing failed because of too many consecutive syntax errors. Can you please try to revise the code? Please provide the full corrected code."
    else:
        ModelFeedback = f"Attempted to run the code but got error messages: \n{Error} \nPlease revise the code to fix the errors. \n"

    print(f"\n\n------------------------ FEEDBACK SENT TO MODEL ------------------------\n {ModelFeedback} \n------------------------------------------------\n\n")
    New_Response = Chat_Session.send_message(ModelFeedback).text
    print(f"\n\n ------------- REPLY FROM LLM MODEL ------------------ \n{New_Response}\n-------------------------------\n")

    with open(GEMINI_OUTPUT_FILE, 'w') as Output:    
        Output.write(New_Response)

def Extract_ST_Code(source, destination):
    Flag = 0
    WaitOneLine = 0
    CheckForCode = 0

    try:
        with open(source) as input_file, open(destination, "w") as output_file:
            print("Writing code to .st file")
            for line in input_file:
                if line.rstrip() in ["```structured-text", "```structured text"]:
                    print("Structure code begins at line " + line)
                    Flag = 1
                    WaitOneLine = 1
                    CheckForCode += 1
                elif line.rstrip() == "```":
                    print("Structured code ends at line " + line)
                    Flag = not Flag
                    CheckForCode += 1

                if Flag and not WaitOneLine:
                    output_file.write(line)
                elif Flag == 1 and WaitOneLine == 1:
                    print("Begin")
                    WaitOneLine = 0

    except Exception as e:
        print("Error formatting st file:", e)
        exit(1)

    return CheckForCode < 2

def RepromptModel(Chat_Session):
    Message = "Can you attempt to generate the code?"
    print(f"\n\n------------------------ FEEDBACK SENT TO MODEL ------------------------\n {Message} \n------------------------------------------------\n\n")
    New_Response = Chat_Session.send_message(Message).text
    print(f"\n\n ------------- REPLY FROM LLM MODEL ------------------ \n{New_Response}\n-------------------------------\n")

    with open(GEMINI_OUTPUT_FILE, 'w') as Output:    
        Output.write(New_Response)

def Setup_Gemini(GOOGLE_API_KEY):
    genai.configure(api_key=GOOGLE_API_KEY)
    Gemini_Model = genai.GenerativeModel('gemini-pro')
    Gemini_convo = Gemini_Model.start_chat(history=[])

    print("Sending first prompt to LLM model")
    with open(FIRST_PROMPT_FILE, 'r') as Prompt1file:
        prompt = Prompt1file.read()

    Gemini_reply = Gemini_convo.send_message(prompt)
    Gemini_response = Gemini_reply.text
    print(f"\n----------- Response from model -------------\n: {Gemini_response} \n -------------------------- \n\n")

    print("Writing LLM response to file")
    with open(GEMINI_OUTPUT_FILE, 'w') as Logs:    
        Logs.write(Gemini_response)

    return Gemini_Model, Gemini_response, Gemini_convo

def extract_a_line_from_a_txt_file(file_path, line_number):
    try:
        with open(file_path, 'r') as file:
            lines = file.readlines()
            if 1 <= line_number <= len(lines):
                return lines[line_number - 1].strip()
            return f"Line {line_number} does not exist in the file."
    except FileNotFoundError:
        print(f"File '{file_path}' not found.")
        exit(1)

if __name__ == '__main__':
    GOOGLE_API_KEY = extract_a_line_from_a_txt_file(KEYCHAIN, 3)
    Model, First_Response, Active_Session = Setup_Gemini(GOOGLE_API_KEY)
    main_control_sequence(Active_Session)