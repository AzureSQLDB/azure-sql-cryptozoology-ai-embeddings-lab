import json
import os
import struct
import logging
import pyodbc
import re

from azure import identity
from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential

user_token = 1

def get_conn():
    credential = DefaultAzureCredential(exclude_interactive_browser_credential=False)
    token_bytes = credential.get_token("https://database.windows.net/.default").token.encode("utf-16le")
    token_struct = struct.pack(f'<I{len(token_bytes)}s', len(token_bytes), token_bytes)
    return token_struct

def get_cryptids(search_text:str) -> str:
    global user_token
    if user_token == 1:
        user_token = get_conn()
    conn_str=os.environ["SQL_PYTHON_DRIVER_CONNECTION_STRING"]
    print(conn_str)
    conn = pyodbc.connect(conn_str, attrs_before={1256:user_token})
    logging.info("Querying MSSQL...")
    logging.info(f"Message content: '{search_text}'")
    try:        
        cursor = conn.cursor()  
        params = (search_text, )
        cursor.execute("{CALL [dbo].[get_cryptids] (?)}", params)
        output_value = cursor.fetchall()

        logging.info(f"Found {len(output_value)} cryptids.")
        
        payload = ""
        for row in output_value:
            payload += f'CryptidName: {row[0]}|TimeOfDay: {row[1]}|Location: {row[2]}|Weather: {row[3]}|VideoSetting: {row[4]}|"VideoDescription: "{row[5]}|"CryptidLore: "{row[6]}|"ThreatLevel: "{row[7]}'
            payload += "\n"
        
        return payload    
    finally:
        cursor.close()    

if __name__ == "__main__":
    print(get_cryptids("bigfoot"))
