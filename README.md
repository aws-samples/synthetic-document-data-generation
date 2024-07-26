# PoC Accelerator Synthetic Document Generator

The Synthetic Document Generator is a Python script that converts PDF documents into synthetic HTML or Markdown formats while preserving the structure and formatting of the original documents. It utilizes the Anthropic Bedrock Converse API, PyMuPDF, and Beautiful Soup libraries. Utilizing Amazon Comprehend's PII Detection, it performs a PII audit scan on the generated synthetic document to identify any personally identifiable information (PII) and saves the results to a reviewable audit file.

![Synthetic Document Generation Demo](assets/synthetic_doc_demo.gif)

## Features

- Convert PDF documents to synthetic HTML or Markdown format
- Option to generate synthetic (fake) data or use the original content
- Replace personally identifiable information (PII) with synthetic data in synthetic mode
- Preserve document structure and formatting (headings, paragraphs, lists, etc.)
- Support for multiple document formats (HTML, Markdown)
- Option to process a specific number of pages per document
- Choice between Anthropic's Sonnet or Haiku models
- User-defined system prompts to influence the conversion process
-  PII Audit Scanning: This feature utilizes Amazon Comprehend's PII Detection to scan the generated synthetic document for personally identifiable information (PII). The results of the scan are subsequently saved in an audit file for review and further analysis.

## Security and Data Handling Guidelines

1. Data Sensitivity: This tool is not intended to be used with sensitive personal data, such as personally identifiable information (PII) or protected health information (PHI). These guidelines explicitly state that users should "Avoid storing or processing any sensitive personal data" within the development environments. Ensure you are only sharing public or synthetic data, and not any real customer data.

2. PII Audit: The tool includes a PII audit feature that uses Amazon Comprehend to scan the generated synthetic documents for any detected PII. This can help identify and remove sensitive information. However, you should review the audit results carefully and ensure no PII is inadvertently included before sharing the documents.

3. Compliance: Customers should be aware of any industry-specific regulations or data privacy laws that may apply to the data they are working with, such as PCI-DSS or HIPAA. The use of this tool must align with the customer's own compliance requirements.

4. Consult with all internal company security guidelines and policies.


## Prerequisites

Before running the script, ensure that you have the following dependencies installed:

- Python 3.x
- boto3 (AWS SDK for Python)
- fitz (PyMuPDF)
- requests
- BeautifulSoup4
- html2text

## Setup

1. Clone the repository or download the source code.

2. (Optional but recommended) Create a virtual environment:

```
python -m venv env
```

3. Activate the virtual environment:

   - On Windows:
   ```
   env\Scripts\activate
   ```

   - On Unix or macOS:
   ```
   source env/bin/activate
   ```

4. Install the required Python packages using the `requirements.txt` file:

```
pip install -r requirements.txt
```

Additionally, you'll need an AWS account and the necessary permissions to use the Bedrock Runtime service.

## Usage

1. Run the script:

```
python synthetic_document_generator.py
```
2. Follow the prompts to provide the necessary information:
   - Enter the PDF URL (e.g., `https://aws-mp-standard-contracts.s3.amazonaws.com/Standard-Contact-for-AWS-Marketplace-2022-07-14.pdf`) or the local file path (e.g., `mydocument.pdf`). For local files, they should be placed in the same directory as the script.
   - Enter the number of documents to create (default: 1)
   - Choose the Anthropic model (Sonnet or Haiku)
   - Choose the export format (HTML or Wiki Markup)
   - Choose to create a synthetic document or use the original content
   - (Optional) Enter a system prompt to influence the conversion
   - (Optional) Enter the number of pages to process per document (default: all pages)
   - Choose to do a PII Audit Scan (default: Yes)

3. The script will download the PDF (if a URL is provided), convert each page to the specified format, and save the output files in a folder named with the first four characters of the PDF filename and the document iteration number.

4. The cleaned HTML or Markdown file for the entire document will be saved in the same folder with the `_cleaned` suffix.

5. The script will also perform a PII Audit Scan on the generated synthetic document and save the results in an audit file named `<filename>_pii_scan._audit.txt` in the `pii-audit` directory. This file will contain any detected PII entities, along with their type, score, offset, and value.

## Customization

You can customize the script by modifying the prompts or adding additional functionality as needed. The prompts used for synthetic document generation and real document conversion are defined in the script and can be modified as per your requirements.

## Example IAM Policy for Running


```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "comprehend:DetectPiiEntities"
            ],
            "Resource": "*"
        },
        {
            "Effect": "Allow",
            "Action": [
                "bedrock:InvokeModel"
            ],
            "Resource": [
                "arn:aws:bedrock:us-east-1:::foundation-model/anthropic.claude-3-sonnet-20240229-v1",
                "arn:aws:bedrock:us-east-1:::foundation-model/anthropic.claude-3-haiku-20240307-v1"
            ]
        }
    ]
}
```

## License

This project is licensed under the [MIT License](LICENSE).

## Notice:

This project requires and may incorporate or retrieve a number of third-party
software packages (such as open source packages) at install-time or build-time
or run-time ("External Dependencies"). The External Dependencies are subject to
license terms that you must accept in order to use this package. If you do not
accept all of the applicable license terms, you should not use this package. We
recommend that you consult your company’s open source approval policy before
proceeding.

Provided below is a list of External Dependencies and the applicable license
identification as indicated by the documentation associated with the External
Dependencies as of Amazon's most recent review.

THIS INFORMATION IS PROVIDED FOR CONVENIENCE ONLY. AMAZON DOES NOT PROMISE THAT
THE LIST OR THE APPLICABLE TERMS AND CONDITIONS ARE COMPLETE, ACCURATE, OR
UP-TO-DATE, AND AMAZON WILL HAVE NO LIABILITY FOR ANY INACCURACIES. YOU SHOULD
CONSULT THE DOWNLOAD SITES FOR THE EXTERNAL DEPENDENCIES FOR THE MOST COMPLETE
AND UP-TO-DATE LICENSING INFORMATION.

YOUR USE OF THE EXTERNAL DEPENDENCIES IS AT YOUR SOLE RISK. IN NO EVENT WILL
AMAZON BE LIABLE FOR ANY DAMAGES, INCLUDING WITHOUT LIMITATION ANY DIRECT,
INDIRECT, CONSEQUENTIAL, SPECIAL, INCIDENTAL, OR PUNITIVE DAMAGES (INCLUDING
FOR ANY LOSS OF GOODWILL, BUSINESS INTERRUPTION, LOST PROFITS OR DATA, OR
COMPUTER FAILURE OR MALFUNCTION) ARISING FROM OR RELATING TO THE EXTERNAL
DEPENDENCIES, HOWEVER CAUSED AND REGARDLESS OF THE THEORY OF LIABILITY, EVEN
IF AMAZON HAS BEEN ADVISED OF THE POSSIBILITY OF SUCH DAMAGES. THESE LIMITATIONS
AND DISCLAIMERS APPLY EXCEPT TO THE EXTENT PROHIBITED BY APPLICABLE LAW.

PyMuPDF (AGPL-3.0) - https://pymupdf.readthedocs.io



## Libraries

This script utilizes the following libraries:

- [PyMuPDF](https://pymupdf.readthedocs.io/en/latest/) for PDF manipulation
- [Beautiful Soup](https://www.crummy.com/software/BeautifulSoup/bs4/doc/) for HTML parsing and manipulation
- [html2text](https://github.com/Alir3z4/html2text) for HTML to Markdown conversion
- [Anthropic Bedrock Converse API](https://www.anthropic.com/bedrock) for document conversion
- [Detecting PII entities with Amazon Comprehend](https://docs.aws.amazon.com/comprehend/latest/dg/how-pii.html)