import paramiko, time
from scp import SCPClient
import google.generativeai as genai

#Important files
Keychain = r'C:\Users\james\OneDrive\Desktop\Capstone_Project_Work\Temp_Keychain.txt'                                   #API Key and SSH Passcode
Windows_log_file = r"C:\Users\james\OneDrive\Desktop\Capstone_Project_Work\Feedback.txt"                                #Windows log file
Linux_st_file = r"/home/james/OpenPLC_v3/webserver/st_files/program_to_check.st"                                        #ST file on OpenPLC Server
First_Prompt_File = r"C:\Users\james\OneDrive\Desktop\Capstone_Project_Work\First_Prompt_V4.txt"                        #First Prompt File
Gemini_Output_File = r"C:\Users\james\OneDrive\Desktop\Capstone_Project_Work\Gemini_API_Raw_Output_V3.txt"              #Raw AI Output
Windows_st_file = r"C:\Users\james\OneDrive\Desktop\Capstone_Project_Work\Extracted_Code.st"                            #Iterative ST file
#Template = r"C:\Users\james\OneDrive\Desktop\Capstone_Project_Work\OpenPLC_Example.txt"                                 #Example of working code

#Add LLM user interface

#****************************************************************************************************************************************************************************

#Main python fuunction for initiating command sequence

#****************************************************************************************************************************************************************************

def main_control_sequence(Chat_session):
    global Gemini_Output_File, Windows_st_file, Windows_log_file, Linux_st_file
    global scp

    #FILENAMES AND FILEPATHS 
    #Windows_ChatGPT_Output = r"C:\Users\james\OneDrive\Desktop\Capstone_Project_Work\Example_of_working_code.txt"
    #Windows_ChatGPT_Output = r"C:\Users\james\OneDrive\Desktop\Capstone_Project_Work\V3_Chat_GPT_Raw_Output.txt"

    #--------------------------------------
    #STAGE 1: COMPILATION
    #--------------------------------------

    Loop = 0
    ErrorFlag = 1
    NoCodeFlag = 0
    MaxIterations = 5
    
    #Iterative While Loop for Coding 
    while Loop <= MaxIterations and ErrorFlag == 1:

        print("\n\n\n *********************************************************************")
        print("While Loop iteration number {}\n".format(Loop+1))

        #PHASE 1 -- EXTRACT STRUCTURED TEXT FROM CHATGPT OUTPUT 
        NoCodeFlag = Extract_ST_Code(Gemini_Output_File, Windows_st_file)

        time.sleep(1)

        #PHASE 1.5 -- CHECK TO SEE IF THE MODEL SENT BACK ACTIONABLE FEEDBACK
        if NoCodeFlag:
            print("Attempting to reprompt model for code (WIP)")
            RepromptModel(Chat_session)            
            continue

        #PHASE 2 -- UPLOAD FILE TO OPENPLC RUNTIME WEBSERVER 
        scp.put(Windows_st_file, recursive=True, remote_path=Linux_st_file) 

        #PHASE 3 -- COMPILE ST FILE USING OPENPLC RUNTIME  
        Activity = 'running complier'
        Command = 'cd OpenPLC_v3/webserver/scripts/; bash compile_program.sh program_to_check.st >> /home/james/log.txt'
        Output, Error = run_command(Command, Activity)

        #PHASE 4 -- RECORD ERROR MESSAGES AND SEND THEM TO MODEL
        print("Writing complier feedback to file")
        Logs = open(Windows_log_file, 'w')     
        if Error:
            print("Sending to error function")
            ClassifyErrorAndFeedback(Error, Chat_session)
            Logs.write(Error)
            ErrorFlag = 1
        else:
            Logs.write(Output)
            print("Successful Compilation, Moving to Next Step")
            SuccessFeedback = "Thank you"
            Reply = Chat_session.send_message(SuccessFeedback).text
            print(Reply)
            ErrorFlag = 0
        Logs.close()

        #Temporary code
        Loop+=1

    #TEMPORARY CODE
    print("While Loop Terminated")
    if Loop > MaxIterations:
        #Send final success message to model 
        SuccessFeedback = "Thank you"
        print("Sends final feedback to LLM")
        Reply = Chat_session.send_message(SuccessFeedback).text
        print(Reply)

    #PHASE 5: FETCH COMPILED FILE (WIP)

    #--------------------------------------
    #STAGE 2: OPENAI GYM SIMULATION
    #--------------------------------------

    print("INITATING STAGE 2")
    time.sleep(1)

    #Imports Ted's python script to run
    #import Ted_code_placeholder as Stage2

    #Executes code
    #Stage2.Run_Simulation()

    """
    STEPS INVOLVED
    - Implement Ted's code here
    - Iteratively run code through OpenAI Gym 
    - Compile code through OpenPLC one last time to catch any final bugs    
    """


    #--------------------------------------
    #STAGE 3: AUTOMATED DEPLOYMENT (WIP)
    #--------------------------------------
    
    """
    STEPS INVOLVED---
    - Trasnmit code over to deployment environment 
        - MODBUS Protocol?
        - Bluetooth file transfer?
    - Use Opennes API to upload and compile code using Siemens TIAPortal
    - Collect any final error messages and repeat Stages 1-2 if neccessary
    - Upload code to Siemens S7-1500 PLC
    - Execute code on FischerTechnik Testbed  
    """

        
    return

#****************************************************************************************************************************************************************************

#Function for error handling

#****************************************************************************************************************************************************************************

def ClassifyErrorAndFeedback(Error, Chat_Session):
    global Gemini_Output_File, Windows_st_file

    #Extract code from file
    try:
        with open(Windows_st_file, 'r') as file:
            code = file.read()
    except FileNotFoundError:
        print("File not found error, aborting...")
        abort(1)

    #-------- INTERPRET ERROR MESSAGES ---------------

    #---List of Error Messages I am looking for---
    print("Determinining response to model")

    #Error message caused when LLM improperly formats ST code block in response and my code can't read it
    CannotReadPromptError =  """mv: cannot stat 'Config0.c': No such file or directory
    mv: cannot stat 'Config0.h': No such file or directory
    mv: cannot stat 'Res0.c': No such file or directory"""

    #Error message caused when code is ineligible to OpenPLC
    IneglibleCodeError = "Parsing failed because of too many consecutive syntax errors. Bailing out!" 

    #------- SEND FEEDBACK TO LLM ----------------------

    #--Gives Feedback to Model--
    if Error is CannotReadPromptError:
        ModelFeedback = "Can you please reformat how the structured text response is enclosed the response?"
    elif Error is IneglibleCodeError:
        ModelFeedback = "OpenPLC is saying that parsing failed because of too many conesective syntax errors. Can you please try to revise the code. Please provide the full corrected code."
    else:
        ModelFeedback = "Attempted to run the code but got error messages: \n{} \nPlease revise the code to fix the errors. \n".format(Error)

    #Send Feedback to Model and Get New Response
    print("\n\n------------------------ FEEDBACK SENT TO MODEL ------------------------\n " + ModelFeedback + "\n------------------------------------------------\n\n")
    New_Response = Chat_Session.send_message(ModelFeedback).text
    print("\n\n ------------- REPLY FROM LLM MODEL ------------------ \n" + New_Response + "\n-------------------------------\n")

    # --------- DATA LOGGING ----------------------
    #Write new response to file
    Output = open(Gemini_Output_File, 'w')    
    Output.write(New_Response)
    Output.close()

    return

#**********************************************************************************************************************************************************************

#Function for managing SSH sessions
#Note: only have one instance of shell per command, so commands must be run in one shot

#**********************************************************************************************************************************************************************

def ssh_login(hostname, username, password):
    try:
        # Create an SSH client instance
        client = paramiko.SSHClient()

        # Automatically add the server's host key to the local HostKeys object
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        # Connect to the SSH server
        client.connect(hostname, username=username, password=password)

        print("Successfully connected to", hostname)
        
        #Return SSH client instance to main function 
        return client
    
    except Exception as e:
        print("Error logging in SSH:", e)
        exit(1)

#Python Function for Interacting with Command Line
def run_command(command, activity):
    global client

    #Display activity
    print("Running: " + command)

    try:
        # Execute the command in the terminal 
        print("Sent command")
        stdin, stdout, stderr = client.exec_command(command)
        
        print("Waiting for response")
        #Capture the output
        output = stdout.read()
        error = stderr.read()
        
        print("\n")
        # Check if there's any error
        if error:
            print("Error occured when " + activity + ":\n", error.decode())
        else:
            print("Output:", output.decode())
        return output.decode(), error.decode()        
    except Exception as e:
        print("An error occurred:", e)
        abort(1)

#****************************************************************************************************************************************************************************

#Function for extracting ST code from file

#****************************************************************************************************************************************************************************

def Extract_ST_Code(source, destination):
      
    #Declares flags 
    Flag = 0
    WaitOneLine = 0
    CheckForCode = 0

    try:
        with open(source) as input:
            with open(destination, "w") as output:

                #Scan files line by line
                print("Writing code to .st file")
                for line in input:
                    #Identifies which parts of output contain structured text code  
                    if ((line.rstrip() == "```structured-text") or (line.rstrip() == "```structured text")):  #Start of structured text 
                        print("Structure code begins at line " + line)
                        Flag = 1
                        WaitOneLine = 1
                        CheckForCode += 1
                    elif line.rstrip() == "```":
                        print("Structured code ends at line " + line)
                        Flag = not Flag
                        CheckForCode += 1

                    #Copies relevant sections into structured text file                
                    if (Flag and not WaitOneLine):
                        output.write(line)
                    elif (Flag == 1 and WaitOneLine == 1):
                        print("Begin")
                        WaitOneLine = 0
                    
                input.close()
                output.close()

    except Exception as e:
        print("Error formatting st file:", e)
        abort(1)

    if CheckForCode < 2:
        print("EDGE CASE DETECTED: AI MODEL DIDN'T RETURN CODE")
        return 1
    else:
        return 0
    

#*****************************************************************************************************************************************************************************

#Function for asking the model to generate code if it fails to provide structural text code

#****************************************************************************************************************************************************************************

def RepromptModel(Chat_Session):
    Message = "Can you attempt to generate the code?"

    #Send Feedback to Model and Get New Response
    print("\n\n------------------------ FEEDBACK SENT TO MODEL ------------------------\n " + Message + "\n------------------------------------------------\n\n")
    New_Response = Chat_Session.send_message(Message).text
    print("\n\n ------------- REPLY FROM LLM MODEL ------------------ \n" + New_Response + "\n-------------------------------\n")

    # --------- DATA LOGGING ----------------------
    #Write new response to file
    Output = open(Gemini_Output_File, 'w')    
    Output.write(New_Response)
    Output.close()
    return


#**********************************************************************************************************************************************************************

#Open Dialoge with AI Model

#****************************************************************************************************************************************************************************

def Setup_Gemini(GOOGLE_API_KEY):
    global Gemini_Output_File, First_Prompt_File
    
    #Step 1: Move API Key 
    genai.configure(api_key=GOOGLE_API_KEY)

    #Step 2: Get Model
    Gemini_Model = genai.GenerativeModel('gemini-pro')
    Gemini_convo = Gemini_Model.start_chat(history=[])

    #Step 3: Get Initial Prompt
    print("Sending first prompt to LLM model")

    prompt = None
    with open(First_Prompt_File, 'r') as Prompt1file:
        prompt = Prompt1file.read()
        Prompt1file.close()

    #Step 4: Test Response
    Gemini_reply = Gemini_convo.send_message(prompt)
    Gemini_response = Gemini_reply.text
    print(f"\n----------- Resonse from model -------------\n: {Gemini_response} \n -------------------------- \n\n")

    #Step 5: Extract Output to File
    print("Writing LLM response to file")
    Logs = open(Gemini_Output_File, 'w')    
    Logs.write(Gemini_response)
    Logs.close()
    return Gemini_Model, Gemini_response, Gemini_convo

#**********************************************************************************************************************************************************************

#Extract A Specific Line from a Text File

#****************************************************************************************************************************************************************************

def extract_a_line_from_a_txt_file(file_path, line_number):
    try:
        with open(file_path, 'r') as file:
            lines = file.readlines()
            if 1 <= line_number <= len(lines):
                desired_line = lines[line_number - 1]  # Adjust for 0-based indexing
                return desired_line.strip()  # Remove leading/trailing whitespace
            else:
                return f"Line {line_number} does not exist in the file."
    except FileNotFoundError:
        return f"File '{file_path}' not found."
        abort(1)

#*****************************************************************************************************************************************************************************

#Controlled shutdown function

#****************************************************************************************************************************************************************************

def abort(mode):
    global client
    scp.close()
    client.close()
    exit(mode)

#************************************************************************************************************************************************************

#Program Entry

#****************************************************************************************************************************************************************************

if __name__ == '__main__':
    
    #Get all needed creds
    hostname = "JamesOMEN"
    username = extract_a_line_from_a_txt_file(Keychain, 6)
    password = extract_a_line_from_a_txt_file(Keychain, 9)
    GOOGLE_API_KEY = extract_a_line_from_a_txt_file(Keychain, 3)

    #Starts a convo with LLM Model 
    Model, First_Response, Active_Session = Setup_Gemini(GOOGLE_API_KEY)
    
    # Call the function to initiate an SSH login & establish clients 
    client = ssh_login(hostname, username, password)
    scp = SCPClient(client.get_transport())
    
    # Start main control sequence  
    main_control_sequence(Active_Session)

    # Close the SSH connection
    abort(0)
    