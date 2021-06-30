from utils.domain.jsonlookupdomain import JSONLookupDomain
import sqlite3

class JSONLookupDomainLarge(JSONLookupDomain):

    def _load_db_to_memory(self, db_file_path : str):
        """ 
        Loads a sqllite3 database from file to memory in order to save I/O operations

        Note: this sub class of JSONLookupDomain supports large data bases 

        Args:
            db_file_path (str): absolute path to database file

        Returns:
            A sqllite3 connection
        """
        file_db = sqlite3.connect(db_file_path, check_same_thread=False)
        db = sqlite3.connect(':memory:', check_same_thread=False)
        file_db.backup(db)
        return db