import requests
import fitz  # PyMuPDF
import os
from pathlib import Path
import boto3
import json
from bs4 import BeautifulSoup
import html2text
import re


def convert_html_to_markdown(html_content: str) -> str:
    # Create an instance of the HTML2Text converter
    converter = html2text.HTML2Text()
    
    # Configure the converter options (optional)
    converter.body_width = 0  # Don't wrap lines
    converter.ignore_links = False  # Convert links to Markdown format
    converter.ignore_images = False  # Convert images to Markdown format
    
    # Convert the HTML content to Markdown
    markdown_content = converter.handle(html_content)
    return markdown_content

def scan_for_pii(text, folder_name="pii-audit", filename="all", page_num=0):
    os.makedirs(folder_name, exist_ok=True)
    comprehend = boto3.client('comprehend')
    max_text_length = 100000  # Maximum allowed text length by Comprehend
    detected_pii = []

    # Split the text into smaller chunks
    chunks = [text[i:i+max_text_length] for i in range(0, len(text), max_text_length)]

    for chunk_index, chunk in enumerate(chunks):
        try:
            # Call the DetectPiiEntities operation for each chunk
            response = comprehend.detect_pii_entities(
                Text=chunk,
                LanguageCode='en'
            )

            # Extract and handle the detected PII entities
            for entity in response['Entities']:
                # Adjust the offsets based on the chunk index
                begin_offset = entity['BeginOffset'] + chunk_index * max_text_length
                end_offset = entity['EndOffset'] + chunk_index * max_text_length

                detected_pii.append({
                    'FileName': filename,
                    'PageNumber': page_num,
                    'Type': entity['Type'],
                    'Score': entity['Score'],
                    'BeginOffset': begin_offset,
                    'EndOffset': end_offset,
                    'Value': text[begin_offset:end_offset]
                })
        except Exception as e:
            print(f"Error scanning chunk {chunk_index}: {str(e)}")
            
    # save the audit findings to file
    audit_file_path = Path(folder_name) / f"{filename}_pii_scan._audit.txt"
    with open(audit_file_path, "a", encoding="utf-8") as audit_file:
        if detected_pii:
            if audit_file.tell() == 0:  # Check if the file is empty
                audit_file.write("FileName,PageNumber,Type,Score,BeginOffset,EndOffset,Value\n")

            # Write the detected PII entities to the file
            for pii in detected_pii:
                pii_data_value = re.sub(r'<br\s*/?>', '\n', pii['Value'])
                pii_data_value = re.sub(r'<br/>', '', pii_data_value)
                pii_data_value = re.sub(r'</p>\s*<p>', '\n', pii_data_value)
                pii_data_value = pii_data_value.replace('\n', ' ').replace('\r', '')
                audit_file.write(f"{pii['FileName']},{pii['PageNumber']},{pii['Type']},{pii['Score']},{pii['BeginOffset']},{pii['EndOffset']},{pii_data_value}\n")
        else:
            print(f"No PII detected in {filename}")

    return detected_pii

import requests

def get_pdf_file(url_or_path):
    # Check if the input is a PDF file
    if url_or_path.endswith((".pdf", ".PDF")):
        if "://" in url_or_path:
            # It's a URL
            try:
                response = requests.get(url_or_path, timeout=30, verify=True)
                response.encoding = 'utf-8'
                if response.headers.get("Content-Type", "").startswith("application/pdf"):
                    return response.content
                else:
                    print(f"Error: The URL {url_or_path} does not point to a PDF file.")
                    return None
            except requests.exceptions.Timeout:
                print(f"Timeout error occurred while fetching content from {url_or_path}")
                return None
            except requests.exceptions.RequestException as e:
                print(f"Error occurred while fetching content from {url_or_path}: {e}")
                return None
        else:
            # It's a local file path
            try:
                with open(url_or_path, "rb") as pdf_file:
                    return pdf_file.read()
            except FileNotFoundError:
                print(f"Error: File '{url_or_path}' not found.")
                return None
            except Exception as e:
                print(f"Error occurred while reading local file '{url_or_path}': {e}")
                return None
    else:
        print(f"Error: '{url_or_path}' is not a PDF file.")
        return None
    
# Initialize the Bedrock Runtime client
bedrock_client = boto3.client("bedrock-runtime", region_name="us-east-1")

# Prompt the user for the PDF URL
# Defaults the AWS Marketplace contract
pdf_url = str(input("Enter the PDF URL: ") or "https://aws-mp-standard-contracts.s3.amazonaws.com/Standard-Contact-for-AWS-Marketplace-2022-07-14.pdf")

# Prompt the user for the number of documents to create
num_docs = int(input("Enter the number of documents to create (default: 1): ") or 1)

# Prompt the user for the model to use (Sonnet or Haiku)
model_choice = input("Enter 'S' for Sonnet or 'H' for Haiku (default: Haiku): ").upper() or 'S'

if model_choice == 'S':
    model_id = "anthropic.claude-3-sonnet-20240229-v1:0"
else:
    model_id = "anthropic.claude-3-haiku-20240307-v1:0"

# Prompt the user for document export format HTML or Wiki markup
document_export_format_choice = input("Enter 'H' for HTML or 'W' for Wiki Markup (default: HTML): ").upper() or 'H'

if document_export_format_choice == 'W':
    document_export_format = "HTML"
    document_export_format_instructions = "The HTML should mirror the structure and formatting of the original document as closely as possible. For example, headings in the document should be converted to heading tags like <h1>, paragraphs should use <p> tags, lists should use <ul> and <li> tags, etc."

    document_export_extension = ".md"  # Save wiki markup files with .md extension
else:
    document_export_format = "HTML"
    document_export_format_instructions = "The HTML should mirror the structure and formatting of the original document as closely as possible. For example, headings in the document should be converted to heading tags like <h1>, paragraphs should use <p> tags, lists should use <ul> and <li> tags, etc."
    document_export_extension = ".html"  # Save HTML files with .html extension
    
# Prompt the user to create a synthetic document or a non-synthetic (real) version prompt
synthetic_choice = input("Enter 'S' for Synthetic or 'R' for Real (default: Synthetic): ").upper() or 'S'

if synthetic_choice == 'S':
    prompt = f"""Here is an text export of the document page. 
                <raw text>{"{page_text}"}</raw_text> 
                Using the <raw text> page content, your task is to convert the text of this document into {document_export_format} format. As you do so, make the following changes to the document text:
                Rewrite it to be a realistic synthetic version of the original document, but aligned the specific meaning of the document. The meaning and intent should be similar, but the exact wording and details should be changed but maintaining the meaning.
                Replace all personally identifiable information (PII), such as names, addresses, phone numbers, etc. with realistic synthetic data. The synthetic PII should be in the same format as the original (e.g. replace a real phone number with a fake phone number, not random digits).
                After making these changes, convert the rewritten synthetic document text to {document_export_format}, preserving the original document structure and formatting as much as possible using {document_export_format} tags.
                {document_export_format_instructions}
                """
else:
    prompt = f"""Here is an text export of the document page. 
                <raw text>{"{page_text}"}</raw_text>
                Please study the document in the image carefully. Using the <raw text> page content, your task is to convert the content of this document into clean, semantic {document_export_format}. 
                {document_export_format_instructions}
                Do your best to preserve styling like bold, italics, font sizes, colors, alignment, etc. using inline CSS styles or appropriate tags.
                Only convert the actual content of the document. Do not add any content that is not present in the original image.
                Please provide the full {document_export_format} for the converted document inside {document_export_format} tags.
                """

# Setup the system prompts and messages to send to the model.
system_prompts = [{"text": "You convert document image to html or wiki markup."}]

# Prompt the user to add a system prompt to influence the model document processing.
system_prompt_user = str(input("Enter a system prompt to influence the conversion): ")) or system_prompts

if len(system_prompt_user) > 2:
    system_prompts = [{
        "text": f"You convert document image to html or wiki markup. {system_prompt_user}"
    }]
else:
    system_prompts = [{
        "text": "You convert document image to html or wiki markup."
    }]


# Prompt the user for the number of pages to process per document
num_pages_input = input("Enter the number of pages to process per document (default: all pages): ")
num_pages = int(num_pages_input) if num_pages_input else None

# Prompt the user to do a PII Audit
pii_audit_choice = input("Enter 'Y' to do a PII Audit or 'N' to skip. (default: Y): ").upper() or 'Y'

# Download the PDF file

response =  get_pdf_file(pdf_url)

pdf_path = "tmp_downloaded_pdf.pdf"

# Save the downloaded PDF to a local file
with open(pdf_path, "wb") as pdf_file:
    pdf_file.write(response)

# Open the PDF file with fitz
with fitz.open(pdf_path) as doc:
    # Get the filename from the URL
    filename = Path(pdf_url).stem

    # Iterate through the PDF file num_docs times
    for iteration in range(num_docs):
        response_message_all = ""
        # Iterate through each page and stop at the specified number of pages or the end of the document
        for page_num in range(len(doc)):
            if num_pages and page_num >= num_pages:
                break
            page = doc.load_page(page_num)

            # get the text contents from the page
            page_text = page.get_text("text")

            pix = page.get_pixmap()
            img_bytes = pix.tobytes()  # Get the image bytes directly from the PixMap
            folder_name = f"{filename[:4]}_{iteration + 1}"
            os.makedirs(folder_name, exist_ok=True)

            img_path = Path(folder_name) / f"{filename}_page_{page_num + 1}.png"
            img = fitz.Pixmap(img_bytes)
            img.save(img_path)
            print(f"Saved image for page {page_num + 1}")

            prompt_with_text = prompt.format(page_text=page_text)

            # Prepare the message for the Bedrock Converse API
            image_message = {
                "role": "user",
                "content": [
                    {"text": f"Page {page_num + 1}:"},
                    {
                        "image": {
                            "format": "png",
                            "source": {
                                "bytes": img_bytes  # Send the PNG image bytes directly
                            }
                        }
                    },
                    {"text": f"{prompt_with_text}"}
                ],
            }

            # Send the request to the Bedrock Converse API
            try:
                response = bedrock_client.converse(
                    modelId=model_id,
                    messages=[image_message],
                    system=system_prompts,
                    inferenceConfig={
                        "maxTokens": 4096,
                        "temperature": 0
                    },
                )
                # Extract and handle the response
                response_message = response['output']['message']['content'][0]['text']
                response_message = response_message.replace('"', '')
                # Remove the first line from the response_message to cleanup the model message
                response_message = '\n'.join(response_message.split('\n')[1:])
                
                # Convert to HTML or Markdown based on the user's choice
                if document_export_format_choice == 'H':
                    soup = BeautifulSoup(response_message, 'html.parser')
                    response_message = str("<!DOCTYPE html>" + soup.prettify())
                    page_number_tag = f"""<p>Page <data property="page">{page_num + 1}</data></p>"""
                    response_message = ''.join([response_message,page_number_tag ])
                    response_message_all = ''.join([response_message_all, response_message])

                else:
                    response_message = convert_html_to_markdown(response_message)
                    # a line break
                    
                    page_number_tag = f"""\n<br>Page: {page_num + 1} <br>\n"""
                    response_message = ''.join([response_message,page_number_tag ])
                    response_message_all = ''.join([response_message_all, response_message])

                # Save the response with the appropriate extension
                output_path = Path(folder_name) / f"{filename}_page_{page_num + 1}{document_export_extension}"

                with open(output_path, "w") as output_file:
                    output_file.write(response_message)
                    
            except Exception as e:
                print(f"Failed to process page {page_num + 1}: {str(e)}")

        # Clean up the HTML/Wiki markup using BeautifulSoup (if applicable)
        if document_export_format_choice == 'H':
            soup = BeautifulSoup(response_message_all, 'html.parser')
            response_message_all = str("<!DOCTYPE html>" + soup.prettify())

        # Write the cleaned HTML to a file
        cleaned_html_path = Path(folder_name) / f"{filename}_cleaned{document_export_extension}"
        with open(cleaned_html_path, "w", encoding="utf-8") as cleaned_html_file:
            cleaned_html_file.write(response_message_all)
            print(f"Cleaned HTML or Wiki saved to {cleaned_html_path}")
        
        # Do an audit check for PII entities and save to the audit file in audit directory
        if pii_audit_choice == 'Y':
            # Scan for PII entities in the response_message_all
            detected_pii = scan_for_pii(response_message_all,"pii-audit",filename)
            print(f"PII Audit Scan completed and saved to audit/{filename}_pii_audit.txt") 
        else:
            print("Skipping PII Audit Scan")
# Clean up the downloaded PDF
os.remove(pdf_path)


