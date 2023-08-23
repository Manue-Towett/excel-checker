import os
import warnings
import configparser

import pandas as pd

from utils import Logger

warnings.simplefilter("ignore")

config = configparser.ConfigParser()

with open("./settings/settings.ini", "r") as file:
    config.read_file(file)

INPUT_PATH = config.get("paths", "input")

OUTPUT_PATH = config.get("paths", "output")

MASTER_EXCEL_PATH = config.get("paths", "master")

PROCESSED_FILES_PATH = config.get("paths", "processed_files")

class ExcelProcessor:
    """Removes rows with blacklisted domains and duplicates from excel files"""
    def __init__(self) -> None:
        self.logger = Logger(__class__.__name__)
        self.logger.info("*****ExcelProcessor Started*****")

        self.input_files = [f for f in os.listdir(INPUT_PATH) if f.endswith(".xlsx")]

        self.logger.info("Input excel files found: {}".format(len(self.input_files)))

        self.blacklisted = self.__read_blacklisted_domains()

        self.processed = self.__read_master_excel()

        self.processed_files = self.__read_processed_files()
    
    def __read_excel_file(self, filename: str) -> list[dict[str, str]]:
        """Reads excel file and returns the data to be processed"""
        self.logger.info("Reading excel file >>> {}".format(filename))

        df = pd.read_excel(f"{INPUT_PATH}{filename}")

        self.logger.info("Rows found: {} || Processing...".format(len(df)))

        df  = df.dropna().drop_duplicates()

        return df.to_dict("records")
    
    def __read_blacklisted_domains(self) -> list[str]:
        """Reads the blacklisted domains from a text file"""
        self.logger.info("Retrieving blacklisted domains...")

        with open("./settings/blacklisted.txt", "r") as file:
            blacklist = list(filter(None, [domain.strip() for domain in file.readlines()]))
        
        self.logger.info("Blacklisted domains found: {}".format(len(blacklist)))

        return blacklist
    
    def __read_master_excel(self) -> list[str]:
        """Reads the processed domains from excel file"""
        processed_domains = []

        if os.path.isfile(f"{MASTER_EXCEL_PATH}master.xlsx"):
            self.logger.info("Retrieving processed domains...")

            df = pd.read_excel(f"{MASTER_EXCEL_PATH}master.xlsx")

            processed_domains = df["processed"].values.tolist()

            self.logger.info("Processed domains found: {}".format(len(processed_domains)))

        return processed_domains
    
    def __read_processed_files(self) -> list[str]:
        """Reads the files processed from a text file"""
        processed = []

        if os.path.isfile(f"{PROCESSED_FILES_PATH}processed_files.txt"):
            self.logger.info("Reading processed files...")

            with open(f"{PROCESSED_FILES_PATH}processed_files.txt", "r") as file:
                processed = list(filter(None, [line.strip() for line in file.readlines()]))

            self.logger.info("Processed files found: {}".format(len(processed)))
        
        return processed
    
    def __remove_blacklisted_domains(self, 
                                     data: list[dict[str, str]]) -> list[dict[str, str]]:
        """Removes blacklisted domains from the data"""
        self.logger.info("Removing blacklisted domains...")

        blacklist, non_blacklist = [], []

        for row in data:
            blacklisted = False

            for domain in self.blacklisted:
                if row["Domain"].endswith(domain):
                    self.logger.info("Blacklisted domain found >>> {}".format(row["Domain"]))
                    blacklisted = True
            
            if not blacklisted:
                non_blacklist.append(row)
            else:
                blacklist.append(row)
        
        self.logger.info(f"Blacklisted: {len(blacklist)} || Non-blacklisted: {len(non_blacklist)}")

        return non_blacklist
    
    def __remove_duplicated_domains(self,
                                    data: list[dict[str, str]]) -> list[dict[str, str]]:
        """Removes duplicated domains from the data"""
        self.logger.info("Removing duplicated domains...")

        duplicates, non_duplicates = [], []

        for row in data:
            if not row["Domain"] in self.processed:
                non_duplicates.append(row)
            else:
                self.logger.info("Duplicate domain found >>> {}".format(row["Domain"]))
                duplicates.append(row)
        
        self.logger.info(f"Duplicates: {len(duplicates)} || Non-duplicates: {len(non_duplicates)}")

        return non_duplicates
    
    def __save_processed_excel(self, data: list[dict[str, str]], filename: str) -> None:
        """Saves the processed excel file to the output folder"""
        self.logger.info("Saving data to excel...")

        name = filename.split("_")[0] + " - Duplicates Checked.xlsx"

        df = pd.DataFrame(data)

        df.to_excel(f"{OUTPUT_PATH}{name}", index=False)

        self.logger.info("Records saved to >> {}".format(name))
    
    def __file_to_text_file(self, filename: str) -> None:
        """Saves the processed file's name to a text file"""
        with open(f"{PROCESSED_FILES_PATH}processed_files.txt", mode="a") as file:
            file.write(filename.split("_")[0])
            file.write("\n")

    def __save_accepted_domains(self, domains: list[dict[str, str]]) -> None:
        """Saves accepted domains to a master excel file"""
        self.logger.info("Saving processed domains to master excel...")

        df = pd.DataFrame(domains)

        if not os.path.isfile(f"{MASTER_EXCEL_PATH}master.xlsx"):
            df.to_excel(f"{MASTER_EXCEL_PATH}master.xlsx", index=False)
        else:
            df_existing = pd.read_excel(f"{MASTER_EXCEL_PATH}master.xlsx")

            df = pd.concat([df_existing, df])

            df.to_excel(f"{MASTER_EXCEL_PATH}master.xlsx", index=False)
        
        self.logger.info("{} domains saved to master excel".format(len(domains)))
    
    def run(self) -> None:
        """Entry point to the excel processor"""
        processed, rejected = [], []

        for file in self.input_files:
            if file.split("_")[0] in self.processed_files:
                self.logger.info("Skipping processed file >> {}".format(file))
                
                rejected.append("")

                continue

            data = self.__read_excel_file(file)

            non_blacklisted = self.__remove_blacklisted_domains(data)

            non_duplicates = self.__remove_duplicated_domains(non_blacklisted)

            self.__save_processed_excel(non_duplicates, file)

            domains = [{"processed": row["Domain"]} for row in non_duplicates]

            self.__save_accepted_domains(domains)

            [self.processed.append(row["Domain"]) for row in non_duplicates]

            self.__file_to_text_file(file)

            self.processed_files.append(file.split("_")[0])

            processed.append("")
        
        self.logger.info("Done processing.")

        self.logger.info("Processed files: {} || Rejected files: {}".format(len(processed), len(rejected)))

if __name__ == "__main__":
    processor = ExcelProcessor()
    processor.run()