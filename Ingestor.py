from abc import ABC, abstractmethod
from QuoteEngine.QuoteModel import QuoteModel
import docx
import pandas as pd
import subprocess
import random
import os


class IngestorInterface(ABC):  # abstract base class
    """ This is docstring. """

    def __init__(self):
        pass

    @classmethod
    def can_ingest(cls, path: str) -> bool:
        pass  # return boolean

    @classmethod
    @abstractmethod
    def parse(cls, path: str) -> list:
        pass  # return  list[QuoteModel]


class TextIngestor(IngestorInterface):  # ingest .txt
    """Ingest text file"""

    @classmethod
    def parse(cls, path: str) -> list:
        """Parse quotes from a text"""
        list_quote = []
        with open(path, encoding='utf-8') as f:
            for line in f.readlines():
                if '-' not in line:
                    continue
                body = line.split('-')[0].strip()
                author = line.split('-')[1].strip().split('\n')[0]
                quote = QuoteModel(body, author)
                list_quote.append(quote)

        return list_quote


class CSVIngestor(IngestorInterface):
    """ ingest a CSV file"""

    @classmethod
    def parse(cls, path: str) -> list:
        """Parse quotes from a CSV"""
        df = pd.read_csv(path)
        list_quote = []
        for _, row in df.iterrows():
            body = row['body']
            author = row['author']
            quote = QuoteModel(body, author)
            list_quote.append(quote)
        return list_quote


class DocxIngestor(IngestorInterface):  # ingest .docx
    """Ingest text file"""

    @classmethod
    def parse(cls, path: str) -> list:
        """Parse quotes from a Doc"""

        list_quote = []
        doc = docx.Document(path)
        for line in doc.paragraphs:
            if '-' not in line.text:
                continue
            body = line.text.split('-')[0].replace('"', '').strip()
            author = line.text.split('-')[1].replace('"', '').strip()
            quote = QuoteModel(body, author)
            list_quote.append(quote)

        return list_quote


class PDFIngestor(IngestorInterface):  # ingest .pdf
    """ Ingest a pdf file"""

    @classmethod
    def parse(cls, path: str) -> list:
        """Parse quotes from a PDF file using pdftotext.

        :param path: A string path to a file containing quotes data.
        :return: A list of valid QuoteModel.
        """
        # tmp = f'./tmp/{random.randint(0, 10)}.txt'
        tmp='f./tmp/1.txt'
        # subprocess.call(['pdftotext', '-layout', path, tmp])
        subprocess.call(['pdftotext','-layout', path, tmp], shell=True)
        quotes = TextIngestor.parse(tmp)
        os.remove(tmp)
        return quotes


class Ingestor(IngestorInterface):
    fmt = ''  # format

    @classmethod
    def can_ingest(cls, path: str) -> bool:
        if path.split('.')[-1].lower() in ['csv', 'docx', 'pdf', 'txt']:
            cls.fmt = path.split('.')[-1].lower()
            return True
        else:
            return False

    @classmethod
    def parse(cls, path: str) -> list:

        dic = {'csv': CSVIngestor, 'docx': DocxIngestor, 'pdf': PDFIngestor, 'txt': TextIngestor}
        if cls.can_ingest(path):
            return dic[cls.fmt].parse(path)
        else:
            print("format only support 'csv','docx','pdf','txt'")
